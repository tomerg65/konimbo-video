import sys, subprocess, numpy as np, json
f=sys.argv[1]; fps=10; W,H=192,108
p=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf',f'fps={fps},scale={W}:{H},format=gray','-f','rawvideo','-'],capture_output=True)
a=np.frombuffer(p.stdout,np.uint8).reshape(-1,H,W).astype(np.float32)
diff=np.abs(np.diff(a,axis=0)).mean(axis=(1,2)); mean=a.mean(axis=(1,2))
print('frames',len(a),'dur',len(a)/fps)
# static stretches (>2.5s with nearly no change)
st=[];run=0
for i,d in enumerate(diff):
    if d<0.15: run+=1
    else:
        if run>=int(2.5*fps): st.append((round((i-run)/fps,1),round(i/fps,1)))
        run=0
if run>=int(2.5*fps): st.append((round((len(diff)-run)/fps,1),round(len(diff)/fps,1)))
print('static stretches >2.5s:',st)
print('dark frames (mean<8):',[round(i/fps,1) for i,m in enumerate(mean) if m<8][:20])
big=[(round(i/fps,1),round(float(d),1)) for i,d in enumerate(diff) if d>25]
print('hard jumps:',big)
