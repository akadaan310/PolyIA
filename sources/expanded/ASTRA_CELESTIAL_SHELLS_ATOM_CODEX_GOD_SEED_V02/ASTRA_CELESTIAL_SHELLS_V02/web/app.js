'use strict';
const $=id=>document.getElementById(id);
const steps=['OBSERVE','PROPOSE','ADMIT','EXECUTE','VERIFY','CHECKPOINT','HOLD'];
const colors={stars:'#78e9df',plasma:'#b18bf5',focus:'#efc593'};
const plateSpring={stars:{y:0,v:0,goal:0,scale:1},plasma:{y:0,v:0,goal:0,scale:1},focus:{y:0,v:0,goal:0,scale:1}};
let state=null,viewKind='journey',allStars=[],isPaused=false,time=0,prev=performance.now(),samples=[],pointer={x:.50,y:.50,known:false,stamp:0},focus={x:.5,y:.5},separation=.36;
const canvases=['plate-stars','plate-plasma','plate-focus','wave-mini'].map(id=>$(id));
function sizeCanvas(c){const b=c.getBoundingClientRect(),pr=Math.min(devicePixelRatio||1,1.5);const w=Math.max(1,Math.round(b.width*pr)),h=Math.max(1,Math.round(b.height*pr));if(c.width!==w||c.height!==h){c.width=w;c.height=h}let ctx=c.getContext('2d');ctx.setTransform(pr,0,0,pr,0,0);return {ctx,w:b.width,h:b.height}}
let skyEngine=null,spaceGPU=null,spatialAudio=null,intentBus=new AstraIntent.IntentBus();
function backgroundStars(t){const {ctx,w,h}=sizeCanvas($('plate-stars'));if(skyEngine)skyEngine.draw(ctx,w,h,t);else ctx.clearRect(0,0,w,h);if(spaceGPU)spaceGPU.draw(skyEngine,w,h,t)}

function plasma(t){const {ctx,w,h}=sizeCanvas($('plate-plasma'));ctx.clearRect(0,0,w,h);const vanish=Math.min(h*.96,450);const origin=h*.48;ctx.save();ctx.translate(0,0);
for(let r=0;r<25;r++){let depth=r/25;let y=origin + ((r/24)*vanish)-h*.17;let alpha=(.14+depth*.32),color=r%4===0?`rgba(128,232,223,${alpha})`:r%3===0?`rgba(168,145,245,${alpha})`:`rgba(77,154,225,${alpha*.70})`;
ctx.strokeStyle=color;ctx.lineWidth=r%5===0?1.15:.65;ctx.beginPath();for(let i=0;i<=100;i++){let u=i/100, x=u*w;let bell=Math.exp(-Math.pow((u-.52)*2.2,2));let amplitude=(15+43*depth)*bell;let wiggle=(Math.sin(u*10.8+t*.78+depth*4.5)+.52*Math.sin(u*21.7-t*.37+depth*5.1)+.20*Math.cos(u*36+depth*8))*amplitude;let v=y+wiggle+Math.cos(t*.43+r)*4; if(i===0)ctx.moveTo(x,v);else ctx.lineTo(x,v)}ctx.stroke()}
// Longitudinal mesh lines contribute the distinctive flowing plasmic sheet.
for(let j=0;j<36;j++){let u=j/35,topx=u*w;ctx.strokeStyle=j%5===0?'rgba(126,220,222,.17)':'rgba(115,150,220,.09)';ctx.lineWidth=.5;ctx.beginPath();for(let i=0;i<=32;i++){let d=i/32,xx=topx+(u-.5)*d*37+Math.sin(d*5+u*10+t*.18)*d*14;let yy=origin+d*vanish-h*.17 + (Math.sin(u*10.8+t*.78+d*4.5)+Math.sin(u*21.7-t*.37+d*5.1)*.52)*(15+43*d)*Math.exp(-Math.pow((u-.52)*2.2,2));if(i===0)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy)}ctx.stroke()}
let halo=ctx.createRadialGradient(w*.55,origin,2,w*.55,origin,w*.34);halo.addColorStop(0,'rgba(74,230,214,.08)');halo.addColorStop(.7,'rgba(99,104,205,.055)');halo.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=halo;ctx.fillRect(0,0,w,h);ctx.restore()}
function focusPlate(t){let {ctx,w,h}=sizeCanvas($('plate-focus'));ctx.clearRect(0,0,w,h);const tar=pointer.known?pointer:{x:.5+Math.cos(t*.25)*.20,y:.48+Math.sin(t*.18)*.13};focus.x+=(tar.x-focus.x)*.055;focus.y+=(tar.y-focus.y)*.055;let x=focus.x*w,y=focus.y*h;
let grad=ctx.createRadialGradient(x,y,5,x,y,110);grad.addColorStop(0,'rgba(178,241,224,.065)');grad.addColorStop(1,'rgba(60,180,198,0)');ctx.fillStyle=grad;ctx.beginPath();ctx.arc(x,y,110,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba(180,244,230,.26)';ctx.lineWidth=.8;ctx.beginPath();ctx.arc(x,y,18+Math.sin(t*1.1)*1.5,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(x-31,y);ctx.lineTo(x-23,y);ctx.moveTo(x+23,y);ctx.lineTo(x+31,y);ctx.moveTo(x,y-31);ctx.lineTo(x,y-23);ctx.moveTo(x,y+23);ctx.lineTo(x,y+31);ctx.stroke();
$('attention').textContent=`${Math.round(focus.x*100)}% · ${Math.round(focus.y*100)}%`;let bl=$('att-blip');bl.style.left=(focus.x*100)+'%';bl.style.top=(focus.y*100)+'%';}
function tinyWave(t){let {ctx,w,h}=sizeCanvas($('wave-mini'));ctx.clearRect(0,0,w,h);ctx.strokeStyle='#233d50';ctx.lineWidth=.7;for(let i=0;i<5;i++){ctx.beginPath();ctx.moveTo(0,h*(i+1)/6);ctx.lineTo(w,h*(i+1)/6);ctx.stroke()}
for(let k=0;k<3;k++){ctx.beginPath();ctx.strokeStyle=['rgba(109,224,212,.9)','rgba(174,148,245,.55)','rgba(95,143,229,.45)'][k];ctx.lineWidth=k===0?1.6:1;for(let i=0;i<=180;i++){let x=i/180*w,y=h*.52+Math.sin(i/180*21-t*.75+k*1.4)*(13+k*8)+Math.sin(i/180*55+t*.5+k)*5; if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.stroke()}}
function draw(timestamp){let dt=Math.min(.1,(timestamp-prev)/1000);prev=timestamp;if(!isPaused)time+=dt;const speed=dt?1/dt:0;samples.push(speed);if(samples.length>120)samples.shift();if(samples.length%20===0){let sorted=samples.slice().sort((a,b)=>a-b);$('fps').textContent= Math.round(sorted[Math.floor(sorted.length/2)]||0)+' FPS'}
for(const [name,item] of Object.entries(plateSpring)){let accel=65*(item.goal-item.y)-14*item.v;item.v+=accel*dt;item.y+=item.v*dt;$('plate-'+name).style.transform=`translateY(${item.y.toFixed(2)}px) scale(${item.scale})`; }
const on=id=>$(id).checked; if(on('enable-stars'))backgroundStars(time);else {sizeCanvas($('plate-stars')).ctx.clearRect(0,0,$('plate-stars').width,$('plate-stars').height);if(spaceGPU)spaceGPU.clear()}
if(on('enable-plasma'))plasma(time);else sizeCanvas($('plate-plasma')).ctx.clearRect(0,0,$('plate-plasma').width,$('plate-plasma').height);
if(on('enable-focus'))focusPlate(time);else sizeCanvas($('plate-focus')).ctx.clearRect(0,0,$('plate-focus').width,$('plate-focus').height);
tinyWave(time);requestAnimationFrame(draw)}
async function api(url,payload){const opts=payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)};let res=await fetch(url,opts);let data=await res.json();if(!res.ok)throw new Error(data.error||'Request error '+res.status);return data}
function event(msg,bad=false){$('last-event').style.color=bad?'#f9b5a4':'#8fd3c9';$('last-event').textContent=msg}
function params(kind){if(kind==='journey')return {destination:$('destination').value};if(kind==='render')return {plates:['stars','plasma','focus'],depth:[.12,.5,.95]};if(kind==='focus')return {x:+focus.x.toFixed(3),y:+focus.y.toFixed(3)};return {}}
async function renderState(){state=await api('/api/state');const p=steps.indexOf(state.phase);$('phase').textContent=state.phase;$('phase-index').textContent=`0${p+1} / 07`;$('phase-bars').innerHTML=steps.map((_,i)=>`<i class="${i<=p?'passed':''}"></i>`).join('');$('clock-tick').textContent='TICK '+String(state.tick).padStart(3,'0');$('checkpoint-count').textContent=String(state.committed.length).padStart(2,'0');$('checkpoint-hash').textContent=state.last_checkpoint?(state.last_checkpoint.slice(0,12)+'…'):'No checkpoint';$('credits').textContent=state.credits;
let explain={OBSERVE:'Choose and register a micro-automaton.',PROPOSE:'Ready to choose a maximin policy action.',ADMIT:'Ready to validate the declared operation contract.',EXECUTE:'Ready to evaluate the admitted pure operation.',VERIFY:'Ready for deterministic result verification.',CHECKPOINT:'Ready to lock a content-addressed snapshot.',HOLD:'Checkpoint locked. Advance once to resume observing.'};$('phase-note').textContent=explain[state.phase];$('step-description').textContent=explain[state.phase]+' Every press advances exactly one phase.';for(const r of document.querySelectorAll('.atomrow')){let kind=r.dataset.kind;let a=Object.values(state.atoms).filter(x=>x.kind===kind);r.querySelector('.atomstate').textContent=a.length?(a.at(-1).runs?'VERIFIED':'ADMITTED'):'READY'}
$('integrity').textContent='VERIFYING';try{let report=await api('/api/report');$('integrity').textContent=report.verification.verified?'CHAIN VALID':'INVALID'}catch(e){$('integrity').textContent='CHECK ERROR'}
$('register').disabled=state.phase!=='OBSERVE';}
$('destination').addEventListener('change',()=>{$('dest-view').innerHTML=$('destination').value+'<br/><small>Shift destination</small>'});
$('atom-kind').addEventListener('change',e=>{viewKind=e.target.value});
$('register').addEventListener('click',async()=>{try{let kind=$('atom-kind').value;let name=kind+'-01';await api('/api/register',{name,kind});event('Registered '+name+' · typed machine ready');await renderState()}catch(e){event(e.message,true)}});
$('step').addEventListener('click',async()=>{try{if(!state)await renderState();const kind=$('atom-kind').value;let name=state.phase==='OBSERVE'?kind+'-01':undefined;let out=await api('/api/advance',{atom:name,params:state.phase==='OBSERVE'?params(kind):{}});event(`TICK ${out.tick} → ${out.phase}${out.checkpoint?' · '+out.checkpoint.slice(0,10):''}`);await renderState()}catch(e){event(e.message,true)}});
$('report').addEventListener('click',async()=>{try{let report=await api('/api/report');await navigator.clipboard.writeText(JSON.stringify(report,null,2));event('Verified ATOM-HANDOFF report copied · paste into Codex or ChatGPT')}catch(e){event('Copy unavailable: '+e.message,true)}});
$('separation').addEventListener('input',e=>{separation=e.target.value/100;$('sepvalue').textContent=e.target.value+'%';plateSpring.stars.goal=-35*separation;plateSpring.stars.scale=1-.055*separation;plateSpring.plasma.goal=23*separation;plateSpring.plasma.scale=1+.03*separation;plateSpring.focus.goal=65*separation;});
$('viewport').addEventListener('pointermove',e=>{let r=$('viewport').getBoundingClientRect();pointer={x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height)),known:true,stamp:performance.now()}});
$('viewport').addEventListener('pointerleave',()=>{pointer.known=false});
(async()=>{try{let stars=await api('/stars.json');allStars=stars.stars.slice(0,100);skyEngine=new CelestialShells.SkyEngine(stars.stars.slice(0,140));if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)skyEngine.autorotate=false;spaceGPU=new CelestialGPU.StarGPU($('plate-gpu'));skyEngine.setSelectHandler(obj=>{const card=$('objectcard');card.querySelector('strong').textContent=obj.name;card.querySelector('p').textContent=obj.description;event('Selected celestial node · '+obj.name);if(spatialAudio)spatialAudio.pulse(obj);});skyEngine.setStateHandler(s=>{$('space-status').textContent=`SHELL ${s.level+1} / 04 · ${s.neighborhood} · ${s.distanceMode}`;});skyEngine.attach($('viewport'));window.__astraSky=skyEngine;let policy=await api('/api/choose');$('policy').textContent=policy.action;$('utility').textContent='+'+String(policy.worst_case_utility).padStart(2,'0');await renderState();event('Scientific render plate initialized · ATOM ledger ready')}catch(e){event('API disconnected: '+e.message,true)}requestAnimationFrame(draw)})();

// Visual actions are typed inputs to local micro-state; stateful build operations
// continue to require the verified ATOM protocol and explicit step admission.
// Register typed handlers once. UI state is speculative/read-only until the
// operator advances the separate durable ATOM machine to CHECKPOINT.
intentBus.register('shell.expand',()=>skyEngine?.expand());
intentBus.register('shell.contract',()=>skyEngine?.contract());
intentBus.register('shell.orbit',()=>{if(skyEngine){skyEngine.autorotate=!skyEngine.autorotate;$('autotour').classList.toggle('active',skyEngine.autorotate)}});
intentBus.register('shell.grid',()=>{if(skyEngine){skyEngine.grid=!skyEngine.grid;$('toggle-grid').classList.toggle('active',skyEngine.grid)}});
intentBus.register('celestial.focus',({name})=>({name}));
intentBus.register('journey.shift',({destination})=>{if(!skyEngine?.travel(destination))throw Error('No such destination');spatialAudio?.shift(destination);event('Visual shift → '+destination+' (schematic, not ephemeris-backed)');if($('haptic-opt-in').checked&&navigator.vibrate)navigator.vibrate(18);return {destination,mode:'MODELED',checkpoint:'NOT_COMMITTED'}});
intentBus.register('sound.enable',async()=>{if(!spatialAudio)spatialAudio=new AstraSound.SpatialSynthesis();await spatialAudio.enable();$('audio-state').textContent='LIVE SYNTHESIS · 7-tone orchestration · limiter active';$('sound-on').textContent='SOUND ACTIVE ✓';$('sound-object').textContent='Generative sound field · headphones enhance spatial movement';return {voices:spatialAudio.voices.length}});
intentBus.register('sound.mute',()=>{if(spatialAudio){spatialAudio.toggleMute();$('sound-mute').textContent=spatialAudio.muted?'UNMUTE':'MUTE'}return {muted:spatialAudio?.muted??false}});
$('go-in').onclick=()=>intentBus.dispatch('shell.expand');
$('go-out').onclick=()=>intentBus.dispatch('shell.contract');
$('autotour').onclick=()=>intentBus.dispatch('shell.orbit');
$('toggle-grid').onclick=()=>intentBus.dispatch('shell.grid');
$('engage-shift').onclick=()=>intentBus.dispatch('journey.shift',{destination:$('destination').value}).catch(e=>event(e.message,true));
$('sound-on').onclick=()=>intentBus.dispatch('sound.enable').catch(e=>$('audio-state').textContent='Audio unavailable: '+e.message);
$('sound-mute').onclick=()=>intentBus.dispatch('sound.mute');
$('mastervolume').oninput=e=>spatialAudio?.setVolume(+e.target.value/100);
window.__astraDiagnostic=()=>({sky:skyEngine?.diagnostic()||null,renderer:spaceGPU?.diagnostic()||null,audio:spatialAudio?.diagnostic()||{enabled:false},atomPhase:state?.phase,intentBus:intentBus.inspect()});
