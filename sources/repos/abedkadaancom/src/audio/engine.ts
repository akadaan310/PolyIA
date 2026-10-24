// Original procedural sound, synthesized live with Web Audio. Nothing plays
// until the visitor turns sound on (a user gesture); no recordings are used.

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let roomFilter: BiquadFilterNode | null = null;
let reverb: ConvolverNode | null = null;
let drone: { stop: () => void } | null = null;

function ensure(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  if (!ctx) {
    const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
    master = ctx.createGain();
    master.gain.value = 0.0;
    roomFilter = ctx.createBiquadFilter();
    roomFilter.type = 'lowpass';
    roomFilter.frequency.value = 2400;
    reverb = ctx.createConvolver();
    reverb.buffer = impulse(ctx, 3.2, 2.6);
    const wet = ctx.createGain();
    wet.gain.value = 0.35;
    roomFilter.connect(master);
    roomFilter.connect(reverb);
    reverb.connect(wet).connect(master);
    master.connect(ctx.destination);
  }
  return ctx;
}

/** A synthetic stone-hall impulse response: decaying filtered noise. */
function impulse(c: AudioContext, seconds: number, decay: number): AudioBuffer {
  const len = Math.floor(c.sampleRate * seconds);
  const buf = c.createBuffer(2, len, c.sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const d = buf.getChannelData(ch);
    for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
  }
  return buf;
}

export function soundOn(): void {
  const c = ensure();
  if (!c || !master) return;
  void c.resume();
  master.gain.setTargetAtTime(0.55, c.currentTime, 0.6);
  if (!drone) drone = startDrone(c);
}

export function soundOff(): void {
  if (!ctx || !master) return;
  master.gain.setTargetAtTime(0, ctx.currentTime, 0.3);
  const d = drone;
  drone = null;
  setTimeout(() => d?.stop(), 1500);
}

function startDrone(c: AudioContext) {
  const out = c.createGain();
  out.gain.value = 0.06;
  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 520;
  const lfo = c.createOscillator();
  const lfoGain = c.createGain();
  lfo.frequency.value = 0.05;
  lfoGain.gain.value = 180;
  lfo.connect(lfoGain).connect(lp.frequency);
  // a fifth (3:2) and an octave over 55 Hz, slightly detuned
  const freqs = [55, 82.5, 110.4, 164.6];
  const oscs = freqs.map((f, i) => {
    const o = c.createOscillator();
    o.type = i % 2 ? 'sawtooth' : 'triangle';
    o.frequency.value = f;
    o.detune.value = (i - 1.5) * 4;
    o.connect(lp);
    o.start();
    return o;
  });
  lp.connect(out).connect(roomFilter!);
  lfo.start();
  return {
    stop: () => {
      oscs.forEach((o) => o.stop());
      lfo.stop();
    },
  };
}

/** Footsteps / transition whoosh when travelling between campus locations; "soundproof" rooms damp highs. */
export function travel(muffled: boolean): void {
  if (!ctx || !master || master.gain.value < 0.01 || !roomFilter) return;
  roomFilter.frequency.setTargetAtTime(muffled ? 900 : 2400, ctx.currentTime, 0.4);
  for (let i = 0; i < 4; i++) step(ctx.currentTime + i * 0.42);
}

function step(at: number) {
  const c = ctx!;
  const len = Math.floor(c.sampleRate * 0.12);
  const b = c.createBuffer(1, len, c.sampleRate);
  const d = b.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.exp((-i / len) * 9);
  const src = c.createBufferSource();
  src.buffer = b;
  const f = c.createBiquadFilter();
  f.type = 'bandpass';
  f.frequency.value = 180 + Math.random() * 60;
  const g = c.createGain();
  g.gain.value = 0.5;
  src.connect(f).connect(g).connect(roomFilter!);
  src.start(at);
}

export function pageTurn(): void {
  if (!ctx || !master || master.gain.value < 0.01) return;
  const c = ctx;
  const len = Math.floor(c.sampleRate * 0.35);
  const b = c.createBuffer(1, len, c.sampleRate);
  const d = b.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.sin((Math.PI * i) / len) * 0.6;
  const src = c.createBufferSource();
  src.buffer = b;
  const f = c.createBiquadFilter();
  f.type = 'highpass';
  f.frequency.setValueAtTime(800, c.currentTime);
  f.frequency.linearRampToValueAtTime(3800, c.currentTime + 0.35);
  src.connect(f).connect(roomFilter!);
  src.start();
}

/** Play the computed interval orbit as tones (MIDI 60 + pitch class). Requires sound on. */
export function playOrbit(pcs: number[], stepSec = 0.32): boolean {
  if (!ctx || !master || master.gain.value < 0.01 || !roomFilter) return false;
  const c = ctx;
  pcs.forEach((pc, i) => {
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = 'sine';
    o.frequency.value = 440 * 2 ** ((60 + pc - 69) / 12);
    const t = c.currentTime + i * stepSec;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.18, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.001, t + stepSec * 1.8);
    o.connect(g).connect(roomFilter!);
    o.start(t);
    o.stop(t + stepSec * 2);
  });
  return true;
}

export function speak(text: string): void {
  if (typeof speechSynthesis === 'undefined') return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 0.95;
  u.pitch = 0.9;
  speechSynthesis.speak(u);
}
