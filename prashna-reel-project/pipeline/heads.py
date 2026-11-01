import json, subprocess, numpy as np
w,h=270,480; S=1080/w
p=subprocess.run(['ffmpeg','-v','error','-i','matte.mp4','-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
fr=np.frombuffer(p,np.uint8).reshape(-1,h,w)
out=[]
for m in fr:
    rows=np.where((m>128).sum(1)>3)[0]
    if len(rows)==0: out.append(None); continue
    top=rows[0]; band=m[top:top+30]>128; xs=np.where(band.any(0))[0]
    out.append([float(xs.mean()*S), float(top*S)])
# smooth
arr=np.array([o if o else [np.nan,np.nan] for o in out]); 
for c in range(2):
    s=arr[:,c]; idx=np.arange(len(s)); good=~np.isnan(s); s=np.interp(idx,idx[good],s[good])
    k=np.ones(9)/9; arr[:,c]=np.convolve(np.pad(s,4,mode='edge'),k,'valid')
tl=json.load(open('../reel/src/timeline.json'))
for s in tl['shots']:
    a,b=round(s['e_in']*30),round(s['e_out']*30); seg=arr[a:b]
    hx,top=np.median(seg[:,0]),np.median(seg[:,1])
    foc=s['zoom'][2]
    s['focus']=[float(hx),float(top+170)] if foc=='face' else ([float(hx-120),float(top+760)] if foc=='hands' else [540.0,960.0])
    s['head']=[float(hx),float(top)]
json.dump({'frames':arr.round(1).tolist()},open('../reel/src/heads.json','w'))
json.dump(tl,open('../reel/src/timeline.json','w'),indent=1,ensure_ascii=False)
print(len(arr)); [print(s['angle'],s['e_in'],[round(v) for v in s['head']]) for s in tl['shots']]
