import subprocess, numpy as np, cv2, json, sys
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
S='/tmp/claude-0/-home-user-claude/72bc255f-5202-5cbe-bb9b-e101156314d2/scratchpad'
V='/root/.claude/uploads/72bc255f-5202-5cbe-bb9b-e101156314d2/a223cf04-copy_E9820242-9872-4BF7-A635-D83D49897C5E-compressed.mov'
W,H=864,1536
G=("colortemperature=temperature=5600:mix=0.5,colorbalance=rs=0.01:bs=-0.02:gh=0.015:rh=0.01:bh=-0.02,"
   "curves=master='0/0.035 0.25/0.235 0.5/0.505 0.75/0.775 0.92/0.9 1/0.955',"
   "selectivecolor=reds='0 0.06 0.08 0':yellows='0 0.04 0.10 0':blues='0 0 0 0.1':magentas='0 0.05 0 0',"
   "huesaturation=saturation=-0.12:colors=b+c,eq=saturation=1.06:contrast=1.04")
p=subprocess.Popen(['ffmpeg','-v','error','-i',V,'-vf',G,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
frames=[]
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    frames.append(np.frombuffer(b,np.uint8).reshape(H,W,3))
N=len(frames); print('frames',N)
F=np.lib.format.open_memmap(f'{S}/work/frames.npy',mode='w+',dtype=np.uint8,shape=(N,H,W,3))
for i,f in enumerate(frames): F[i]=f
F.flush(); del frames

opt=vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=f'{S}/models/multiclass.tflite'),output_confidence_masks=True,running_mode=vision.RunningMode.IMAGE)
seg=vision.ImageSegmenter.create_from_options(opt)
def person(img):
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(img)))
    m=1-np.squeeze(r.confidence_masks[0].numpy_view())
    return cv2.resize(m.astype(np.float32),(img.shape[1],img.shape[0]),interpolation=cv2.INTER_LINEAR)
M=np.lib.format.open_memmap(f'{S}/work/masks.npy',mode='w+',dtype=np.uint8,shape=(N,H,W))
head=[]; prev=None
for i in range(N):
    f=F[i]
    c=person(f)
    rows=np.where((c>0.5).sum(1)>12)[0]
    top=int(rows[0]) if len(rows) else 400
    y0=int(np.clip(top-220,0,H-W))
    fine=person(f[y0:y0+W])
    m=c.copy()
    wgt=np.ones(W,np.float32); r=80
    if y0>0: wgt[:r]=np.linspace(0,1,r)
    if y0+W<H: wgt[-r:]=np.linspace(1,0,r)
    m[y0:y0+W]=fine*wgt[:,None]+c[y0:y0+W]*(1-wgt[:,None])
    if prev is not None: m=0.72*m+0.28*prev
    prev=m
    mm=np.clip((m-0.35)/0.3,0,1); mm=mm*mm*(3-2*mm)
    mm=cv2.GaussianBlur(mm,(0,0),1.2)
    M[i]=(mm*255).astype(np.uint8)
    rows=np.where((mm>0.5).sum(1)>10)[0]
    top=int(rows[0]) if len(rows) else 400
    band=mm[top:top+170]
    xs=np.arange(W)[None,:]*np.ones((band.shape[0],1))
    cx=float((xs*band).sum()/max(band.sum(),1))
    head.append([cx,top])
    if i%100==0: print(i,top,cx,flush=True)
M.flush()
head=np.array(head)
k=9; ker=np.ones(k)/k
hs=np.stack([np.convolve(np.pad(head[:,j],(k//2,k//2),mode='edge'),ker,'valid') for j in range(2)],1)
np.save(f'{S}/work/head.npy',hs)

# stabilisation trajectory for the handheld part (src frames 0..330)
END=330
traj=[[0,0,0]]; T=[np.eye(2,3,dtype=np.float32)]
pg=cv2.cvtColor(F[0],cv2.COLOR_RGB2GRAY)
acc=np.zeros(3)
for i in range(1,END):
    g=cv2.cvtColor(F[i],cv2.COLOR_RGB2GRAY)
    bgmask=((M[i-1]<40)*255).astype(np.uint8)
    pts=cv2.goodFeaturesToTrack(pg,400,0.01,20,mask=bgmask)
    dx=dy=da=0
    if pts is not None and len(pts)>10:
        nxt,st,_=cv2.calcOpticalFlowPyrLK(pg,g,pts,None)
        a=pts[st[:,0]==1]; b=nxt[st[:,0]==1]
        if len(a)>8:
            A,_=cv2.estimateAffinePartial2D(a,b)
            if A is not None:
                dx,dy=A[0,2],A[1,2]; da=np.arctan2(A[1,0],A[0,0])
    acc=acc+[dx,dy,da]; traj.append(acc.copy()); pg=g
traj=np.array(traj)
k=21; ker=np.ones(k)/k
sm=np.stack([np.convolve(np.pad(traj[:,j],(k//2,k//2),mode='edge'),ker,'valid') for j in range(3)],1)
np.save(f'{S}/work/stab.npy',sm-traj)
print('done')
