import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import tarfile
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / 'bin/grok-bot-update'
loader = importlib.machinery.SourceFileLoader('updater', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
updater = importlib.util.module_from_spec(spec)
loader.exec_module(updater)


class UpdaterTests(unittest.TestCase):
    def test_source_selection_ignores_partial_and_repacked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('grok-bot-old.rpm', 'grok-bot-new.deb', 'grok-bot.rpm.part', 'grok-bot.pkg.tar.zst'):
                (root / name).touch()
            os.utime(root / 'grok-bot-old.rpm', ns=(1, 1))
            os.utime(root / 'grok-bot-new.deb', ns=(2, 2))
            self.assertEqual(updater.choose_source(root).name, 'grok-bot-new.deb')

    def test_archive_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'bad.tar'
            with tarfile.open(archive, 'w') as tar:
                item = tarfile.TarInfo('../escaped')
                item.size = 1
                tar.addfile(item, io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
                updater.archive_names(archive)

    def test_archive_symlink_cannot_write_outside_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / 'stage'
            stage.mkdir()
            outside = root / 'outside'
            outside.mkdir()
            archive = root / 'grok-bot.rpm'
            with tarfile.open(archive, 'w') as tar:
                link = tarfile.TarInfo('./opt/link')
                link.type = tarfile.SYMTYPE
                link.linkname = str(outside)
                tar.addfile(link)
                item = tarfile.TarInfo('./opt/link/escaped')
                item.size = 1
                tar.addfile(item, io.BytesIO(b'x'))
            with self.assertRaises(updater.subprocess.CalledProcessError):
                updater.extract_payload(archive, stage)
            self.assertFalse((outside / 'escaped').exists())

    def test_shell_interpolation_inputs_are_rejected(self):
        for version, filename in [('1.2.3;touch /tmp/x', 'grok-bot.rpm'), ('1.2.3', '$(id).rpm')]:
            with self.assertRaises(ValueError):
                updater.pkgbuild(version, filename, 'a' * 64, False)

    def test_asar_reads_embedded_version_and_rejects_other_apps(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'app.asar'
            for name, expected in [('sand', '0.75.3'), ('another-app', None)]:
                data = json.dumps({'name': name, 'version': '0.75.3'}).encode()
                header = json.dumps({'files': {'package.json': {'size': len(data), 'offset': '0'}}}).encode()
                target.write_bytes(struct.pack('<4I', 4, len(header) + 8, len(header) + 4, len(header)) + header + data)
                if expected:
                    self.assertEqual(updater.app_version(target), expected)
                else:
                    with self.assertRaises(ValueError):
                        updater.app_version(target)

    def test_rejects_truncated_asar(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'app.asar'
            target.write_bytes(b'bad')
            with self.assertRaises(ValueError):
                updater.app_version(target)


if __name__ == '__main__':
    unittest.main()
