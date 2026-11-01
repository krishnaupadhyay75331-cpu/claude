import sys, json, subprocess, numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
SRC=sys.argv[1]; K0,K1=int(sys.argv[2]),int(sys.argv[3]); TAG=sys.argv[4]; W,H=1080,1920; SW,SH=1014,1804; FPS=30
keep=json.load(open('edl.json'))['keep'][K0:K1]
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path='seg.tflite'),output_confidence_masks=True,output_category_mask=False))
T0=max(0,np.floor((keep[0][0]-0.5)*30)/30)
dec=subprocess.Popen(['ffmpeg','-v','error','-ss',f'{T0:.4f}','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
    '-c:v','libx264','-crf','14','-preset','medium','-pix_fmt','yuv420p',f'aroll_{TAG}.mp4'],stdin=subprocess.PIPE)
mat=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r','30','-i','-',
    '-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p',f'matte_{TAG}.mp4'],stdin=subprocess.PIPE)
yy,xx=np.mgrid[0:H,0:W]
def keepf(t): return any(a<=t<b for a,b in keep)
def largest(m):
    b=(m>0.5).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(b,8)
    if n<=1: return m
    i=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); comp=(lab==i).astype(np.uint8)
    comp=cv2.dilate(comp,np.ones((25,25),np.uint8)); comp=cv2.GaussianBlur(comp.astype(np.float32),(0,0),8)
    return m*np.clip(comp*1.5,0,1)
def smooth_curve(x):  # gentle S with matte toe
    x=np.clip(x,0,1); s=x*x*(3-2*x); y=0.55*x+0.45*s
    return 0.035+y*(0.94-0.035)
prev=None; n=0; out=0
fsz=SW*SH*3
while True:
    buf=dec.stdout.read(fsz)
    if len(buf)<fsz: break
    t=T0+n/FPS; n+=1
    if t>=keep[-1][1]: break
    if not keepf(t): continue
    src=np.frombuffer(buf,np.uint8).reshape(SH,SW,3)
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(src)))
    cm=[np.squeeze(c.numpy_view()) for c in r.confidence_masks]
    person=1-cm[0]; face=cm[3]
    person=cv2.resize(person,(W,H)); face=cv2.resize(face,(W,H))
    person=largest(person)
    if prev is not None: person=0.55*person+0.45*prev
    prev=person
    pm=cv2.GaussianBlur(person,(0,0),3)[...,None]
    img=cv2.resize(src,(W,H),interpolation=cv2.INTER_LANCZOS4).astype(np.float32)/255
    # --- retouch: skin smoothing on face (bilateral, 35%) + face relight
    fm=cv2.GaussianBlur(np.clip(face*1.3,0,1),(0,0),6)
    ys,xs=np.where(fm>0.05)
    if len(ys)>50:
        y0,y1,x0,x1=max(ys.min()-20,0),min(ys.max()+20,H),max(xs.min()-20,0),min(xs.max()+20,W)
        crop=(img[y0:y1,x0:x1]*255).astype(np.uint8)
        bil=cv2.bilateralFilter(crop,9,28,7).astype(np.float32)/255
        a=(fm[y0:y1,x0:x1]*0.38)[...,None]
        img[y0:y1,x0:x1]=img[y0:y1,x0:x1]*(1-a)+bil*a
        img[y0:y1,x0:x1]*=1+0.07*fm[y0:y1,x0:x1][...,None]
    # --- base: warm WB, contrast curve
    img*=np.array([1.03,1.0,0.95],np.float32)
    img=smooth_curve(img*0.98)
    hsv=cv2.cvtColor(np.clip(img,0,1),cv2.COLOR_RGB2HSV)  # H 0-360
    h=hsv[...,0]; gold=((h>30)&(h<60)).astype(np.float32); purple=((h>265)&(h<345)).astype(np.float32)
    gold=cv2.GaussianBlur(gold,(0,0),3); purple=cv2.GaussianBlur(purple,(0,0),3)
    # background version
    bg=img.copy()
    hsb=hsv.copy(); hsb[...,1]*=0.62+0.36*gold; hsb[...,2]*=0.50+0.12*gold
    hl=np.clip((hsb[...,2]-0.35)/0.65,0,1); hsb[...,2]-=0.18*hl*hl     # tame bright panels
    bg=cv2.cvtColor(hsb,cv2.COLOR_HSV2RGB)
    bg=bg*0.85+0.15*np.array([0.17,0.09,0.07],np.float32)*(1-bg.mean(2,keepdims=True))*3  # walnut shadow tint
    bg=cv2.resize(cv2.GaussianBlur(cv2.resize(bg,(W//2,H//2),interpolation=cv2.INTER_AREA),(0,0),2.8),(W,H),interpolation=cv2.INTER_LINEAR)
    # foreground version
    hsf=hsv.copy(); hsf[...,1]*=0.93+0.10*purple; hsf[...,2]*=0.97
    fg=cv2.cvtColor(hsf,cv2.COLOR_HSV2RGB)
    o=fg*pm+bg*(1-pm)
    # split tone: plum shadows, gold highlights
    L=o.mean(2,keepdims=True)
    o=o+(1-L)**3*np.array([0.035,-0.01,0.045],np.float32)+L**3*np.array([0.03,0.015,-0.025],np.float32)
    o=np.clip(o,0,1)
    enc.stdin.write((o*255+0.5).astype(np.uint8).tobytes())
    mat.stdin.write((np.clip(person,0,1)*255).astype(np.uint8).tobytes())
    out+=1
    if out%100==0: print(TAG,out,flush=True)
enc.stdin.close(); mat.stdin.close(); enc.wait(); mat.wait(); print('frames',out)
