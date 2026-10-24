"""Local-only reference HTTP surface. No arbitrary files or programs run."""
import json,mimetypes,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,unquote
from .core import Universe,AtomError

class LocalServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,project):
        self.project=Path(project).resolve();self.universe=Universe(self.project/'.atom-state');self.lock=threading.Lock()
        super().__init__(address,Handler)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,format,*args):pass
    def out(self,status,obj):
        body=json.dumps(obj,ensure_ascii=False,sort_keys=True).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        route=unquote(urlsplit(self.path).path)
        if route=='/api/celestial/capabilities':
            return self.out(200,{'protocol':'ASTRA-CELESTIAL/0.2','engine':'ASTRA',
              'render':{'cpu':'3D geometry to Canvas2D','gpu':'optional WebGL2 points','fallback':'Canvas2D'},
              'shells':['INNER OBSERVATORY','LOCAL CONSTELLATION','SOLAR NEIGHBORHOOD','GALACTIC STRUCTURE'],
              'models':{'catalog':'20 Hipparcos directions','illustrative_planets':True,'ephemerides':'NOT_CONNECTED', 'billion_scale':'NOT_INGESTED'},
              'audio':{'type':'locally synthesized seven-tone/spatial pads','play':'user-gesture-only','initial_gain':'reduced','compressor':True},
              'control':{'state_machine':'ATOM/0.1','actions':['shell.expand','shell.contract','journey.shift','sound.enable','sound.mute'],'writes_require_atom_admission':True}})
        if route=='/api/state':return self.out(200,self.server.universe.state())
        if route=='/api/protocol':return self.out(200,self.server.universe.protocol())
        if route=='/api/report':return self.out(200,self.server.universe.report())
        if route=='/api/choose':return self.out(200,self.server.universe.choose())
        if route=='/':route='/index.html'
        allowed={'/index.html':'web/index.html','/app.js':'web/app.js','/style.css':'web/style.css','/stars.json':'examples/hipparcos_sample.json','/atom-bus.js':'web/atom-bus.js','/sky.js':'web/sky.js','/star-gpu.js':'web/star-gpu.js','/audio.js':'web/audio.js','/audio/celestial-drift.wav':'audio_assets/celestial-drift.wav','/audio/portal-chime.wav':'audio_assets/portal-chime.wav'}
        if route not in allowed:return self.out(404,{'error':'not-found'})
        path=self.server.project/allowed[route]
        if not path.exists():return self.out(404,{'error':'missing-file'})
        content=path.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(path))[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(content)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(content)
    def do_POST(self):
        if self.path not in ('/api/register','/api/advance'):return self.out(404,{'error':'not-found'})
        # Browser sends only same-origin requests from this local page, but loopback alone is not production auth.
        if self.headers.get('Origin') and self.headers['Origin'] not in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)):
            return self.out(403,{'error':'origin-denied'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=16000:raise AtomError('Body limit exceeded')
            payload=json.loads(self.rfile.read(n))
            if not isinstance(payload,dict):raise AtomError('Object body required')
            with self.server.lock:
                if self.path=='/api/register':result=self.server.universe.register(payload.get('name'),payload.get('kind'))
                else:result=self.server.universe.advance(payload.get('atom'),payload.get('params'))
            return self.out(200,result)
        except (ValueError,TypeError,AtomError) as e:return self.out(422,{'error':str(e)})

def serve(project='.',port=8765):
    addr=('127.0.0.1',port)
    srv=LocalServer(addr,project)
    print('ASTRA ATOM local lab: http://127.0.0.1:'+str(srv.server_port),flush=True)
    try:srv.serve_forever()
    except KeyboardInterrupt:pass
    finally:srv.server_close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--project',default='.')
    a=p.parse_args();serve(a.project,a.port)
