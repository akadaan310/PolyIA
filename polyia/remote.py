"""Durable, bounded HTTP command client; no tokens are stored in its journal.

This is an explicitly configured network client, separate from pure kernels.
An unresolved command keeps its original ID/request across process restarts.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import urllib.error
import urllib.parse
import urllib.request


MAX_REQUEST = 64 * 1024
MAX_RESPONSE = 16 * 1024 * 1024
IDENTIFIER = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
DIGEST = re.compile(r'^[0-9a-f]{64}$')


class RemoteError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                          allow_nan=False)
    except (ValueError, TypeError, RecursionError, OverflowError) as error:
        raise RemoteError('INVALID_COMMAND', 'Input must be finite bounded JSON') from error


def _command(value):
    if (type(value) is not dict or set(value) != {'command_id', 'kind', 'payload', 'expected_revision'}
            or not isinstance(value['command_id'], str) or not IDENTIFIER.fullmatch(value['command_id'])
            or type(value['expected_revision']) is not int or value['expected_revision'] < 0
            or not isinstance(value['kind'], str) or not IDENTIFIER.fullmatch(value['kind'])
            or type(value['payload']) is not dict):
        raise RemoteError('INVALID_COMMAND', 'Use a complete guarded command with a stable ID and integer revision')
    raw = _json(value)
    if len(raw.encode()) > MAX_REQUEST:
        raise RemoteError('REQUEST_TOO_LARGE', 'Command exceeds 64 KiB')
    return raw


def _digest(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def _has_credential(value, credential):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, str) and credential in item:
            return True
        if isinstance(item, dict):
            pending.extend(item.keys()); pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return False


def _private_file(path):
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise RemoteError('UNSAFE_JOURNAL', 'Journal files must be owned private regular files')
        return False
    else:
        os.close(fd)
        return True


class RemoteClient:
    def __init__(self, origin, token, journal, *, allow_loopback_http=False, timeout=10):
        try:
            parts = urllib.parse.urlsplit(origin)
            valid = (parts.hostname and parts.path == '' and not parts.query and not parts.fragment
                     and parts.username is None and parts.password is None and parts.port != 0
                     and not any(c.isspace() for c in origin)
                     and (parts.scheme == 'https' or allow_loopback_http and parts.scheme == 'http'
                          and parts.hostname in ('127.0.0.1', '::1')))
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise RemoteError('UNSAFE_ORIGIN', 'Use one HTTPS origin; only explicit literal loopback HTTP is permitted for tests')
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise RemoteError('INVALID_CREDENTIAL', 'Provide a bearer credential without whitespace')
        if type(timeout) not in (int, float) or not 0 < timeout <= 60:
            raise RemoteError('INVALID_TIMEOUT', 'Timeout must be positive and at most 60 seconds')
        self.origin, self._token, self.timeout = origin, token, timeout
        self.path = Path(journal).absolute()
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        parent = self.path.parent.lstat()
        if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid() or parent.st_mode & 0o077:
            raise RemoteError('UNSAFE_JOURNAL', 'Journal directory must be owned and private')
        lock = self.path.with_name(self.path.name + '.lock')
        _private_file(lock)
        self._lock = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
        self._db = None
        self._protocol_checked = False
        self._opener = urllib.request.build_opener(_NoRedirect())
        try:
            with self._locked():
                created = _private_file(self.path)
                self._db = sqlite3.connect(self.path, timeout=5)
                self._db.row_factory = sqlite3.Row
                self._db.execute('PRAGMA synchronous=FULL')
                if created:
                    with self._db:
                        self._db.execute('CREATE TABLE configuration(origin TEXT NOT NULL, schema_version INTEGER NOT NULL)')
                        self._db.execute('INSERT INTO configuration VALUES(?,1)', (origin,))
                        self._db.execute('CREATE TABLE requests(command_id TEXT PRIMARY KEY, request_json TEXT NOT NULL, request_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN (\'PENDING\',\'DONE\',\'REFUSED\')), response_json TEXT)')
                        self._db.execute("CREATE UNIQUE INDEX one_pending ON requests(state) WHERE state='PENDING'")
                rows = self._db.execute('SELECT * FROM configuration').fetchall()
                if len(rows) != 1 or rows[0]['schema_version'] != 1:
                    raise RemoteError('JOURNAL_INTEGRITY', 'Unsupported or damaged client journal')
                if rows[0]['origin'] != origin:
                    raise RemoteError('ORIGIN_CHANGED', 'A journal is bound to its original service origin')
                if self._db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise RemoteError('JOURNAL_INTEGRITY', 'Client journal integrity check failed')
        except Exception:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if self._db is not None:
            self._db.close(); self._db = None
        if self._lock is not None:
            os.close(self._lock); self._lock = None

    @contextmanager
    def _locked(self):
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RemoteError('CLIENT_BUSY', 'Another process is using this client journal') from error
        try:
            yield
        finally:
            fcntl.flock(self._lock, fcntl.LOCK_UN)

    def _request(self, path, body=None):
        # No redirect can forward the credential to a second origin. TLS uses
        # the standard verified trust store; callers cannot disable verification.
        req = urllib.request.Request(self.origin + path, data=None if body is None else _command(body).encode(),
            headers={'Authorization': 'Bearer ' + self._token, 'Content-Type': 'application/json'})
        try:
            try:
                response = self._opener.open(req, timeout=self.timeout)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                status, data = response.code, response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE or self._token.encode() in data:
                raise RemoteError('UNCERTAIN', 'Response exceeds the client boundary or contains credential material')
            result = json.loads(data, object_pairs_hook=_pairs,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite response')))
            if _has_credential(result, self._token):
                raise RemoteError('UNCERTAIN', 'Response contains configured credential material')
            return status, result
        except (OSError, ValueError, RecursionError, urllib.error.URLError) as error:
            raise RemoteError('UNCERTAIN', 'No trustworthy response was received; retain and recover the same command ID') from error

    def state(self):
        self._check_protocol()
        status, result = self._request('/v1/state')
        if status != 200 or type(result) is not dict or type(result.get('revision')) is not int:
            raise RemoteError('READ_FAILED', 'No valid state response was received')
        return result

    def _check_protocol(self):
        if not self._protocol_checked:
            status, result = self._request('/.well-known/polyia.json')
            if (status != 200 or type(result) is not dict or result.get('protocol') != 'polyia.command-plane'
                    or result.get('protocol_version') != '1.0.0' or result.get('api_base') != '/v1'):
                raise RemoteError('PROTOCOL_MISMATCH', 'This client requires polyia.command-plane 1.0.0 at /v1; pending requests remain retained')
            self._protocol_checked = True

    def _checked(self, row):
        try:
            command = json.loads(row['request_json'])
            raw = _command(command)
            if raw != row['request_json'] or _digest(raw) != row['request_sha256'] or command['command_id'] != row['command_id']:
                raise ValueError('request identity mismatch')
            response = None if row['response_json'] is None else json.loads(row['response_json'])
            if (row['state'] == 'PENDING') != (response is None):
                raise ValueError('response lifecycle mismatch')
            return command, response
        except (ValueError, KeyError, TypeError, RemoteError) as error:
            raise RemoteError('JOURNAL_INTEGRITY', 'Stored command identity is damaged') from error

    def pending(self):
        row = self._db.execute("SELECT * FROM requests WHERE state='PENDING'").fetchone()
        return None if row is None else self._checked(row)[0]

    @staticmethod
    def _valid_receipt(command, result):
        return (type(result) is dict and result.get('ok') is True
                and result.get('command_id') == command['command_id'] and result.get('actor') == 'operator'
                and type(result.get('revision')) is int and result['revision'] == command['expected_revision'] + 1
                and isinstance(result.get('head'), str) and DIGEST.fullmatch(result['head'])
                and type(result.get('result')) is dict)

    def _resolve(self, command, status, result, *, retained=False):
        if _has_credential(result, self._token):
            raise RemoteError('UNCERTAIN', 'Receipt contains configured credential material')
        accepted = status == 200 and self._valid_receipt(command, result)
        error = result.get('error', {}) if type(result) is dict else {}
        details = error.get('details', {}) if type(error) is dict else {}
        refused = (status == 409 and type(error) is dict and error.get('code') == 'REVISION_CONFLICT' and type(details) is dict
                   and type(details.get('expected_revision')) is int and details['expected_revision'] == command['expected_revision']
                   and type(details.get('current_revision')) is int and details['current_revision'] >= 0
                   and details['current_revision'] != command['expected_revision'])
        if not accepted and not refused:
            raise RemoteError('UNCERTAIN', 'Receipt is unresolved; recover the original command before issuing new work')
        if not retained:
            with self._db:
                self._db.execute('UPDATE requests SET state=?,response_json=? WHERE command_id=?',
                    ('DONE' if accepted else 'REFUSED', _json(result), command['command_id']))
        if refused:
            raise RemoteError('REVISION_CONFLICT', 'The original command was definitively refused at its stale revision')
        return result

    def submit(self, command):
        raw = _command(command)
        # Serialize/parse severs aliases to mutable caller data before dispatch.
        command = json.loads(raw)
        if _has_credential(command, self._token):
            raise RemoteError('CREDENTIAL_IN_COMMAND', 'Do not place the configured credential in command data')
        with self._locked():
            row = self._db.execute('SELECT * FROM requests WHERE command_id=?', (command['command_id'],)).fetchone()
            if row is not None:
                original, response = self._checked(row)
                if row['request_json'] != raw:
                    raise RemoteError('ID_REUSE', 'A command ID cannot name different request bytes')
                if response is not None:
                    return self._resolve(command, 200 if row['state'] == 'DONE' else 409, response, retained=True)
            else:
                if self.pending() is not None:
                    raise RemoteError('PENDING_COMMAND', 'Recover the existing unresolved command first')
                with self._db:
                    self._db.execute('INSERT INTO requests VALUES(?,?,?,\'PENDING\',NULL)', (command['command_id'], raw, _digest(raw)))
            self._check_protocol()
            return self._resolve(command, *self._request('/v1/commands', command))

    def recover(self):
        with self._locked():
            command = self.pending()
            if command is None:
                raise RemoteError('NO_PENDING_COMMAND', 'No unresolved request is stored')
            self._check_protocol()
            # A GET receipt has no request digest and can belong to a conflicting
            # request with this ID/revision. Only exact POST replay asks the
            # server to compare the complete actor-bound request identity.
            return self._resolve(command, *self._request('/v1/commands', command))


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Poly IA durable HTTP command client')
    parser.add_argument('--origin', default=os.environ.get('POLYIA_PUBLIC_ORIGIN'), required=not os.environ.get('POLYIA_PUBLIC_ORIGIN'))
    parser.add_argument('--journal', required=True, type=Path)
    parser.add_argument('--token-env', choices=['POLYIA_OPERATOR_TOKEN', 'POLYIA_READ_TOKEN'], default='POLYIA_OPERATOR_TOKEN')
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('state'); commands.add_parser('pending'); commands.add_parser('recover')
    submit = commands.add_parser('submit'); submit.add_argument('--file', type=Path, required=True)
    args = parser.parse_args()
    try:
        with RemoteClient(args.origin, os.environ.get(args.token_env), args.journal) as client:
            if args.action == 'submit':
                with args.file.open('rb') as source:
                    raw = source.read(MAX_REQUEST + 1)
                if len(raw) > MAX_REQUEST:
                    raise RemoteError('REQUEST_TOO_LARGE', 'Command exceeds 64 KiB')
                value = client.submit(json.loads(raw, object_pairs_hook=_pairs,
                    parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite input'))))
            else:
                value = getattr(client, args.action)()
            print(json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False))
    except (RemoteError, OSError, ValueError, sqlite3.Error) as error:
        # Do not expose raw URLs, credentials, file bytes or remote error bodies.
        print(json.dumps({'ok': False, 'code': getattr(error, 'code', 'CLIENT_ERROR'),
                          'message': str(error) if isinstance(error, RemoteError) else 'Client input or journal operation failed'}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
