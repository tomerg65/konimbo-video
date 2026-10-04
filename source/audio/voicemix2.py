import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
P=json.load(open('place_v2.json')); SR=44100
m,_=sf.read('music_long.wav'); N=len(m); voice=np.zeros(N)
starts={}; acc=0
for k,d in P['TL']: starts[k]=acc; acc+=d
rep=[]
for sc,cue,st in P['place']:
    v,vsr=sf.read(f'/home/claude/tts/out_v2/{sc}_{cue}.wav'); v=resample_poly(v,SR,vsr)
    v=sosfilt(butter(2,90,'high',fs=SR,output='sos'),v); v=v*(10**(-29/20)/np.sqrt(np.mean(v**2)))
    i=int((starts[sc]+st)*SR); j=min(N,i+len(v)); voice[i:j]+=v[:j-i]; rep.append((sc,cue,round(starts[sc]+st,2),round((starts[sc]+st)+len(v)/SR,2)))
voice=voice/np.max(np.abs(voice))*0.9
env=np.abs(voice); w=int(0.3*SR); env=np.convolve(env,np.ones(w)/w,'same'); env/=env.max()
duck=1-0.75*np.clip(env*4,0,1)
mix=m*0.5*duck[:,None]+voice[:,None]*0.95
mix=np.tanh(mix*1.2)/1.2; mix=mix/np.max(np.abs(mix))*0.89
sf.write('mix_long2.wav',mix,SR)
bounds=[starts[k] for k in starts][1:]+[acc]
over=[r for r in rep if r[3]> [b for b in bounds if b>r[2]][0]-0.2]
print('segments',len(rep),'overruns',over)
