import json, sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
ev=json.load(open(sys.argv[1])); vdir=sys.argv[2]; music=sys.argv[3]; out=sys.argv[4]; keys=sys.argv[5].split(',')
OFF=json.loads(sys.argv[6]) if len(sys.argv)>6 else {}
SR=44100; m,msr=sf.read(music); assert msr==SR
if m.ndim==1: m=np.stack([m,m],1)
N=len(m); voice=np.zeros(N)
starts=[0]+ev['boundaries']
items=[]
for k,t0 in zip(keys,starts):
    for kk,off in (OFF.get(k) or [[k,0.25]]): items.append((kk,t0+off-0.25))
report=[]
for k,t0 in items:
    v,vsr=sf.read(f'{vdir}/{k}.wav'); report.append((k,round(t0+0.25,2),round(t0+0.25+len(v)/vsr,2)))
    v=resample_poly(v,SR,vsr); v=v*(10**(-29/20)/np.sqrt(np.mean(v**2)))
    # voice eq: slight low cut + presence
    v=sosfilt(butter(2,90,'high',fs=SR,output='sos'),v)
    i=int((t0+0.25)*SR); j=min(N,i+len(v)); voice[i:j]+=v[:j-i]
voice=voice/np.max(np.abs(voice))*0.9
# duck music by voice envelope
env=np.abs(voice); w=int(0.25*SR); env=np.convolve(env,np.ones(w)/w,'same'); env=env/env.max()
duck=1-0.72*np.clip(env*4,0,1)
mix=m*0.55*duck[:,None]+voice[:,None]*0.95
mix=np.tanh(mix*1.2)/1.2; mix=mix/np.max(np.abs(mix))*0.89
sf.write(out,mix,SR); print('ok',len(mix)/SR); json.dump(report,open(out+'.json','w'))
