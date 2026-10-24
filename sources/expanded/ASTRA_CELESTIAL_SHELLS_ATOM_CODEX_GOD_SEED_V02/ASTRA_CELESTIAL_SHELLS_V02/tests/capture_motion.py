"""Capture browser-native plate animation frames and assemble an indicative GIF.
This is not a jitter/FPS benchmark; frame capture changes timing.
"""
import json,sys,io,tempfile,shutil,threading
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atom.server import LocalServer
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
  project=Path(temp)
  for folder in ('web','examples','atom'):
    shutil.copytree(root/folder,project/folder,ignore=shutil.ignore_patterns('__pycache__'))
  server=LocalServer(('127.0.0.1',0),project);threading.Thread(target=server.serve_forever,daemon=True).start()
  url='http://127.0.0.1:'+str(server.server_port)
  html=(root/'web/index.html').read_text().replace('<link rel="stylesheet" href="/style.css"/>','').replace('<script src="/app.js"></script>','')
  with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':1280,'height':860},device_scale_factor=1)
    page.goto('about:blank');page.set_content(html);page.add_style_tag(content=(root/'web/style.css').read_text())
    payloads={ '/api/state':json.loads(urlopen(url+'/api/state').read()),'/api/report':json.loads(urlopen(url+'/api/report').read()),'/api/choose':json.loads(urlopen(url+'/api/choose').read()),'/stars.json':json.loads(urlopen(url+'/stars.json').read())}
    page.evaluate('''(payloads)=>{window.fetch=async (url)=>({ok:!!payloads[url],status:payloads[url]?200:404,json:async()=>payloads[url]})}''',payloads)
    page.add_script_tag(content=(root/'web/app.js').read_text());page.wait_for_timeout(700)
    images=[]
    for i in range(16):
      data=page.locator('#viewport').screenshot(type='png')
      im=Image.open(io.BytesIO(data)).convert('RGB');im.thumbnail((760,425));images.append(im)
      page.wait_for_timeout(110)
    path=root/'evidence/astra-wave-motion.gif'
    images[0].save(path,save_all=True,append_images=images[1:],loop=0,duration=130,optimize=True)
    print('GIF',path,path.stat().st_size,'bytes',len(images),'actual browser frames')
    b.close()
  server.shutdown()
