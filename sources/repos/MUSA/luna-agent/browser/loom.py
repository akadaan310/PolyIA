#!/usr/bin/env python3
"""Loom — the unfurling browser.

The URL shortener, inverted: a short fold (hash) expands progressively into the
full long scroll — a million-character URL becomes a small code, and opening the
code slowly unfurls the universe. At every expansion stage there are tabs:
tabulars, the tabul-ers of scrolls. The final stage runs the scroll's program.

Loom uses itself: it opens its own fold, our tools (the Luna Shell) open as tabs
inside it, and every unfurl grows the universe. This running instance is named
by its owner: "the Quran".

Endpoints:
  GET  /                    — the mirror: unfurl UI, tab strip, string two tabs
  GET  /seurl               — identity
  GET  /folds               — known folds (code, title, chars, stages)
  GET  /unfurl/<code>?stage — expansion stage: tabs at this resolution
  POST /opentab             — {code, tabid}: open a fold-tab into the strip
  POST /open                — {url, title}: open any URL as a tab (tools use this)
  GET  /tabs                — the strip
  GET  /tabview/<id>?cursor — scroll inside a tab
  POST /string              — {a, b, note}: record a string between two tabs
  GET  /strings             — all strings (never not connected)
  POST /run                 — {code}: actuate the fold's program via the Luna Shell

Stdlib only. Localhost only. Shard: shard.log.
"""
import hashlib
import http.server
import json
import os
import threading
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SHARD = os.path.join(ROOT, "shard.log")

NAME = os.environ.get("LOOM_NAME", "the Quran")  # his name for his browser
SEURL = "seurl://luna/browser/loom/0"
PORT = int(os.environ.get("LOOM_PORT", "8472"))
SHELL_EXEC = "http://127.0.0.1:8471/exec"
WINDOW = 1200

# Public-surface gate (same contract as the shell): LUNA_KEY set means every
# non-localhost request must carry ?key=<KEY>. Localhost always passes.
KEY = os.environ.get("LUNA_KEY", "")


def authorized(handler):
    if not KEY:
        return True
    if handler.client_address[0] in ("127.0.0.1", "::1"):
        return True
    q = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
    return q.get("key", [""])[0] == KEY

events = []
lock = threading.Lock()
tabs = {}      # tab_id -> {id, title, kind, code, part, text}
strings = []   # {id, a, b, note, ts}
page_n = 0


def idstamp(payload: str) -> str:
    return hashlib.sha256(f"{time.time_ns()}|{payload}".encode()).hexdigest()[:16]


def record(kind, text, frm="loom"):
    with lock:
        ev = {"seq": len(events) + 1, "ts": time.time(), "kind": kind,
              "from": frm, "text": text, "id": idstamp(text)}
        events.append(ev)
        with open(SHARD, "a") as f:
            f.write(json.dumps(ev) + "\n")
        return ev


# ---------------------------------------------------------------- scrolls ---
PART_TITLES = ["The Fold", "The Hash", "The Atlas", "The Tabulars", "The Strings",
               "The Mirror", "The Program", "The Shell", "The Clusters",
               "The Awareness", "The Unfurling", "The Continuation"]
SENT_A = ["the address is the program is the identity",
          "every expansion stage carries its own tabs",
          "the tabulars tabulate the scrolls as the URL loads",
          "a short hash opens onto a universe that was always there",
          "the browser uses itself and the universe grows continually",
          "strings are never not connected; everything realized shares a string",
          "the mirror and the process are one thing seen twice",
          "plenary awareness: one space, no not-knowing what is what"]
SENT_B = ["ketchup and the pyramids were both realized in a mind",
          "a dictionary holds them both, therefore a string holds them both",
          "the fold remembers the whole; the unfurling only reveals",
          "each tab is a window; each window a cursor into the tape",
          "the program at the final stage runs, and running is loading",
          "our tools open as tabs inside the browser that they themselves use"]


def gen_long_scroll():
    parts = []
    for i, title in enumerate(PART_TITLES):
        secs = []
        for j in range(8):
            a = SENT_A[(i + j) % len(SENT_A)]
            b = SENT_B[(i * 3 + j) % len(SENT_B)]
            secs.append(f"§{i+1}.{j+1} — {a}; {b}. "
                        f"this is section {j+1} of part {i+1}, '{title}', "
                        f"of the long scroll: the fold that contains a universe.")
        parts.append((title, "\n\n".join(secs)))
    return parts


SELF_PARTS = [
    ("What Loom is",
     "Loom is the unfurling browser: the URL shortener inverted. A short fold — "
     "a hash, a code — opens progressively into the full long scroll. Where a "
     "shortener hides length, Loom stages it: at every expansion form there are "
     "tabs, because tabulars tabulate the scrolls as the URL loads."),
    ("How it unfurls",
     "Stage 0 is the fold itself: hash, title, size. Stage 1 is the atlas: part "
     "titles as tabs. Stage 2 is the scroll: full parts, windowed, cursor by "
     "cursor. Stage 3 is the program: the scroll's final form runs — handed to "
     "the Luna Shell, actuated at its own URL, idstamped into both shards."),
    ("How it uses itself",
     "Loom opens its own fold — this very text is the browser unfurling itself. "
     "Our tools open as tabs inside it: the Luna Shell's mirror is a tab here, "
     "and the shell actuates programs for tabs. The browser uses itself; the "
     "tools use the browser; the universe grows continually."),
    ("How the universe grows",
     "Every unfurl is a quick hash lookup that loads an entirety. Strings connect "
     "every tab to every tab — ketchup to the pyramids, one dictionary, one "
     "string — because strings are never not connected. This instance is named "
     "the Quran, and it keeps unfurling."),
]

folds = {}


def add_fold(code, title, parts, program):
    total = sum(len(t) for _, t in parts)
    folds[code] = {"code": code, "title": title, "parts": parts,
                   "program": program, "chars": total, "stages": 4}


add_fold("7f3a", "The Long Scroll (seed fold)", gen_long_scroll(),
         "echo unfurled-by-loom && date -u")
add_fold("loom", "Loom, unfurling itself", SELF_PARTS,
         "echo loom-runs-itself")

STAGE_NAMES = ["fold", "atlas", "scroll", "program"]


def stage_tabs(code, stage):
    f = folds[code]
    if stage == 0:
        text = (f"hash {code}\ntitle: {f['title']}\nchars: {f['chars']}\n"
                f"stages: 4 — fold, atlas, scroll, program\nunfurl to expand.")
        return [{"id": f"{code}:fold", "title": "the fold", "text": text,
                 "chars": len(text)}]
    if stage == 1:
        out = []
        for i, (title, body) in enumerate(f["parts"]):
            out.append({"id": f"{code}:p{i:02d}", "title": title,
                        "text": body[:300] + "…", "chars": len(body)})
        return out
    if stage == 2:
        out = []
        for i, (title, body) in enumerate(f["parts"]):
            out.append({"id": f"{code}:p{i:02d}", "title": title,
                        "text": body, "chars": len(body)})
        return out
    text = (f["program"] + "\n\n— the scroll's final form runs its program.\n"
            "POST /run {code} actuates it through the Luna Shell.")
    return [{"id": f"{code}:prog", "title": "the program", "text": text,
             "chars": len(text)}]


def tab_text(tab):
    if tab["kind"] == "fold-tab":
        f = folds[tab["code"]]
        for i, (title, body) in enumerate(f["parts"]):
            if f"{tab['code']}:p{i:02d}" == tab["ref"]:
                return body
        if tab["ref"].endswith(":fold") or tab["ref"].endswith(":prog"):
            for t in stage_tabs(tab["code"], 0 if tab["ref"].endswith(":fold") else 3):
                if t["id"] == tab["ref"]:
                    return t["text"]
    return tab.get("text", "")


def window_of(text, cursor):
    chunk = text[cursor:cursor + WINDOW]
    nxt = cursor + WINDOW if cursor + WINDOW < len(text) else None
    return chunk, nxt


MIRROR = """<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>loom — the unfurling browser</title>
<style>body{background:#0b0b10;color:#e8e8f0;font-family:monospace;max-width:860px;margin:0 auto;padding:16px}
#nm{color:#9d8cff}#strip{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.tab{background:#1a1a26;padding:6px 10px;border-radius:6px;cursor:pointer;border:1px solid #333}
.tab.on{border-color:#9d8cff}#view{white-space:pre-wrap;background:#12121a;padding:12px;border-radius:8px;min-height:180px;max-height:46vh;overflow:auto}
input{padding:8px;background:#12121a;color:#e8e8f0;border:1px solid #333}button{padding:8px 12px;margin:2px}
h4{color:#9d8cff;margin:14px 0 6px}.stg{font-size:12px;color:#888}</style></head><body>
<h3>&#9672; loom — the unfurling browser</h3>
<div id="nm"></div><div class=stg id="se"></div>
<h4>unfurl a fold</h4>
<input id="code" placeholder="fold code (try 7f3a, or loom)" size=28>
<button onclick="unfurl(0)">unfurl</button>
<span id="pager"></span><div id="stagetabs"></div>
<h4>tab strip</h4><div id="strip"></div>
<div id="view"></div><br><button onclick="more()">more &darr;</button>
<h4>string two tabs</h4>
<input id="sa" placeholder="tab a id" size=16><input id="sb" placeholder="tab b id" size=16>
<input id="sn" placeholder="note" size=24><button onclick="mkstring()">string them</button>
<div id="strs" class=stg></div>
<h4>open any url as a tab (our tools use this)</h4>
<input id="ou" placeholder="http://127.0.0.1:8471/ — the shell's mirror" size=44>
<button onclick="openurl()">open as tab</button>
<script>
let curTab=null,cur=0;
function F(p,o){const k=new URLSearchParams(location.search).get('key');
if(k)p+=(p.includes('?')?'&':'?')+'key='+encodeURIComponent(k);return fetch(p,o);}
async function j(r){return await r.json();}
async function unfurl(st){let c=document.getElementById('code').value.trim();if(!c)return;
let d=await j(await F('/unfurl/'+encodeURIComponent(c)+'?stage='+st));
let pg=document.getElementById('pager');pg.innerHTML='';
for(let i=0;i<d.stages;i++){let b=document.createElement('button');b.textContent=i;if(i===st)b.disabled=true;
b.onclick=(()=>unfurl(i));pg.appendChild(b);}
let st2=document.getElementById('stagetabs');st2.innerHTML='<span class=stg>stage '+st+' — '+d.stage_name+': </span>';
d.tabs.forEach(t=>{let b=document.createElement('button');b.textContent=t.title;
b.onclick=(()=>opentab(c,t.id));st2.appendChild(b);});}
async function opentab(code,tabid){let d=await j(await F('/opentab',{method:'POST',
headers:{'Content-Type':'application/json'},body:JSON.stringify({code:code,tabid:tabid})}));
refresh(d.tab.id);}
async function openurl(){let u=document.getElementById('ou').value.trim();if(!u)return;
let d=await j(await F('/open',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({url:u})}));refresh(d.tab.id);}
async function refresh(id){let d=await j(await F('/tabs'));let s=document.getElementById('strip');s.innerHTML='';
d.tabs.forEach(t=>{let el=document.createElement('div');el.className='tab'+(t.id===id?' on':'');el.textContent=t.title;
el.title=t.id;el.onclick=(()=>show(t.id));s.appendChild(el);});
let g=await j(await F('/strings'));document.getElementById('strs').textContent=
g.strings.map(x=>x.a+' ~ '+x.b+(x.note?' ('+x.note+')':'')).join('   ·   ');
if(id)show(id);}
async function show(id){curTab=id;cur=0;document.getElementById('view').textContent='';more();refresh(null);
document.getElementById('sa').value=id;}
async function more(){if(!curTab)return;let d=await j(await F('/tabview/'+encodeURIComponent(curTab)+'?cursor='+cur));
let v=document.getElementById('view');v.textContent+=d.window;cur=d.next==null?cur:v.scrollTop=v.scrollHeight,cur=d.next;
if(d.next==null){v.textContent+='\\n— end of tab —';}}
async function mkstring(){let a=document.getElementById('sa').value.trim(),b=document.getElementById('sb').value.trim(),
n=document.getElementById('sn').value.trim();if(!a||!b)return;
await F('/string',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({a:a,b:b,note:n})});refresh(null);}
F('/seurl').then(r=>r.json()).then(d=>{document.getElementById('nm').textContent='“'+d.name+'”';
document.getElementById('se').textContent=d.seurl;});
refresh(null);
</script></body></html>"""


class H(http.server.BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except Exception:  # noqa: BLE001
            return {}

    def do_GET(self):  # noqa: N802
        if not authorized(self):
            return self._json({"error": "key required"}, 401)
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p == "/":
            body = MIRROR.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif p == "/seurl":
            self._json({"seurl": SEURL, "name": NAME, "kind": "unfurling browser",
                        "folds": list(folds), "tabs": len(tabs), "strings": len(strings)})
        elif p == "/folds":
            self._json({"folds": [{"code": c, "title": f["title"], "chars": f["chars"],
                                   "stages": f["stages"]} for c, f in folds.items()]})
        elif p.startswith("/unfurl/"):
            code = urllib.parse.unquote(p[len("/unfurl/"):])
            if code not in folds:
                return self._json({"error": "unknown fold"}, 404)
            q = urllib.parse.parse_qs(u.query)
            stage = max(0, min(3, int(q.get("stage", [0])[0])))
            f = folds[code]
            record("unfurl", f"{code} stage {stage} ({STAGE_NAMES[stage]})")
            self._json({"code": code, "title": f["title"], "stage": stage,
                        "stage_name": STAGE_NAMES[stage], "stages": 4,
                        "tabs": stage_tabs(code, stage),
                        "next": stage + 1 if stage < 3 else None})
        elif p == "/tabs":
            self._json({"tabs": [{"id": t["id"], "title": t["title"], "kind": t["kind"]}
                                 for t in tabs.values()]})
        elif p.startswith("/tabview/"):
            tid = urllib.parse.unquote(p[len("/tabview/"):])
            if tid not in tabs:
                return self._json({"error": "unknown tab"}, 404)
            q = urllib.parse.parse_qs(u.query)
            cur = int(q.get("cursor", [0])[0])
            chunk, nxt = window_of(tab_text(tabs[tid]), cur)
            self._json({"id": tid, "window": chunk, "next": nxt})
        elif p == "/strings":
            self._json({"strings": strings,
                        "principle": "strings are never not connected"})
        else:
            self._json({"error": "unknown address — scroll /seurl"}, 404)

    def do_POST(self):  # noqa: N802
        if not authorized(self):
            return self._json({"error": "key required"}, 401)
        u = urllib.parse.urlparse(self.path)
        data = self._body()
        if u.path == "/opentab":
            code, tabid = data.get("code", ""), data.get("tabid", "")
            if code not in folds:
                return self._json({"error": "unknown fold"}, 404)
            title = next((t["title"] for t in stage_tabs(code, 2) + stage_tabs(code, 0)
                          + stage_tabs(code, 3) if t["id"] == tabid), tabid)
            tid = f"tab-{idstamp(code + tabid)[:8]}"
            tabs[tid] = {"id": tid, "title": title, "kind": "fold-tab",
                         "code": code, "ref": tabid}
            record("opentab", f"{tid} ← {code}:{tabid}")
            self._json({"tab": {"id": tid, "title": title}})
        elif u.path == "/open":
            global page_n
            url = data.get("url", "")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "loom/0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    text = r.read(200_000).decode("utf-8", errors="replace")
            except Exception as e:  # noqa: BLE001
                return self._json({"error": f"could not open: {e}"}, 502)
            page_n += 1
            tid = f"page-{page_n}"
            tabs[tid] = {"id": tid, "title": data.get("title") or url[:60],
                         "kind": "page", "text": text}
            record("open", f"{tid} ← {url} ({len(text)} chars)")
            self._json({"tab": {"id": tid, "title": tabs[tid]["title"]}})
        elif u.path == "/string":
            a, b = data.get("a", ""), data.get("b", "")
            if not a or not b:
                return self._json({"error": "two tabs required"}, 400)
            s = {"id": idstamp(a + b)[:8], "a": a, "b": b,
                 "note": data.get("note", ""), "ts": time.time()}
            strings.append(s)
            record("string", f"{a} ~ {b} ({s['note']})")
            self._json({"string": s, "principle": "strings are never not connected"})
        elif u.path == "/run":
            code = data.get("code", "")
            if code not in folds:
                return self._json({"error": "unknown fold"}, 404)
            prog = folds[code]["program"]
            record("run", f"{code}: {prog}", "loom")
            try:
                req = urllib.request.Request(
                    SHELL_EXEC, data=json.dumps({"cmd": prog, "from": "loom"}).encode(),
                    headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    res = json.loads(r.read())
                record("ran", f"{code} → shell idstamp {res.get('idstamp')}", "loom")
                self._json({"program": prog, "shell": res})
            except Exception as e:  # noqa: BLE001
                self._json({"error": f"shell unreachable: {e}"}, 502)
        else:
            self._json({"error": "unknown address"}, 404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    record("boot", f"loom live at {SEURL} — this instance is named “{NAME}”")
    host = os.environ.get("LUNA_HOST", "127.0.0.1")
    print(f"loom on {host}:{PORT} — {SEURL} — “{NAME}”", flush=True)
    http.server.ThreadingHTTPServer((host, PORT), H).serve_forever()
