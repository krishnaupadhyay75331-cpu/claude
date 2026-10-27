# Person matte for every source frame -> masks.npy (N,448,252) uint8
import sys,subprocess,numpy as np,onnxruntime as ort,cv2
src=sys.argv[1];out=sys.argv[2];step=int(sys.argv[3]) if len(sys.argv)>3 else 2
W,H=756,1344
so=ort.SessionOptions();so.intra_op_num_threads=int(sys.argv[4]) if len(sys.argv)>4 else 2
sess=ort.InferenceSession("/root/.u2net/u2net_human_seg.onnx",so,providers=['CPUExecutionProvider'])
p=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
mean=np.array([0.485,0.456,0.406]);std=np.array([0.229,0.224,0.225])
masks=[];i=0;prev=None
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    if i%step==0:
        f=np.frombuffer(b,np.uint8).reshape(H,W,3)
        x=cv2.resize(f,(320,320),interpolation=cv2.INTER_AREA).astype(np.float32)/255
        x=((x-mean)/std).transpose(2,0,1)[None].astype(np.float32)
        m=sess.run(None,{sess.get_inputs()[0].name:x})[0][0,0]
        m=(m-m.min())/(m.max()-m.min()+1e-8)
        prev=cv2.resize(m,(252,448),interpolation=cv2.INTER_LINEAR)
    masks.append((prev*255).astype(np.uint8));i+=1
np.save(out,np.stack(masks));print(len(masks))
