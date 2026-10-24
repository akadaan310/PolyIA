#!/usr/bin/env python3
"""One-time, fail-closed reconstruction of the source-bearing GitHub commission.

Only this package's verifier executes. Preserved upstream source remains data.
The final checkout has no dependency on this transport archive or on submodules.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
READY = '.commission-import/READY.json'
PAYLOAD = '.commission-import/payload.tar.xz'
MANIFEST = 'MANIFEST_SHA256.json'
MAX_FILE = 64 * 1024 * 1024
MAX_ARCHIVE = 128 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_FILES = 5000
HEX64 = re.compile(r'^[0-9a-f]{64}$')
HEX40 = re.compile(r'^[0-9a-f]{40}$')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def relative(name):
    require(isinstance(name, str) and name and len(name) <= 4096, 'Invalid archive path')
    require('\\' not in name and '\0' not in name and not name.startswith('/'), 'Unsafe archive path')
    parts = name.split('/')
    require(all(part not in ('', '.', '..', '.git') for part in parts), 'Unsafe archive path component')
    require(parts[0] != '.commission-import', 'Payload must not contain its own transport')
    require(not re.match(r'^[A-Za-z]:', name), 'Drive path refused')
    return PurePosixPath(name)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique_object)


def manifest_entries(data):
    document = decode(data)
    entries = {}
    require(isinstance(document.get('files'), list) and len(document['files']) <= MAX_FILES, 'Invalid manifest census')
    total = 0
    for entry in document['files']:
        name = str(relative(entry['path']))
        require(name != MANIFEST and name not in entries, 'Duplicate or self-referential manifest entry')
        require(type(entry['bytes']) is int and 0 <= entry['bytes'] <= MAX_FILE, 'Invalid manifest byte budget')
        require(isinstance(entry['sha256'], str) and HEX64.fullmatch(entry['sha256']), 'Invalid manifest digest')
        entries[name] = entry
        total += entry['bytes']
    require(total <= MAX_TOTAL, 'Manifest exceeds aggregate byte budget')
    return entries


def capture_regular(path, maximum=MAX_FILE):
    require(not path.is_symlink() and path.is_file(), 'Expected a regular file: ' + str(path))
    require(path.stat().st_size <= maximum, 'File exceeds byte budget: ' + str(path))
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    require(len(data) <= maximum, 'File grew beyond byte budget')
    return data


def write_new(root, name, data, mode=0o644):
    target = root.joinpath(*relative(name).parts)
    parent = root
    for part in relative(name).parts[:-1]:
        parent = parent / part
        require(not parent.is_symlink(), 'Symlink parent refused')
        parent.mkdir(exist_ok=True)
    if target.exists() or target.is_symlink():
        require(capture_regular(target) == data, 'Existing file differs: ' + name)
    else:
        with target.open('xb') as stream:
            stream.write(data)
    target.chmod(mode)


def unpack_payload(archive_path, ready, stage):
    payload = ready.get('payload', {})
    require(ready.get('schema_version') == 1 and payload.get('path') == PAYLOAD, 'Unsupported READY contract')
    require(type(payload.get('bytes')) is int and 0 < payload['bytes'] <= MAX_ARCHIVE, 'Invalid payload size')
    require(isinstance(payload.get('sha256'), str) and HEX64.fullmatch(payload['sha256']), 'Invalid payload digest')
    require(isinstance(ready.get('manifest_sha256'), str) and HEX64.fullmatch(ready['manifest_sha256']), 'Invalid manifest pin')
    archive_bytes = capture_regular(archive_path, MAX_ARCHIVE)
    require(len(archive_bytes) == payload['bytes'] and digest(archive_bytes) == payload['sha256'], 'Payload identity mismatch')
    with tarfile.open(archive_path, mode='r:xz') as archive:
        members = {}
        total = 0
        for member in archive:
            require(len(members) < MAX_FILES, 'Too many payload members')
            name = str(relative(member.name))
            require(member.isfile(), 'Only regular payload files are allowed')
            require(name not in members, 'Duplicate payload member')
            require(0 <= member.size <= MAX_FILE, 'Payload member exceeds byte budget')
            total += member.size
            require(total <= MAX_TOTAL, 'Payload expansion exceeds aggregate budget')
            members[name] = member
        require(MANIFEST in members, 'Payload has no final manifest')
        with archive.extractfile(members[MANIFEST]) as stream:
            manifest_bytes = stream.read(MAX_FILE + 1)
        require(digest(manifest_bytes) == ready['manifest_sha256'], 'Final manifest pin mismatch')
        entries = manifest_entries(manifest_bytes)
        expected = {name for name in entries if not name.startswith('sources/repos/')} | {MANIFEST}
        require(set(members) == expected, 'Payload file census differs from final manifest')
        for name, member in members.items():
            with archive.extractfile(member) as stream:
                data = stream.read(member.size + 1)
            require(len(data) == member.size, 'Truncated payload member')
            if name != MANIFEST:
                require(len(data) == entries[name]['bytes'] and digest(data) == entries[name]['sha256'], 'Payload member identity mismatch: ' + name)
            write_new(stage, name, data, 0o755 if member.mode & 0o111 else 0o644)
    return entries


def snapshot_url(repository):
    name, commit = repository['repository'], repository['commit']
    require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name), 'Invalid repository identity')
    require(isinstance(commit, str) and HEX40.fullmatch(commit), 'Repository commit must be pinned')
    url = 'https://codeload.github.com/' + name + '/zip/' + commit
    require(repository['acquisition_url'] == url, 'Repository download URL differs from its pin')
    return url


def download(url, destination):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'PolyIA-Commission-Importer/1.0'})
            started = time.monotonic()
            with urllib.request.urlopen(request, timeout=30) as response, destination.open('wb') as output:
                require(response.geturl().startswith('https://codeload.github.com/'), 'Unexpected download redirect')
                count = 0
                while True:
                    chunk = response.read(512 * 1024)
                    if not chunk:
                        break
                    count += len(chunk)
                    require(count <= MAX_ARCHIVE and time.monotonic() - started <= 180, 'Repository download exceeds budget')
                    output.write(chunk)
            return
        except (urllib.error.URLError, TimeoutError, OSError):
            if destination.exists():
                destination.unlink()
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def copy_snapshot(archive_path, repository, entries, stage):
    raw = capture_regular(archive_path, MAX_ARCHIVE)
    require(digest(raw) == repository['archive_sha256'], 'Pinned repository archive digest differs: ' + repository['repository'])
    files = repository['files']
    require(repository['complete_tree'] is True and repository['truncated'] is False, 'Incomplete pinned Git tree')
    require(len(files) == repository['file_count'] and len(files) <= MAX_FILES, 'Repository file count differs')
    expected = {str(relative(entry['repository_path'])): entry for entry in files}
    require(len(expected) == len(files), 'Duplicate repository file')
    prefix = 'sources/repos/' + repository['repository'].split('/')[-1] + '/'
    with zipfile.ZipFile(archive_path) as archive:
        members = {}
        roots = set()
        total = 0
        require(len(archive.infolist()) <= MAX_FILES, 'Too many repository ZIP entries')
        for info in archive.infolist():
            name = info.filename.rstrip('/') if info.is_dir() else info.filename
            parts = relative(name).parts
            roots.add(parts[0])
            require(len(roots) == 1, 'Repository ZIP has multiple roots')
            kind = stat.S_IFMT(info.external_attr >> 16)
            require(kind in (0, stat.S_IFREG, stat.S_IFDIR), 'Repository link or special file refused')
            if info.is_dir():
                continue
            require(len(parts) > 1, 'Repository member is outside archive root')
            key = '/'.join(parts[1:])
            require(key not in members, 'Duplicate repository ZIP path')
            require(info.file_size <= MAX_FILE, 'Repository file exceeds budget')
            total += info.file_size
            require(total <= MAX_TOTAL, 'Repository ZIP exceeds expansion budget')
            members[key] = info
        require(set(members) == set(expected), 'Pinned repository ZIP census differs: ' + repository['repository'])
        for key, entry in expected.items():
            name = prefix + key
            require(entry['path'] == name and name in entries, 'Repository path does not match final manifest')
            require(entry['git_mode'] in ('100644', '100755'), 'Unsupported source Git mode')
            info = members[key]
            require(info.file_size == entry['bytes'], 'Repository member size mismatch')
            source_mode = (info.external_attr >> 16) & 0o777
            if source_mode:
                require(bool(source_mode & 0o111) == (entry['git_mode'] == '100755'), 'Repository executable-mode mismatch')
            data = archive.read(info)
            require(len(data) == entry['bytes'] and digest(data) == entry['sha256'] and git_blob(data) == entry['git_blob'], 'Pinned repository blob mismatch: ' + name)
            require(len(data) == entries[name]['bytes'] and digest(data) == entries[name]['sha256'], 'Repository blob differs from final manifest')
            write_new(stage, name, data, 0o755 if entry['git_mode'] == '100755' else 0o644)
    return len(files)


def verify_package(root):
    subprocess.run([sys.executable, str(root / 'tools/verify_package.py'), '--require-release-manifest'], cwd=root, check=True)


def install_stage(stage, root, entries):
    expected = set(entries) | {MANIFEST}
    # Refuse overwriting concurrent or unrelated seed work before copying anything.
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in list(dirs):
            child = parent / name
            if parent == root and name in ('.git', '.commission-import'):
                dirs.remove(name)
                continue
            require(not child.is_symlink(), 'Existing directory symlink refused')
        for name in files:
            path = parent / name
            rel = path.relative_to(root).as_posix()
            if rel == '.git':
                continue
            require(rel in expected, 'Unrelated seed file refused: ' + rel)
            require(capture_regular(path) == capture_regular(stage / rel), 'Seed file differs from final production: ' + rel)
    for name in sorted(expected):
        source = stage / name
        write_new(root, name, capture_regular(source), stat.S_IMODE(source.stat().st_mode))
    transport = root / '.commission-import'
    require(not transport.is_symlink() and {p.name for p in transport.iterdir()} == {'READY.json', 'payload.tar.xz'}, 'Unexpected transport directory contents')
    for name in (READY, PAYLOAD):
        path = root / name
        require(not path.is_symlink() and path.is_file(), 'Transport cleanup target changed')
        path.unlink()
    transport.rmdir()


def stage_git(root, entries):
    expected = set(entries) | {MANIFEST}
    paths = sorted(expected) + [READY, PAYLOAD]
    environment = dict(os.environ, GIT_LITERAL_PATHSPECS='1')
    subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'core.safecrlf=false', 'add', '--all', '--force',
                    '--pathspec-from-file=-', '--pathspec-file-nul'], cwd=root,
                   input=('\0'.join(paths) + '\0').encode(), env=environment, check=True)
    output = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)
    index = {}
    for item in output.split(b'\0'):
        if not item:
            continue
        metadata, raw_path = item.split(b'\t', 1)
        mode, blob, stage = metadata.decode('ascii').split()
        require(stage == '0', 'Unmerged Git index refused')
        index[raw_path.decode('utf-8')] = (mode, blob)
    require(set(index) == expected, 'Staged Git file census differs from final manifest')
    for name in expected:
        path = root / name
        require(index[name] == ('100755' if path.stat().st_mode & 0o111 else '100644', git_blob(capture_regular(path))),
                'Git staging changed source bytes or mode: ' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage-git', action='store_true')
    args = parser.parse_args()
    imported = False
    if (ROOT / READY).exists():
        ready = decode(capture_regular(ROOT / READY, 1024 * 1024))
        require(ready.get('expected_repository_count') == 8 and ready.get('expected_repository_files') == 757, 'Unexpected canonical snapshot contract')
        with tempfile.TemporaryDirectory(prefix='polyia-github-import-') as directory:
            temporary = Path(directory)
            stage = temporary / 'stage'
            stage.mkdir()
            entries = unpack_payload(ROOT / PAYLOAD, ready, stage)
            repositories = decode(capture_regular(stage / 'registry/repositories.json'))['repositories']
            require(len(repositories) == 8 and len({r['repository'] for r in repositories}) == 8, 'Repository census mismatch')
            copied = 0
            for number, repository in enumerate(repositories):
                archive = temporary / (str(number) + '.zip')
                download(snapshot_url(repository), archive)
                copied += copy_snapshot(archive, repository, entries, stage)
                print(json.dumps({'repository': repository['repository'], 'commit': repository['commit'], 'verified_files': repository['file_count']}), flush=True)
            require(copied == 757, 'Canonical source blob census mismatch')
            verify_package(stage)
            install_stage(stage, ROOT, entries)
        verify_package(ROOT)
        if args.stage_git:
            stage_git(ROOT, entries)
        imported = True
    else:
        require(not (ROOT / PAYLOAD).exists(), 'Payload exists without its READY marker')
        verify_package(ROOT)
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a', encoding='utf-8') as stream:
            stream.write('imported=' + ('true' if imported else 'false') + '\n')
    print(json.dumps({'ok': True, 'imported': imported, 'status': 'EXTRACTED_AND_VERIFIED' if imported else 'ALREADY_IMPORTED',
                      'mission_status': 'NOT_COMMISSIONED'}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, tarfile.TarError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': type(error).__name__, 'message': str(error)}), file=sys.stderr)
        sys.exit(1)
