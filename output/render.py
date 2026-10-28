"""Before/After stage compositor: raw clip on the left card, edited reel on the right card."""
import subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

RAW, EDIT, OUT, DUR = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

# ---------- stage background: white top third -> mid grey floor ----------
y = np.linspace(0, 1, H)[:, None]
t = np.clip((y - 0.33) / 0.67, 0, 1)
t = t * t * (3 - 2 * t)
g = 255 - (255 - 0x84) * t
bg = np.repeat(np.repeat(g[:, :, None], W, 1), 3, 2).astype(np.float32)

def rounded_mask(w, h, r, bottom_fade=0.0):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], r * 2, fill=255)
    m = np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255
    if bottom_fade:
        f = np.ones(h, np.float32)
        n = int(h * bottom_fade)
        ramp = np.linspace(1, 0.08, n)
        f[-n:] = ramp * ramp * (3 - 2 * ramp)
        m *= f[:, None]
    return m

# card source sizes (9:16) and destination quads (TL, TR, BR, BL)
C1 = dict(w=470, h=836, quad=[(-30, 548), (472, 578), (472, 1352), (-30, 1384)], fade=0.0)
C2 = dict(w=644, h=1145, quad=[(452, 428), (1102, 396), (1102, 1541), (452, 1511)], fade=0.13)

for c in (C1, C2):
    src = np.float32([[0, 0], [c["w"], 0], [c["w"], c["h"]], [0, c["h"]]])
    c["M"] = cv2.getPerspectiveTransform(src, np.float32(c["quad"]))
    c["mask"] = cv2.warpPerspective(rounded_mask(c["w"], c["h"], 30, c["fade"]), c["M"], (W, H))[:, :, None]

def shadow(c, dx, dy, blur, op):
    hard = cv2.warpPerspective(rounded_mask(c["w"], c["h"], 30), c["M"], (W, H))
    hard = np.roll(np.roll(hard, dy, 0), dx, 1)
    return (cv2.GaussianBlur(hard, (0, 0), blur) * op)[:, :, None]

sh1 = shadow(C1, 18, 28, 32, 0.38)
sh2 = shadow(C2, -22, 40, 55, 0.55)
base = bg * (1 - sh1)

# ---------- labels: heavy, wide, all caps, warped to match card perspective ----------
def label(text, size, quad):
    f = ImageFont.truetype(FONT, size)
    l, tp, r, b = f.getbbox(text)
    tw, th = r - l, b - tp
    pad = 10
    img = Image.new("L", (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(img).text((pad - l, pad - tp), text, font=f, fill=255)
    a = np.asarray(img, np.float32) / 255
    sw, sh = a.shape[1], a.shape[0]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), np.float32(quad))
    return cv2.warpPerspective(a, M, (W, H), flags=cv2.INTER_CUBIC)[:, :, None]

# BEFORE: small, above left card, right side recedes (shorter) like the card
lb = label("BEFORE", 92, [(28, 454), (412, 474), (412, 528), (28, 518)])
# AFTER: ~1.4x larger, above right card, top edge rising to the right
la = label("AFTER", 128, [(560, 300), (1000, 280), (1000, 362), (560, 376)])
labels = np.clip(lb + la, 0, 1)
base = base * (1 - labels) + 12 * labels  # near-black ink

def reader(path, w, h, pre=""):
    vf = f"{pre}scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},fps={FPS}"
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-t", str(DUR + 1), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n, last = w * h * 3, None
    while True:
        buf = p.stdout.read(n)
        if len(buf) == n:
            last = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        yield last  # hold last frame if a source runs short

# raw lags the edit by ~0.03 s (1 frame): clone its first frame once to line them up
r1 = reader(RAW, C1["w"], C1["h"], "tpad=start=1:start_mode=clone,")
r2 = reader(EDIT, C2["w"], C2["h"])

enc = subprocess.Popen([
    "ffmpeg", "-v", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-ss", "0", "-t", str(DUR), "-i", EDIT,
    "-map", "0:v", "-map", "1:a",
    "-af", f"afade=t=in:d=0.05,afade=t=out:st={DUR - 0.35}:d=0.35",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT,
], stdin=subprocess.PIPE)

nframes = int(round(DUR * FPS))
for i in range(nframes):
    f1 = next(r1).astype(np.float32)
    f2 = next(r2).astype(np.float32)
    w1 = cv2.warpPerspective(f1, C1["M"], (W, H), flags=cv2.INTER_LINEAR)
    w2 = cv2.warpPerspective(f2, C2["M"], (W, H), flags=cv2.INTER_LINEAR)
    m1, m2 = C1["mask"], C2["mask"]
    out = base * (1 - m1) + w1 * m1
    out = out * (1 - sh2 * (1 - m2))
    out = out * (1 - m2) + w2 * m2
    enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    if i % 60 == 0:
        print(f"{i}/{nframes}", flush=True)
enc.stdin.close()
enc.wait()
print("done", OUT)
