"""Browser rendering with file content injected; local navigations blocked by administrator.
The web UI's fetch calls are bridged to the actual local ATOM HTTP API.
"""
from playwright.sync_api import sync_playwright
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from pathlib import Path
import tempfile,shutil,threading,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atom.server import LocalServer
import json
root=Path(__file__).resolve().parents[1];out=root/'evidence'
tmp=tempfile.TemporaryDirectory();temp_project=Path(tmp.name)
for folder in ('web','examples','atom'):
    shutil.copytree(root/folder,temp_project/folder,ignore=shutil.ignore_patterns('__pycache__'))
http=LocalServer(('127.0.0.1',0),temp_project);threading.Thread(target=http.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(http.server_port)
html=(root/'web/index.html').read_text().replace('<link rel="stylesheet" href="/style.css"/>','').replace('<script src="/app.js"></script>','')
style=(root/'web/style.css').read_text();js=(root/'web/app.js').read_text()
results={'mode':'Chromium set_content with exact local UI files and Python-bridged real HTTP API (administrator blocks browser navigation)','tests':{},'errors':[]}
def bridge(source,url,body=None):
    if not url.startswith(('/api/','/stars.json')):raise ValueError('Disallowed request')
    method='POST' if body is not None else 'GET'
    req=Request(base+url,method=method,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
    try:
        with urlopen(req,timeout=6) as r:return {'ok':True,'status':r.status,'value':json.loads(r.read())}
    except HTTPError as e:return {'ok':False,'status':e.code,'value':json.loads(e.read())}

def make_page(browser,viewport,mobile=False):
    page=browser.new_page(viewport=viewport,device_scale_factor=1,is_mobile=mobile,has_touch=mobile)
    page.on('pageerror',lambda e:results['errors'].append(str(e)))
    page.goto('about:blank')
    page.set_content(html)
    page.add_style_tag(content=style)
    page.expose_binding('atomBridge',bridge)
    page.evaluate('''() => {window.fetch=async (url,opts={})=>{let data=await window.atomBridge(url,opts.body?JSON.parse(opts.body):undefined);return {ok:data.ok,status:data.status,json:async()=>data.value}}}''')
    page.add_script_tag(content=js)
    page.wait_for_timeout(1700)
    return page

def api(route,body=None):return bridge(None,route,body)['value']
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu-sandbox'])
    page=make_page(browser,{'width':1536,'height':920})
    results['tests']['real_canvas']=page.locator('#plate-plasma').evaluate('(x)=>x.width')>0
    results['tests']['api_alive']='ATOM/0.1'==api('/api/state')['protocol']
    page.screenshot(path=str(out/'astra-desktop.png'),full_page=True)
    page.locator('#register').click();page.wait_for_timeout(200)
    results['tests']['registered']='journey-01' in api('/api/state')['atoms']
    for _ in range(6):page.locator('#step').click();page.wait_for_timeout(170)
    s=api('/api/state');results['tests']['checkpoint_one']=s['phase']=='HOLD' and len(s['committed'])==1
    page.locator('#step').click();page.wait_for_timeout(160)
    results['tests']['resume']=page.locator('#phase').inner_text()=='OBSERVE'
    page.locator('#atom-kind').select_option('render');page.locator('#register').click();page.wait_for_timeout(170)
    for _ in range(6):page.locator('#step').click();page.wait_for_timeout(170)
    s=api('/api/state');results['tests']['checkpoint_two']=len(s['committed'])==2
    page.locator('#separation').fill('70');page.wait_for_timeout(400)
    results['tests']['spring_separation']=page.locator('#sepvalue').inner_text()=='70%'
    page.locator('#viewport').hover(position={'x':230,'y':115});page.wait_for_timeout(250)
    results['tests']['focus_label']='%' in page.locator('#attention').inner_text()
    page.screenshot(path=str(out/'astra-interaction.png'),full_page=True)
    mobile=make_page(browser,{'width':412,'height':915},True)
    mobile.screenshot(path=str(out/'astra-mobile.png'),full_page=True)
    results['tests']['mobile_render']=mobile.locator('#plate-plasma').evaluate('(x)=>x.width')>0
    results['tests']['api_report_verified']=api('/api/report')['verification']['verified']
    browser.close()
http.shutdown();http.server_close();tmp.cleanup()
results['ok']=all(results['tests'].values()) and not results['errors']
(out/'browser_report.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
if not results['ok']:raise SystemExit(1)
