"""No dependencies; confirm original WAV assets and peak/rms of signal."""
from pathlib import Path
import wave,struct,math,json
root=Path(__file__).resolve().parents[1]
results=[]
for p in sorted((root/'audio_assets').glob('*.wav')):
 with wave.open(str(p),'rb') as w:
  assert w.getnchannels()==2 and w.getsampwidth()==2 and w.getframerate()==24000
  raw=w.readframes(w.getnframes());frames=w.getnframes()
  pcm=struct.unpack('<'+'h'*(frames*2),raw)
  peak=max(abs(x) for x in pcm)/32768
  rms=math.sqrt(sum(x*x for x in pcm)/len(pcm))/32768
  results.append({'filename':p.name,'channels':2,'frames':frames,'seconds':frames/24000,'peak_sample':peak,'rms':rms,'clipped_samples':sum(abs(x)>=32767 for x in pcm)})
assert len(results)==2
assert all(r['peak_sample']<.75 and r['clipped_samples']==0 for r in results)
print(json.dumps(results,indent=2))
