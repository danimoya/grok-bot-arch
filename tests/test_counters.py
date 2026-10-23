import functools
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

spec = importlib.util.spec_from_file_location('hub', Path(__file__).resolve().parents[1] / 'site/server.py')
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class CounterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'index.html').write_text('hub')
        self.db = self.root / 'private' / 'counts.db'
        self.db.parent.mkdir()
        with hub.connect(self.db):
            pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(hub.Handler, directory=self.root, database=self.db))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.client = urllib.request.build_opener(NoRedirect())

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def get(self, path, method='GET', agent='human-browser'):
        try:
            return self.client.open(urllib.request.Request(self.url + path, method=method, headers={'User-Agent': agent}))
        except urllib.error.HTTPError as response:
            return response

    def test_counts_persist_and_redirect_is_fixed(self):
        response = self.get('/download/google-drive?source=reddit&url=https://example.com')
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers['Location'], hub.PROJECTS['google-drive'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        response.close()
        with hub.connect(self.db) as db:
            rows = db.execute('SELECT project,source,requests FROM downloads').fetchall()
        self.assertEqual(rows, [('google-drive', 'reddit', 1)])

    def test_head_and_known_previews_do_not_count(self):
        for method, agent in [('HEAD', 'human-browser'), ('GET', 'LinkedInBot'), ('GET', 'Twitterbot')]:
            self.get('/download/grok-bot-arch', method, agent).close()
        with hub.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM downloads').fetchone()[0], 0)

    def test_unknown_project_and_public_stats_are_unavailable(self):
        for path in ['/download/unknown', '/stats', '/admin', '/metrics', '/data/downloads.sqlite3']:
            with self.get(path) as response:
                self.assertEqual(response.code, 404)

    def test_arbitrary_source_not_stored_and_static_page_not_counted(self):
        self.get('/download/monitor-mirror?source=private-user-email').close()
        with self.get('/') as response:
            self.assertEqual(response.read(), b'hub')
        with hub.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT source,requests FROM downloads').fetchall(), [('direct', 1)])


if __name__ == '__main__':
    unittest.main()
