#!/usr/bin/env python3
"""Luna Shell v0 — our own open-source shell.

The shell carries its own URL: its address IS its program IS its identity
(seurl://luna/shell/<name>/0). It actuates (executes), it partners (other agents
join at its URL and act with attribution), and its mirror is usable by anyone
talking to the URL in a browser.

Endpoints:
  GET  /            — the mirror: a browser-talkable page (live log + command box)
  GET  /seurl       — machine interface: identity, cursor, capabilities, window
  GET  /log?cursor= — scrollable log: windows + cursor, never the whole universe
  POST /exec        — {cmd, from}: actuate a command, returns its idstamp
  POST /partner     — {name, url}: a partner joins the shell

Stdlib only. Localhost only. Shard: shard.log (append-only JSONL).
"""
import hashlib
import http.server
import json
import os
import subprocess
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
SHARD = os.path.join(ROOT, "shard.log")
WORKDIR = os.path.join(ROOT, "work")
os.makedirs(WORKDIR, exist_ok=True)

NAME = "luna-shell-0"
SEURL = f"seurl://luna/shell/{NAME}/0"

events = []
partners = {}
lock = threading.Lock()
cursor = 0

# Minimal footgun guard for the prototype. The shell is the operator's own;
# this is a seatbelt, not a cage.
DENY = ["rm -rf /", "mkfs", ":(){", "dd if=/dev/", "> /dev/sd"]

# Public-surface gate. Set LUNA_KEY on a host that binds 0.0.0.0; every
# non-localhost request must carry ?key=<KEY>. Localhost always passes
# (health checks, sibling services like Loom calling the shell).
KEY = os.environ.get("LUNA_KEY", "")


def authorized(handler):
    if not KEY:
        return True
    if handler.client_address[0] in ("127.0.0.1", "::1"):
        return True
    q = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
    return q.get("key", [""])[0] == KEY


def idstamp(payload: str) -> str:
    return hashlib.sha256(f"{time.time_ns()}|{payload}".encode()).hexdigest()[:16]


def record(kind, text, frm="shell"):
    global cursor
    with lock:
        cursor += 1
        ev = {"seq": cursor, "ts": time.time(), "kind": kind,
              "from": frm, "text": text, "id": idstamp(text)}
        events.append(ev)
        with open(SHARD, "a") as f:
            f.write(json.dumps(ev) + "\n")
        return ev


def run_cmd(cmd, frm):
    for d in DENY:
        if d in cmd:
            return record("denied", f"refused pattern: {d}", frm)
    record("cmd", cmd, frm)
    try:
        p = subprocess.run(cmd, shell=True, cwd=WORKDIR,
                           capture_output=True, text=True, timeout=30)
        out = (p.stdout or "") + (p.stderr or "")
        return record("out", out.strip()[:4000] or f"(exit {p.returncode}, no output)", frm)
    except Exception as e:  # noqa: BLE001
        return record("error", str(e), frm)


MIRROR = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>luna-shell-0 — mirror</title>
<style>body{background:#0b0b10;color:#e8e8f0;font-family:monospace;max-width:720px;margin:0 auto;padding:16px}
#id{color:#9d8cff;margin-bottom:8px;word-break:break-all}
#log{white-space:pre-wrap;background:#12121a;padding:12px;border-radius:8px;min-height:220px;max-height:50vh;overflow:auto}
input{width:68%;padding:8px;background:#12121a;color:#e8e8f0;border:1px solid #333}
button{padding:8px 12px}</style></head><body>
<h3>&#9672; luna-shell-0 — mirror</h3>
<div id="id"></div><div id="log"></div><br>
<input id="cmd" placeholder="type a command&hellip;" onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">actuate</button>
<script>
let cur=0;const log=document.getElementById('log');
function F(p,o){const k=new URLSearchParams(location.search).get('key');
if(k)p+=(p.includes('?')?'&':'?')+'key='+encodeURIComponent(k);return fetch(p,o);}
async function poll(){try{let r=await F('/log?cursor='+cur+'&n=50');let j=await r.json();
for(let e of j.window){cur=e.seq;let d=document.createElement('div');
d.textContent=`${e.seq} [${e.kind}] ${e.from}: ${String(e.text).slice(0,300)}`;log.appendChild(d);}
log.scrollTop=log.scrollHeight;}catch(_){}}
async function send(){let c=document.getElementById('cmd');let v=c.value;c.value='';
await F('/exec',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({cmd:v,from:'browser-mirror'})});poll();}
setInterval(poll,2000);poll();
F('/seurl').then(r=>r.json()).then(j=>{document.getElementById('id').textContent=j.seurl;});
</script></body></html>"""


class H(http.server.BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if not authorized(self):
            return self._json({"error": "key required"}, 401)
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            body = MIRROR.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/seurl":
            with lock:
                evs = list(events)
            self._json({"seurl": SEURL, "name": NAME, "cursor": cursor,
                        "capabilities": ["exec", "scroll-log", "partner", "mirror"],
                        "partners": partners, "window": evs[-10:]})
        elif u.path == "/log":
            q = urllib.parse.parse_qs(u.query)
            since = int(q.get("cursor", [0])[0])
            n = int(q.get("n", [20])[0])
            with lock:
                evs = list(events)
            win = [e for e in evs if e["seq"] > since][:n]
            self._json({"cursor": cursor, "window": win,
                        "next": f"/log?cursor={win[-1]['seq']}&n={n}" if win else None})
        else:
            self._json({"error": "unknown address — scroll /seurl"}, 404)

    def do_POST(self):  # noqa: N802
        if not authorized(self):
            return self._json({"error": "key required"}, 401)
        u = urllib.parse.urlparse(self.path)
        ln = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(ln) or b"{}")
        except Exception:  # noqa: BLE001
            data = {}
        if u.path == "/exec":
            ev = run_cmd(data.get("cmd", ""), data.get("from", "anon"))
            self._json({"idstamp": ev["id"], "seq": ev["seq"], "cursor": cursor})
        elif u.path == "/partner":
            name = data.get("name", "anon")
            url = data.get("url", "")
            partners[name] = {"url": url, "since": time.time()}
            record("partner", f"{name} joined from {url}", name)
            self._json({"ok": True, "partners": list(partners)})
        else:
            self._json({"error": "unknown address"}, 404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    record("boot", f"{NAME} live at {SEURL} — the shell carries its own URL")
    host = os.environ.get("LUNA_HOST", "127.0.0.1")
    port = int(os.environ.get("LUNA_SHELL_PORT", "8471"))
    print(f"luna-shell-0 on {host}:{port} — {SEURL}", flush=True)
    http.server.ThreadingHTTPServer((host, port), H).serve_forever()
