import subprocess, numpy as np, mediapipe as mp, cv2, sys
from mediapipe.tasks.python import vision, BaseOptions
W,H=720,1280
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="models/selfie_multiclass.tflite"),
    running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))
p = subprocess.Popen(["ffmpeg","-v","error","-i","src.mov","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
N=1141
out = np.lib.format.open_memmap("matte.npy", mode="w+", dtype=np.uint8, shape=(N,640,360))
i=0
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    fr=np.frombuffer(b,np.uint8).reshape(H,W,3)
    r=seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=fr), int(i*1000/30))
    bg=r.confidence_masks[0].numpy_view()
    a=np.clip(1.0-bg,0,1)
    a=cv2.resize(a,(360,640),interpolation=cv2.INTER_LINEAR)
    if i<N: out[i]=(a*255).astype(np.uint8)
    i+=1
out.flush(); print("frames",i)
