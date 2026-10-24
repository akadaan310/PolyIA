"""Loopback-only HTTP projection of the durable Poly IA command ledger.

This is a portable commissioning server. It performs no inference, executes no
ambient host code, and delegates all state changes to Ledger.command. Typed
Poly IA programs run only through the bounded registered native interpreter.
"""
from __future__ import annotations

import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import logging
import math
from pathlib import Path
import re
import socket
import threading
import time
from urllib.parse import parse_qs, unquote_to_bytes, urlsplit
import uuid

from .store import CommandError, REGISTERED_EXPERIMENTS

MAX_BODY_BYTES = 64 * 1024
MAX_HEADER_BYTES = 16 * 1024
MAX_JSON_DEPTH = 32
MAX_PAGE_SIZE = 1000
SOCKET_TIMEOUT = 10
MAX_ACTIVE_REQUESTS = 32
REQUEST_RATE = 20.0
REQUEST_BURST = 60
_MAX_INTEGER = 2**63 - 1
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_COMMANDS = ("guidance.submit", "guidance.ack", "guidance.apply", "requirement.produce",
             "requirement.verify", "requirement.accept", "checkpoint.create", "experiment.run")
_ROOT = Path(__file__).resolve().parent.parent
_STATIC = {
    "/": (_ROOT / "web" / "index.html", "text/html; charset=utf-8"),
    "/app.js": (_ROOT / "web" / "app.js", "text/javascript; charset=utf-8"),
    "/client.mjs": (_ROOT / "web" / "client.mjs", "text/javascript; charset=utf-8"),
    "/styles.css": (_ROOT / "web" / "styles.css", "text/css; charset=utf-8"),
    "/openapi.json": (_ROOT / "registry" / "openapi.json", "application/json; charset=utf-8"),
}
_PUBLIC = frozenset((*_STATIC, "/healthz", "/.well-known/polyia.json"))
_PRIVATE = frozenset(("/v1/state", "/v1/events", "/v1/verify", "/v1/refusals", "/v1/commands"))
_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
        "img-src 'self' data:; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
        "form-action 'self'; object-src 'none'")
_LOG_METHODS = frozenset(("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT"))
_LOG_ROUTES = {"/": "asset", "/app.js": "asset", "/client.mjs": "asset", "/styles.css": "asset",
               "/openapi.json": "schema", "/healthz": "health", "/.well-known/polyia.json": "discovery",
               "/v1/state": "state", "/v1/events": "events", "/v1/verify": "verification",
               "/v1/refusals": "refusals", "/v1/commands": "commands"}


def _http_log(request_id, method, route, status):
    """Only finite categories and a locally generated identifier enter the sink."""
    category = _LOG_ROUTES.get(route, "unknown") if route is not None else "unparsed"
    if route is not None and route.startswith("/v1/commands/"):
        category = "command_receipt"
    elif route is not None and route.startswith("/v1/checkpoints/"):
        category = "checkpoint"
    record = {"event": "http_access", "request_id": request_id,
              "method": method if method in _LOG_METHODS else "OTHER",
              "route": category, "status": status}
    logging.getLogger(__name__).log(logging.ERROR if status >= 500 else logging.INFO,
                                   json.dumps(record, separators=(",", ":"), sort_keys=True))


def _refuse(code, message, status=400, details=None):
    raise CommandError(code, message, status, details)


def _token_bytes(value, label):
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise ValueError(f"{label} must be a nonempty bearer token of at most 4096 characters")
    if any(ord(character) < 33 or ord(character) > 126 for character in value):
        raise ValueError(f"{label} must contain printable ASCII without whitespace")
    return value.encode("ascii")


def _public_origin(value):
    if value is None:
        return None
    if not isinstance(value, str) or any(character.isspace() for character in value):
        raise ValueError("public_origin must be one HTTPS origin")
    try:
        parsed = urlsplit(value)
        hostname, port = parsed.hostname, parsed.port
    except ValueError as error:
        raise ValueError("public_origin must be one HTTPS origin") from error
    if (parsed.scheme != "https" or not hostname or parsed.username is not None or
            parsed.password is not None or parsed.path or parsed.query or parsed.fragment or
            "?" in value or "#" in value or "\\" in value):
        raise ValueError("public_origin must be one HTTPS origin without credentials, path, query, or fragment")
    try:
        address = ipaddress.ip_address(hostname)
        host = f"[{address}]" if address.version == 6 else str(address)
    except ValueError:
        if (not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", hostname) or
                ".." in hostname or len(hostname) > 253):
            raise ValueError("public_origin must have a literal domain or IP authority")
        host = hostname
    if port == 0:
        raise ValueError("public_origin port must be positive")
    authority = host + (f":{port}" if port not in (None, 443) else "")
    return "https://" + authority


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _refuse("INVALID_JSON", "JSON object keys must be unique")
        result[key] = value
    return result


def _finite_constant(value):
    _refuse("INVALID_JSON", "Non-finite JSON numbers are not accepted")


def _bounded_json(value):
    pending = [(value, 0)]
    count = 0
    while pending:
        current, depth = pending.pop()
        count += 1
        if depth > MAX_JSON_DEPTH or count > 10000:
            _refuse("INVALID_JSON", "JSON exceeds the nesting or value-count budget")
        if isinstance(current, dict):
            pending.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            pending.extend((item, depth + 1) for item in current)
        elif isinstance(current, float) and (current == float("inf") or current == float("-inf")):
            _refuse("INVALID_JSON", "Non-finite JSON numbers are not accepted")
        elif isinstance(current, str):
            try:
                current.encode("utf-8")
            except UnicodeEncodeError:
                _refuse("INVALID_JSON", "JSON strings must contain valid Unicode")


def _command_schema(request):
    required = {"command_id", "expected_revision", "kind", "payload"}
    if not isinstance(request, dict) or set(request) != required:
        _refuse("INVALID_REQUEST", "The command must contain exactly command_id, expected_revision, kind, and payload")
    if not isinstance(request["command_id"], str) or not _IDENTIFIER.fullmatch(request["command_id"]):
        _refuse("INVALID_REQUEST", "command_id must be a stable ASCII identifier of 1 to 128 characters")
    revision = request["expected_revision"]
    if type(revision) is not int or not 0 <= revision <= _MAX_INTEGER:
        _refuse("INVALID_REQUEST", "expected_revision must be a nonnegative integer")
    if not isinstance(request["kind"], str) or not _IDENTIFIER.fullmatch(request["kind"]):
        _refuse("INVALID_REQUEST", "kind must be a registered command identifier")
    if not isinstance(request["payload"], dict):
        _refuse("INVALID_REQUEST", "payload must be a JSON object")


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 16

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(self.socket_timeout)
        return connection, address

    def _rate_retry_after(self):
        with self._rate_lock:
            now = time.monotonic()
            self._rate_tokens = min(self.request_burst, self._rate_tokens +
                                    (now - self._rate_updated) * self.request_rate)
            self._rate_updated = now
            if self._rate_tokens < 1:
                return max(1, math.ceil((1 - self._rate_tokens) / self.request_rate))
            self._rate_tokens -= 1
            return 0

    def _reject_connection(self, connection, status, retry_after):
        request_id = uuid.uuid4().hex
        code, reason, message = (("RATE_LIMITED", "Too Many Requests", "Global request admission limit reached")
                                 if status == 429 else
                                 ("SERVER_BUSY", "Service Unavailable", "Active request capacity reached"))
        body = json.dumps({"ok": False, "error": {"code": code, "message": message},
                           "request_id": request_id}, separators=(",", ":")).encode("ascii")
        headers = (f"HTTP/1.1 {status} {reason}\r\nContent-Type: application/json; charset=utf-8\r\n"
                   f"Content-Length: {len(body)}\r\nRetry-After: {retry_after}\r\n"
                   f"X-Request-ID: {request_id}\r\nCache-Control: no-store\r\n"
                   f"Content-Security-Policy: {_CSP}\r\nX-Frame-Options: DENY\r\n"
                   "Referrer-Policy: no-referrer\r\nPermissions-Policy: camera=(), microphone=(), geolocation=()\r\n"
                   "X-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n")
        try:
            # Refusal must not create another worker or wait on request input.
            connection.settimeout(0.1)
            connection.sendall(headers.encode("ascii") + body)
        except OSError:
            pass
        finally:
            self.shutdown_request(connection)
            _http_log(request_id, None, None, status)

    def process_request(self, request, client_address):
        retry_after = self._rate_retry_after()
        if retry_after:
            self._reject_connection(request, 429, retry_after)
            return
        if not self._active_slots.acquire(blocking=False):
            self._reject_connection(request, 503, 1)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._active_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._active_slots.release()

    def handle_error(self, request, client_address):
        # socketserver's default includes exception traces and client input.
        _http_log(uuid.uuid4().hex, None, None, 500)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "PolyIA/1"
    sys_version = ""

    def log_message(self, format, *args):
        # Default access logs echo complete URLs. Tokens must never enter logs.
        return

    def handle_one_request(self):
        self.request_id = uuid.uuid4().hex
        self.auth_scope = None
        self.route = None
        self.command = None
        self._response_status = 0
        try:
            super().handle_one_request()
        finally:
            _http_log(self.request_id, self.command, self.route, self._response_status)

    def _send(self, status, body, content_type="application/json; charset=utf-8", extra=None):
        self._response_status = status
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        for key, value in {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": _CSP,
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Connection": "close",
            "X-Request-ID": getattr(self, "request_id", ""),
        }.items():
            self.send_header(key, value)
        if getattr(self, "auth_scope", None):
            self.send_header("X-PolyIA-Scope", self.auth_scope)
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    def _error(self, error):
        if not getattr(self, "request_id", None):
            self.request_id = uuid.uuid4().hex
        details = {"code": error.code, "message": error.message}
        if error.details is not None:
            details["details"] = error.details
        extra = {}
        if error.http_status == 401:
            extra["WWW-Authenticate"] = 'Bearer realm="polyia"'
        if error.http_status == 405:
            extra["Allow"] = "POST" if getattr(self, "route", "") == "/v1/commands" else "GET, HEAD"
        self._send(error.http_status, {"ok": False, "error": details, "request_id": self.request_id}, extra=extra)

    def send_error(self, code, message=None, explain=None):
        # BaseHTTPRequestHandler uses this for invalid request lines and methods.
        self._error(CommandError("HTTP_ERROR", "The HTTP request could not be processed", code))

    def _one_header(self, name, *, required=False):
        values = self.headers.get_all(name, [])
        if len(values) > 1:
            _refuse("INVALID_HEADERS", f"Multiple {name} headers are not accepted")
        if not values:
            if required:
                _refuse("INVALID_HEADERS", f"A single {name} header is required")
            return None
        value = values[0]
        if "\r" in value or "\n" in value or "\x00" in value:
            _refuse("INVALID_HEADERS", "Header values must not contain control characters")
        return value

    def _request_boundary(self):
        if sum(len(key) + len(value) + 4 for key, value in self.headers.items()) > MAX_HEADER_BYTES:
            _refuse("HEADERS_TOO_LARGE", "Request headers exceed the 16 KiB budget", 431)
        authority = self._one_header("Host", required=True)
        if authority.lower() not in self.server.allowed_authorities:
            _refuse("HOST_FORBIDDEN", "Host is not an allowed service authority", 421)
        expected_origin = self.server.allowed_authorities[authority.lower()]
        origin = self._one_header("Origin")
        if origin is not None and origin != expected_origin:
            _refuse("ORIGIN_FORBIDDEN", "The request Origin must match its service authority", 403)
        if self._one_header("Sec-Fetch-Site") == "cross-site":
            _refuse("ORIGIN_FORBIDDEN", "Cross-site browser requests are not accepted", 403)
        if self._one_header("Transfer-Encoding") is not None:
            _refuse("INVALID_FRAMING", "Transfer-Encoding is not supported")
        length = self._one_header("Content-Length")
        if length is not None and not re.fullmatch(r"[0-9]{1,20}", length):
            _refuse("INVALID_FRAMING", "Content-Length must be one nonnegative decimal integer")
        if length is not None and int(length) > MAX_BODY_BYTES:
            _refuse("BODY_TOO_LARGE", "Request body exceeds 65536 bytes", 413)
        self.body_length = int(length) if length is not None else None
        if self.command not in ("POST",) and self.body_length not in (None, 0):
            _refuse("INVALID_FRAMING", "This method does not accept a request body")

    def _target(self):
        target = self.path
        if len(target) > 4096 or not target.startswith("/") or target.startswith("//") or "\\" in target:
            _refuse("INVALID_PATH", "Request target must be a bounded local path")
        if any(ord(character) < 33 for character in target):
            _refuse("INVALID_PATH", "Request target contains invalid characters")
        try:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or parsed.fragment or "#" in target:
                raise ValueError("not a local target")
            if re.search(r"%(?![0-9a-fA-F]{2})", parsed.path):
                raise ValueError("malformed escape")
            path = unquote_to_bytes(parsed.path).decode("utf-8")
        except (ValueError, UnicodeError):
            _refuse("INVALID_PATH", "Request target is malformed")
        if ("\\" in path or any(ord(character) < 33 for character in path) or
                any(segment in (".", "..") for segment in path.split("/")) or
                "%2f" in parsed.path.lower() or "%5c" in parsed.path.lower()):
            _refuse("INVALID_PATH", "Path segments are not allowed")
        try:
            query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True, max_num_fields=8)
        except ValueError:
            _refuse("INVALID_QUERY", "Query parameters are malformed or exceed the budget")
        self.route, self.query = path, query

    def _authorize(self, mutation=False):
        authorization = self._one_header("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            _refuse("UNAUTHORIZED", "A valid bearer token is required", 401)
        value = authorization[7:]
        try:
            candidate = value.encode("ascii")
        except UnicodeEncodeError:
            _refuse("UNAUTHORIZED", "A valid bearer token is required", 401)
        if hmac.compare_digest(candidate, self.server._operator_token):
            self.auth_scope = "operator"
        elif self.server._read_token is not None and hmac.compare_digest(candidate, self.server._read_token):
            self.auth_scope = "read"
        else:
            _refuse("UNAUTHORIZED", "A valid bearer token is required", 401)
        if mutation and self.auth_scope != "operator":
            _refuse("FORBIDDEN", "This token permits reads only", 403)

    def _query_numbers(self, allowed):
        if set(self.query) - set(allowed):
            _refuse("INVALID_QUERY", "This route does not accept those query parameters")
        result = {}
        for key, (default, minimum, maximum) in allowed.items():
            values = self.query.get(key)
            if values is None:
                result[key] = default
                continue
            if len(values) != 1 or not re.fullmatch(r"[0-9]{1,19}", values[0]):
                _refuse("INVALID_QUERY", f"{key} must be one decimal integer")
            value = int(values[0])
            if not minimum <= value <= maximum:
                _refuse("INVALID_QUERY", f"{key} is outside its permitted range")
            result[key] = value
        return result

    def _read_command(self):
        media_type = self._one_header("Content-Type")
        if media_type is None or not re.fullmatch(r"application/json(?:\s*;\s*charset=utf-8)?", media_type, re.IGNORECASE):
            _refuse("UNSUPPORTED_MEDIA_TYPE", "Use application/json with UTF-8 encoding", 415)
        if self.body_length is None:
            _refuse("LENGTH_REQUIRED", "Content-Length is required", 411)
        data = self.rfile.read(self.body_length)
        if len(data) != self.body_length:
            _refuse("INVALID_FRAMING", "Request body ended before Content-Length bytes")
        try:
            request = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_finite_constant)
        except (ValueError, UnicodeError, RecursionError):
            _refuse("INVALID_JSON", "Request body must be valid bounded UTF-8 JSON")
        _bounded_json(request)
        _command_schema(request)
        return request

    def _discovery(self):
        return {
            "protocol": "polyia.command-plane", "protocol_version": "1.0.0", "api_base": "/v1",
            "openapi": "/openapi.json", "service": "Poly IA commissioning bootstrap",
            "authentication": {"scheme": "Bearer", "operator_scopes": ["read", "command"], "read_scopes": ["read"]},
            "capabilities": {
                "state": True, "event_polling": True, "sse": False, "websocket": False,
                "command_receipts": True, "checkpoint_reads": True, "ledger_verification": True,
                "refusal_reads": True, "llm_inference": False, "remote_binding": False,
                "commands": list(_COMMANDS), "experiments": sorted(REGISTERED_EXPERIMENTS),
            },
            "limits": {"command_body_bytes": MAX_BODY_BYTES, "header_bytes": MAX_HEADER_BYTES,
                       "json_nesting_depth": MAX_JSON_DEPTH, "event_page_size": MAX_PAGE_SIZE,
                       "active_handlers": self.server.max_active_requests,
                       "connections_per_second": self.server.request_rate,
                       "connection_burst": self.server.request_burst},
            "transport": {"binding": "loopback", "public_origin": self.server.public_origin,
                          "tls": "external reverse proxy when configured", "cors": False},
            "assurance": {"scope": "portable bootstrap; not full commission acceptance",
                          "http_refusal_audit": "redacted fixed-schema operational logs; separate from the immutable ledger"},
        }

    def _dispatch(self):
        self._request_boundary()
        self._target()
        path = self.route
        identifier = None
        kind = None
        for prefix, candidate_kind in (("/v1/commands/", "command"), ("/v1/checkpoints/", "checkpoint")):
            if path.startswith(prefix):
                identifier, kind = path[len(prefix):], candidate_kind
                if not _IDENTIFIER.fullmatch(identifier):
                    _refuse("NOT_FOUND", "Route not found", 404)
                break
        if path not in _PUBLIC and path not in _PRIVATE and kind is None:
            _refuse("NOT_FOUND", "Route not found", 404)
        if path not in _PUBLIC:
            self._authorize(mutation=self.command == "POST" and path == "/v1/commands")
        method = "GET" if self.command == "HEAD" else self.command
        permitted = "POST" if path == "/v1/commands" else "GET"
        if method != permitted:
            _refuse("METHOD_NOT_ALLOWED", "Method is not allowed for this route", 405)
        if path == "/v1/events":
            parameters = self._query_numbers({"after": (0, 0, _MAX_INTEGER), "limit": (100, 1, MAX_PAGE_SIZE)})
            events = self.server.ledger.events(**parameters)
            self._send(200, {"events": events, "next_after": events[-1]["sequence"] if events else parameters["after"]})
            return
        if path == "/v1/refusals":
            parameters = self._query_numbers({"limit": (100, 1, MAX_PAGE_SIZE)})
            self._send(200, {"refusals": self.server.ledger.refusals(**parameters)})
            return
        self._query_numbers({})
        if path in _STATIC:
            filename, media_type = _STATIC[path]
            try:
                body = filename.read_bytes()
            except OSError:
                _refuse("ASSET_UNAVAILABLE", "A packaged interface asset is unavailable", 503)
            self._send(200, body, media_type)
        elif path == "/healthz":
            self._send(200, {"ok": True, "service": "polyia-bootstrap"})
        elif path == "/.well-known/polyia.json":
            self._send(200, self._discovery())
        elif path == "/v1/state":
            self._send(200, self.server.ledger.state())
        elif path == "/v1/verify":
            self._send(200, self.server.ledger.verify())
        elif path == "/v1/commands":
            receipt = self.server.ledger.command(self._read_command(), actor="operator", scopes=("read", "command"))
            self._send(200, receipt)
        elif kind == "command":
            self._send(200, self.server.ledger.get_command(identifier, actor=None))
        elif kind == "checkpoint":
            if identifier == "latest":
                latest = self.server.ledger.state()["latest_checkpoint"]
                if latest is None:
                    _refuse("NOT_FOUND", "No checkpoint has been created", 404)
                identifier = latest["id"]
            self._send(200, self.server.ledger.get_checkpoint(identifier))

    def _handle(self):
        try:
            self._dispatch()
        except CommandError as error:
            self._error(error)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        except TimeoutError:
            self._error(CommandError("REQUEST_TIMEOUT", "The request exceeded the read timeout", 408))
        except Exception:
            self._error(CommandError("INTERNAL_ERROR", "The service could not complete this request; inspect local diagnostics", 500))

    do_GET = _handle
    do_HEAD = _handle
    do_POST = _handle
    do_PUT = _handle
    do_PATCH = _handle
    do_DELETE = _handle
    do_OPTIONS = _handle
    do_TRACE = _handle
    do_CONNECT = _handle


def make_server(ledger, host="127.0.0.1", port=0, token=..., read_token=None, public_origin=None, *,
                max_active_requests=MAX_ACTIVE_REQUESTS, request_rate=REQUEST_RATE,
                request_burst=REQUEST_BURST, socket_timeout=SOCKET_TIMEOUT):
    """Return a configured ThreadingHTTPServer; the caller owns serve/shutdown.

    Tokens are required configuration and never enter a URL, asset, or log.
    Optional public_origin permits one HTTPS reverse-proxy authority in addition
    to local access. It does not change binding or trust forwarded headers.
    """
    operator = _token_bytes(token, "token")
    reader = _token_bytes(read_token, "read_token") if read_token is not None else None
    if reader is not None and hmac.compare_digest(operator, reader):
        raise ValueError("Operator and read tokens must be different")
    public = _public_origin(public_origin)
    if host == "localhost":
        host = "127.0.0.1"
    try:
        address = ipaddress.ip_address(host)
    except ValueError as error:
        raise ValueError("Bootstrap host must be a literal loopback address or localhost") from error
    if not address.is_loopback:
        raise ValueError("The bootstrap service can bind only to loopback")
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("port must be an integer from 0 through 65535")
    for name, value, maximum in (("max_active_requests", max_active_requests, 1024),
                                 ("request_burst", request_burst, 1000000)):
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f"{name} must be an integer from 1 through {maximum}")
    for name, value, maximum in (("request_rate", request_rate, 1000000),
                                 ("socket_timeout", socket_timeout, 60)):
        if type(value) not in (int, float) or not 0.001 <= value <= maximum:
            raise ValueError(f"{name} must be a finite number from 0.001 through {maximum}")
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    server_class = type("LoopbackHTTPServer", (_Server,), {"address_family": socket.AF_INET6 if address.version == 6 else socket.AF_INET})
    server = server_class((str(address), port), _Handler)
    server.max_active_requests = max_active_requests
    server.socket_timeout = socket_timeout
    server._active_slots = threading.BoundedSemaphore(max_active_requests)
    server.request_rate, server.request_burst = request_rate, request_burst
    server._rate_lock = threading.Lock()
    server._rate_tokens, server._rate_updated = request_burst, time.monotonic()
    server.ledger = ledger
    server._operator_token = operator
    server._read_token = reader
    server.public_origin = public
    local_host = f"[{address}]" if address.version == 6 else str(address)
    authorities = {}
    for hostname in (local_host, "localhost"):
        authority = hostname + (f":{server.server_port}" if server.server_port != 80 else "")
        authorities[authority] = "http://" + authority
        if server.server_port == 80:
            authorities[hostname + ":80"] = "http://" + hostname
    if public:
        authority = public.removeprefix("https://")
        authorities[authority] = public
        if ":" not in authority:
            authorities[authority + ":443"] = public
    server.allowed_authorities = authorities
    return server
