"""Generate the project-owned synthetic audio samples reproducibly.
Requires optional numpy >=1.24; runtime ASTRA itself needs no numpy.
These samples are not recordings of actual celestial acoustic events.
"""
from pathlib import Path
import wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]/'audio_assets';ROOT.mkdir(exist_ok=True)
SAMPLE_RATE=24000

def emit(name,length):
    t=np.arange(SAMPLE_RATE*length)/SAMPLE_RATE
    if name=='celestial-drift':
        notes=(130.8128,164.8138,195.9977,246.9417)
        left=np.zeros_like(t);right=np.zeros_like(t)
        for j,n in enumerate(notes):
            f=n*(1+.0015*np.sin(2*np.pi*.09*t+j))
            ph=2*np.pi*np.cumsum(f)/SAMPLE_RATE
            env=(.3+.7*(.5+.5*np.sin(2*np.pi*.08*t+j*1.4)))*(.35+.65*np.sin(np.pi*np.minimum(t/length,1))**.3)
            tone=(np.sin(ph)+.22*np.sin(2.01*ph))*.12*env
            left+=tone*(.75+.25*np.sin(2*np.pi*.045*t+j))
            right+=tone*(.75-.25*np.sin(2*np.pi*.045*t+j))
    else:
        base=392;env=np.exp(-t*3.4)*(1-np.exp(-t*40))
        sig=(.4*np.sin(2*np.pi*base*t)+.18*np.sin(2*np.pi*base*1.5*t))*env
        left=sig;right=sig*np.cos(t*1.2)
    samples=np.stack((left,right),axis=-1)
    samples=np.clip(samples,-.72,.72)
    pcm=(samples*32767).astype('<i2').tobytes()
    path=ROOT/(name+'.wav')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SAMPLE_RATE);f.writeframes(pcm)
    print(name, len(pcm), 'peak',round(float(np.max(abs(samples))),4))

if __name__=='__main__':
    emit('celestial-drift',11);emit('portal-chime',2)
