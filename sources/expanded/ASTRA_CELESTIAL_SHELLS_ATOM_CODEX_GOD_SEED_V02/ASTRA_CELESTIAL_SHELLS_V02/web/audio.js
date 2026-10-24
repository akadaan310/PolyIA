/* Original live WebAudio composition: note frequencies form the C major set;
   panning is a perceptual sonification, NOT audible sound in vacuum.
   Never modifies device volume; initial master gain modest + compressor. */
(function(global){'use strict';
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const NOTES=[130.8128,146.8324,164.8138,174.6141,195.9977,220,246.9417];
class SpatialSynthesis{
 constructor(){this.ctx=null;this.enabled=false;this.muted=false;this.volume=.34;this.voices=[];this.started=0;this.master=null;this.analyser=null;this.liveSources=[];}
 async enable(){if(this.enabled){await this.ctx.resume();return}let C=global.AudioContext||global.webkitAudioContext;if(!C)throw Error('Web Audio unsupported');let ac=new C();await ac.resume();this.ctx=ac;this.started=ac.currentTime;this.mix=ac.createGain();this.mix.gain.value=0;
 const limiter=ac.createDynamicsCompressor();limiter.threshold.value=-22;limiter.knee.value=14;limiter.ratio.value=12;limiter.attack.value=.006;limiter.release.value=.24;this.limiter=limiter;this.analyser=ac.createAnalyser();this.analyser.fftSize=512;this.master=ac.createGain();this.master.gain.value=.35;
 this.mix.connect(limiter);limiter.connect(this.master);this.master.connect(this.analyser);this.analyser.connect(ac.destination);
 // 7-note spatial pad with gentle partials; loops indefinitely until stopped.
 for(let i=0;i<7;i++){const panner=ac.createStereoPanner(),lowpass=ac.createBiquadFilter(),gain=ac.createGain();lowpass.type='lowpass';lowpass.frequency.value=850+i*90;gain.gain.value=0;panner.pan.value=(i-3)/5.5;
 let base=NOTES[i]*(i%2===0?1:0.5),osc=ac.createOscillator();osc.type=i%3===0?'sine':'triangle';osc.frequency.value=base;let harmonic=ac.createOscillator();harmonic.type='sine';harmonic.frequency.value=base*2.001;
 const hg=ac.createGain();hg.gain.value=.095;osc.connect(gain);harmonic.connect(hg);hg.connect(gain);gain.connect(lowpass);lowpass.connect(panner);panner.connect(this.mix);osc.start();harmonic.start();this.voices.push({osc,harmonic,gain,panner,lowpass,i,base})}
 // Synthesized low-frequency breath; quiet, filtered, source-local.
 const noise=ac.createBuffer(1,ac.sampleRate*3,ac.sampleRate),data=noise.getChannelData(0);let x=3389;for(let i=0;i<data.length;i++){x=(1664525*x+1013904223)>>>0;data[i]=((x/4294967295)*2-1)*.12};let src=ac.createBufferSource();src.buffer=noise;src.loop=true;let filter=ac.createBiquadFilter();filter.type='lowpass';filter.frequency.value=170;let ng=ac.createGain();ng.gain.value=.017;src.connect(filter);filter.connect(ng);ng.connect(this.mix);src.start();this.liveSources.push(src);
 this.enabled=true;this.setVolume(this.volume);this.update();}
 update(){if(!this.enabled)return;const t=this.ctx.currentTime-this.started;for(const v of this.voices){let pulse=.008+(.01+.003*Math.sin(v.i))* (.5+.5*Math.sin(t*.29+v.i*1.7))*(.75+.25*Math.cos(t*.12));v.gain.gain.setTargetAtTime(pulse,this.ctx.currentTime,.17);v.panner.pan.setTargetAtTime(clamp(Math.sin(t*.17+v.i*1.08)*.9,-1,1),this.ctx.currentTime,.22);v.lowpass.frequency.setTargetAtTime(350+480*(.5+.5*Math.sin(t*.08+v.i)),this.ctx.currentTime,.24)}this.animation=global.requestAnimationFrame?.(()=>this.update())}
 setVolume(v){this.volume=clamp(v,0,1);if(this.master){let actual=this.muted?0:Math.pow(this.volume,1.6)*.65;this.master.gain.setTargetAtTime(actual,this.ctx.currentTime,.09)} }
 toggleMute(){this.muted=!this.muted;this.setVolume(this.volume);return this.muted}
 pulse(obj){if(!this.enabled||this.muted)return;let idx=Math.abs([...String(obj?.name||'star')].reduce((n,ch)=>n*31+ch.codePointAt(0),7))%7;this.chime(idx,.09)}
 shift(dest){if(!this.enabled||this.muted)return;for(let i=0;i<3;i++)global.setTimeout(()=>this.chime((i+2)%7,.11),i*140)}
 chime(idx=.0,weight=.1){const ac=this.ctx;if(!ac||ac.state!=='running')return;let now=ac.currentTime,osc=ac.createOscillator(),g=ac.createGain(),pan=ac.createStereoPanner();osc.type='sine';osc.frequency.setValueAtTime(NOTES[idx%7]*2,now);osc.frequency.exponentialRampToValueAtTime(NOTES[idx%7]*2.018,now+.25);g.gain.setValueAtTime(.0001,now);g.gain.exponentialRampToValueAtTime(weight*.5,now+.014);g.gain.exponentialRampToValueAtTime(.0001,now+.6);pan.pan.value=Math.sin(idx*.9)*.75;osc.connect(g);g.connect(pan);pan.connect(this.mix);osc.start(now);osc.stop(now+.64)}
 diagnostic(){return {enabled:this.enabled,muted:this.muted,voices:this.voices.length,volume:this.volume,limiter:!!this.limiter,source:'generated oscillator pads / deterministic filtered noise',policy:'user-activated; reduced starting level'}}
 stop(){global.cancelAnimationFrame?.(this.animation);for(const v of this.voices){try{v.osc.stop();v.harmonic.stop()}catch{}}for(const s of this.liveSources){try{s.stop()}catch{}}this.ctx?.close();this.enabled=false}
}
const api={SpatialSynthesis,NOTES};if(typeof module!=='undefined'&&module.exports)module.exports=api;global.AstraSound=api;
})(typeof window!=='undefined'?window:globalThis);
