import sys, subprocess, numpy as np, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, model, out = sys.argv[1:4]
W, H = 540, 960
opts = vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=model),
        running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True)
seg = vision.ImageSegmenter.create_from_options(opts)
p = subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf",f"scale={W}:{H}","-r","30","-f","rawvideo","-pix_fmt","rgb","-"] if False else
     ["ffmpeg","-v","error","-i",src,"-vf",f"fps=30,scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
masks = []
while True:
    b = p.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    # run on two overlapping square-ish crops for better resolution: top and bottom halves
    acc = np.zeros((H, W), np.float32); cnt = np.zeros((H, W), np.float32)
    for y0 in (0, 240, 420):
        crop = np.ascontiguousarray(fr[y0:y0+W])
        r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=crop))
        bg = np.asarray(r.confidence_masks[0].numpy_view()).reshape(W, W)
        acc[y0:y0+W] += 1 - bg; cnt[y0:y0+W] += 1
    masks.append((acc / np.maximum(cnt, 1) * 255).astype(np.uint8))
m = np.stack(masks)
np.save(out, m); print(m.shape)
