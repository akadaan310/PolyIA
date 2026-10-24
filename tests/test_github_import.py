"""Finite importer checks; no network or upstream source execution."""
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile
import unittest
import zipfile

from tools import github_import as importer


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.stage = self.root / 'stage'
        self.stage.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def entry(self, name, data):
        return {'path': name, 'bytes': len(data), 'sha256': importer.digest(data)}

    def payload(self, extra=None):
        data = b'Final commission.\n'
        entries = [self.entry('README.md', data), self.entry('sources/repos/demo/data.txt', b'source')]
        manifest = json.dumps({'files': entries}).encode()
        path = self.root / 'payload.tar.xz'
        with tarfile.open(path, 'w:xz') as archive:
            for name, value in [('README.md', data), (importer.MANIFEST, manifest)]:
                member = tarfile.TarInfo(name)
                member.size = len(value)
                member.mode = 0o644
                archive.addfile(member, io.BytesIO(value))
            if extra is not None:
                archive.addfile(extra, io.BytesIO(b'x' * extra.size))
        ready = {'schema_version': 1, 'payload': {'path': importer.PAYLOAD, 'bytes': path.stat().st_size,
                 'sha256': importer.digest(path.read_bytes())}, 'manifest_sha256': importer.digest(manifest)}
        return path, ready

    def snapshot(self):
        values = {'text.txt': (b'Preserved source\n', '100644'), 'run.sh': (b'#!/bin/sh\nexit 0\n', '100755')}
        path = self.root / 'snapshot.zip'
        records = []
        with zipfile.ZipFile(path, 'w') as archive:
            for name, (data, mode) in values.items():
                info = zipfile.ZipInfo('demo-012345/' + name)
                info.create_system = 3
                info.external_attr = int(mode, 8) << 16
                archive.writestr(info, data)
                record = self.entry('sources/repos/demo/' + name, data)
                record.update(repository_path=name, git_mode=mode, git_blob=importer.git_blob(data))
                records.append(record)
        repository = {'repository': 'akadaan310/demo', 'archive_sha256': importer.digest(path.read_bytes()),
                      'files': records, 'file_count': len(records), 'complete_tree': True, 'truncated': False}
        entries = {entry['path']: entry for entry in records}
        return path, repository, entries

    def test_payload_exact_hash_census_and_bytes(self):
        path, ready = self.payload()
        entries = importer.unpack_payload(path, ready, self.stage)
        self.assertEqual((self.stage / 'README.md').read_bytes(), b'Final commission.\n')
        self.assertEqual(len(entries), 2)
        self.assertFalse((self.stage / 'sources').exists())

    def test_payload_wrong_digest_refused_before_extraction(self):
        path, ready = self.payload()
        ready['payload']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            importer.unpack_payload(path, ready, self.stage)
        self.assertEqual(list(self.stage.iterdir()), [])

    def test_payload_traversal_and_git_paths_refused(self):
        for name in ('../escape', '/absolute', 'a/../../escape', '.git/config', 'a/.git/config', 'C:/drive', 'a\\escape'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                importer.relative(name)

    def test_payload_symlink_refused(self):
        member = tarfile.TarInfo('link')
        member.type = tarfile.SYMTYPE
        member.linkname = '../outside'
        path, ready = self.payload(member)
        with self.assertRaisesRegex(ValueError, 'regular payload files'):
            importer.unpack_payload(path, ready, self.stage)

    def test_payload_duplicate_member_refused(self):
        member = tarfile.TarInfo('README.md')
        path, ready = self.payload(member)
        with self.assertRaisesRegex(ValueError, 'Duplicate payload'):
            importer.unpack_payload(path, ready, self.stage)

    def test_payload_unregistered_member_refused(self):
        member = tarfile.TarInfo('extra.txt')
        path, ready = self.payload(member)
        with self.assertRaisesRegex(ValueError, 'file census differs'):
            importer.unpack_payload(path, ready, self.stage)

    def test_snapshot_hashes_and_executable_mode_preserved(self):
        path, repository, entries = self.snapshot()
        self.assertEqual(importer.copy_snapshot(path, repository, entries, self.stage), 2)
        self.assertEqual((self.stage / 'sources/repos/demo/text.txt').read_bytes(), b'Preserved source\n')
        self.assertEqual(stat.S_IMODE((self.stage / 'sources/repos/demo/run.sh').stat().st_mode), 0o755)

    def test_snapshot_git_blob_mismatch_refused(self):
        path, repository, entries = self.snapshot()
        repository['files'][0]['git_blob'] = '0' * 40
        with self.assertRaisesRegex(ValueError, 'blob mismatch'):
            importer.copy_snapshot(path, repository, entries, self.stage)

    def test_snapshot_archive_identity_mismatch_refused(self):
        path, repository, entries = self.snapshot()
        repository['archive_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'archive digest differs'):
            importer.copy_snapshot(path, repository, entries, self.stage)

    def test_snapshot_missing_file_refused(self):
        path, repository, entries = self.snapshot()
        repository['files'].pop()
        repository['file_count'] -= 1
        with self.assertRaisesRegex(ValueError, 'ZIP census differs'):
            importer.copy_snapshot(path, repository, entries, self.stage)

    def test_existing_conflicting_seed_refused_without_overwrite(self):
        root = self.root / 'checkout'
        root.mkdir()
        (root / 'README.md').write_bytes(b'Concurrent owner work')
        (self.stage / 'README.md').write_bytes(b'Final commission')
        (self.stage / importer.MANIFEST).write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, 'differs from final production'):
            importer.install_stage(self.stage, root, {'README.md': {}})
        self.assertEqual((root / 'README.md').read_bytes(), b'Concurrent owner work')

    def test_exact_staging_and_transport_deletion(self):
        root = self.root / 'checkout'
        root.mkdir()
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        transport = root / '.commission-import'
        transport.mkdir()
        (root / importer.READY).write_bytes(b'{}')
        (root / importer.PAYLOAD).write_bytes(b'payload')
        subprocess.run(['git', 'add', '--', importer.READY, importer.PAYLOAD], cwd=root, check=True)
        (self.stage / 'README.md').write_bytes(b'Final commission')
        (self.stage / importer.MANIFEST).write_bytes(b'{}')
        entries = {'README.md': self.entry('README.md', b'Final commission')}
        importer.install_stage(self.stage, root, entries)
        importer.stage_git(root, entries)
        self.assertFalse(transport.exists())
        paths = subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines()
        self.assertEqual(paths, ['MANIFEST_SHA256.json', 'README.md'])


if __name__ == '__main__':
    unittest.main()
