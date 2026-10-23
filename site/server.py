#!/usr/bin/env python3
"""Static tools hub with private, aggregate download-link counters."""
import argparse
import csv
from contextlib import contextmanager
from datetime import datetime, timezone
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import sys
from urllib.parse import parse_qs, urlsplit

PROJECTS = {
    'grok-bot-arch': 'https://github.com/danimoya/grok-bot-arch/releases/download/v0.1.0/grok-bot-arch-v0.1.0.zip',
    'google-drive': 'https://github.com/danimoya/omarchy-google-drive/archive/refs/heads/main.zip',
    'animated-screensaver': 'https://github.com/danimoya/omarchy-animated-screensaver/archive/refs/heads/main.zip',
    'monitor-mirror': 'https://github.com/danimoya/omarchy-monitor-mirror/archive/refs/heads/main.zip',
}
SOURCES = {'direct', 'reddit', 'linkedin', 'discord', 'x', 'mastodon', 'devto', 'hn', 'github', 'newsletter'}


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('''CREATE TABLE IF NOT EXISTS downloads (
        day TEXT NOT NULL, project TEXT NOT NULL, source TEXT NOT NULL,
        requests INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day, project, source))''')
    try:
        with db:
            yield db
    finally:
        db.close()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, database, **kwargs):
        self.database = database
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        # Counters retain no IP addresses, cookies, or visitor identifiers.
        pass

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None

    def do_HEAD(self):
        self.route(head=True)

    def do_GET(self):
        self.route(head=False)

    def route(self, head=False):
        path = urlsplit(self.path)
        if path.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '3')
            self.end_headers()
            if not head:
                self.wfile.write(b'ok\n')
            return
        if path.path.startswith('/download/'):
            slug = path.path.removeprefix('/download/').rstrip('/')
            if slug not in PROJECTS:
                self.send_error(404)
                return
            source = parse_qs(path.query).get('source', ['direct'])[0]
            if source not in SOURCES:
                source = 'direct'
            agent = self.headers.get('User-Agent', '').lower()
            is_preview = any(word in agent for word in ('bot', 'spider', 'crawler', 'slack', 'preview'))
            if not head and not is_preview:
                try:
                    with connect(self.database) as db:
                        db.execute('''INSERT INTO downloads(day, project, source, requests) VALUES(?,?,?,1)
                                      ON CONFLICT(day,project,source) DO UPDATE SET requests=requests+1''',
                                   (datetime.now(timezone.utc).date().isoformat(), slug, source))
                except sqlite3.Error:
                    # Download links remain usable if counting temporarily fails.
                    print('Counter write failed', file=sys.stderr, flush=True)
            self.send_response(302)
            self.send_header('Location', PROJECTS[slug])
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if path.path == '/grok-bot':
            self.send_response(301)
            self.send_header('Location', '/grok-bot/')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        # No HTTP endpoint serves counter records; only the operator CLI can read them.
        if path.path.startswith(('/admin', '/stats', '/metrics', '/data')):
            self.send_error(404)
            return
        if head:
            super().do_HEAD()
        else:
            super().do_GET()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('serve', 'stats', 'export', 'backup'), nargs='?', default='serve')
    parser.add_argument('--database', default=os.environ.get('TOOLS_DATABASE', '/data/downloads.sqlite3'))
    parser.add_argument('--directory', default=os.environ.get('TOOLS_PUBLIC', '/app/public'))
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--output', help='backup destination, outside the public directory')
    args = parser.parse_args()
    with connect(args.database) as db:
        if args.command in ('stats', 'export'):
            rows = db.execute('SELECT day, project, source, requests FROM downloads ORDER BY day, project, source').fetchall()
            if args.command == 'export':
                writer = csv.writer(sys.stdout)
                writer.writerow(('day_utc', 'project', 'source', 'download_link_requests'))
                writer.writerows(rows)
            else:
                print(json.dumps([dict(zip(('day_utc', 'project', 'source', 'download_link_requests'), row)) for row in rows], indent=2))
            return
        if args.command == 'backup':
            if not args.output:
                parser.error('backup requires --output')
            with sqlite3.connect(args.output) as dest:
                db.backup(dest)
            return
    handler = functools.partial(Handler, directory=args.directory, database=args.database)
    server = ThreadingHTTPServer(('0.0.0.0', args.port), handler)
    print(f'Tools hub listening on {args.port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
