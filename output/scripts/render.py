# Ramdev Vatika II reel renderer: composites graded footage + motion graphics frame by frame,
# pipes raw frames into ffmpeg. Usage: python3 render.py OUT.mp4 AUDIO.wav [--phone "+91 ..."] [--preview t1,t2,...]
import sys, json, math, subprocess, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = "/tmp/claude-0/-home-user-claude/bfdaaa72-6b03-501f-8ea5-6ea121ccb71a/scratchpad"
U = "/root/.claude/uploads/bfdaaa72-6b03-501f-8ea5-6ea121ccb71a"
PRES = f"{U}/d77f5bac-copy_1CF32808-1170-4210-9245-ABC211D9DC33-compressed.mov"
BROCH = f"{U}/f8480abd-IMG_0535.mov"
SAPL = f"{U}/8e284084-IMG_0507.mov"
BIKE = f"{U}/8882b8b4-IMG_0540.mov"
WIDE = f"{U}/11f52367-IMG_0499-compressed.mov"
W, H, FPS = 1080, 1920, 30
DUR = 41.6
N = int(round(DUR * FPS))

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("audio")
ap.add_argument("--phone", default="+91 XXXXX XXXXX")
ap.add_argument("--preview", default="")
ARGS = ap.parse_args()

# ---------------------------------------------------------------- colours / fonts
CYAN, BLUE = (63, 200, 255), (30, 107, 255)
LIME = (124, 255, 58)
GOLD1, GOLD2 = (255, 224, 138), (201, 150, 43)
MAG, VIO = (214, 58, 249), (123, 59, 255)
G_BLUE, G_GOLD, G_LIME = ("grad", CYAN, BLUE), ("grad", GOLD1, GOLD2), ("grad", (190, 255, 120), (96, 220, 40))
FD = f"{S}/fonts"
FONTS = {"black": f"{FD}/Montserrat-Black.ttf", "xbold": f"{FD}/Montserrat-ExtraBold.ttf",
         "med": f"{FD}/Poppins-Medium.ttf", "semi": f"{FD}/Poppins-SemiBold.ttf", "bold": f"{FD}/Poppins-Bold.ttf",
         "pxb": f"{FD}/Poppins-ExtraBold.ttf", "cinzel": f"{FD}/Cinzel-Bold.ttf",
         "deva": f"{FD}/NotoDeva-Bold.ttf", "devas": f"{FD}/NotoDeva-SemiBold.ttf",
         "emoji": "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"}
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS[name], size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]

def is_deva(s): return any("ऀ" <= c <= "ॿ" for c in s)

# ---------------------------------------------------------------- premultiplied RGBA helpers
def pil_to_p(im):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    al = a[..., 3:4] / 255.0
    return np.concatenate([a[..., :3] * al, al * 255.0], axis=2)

def blit(canvas, p, x, y, op=1.0):
    """composite premultiplied float RGBA p onto float RGB canvas with top-left (x,y)."""
    if op <= 0.002 or p is None: return
    x, y = int(round(x)), int(round(y))
    h, w = p.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    sub = p[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4] * (op / 255.0)
    reg = canvas[y0:y1, x0:x1]
    reg *= (1 - a); reg += sub[..., :3] * op

def blitc(canvas, p, cx, cy, op=1.0):
    blit(canvas, p, cx - p.shape[1] / 2, cy - p.shape[0] / 2, op)

def scale_p(p, s):
    if abs(s - 1) < 1e-3: return p
    h, w = p.shape[:2]
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    return cv2.resize(p, (nw, nh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)

def hblur(p, k):
    k = int(k)
    if k < 2: return p
    pad = np.zeros((p.shape[0], k, 4), np.float32)
    q = np.concatenate([pad, p, pad], axis=1)
    return cv2.blur(q, (k, 1))

def warp3d(p, s=1.0, ry=0.0, rx=0.0, rz=0.0, f=1700.0):
    """rotate around centre (degrees) with perspective; returns warped image (centre stays at centre)."""
    h, w = p.shape[:2]
    if abs(ry) < 0.05 and abs(rx) < 0.05 and abs(rz) < 0.05: return scale_p(p, s)
    cy_, sy_ = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    cx_, sx_ = math.cos(math.radians(rx)), math.sin(math.radians(rx))
    cz_, sz_ = math.cos(math.radians(rz)), math.sin(math.radians(rz))
    src, dst = [], []
    for (u, v) in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y, Z = (u - w / 2) * s, (v - h / 2) * s, 0.0
        X, Y = X * cz_ - Y * sz_, X * sz_ + Y * cz_
        X, Z = X * cy_ + Z * sy_, -X * sy_ + Z * cy_
        Y, Z = Y * cx_ - Z * sx_, Y * sx_ + Z * cx_
        k = f / (f + Z)
        src.append((u, v)); dst.append((X * k, Y * k))
    dst = np.float32(dst); src = np.float32(src)
    mx = np.abs(dst).max(axis=0) + 2
    dst += mx
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(p, M, (int(mx[0] * 2), int(mx[1] * 2)), flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def grad_img(w, h, c1, c2, horizontal=False):
    t = np.linspace(0, 1, w if horizontal else h, dtype=np.float32)
    g = np.array(c1, np.float32)[None] * (1 - t[:, None]) + np.array(c2, np.float32)[None] * t[:, None]
    g = g[None, :, :].repeat(h, 0) if horizontal else g[:, None, :].repeat(w, 1)
    return g

def add_shadow(p, dx=0, dy=6, blur=12, alpha=0.4, pad=None):
    pad = pad or blur * 2 + max(abs(dx), abs(dy))
    h, w = p.shape[:2]
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    sh = np.zeros_like(out)
    sh[pad + dy:pad + dy + h, pad + dx:pad + dx + w, 3] = p[..., 3]
    sh[..., 3] = cv2.GaussianBlur(sh[..., 3], (0, 0), blur) * alpha
    out[:] = sh
    reg = out[pad:pad + h, pad:pad + w]
    a = p[..., 3:4] / 255.0
    reg *= (1 - a); reg += p
    return out

_tc = {}
def text_p(text, fname, size, fill=(255, 255, 255), tracking=0.0, shadow=(0, 6, 12, 0.4), stroke=0, stroke_fill=(0, 0, 0)):
    key = (text, fname, size, str(fill), tracking, shadow, stroke)
    if key in _tc: return _tc[key]
    f = font(fname, size)
    asc, desc = f.getmetrics()
    if tracking and not is_deva(text):
        adv = [f.getlength(c) + tracking * size for c in text]
        tw = int(sum(adv) - tracking * size) + 4
    else:
        tw = int(f.getlength(text)) + 4
    pad = 6 + stroke
    w, h = tw + 2 * pad, asc + desc + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if tracking and not is_deva(text):
        x = pad
        for c, a in zip(text, adv):
            d.text((x, pad), c, font=f, fill=255, stroke_width=stroke, stroke_fill=255); x += a
    else:
        d.text((pad, pad), text, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    m = np.asarray(mask).astype(np.float32)
    # trim to ink bbox vertically (keeps consistent look)
    rows = np.where(m.max(1) > 0)[0]; cols = np.where(m.max(0) > 0)[0]
    m = m[max(rows[0] - 4, 0):rows[-1] + 5, max(cols[0] - 4, 0):cols[-1] + 5]
    hh, ww = m.shape
    if isinstance(fill, tuple) and fill and fill[0] == "grad":
        col = grad_img(ww, hh, fill[1], fill[2])
    else:
        col = np.ones((hh, ww, 3), np.float32) * np.array(fill, np.float32)
    al = m[..., None] / 255.0
    p = np.concatenate([col * al, m[..., None]], axis=2)
    if stroke:
        # stroke drawn as darker outline behind: re-render fill without stroke on top
        inner = text_p(text, fname, size, fill, tracking, None, 0)
        base = np.zeros_like(p); base[..., :3] = np.array(stroke_fill, np.float32) * al; base[..., 3] = m
        oy, ox = (hh - inner.shape[0]) // 2, (ww - inner.shape[1]) // 2
        blit_p(base, inner, ox, oy); p = base
    if shadow: p = add_shadow(p, *shadow)
    _tc[key] = p
    return p

def blit_p(dst, src, x, y, op=1.0):
    """premultiplied over premultiplied."""
    h, w = src.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0: return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x] * op
    a = s[..., 3:4] / 255.0
    reg = dst[y0:y1, x0:x1]
    reg *= (1 - a); reg += s

_ec = {}
def emoji_p(ch, size):
    k = (ch, size)
    if k in _ec: return _ec[k]
    f = font("emoji", 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    bb = im.getbbox(); im = im.crop(bb)
    s = size / max(im.size)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    _ec[k] = pil_to_p(im)
    return _ec[k]

def rrect_mask(w, h, r, ss=3):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32)

def solid_p(mask, color):
    al = mask[..., None] / 255.0
    col = color if isinstance(color, np.ndarray) else np.array(color, np.float32)
    return np.concatenate([np.broadcast_to(col, mask.shape + (3,)) * al, mask[..., None]], axis=2).astype(np.float32)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def pop_scale(fr):  # 0 -> 1.15 (6f) -> 1.0 (10f)
    if fr <= 0: return 0.0
    if fr < 6: return 1.15 * ease_out(fr / 6)
    if fr < 10: return 1.15 - 0.15 * ease_io((fr - 6) / 4)
    return 1.0

# ---------------------------------------------------------------- footage readers
GRADE = ("eq=contrast=1.08:saturation=1.06:gamma=0.97,vibrance=intensity=0.18,"
         "colorbalance=rm=0.025:gm=0.005:bm=-0.03:rh=0.012:bh=-0.005,unsharp=5:5:0.45:5:5:0")

class Reader:
    def __init__(self, path, start, extra="", fps=30):
        vf = f"fps={fps},scale={W}:{H}:flags=lanczos,setsar=1,{GRADE}" + (("," + extra) if extra else "")
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-an", "-vf", vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
        self.idx, self.cur, self.prev = -1, None, None
    def get(self, idx):
        while self.idx < idx:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.prev = self.cur
            self.cur = np.frombuffer(b, np.uint8).reshape(H, W, 3)
            self.idx += 1
        return self.cur, self.prev
    def close(self):
        self.p.stdout.close(); self.p.kill()

# sky grad + vignette applied to every footage frame
_yy = np.linspace(0, 1, H, dtype=np.float32)
_sky = np.clip(1 - _yy / 0.42, 0, 1) ** 1.5
SKYMUL = (1 + _sky[:, None, None] * np.array([-0.05, -0.01, 0.06], np.float32)).astype(np.float32)
_xx = np.linspace(-1, 1, W, dtype=np.float32)
_r = np.sqrt(_xx[None, :] ** 2 * 0.9 + ((_yy[:, None] - 0.5) * 2) ** 2 * 0.6)
VIG = (1 - 0.16 * np.clip(_r - 0.55, 0, 1) ** 1.6)[..., None].astype(np.float32)
def finish_footage(fr):
    return fr.astype(np.float32) * SKYMUL * VIG

MASKS = np.load(f"{S}/work/masks.npy", mmap_mode="r")
def pres_mask(idx):
    idx = int(clamp(idx, 0, len(MASKS) - 1))
    m = np.asarray(MASKS[idx]).astype(np.float32)
    if idx > 0:  # light temporal smoothing
        m = 0.7 * m + 0.3 * np.asarray(MASKS[idx - 1]).astype(np.float32)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    m = np.clip((m - 70) / 130, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 1.6)
    return m[..., None]

def head_top(idx):
    m = np.asarray(MASKS[int(clamp(idx, 0, len(MASKS) - 1))])
    rows = np.where((m > 150).sum(1) > 4)[0]
    return rows[0] * 2 if len(rows) else 900

def head_top_range(src0, src1):
    ids = range(int(src0 * 30), int(src1 * 30) + 1, 3)
    return float(np.median([head_top(i) for i in ids]))

# ---------------------------------------------------------------- timeline: background scenes
OFF2, OFF3 = 1.72, 9.49     # presenter source = out - offset
SCENES = [  # (t0, t1, kind, params)
    (0.00, 7.73, "pres", dict(off=0.0)),
    (7.73, 9.62, "clip", dict(path=BROCH, src=0.60, zoom=(1.0, 1.06))),
    (9.62, 17.00, "pres", dict(off=OFF2)),
    (17.00, 18.50, "clip", dict(path=BIKE, src=2.60, zoom=(1.04, 1.08))),
    (18.50, 25.36, "pres", dict(off=OFF2)),
    (25.36, 27.76, "ramp", dict(path=BIKE, src=15.0)),
    (27.76, 29.56, "clip", dict(path=SAPL, src=3.30, zoom=(1.0, 1.07))),
    (29.56, 33.40, "clip", dict(path=WIDE, src=5.00, zoom=(1.02, 1.08), dark=0.72)),
    (33.40, 37.10, "pres", dict(off=OFF3)),
    (37.10, DUR, "black", {}),
]

def ramp_speed(u):  # u = seconds into ramp scene (2.4 s)
    pts = [(0, 2.0), (0.55, 2.0), (0.95, 1.0), (1.55, 1.0), (1.95, 2.0), (2.4, 2.0)]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if u <= b: return va + (vb - va) * ease_io((u - a) / (b - a))
    return 2.0
RAMP_T = [0.0]
for i in range(int(2.4 * FPS) + 2):
    RAMP_T.append(RAMP_T[-1] + ramp_speed(i / FPS) / FPS)

def src_of_pres(t):
    for (a, b, kind, pr) in SCENES:
        if kind == "pres" and a <= t < b + 0.5 and pr["off"] in (0.0, OFF2, OFF3):
            pass
    if t < 9.0: return t
    if t < 30: return t - OFF2
    return t - OFF3

# ---------------------------------------------------------------- elements
ELS = []   # dicts: t0, t1, layer ('back'|'front'|'top'), fn(canvas, t)
SFX = []   # (time, kind)
def el(t0, t1, layer, fn): ELS.append(dict(t0=t0, t1=t1, layer=layer, fn=fn))

def fit_size(text, fname, maxw, maxsize, tracking=-0.02):
    s = maxsize
    while s > 40:
        if text_p(text, fname, s, (255, 255, 255), tracking, None).shape[1] <= maxw: return s
        s -= 6
    return s

def hero(t0, t1, lead, word, fill=G_BLUE, layer="back", cy=None, pres=True, maxsize=190, lead_fill=(255, 255, 255),
         cx=W / 2, overlap=0.42):
    fname = "deva" if is_deva(word) else "black"
    size = fit_size(word, fname, 960, maxsize)
    hp = text_p(word, fname, size, fill, -0.02 if fname == "black" else 0, (0, 8, 12, 0.4))
    lp = text_p(lead, "semi", max(34, int(size * 0.35)), lead_fill, 0, (0, 3, 8, 0.45)) if lead else None
    if cy is None:
        ht = head_top_range(src_of_pres(t0 + 0.1), src_of_pres(t1 - 0.1))
        cy = ht - hp.shape[0] / 2 + min(hp.shape[0] * overlap, 95)
        cy = clamp(cy, 470, 1150)
    def draw(c, t):
        fr = (t - t0) * FPS
        exit_fr = (t1 - t) * FPS
        for k, (img, y, delay) in enumerate([(hp, cy, 0), (lp, cy - hp.shape[0] / 2 - (lp.shape[0] / 2 - 18 if lp is not None else 0), 3)]):
            if img is None: continue
            f2 = fr - delay
            if f2 < 0: continue
            p = ease_out(f2 / 9)
            s = (0.9 + 0.1 * p) * (1 + 0.03 * (t - t0) / max(t1 - t0, 0.1))
            im = scale_p(img, s)
            blur = 40 * (1 - p)
            op = p
            if exit_fr < 5:
                q = clamp(exit_fr / 5); op *= q; blur = max(blur, 30 * (1 - q))
            im = hblur(im, blur)
            blitc(c, im, cx - 120 * (1 - p), y, op)
    el(t0, t1, layer, draw)
    return cy, hp.shape

def pop_icon(t0, t1, img, cx, cy, layer="front", tilt=10, float_amp=6, sfx=True, phase=0.0):
    if sfx: SFX.append((t0, "pop"))
    def draw(c, t):
        fr = (t - t0) * FPS
        s = pop_scale(fr)
        ex = (t1 - t) * FPS
        op = 1.0
        if ex < 6: s *= 0.6 + 0.4 * ex / 6; op = ex / 6
        if s <= 0.01: return
        fl = float_amp * math.sin(2 * math.pi * (t - t0) / 2.0 + phase)
        im = warp3d(img, s, ry=tilt * math.sin(2 * math.pi * (t - t0) / 3.0 + phase), rx=5)
        blitc(c, im, cx, cy + fl, op)
    el(t0, t1, layer, draw)

def glass_card(w, h, tint=(155, 227, 176), tint_a=0.70, r=28):
    m = rrect_mask(w, h, r)
    card = solid_p(m * tint_a, tint)
    # top sheen
    sheen = np.clip(1 - np.linspace(0, 1, h, dtype=np.float32) / 0.5, 0, 1)[:, None] * 0.18
    card[..., :3] += (255 * sheen * (m / 255.0))[..., None]
    card[..., 3] = np.clip(card[..., 3] + 255 * sheen * (m / 255.0) * 0.2, 0, 255)
    # 1px white border
    inner = rrect_mask(w - 4, h - 4, r - 2)
    border = m.copy(); border[2:-2, 2:-2] -= inner; border = np.clip(border, 0, 255) * 0.9
    blit_p(card, solid_p(border, (255, 255, 255)), 0, 0)
    return card, m

def draw_glass(c, card, shape, cx, cy, s=1.0, ry=0.0, rx=0.0, op=1.0, shadow=True):
    if op <= 0.01: return
    wc = warp3d(card, s, ry, rx); ws = warp3d(np.dstack([shape] * 4), s, ry, rx)[..., 3]
    h, w = wc.shape[:2]
    x, y = int(cx - w / 2), int(cy - h / 2)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    m = ws[y0 - y:y1 - y, x0 - x:x1 - x, None] / 255.0 * op
    if shadow:
        sh = cv2.GaussianBlur(ws, (0, 0), 18)[..., None] / 255.0 * 0.35 * op
        sh = np.roll(sh, 14, axis=0)[y0 - y:y1 - y, x0 - x:x1 - x]
        c[y0:y1, x0:x1] *= (1 - sh)
    reg = c[y0:y1, x0:x1]
    bl = cv2.GaussianBlur(reg, (0, 0), 18)
    reg[:] = reg * (1 - m) + bl * m
    blit(c, wc, x, y, op)

def swing_in(t, t0, t1, frames=12):
    fr = (t - t0) * FPS
    p = ease_out(fr / frames)
    ex = (t1 - t) * FPS
    op = p * clamp(ex / 6)
    return p, op, 25 * (1 - p)

def caption_words():
    G = [  # (src time, word, accent)
        [(0.00, "agar"), (0.20, "jodhpur", 1), (0.58, "mein")],
        [(0.68, "apna"), (0.86, "plot", 1), (1.08, "lene"), (1.30, "ka")],
        [(1.46, "soch"), (1.70, "rahe"), (1.90, "ho...")],
        [(2.10, "to"), (2.22, "ye"), (2.34, "video")],
        [(2.56, "aapke"), (2.92, "liye"), (3.30, "hai")],
        [(3.54, "mahalaxmi", 1), (4.34, "properties", 1)],
        [(4.76, "lekar"), (5.08, "aayi"), (5.30, "hai")],
        [(5.56, "aap"), (5.64, "logon"), (5.86, "ke"), (6.04, "liye")],
        [(6.16, "profitable", 1), (6.68, "plots", 1)],
        [(7.02, "wo"), (7.14, "bhi"), (7.28, "jodhpur"), (7.62, "mein")],
        [(7.94, "jda", 1), (8.38, "approved", 1), (8.74, "scheme")],
        [(9.00, "patta", 1), (9.40, "shuda", 1), (9.62, "plot")],
        [(9.98, "yaani"), (10.24, "clear"), (10.58, "documentation")],
        [(11.36, "bank", 1), (11.90, "loanable", 1)],
        [(12.28, "wo"), (12.42, "bhi")],
        [(12.52, "aasan"), (12.84, "finance", 1), (13.24, "ke"), (13.38, "saath")],
        [(13.88, "60", 1), (14.34, "feet"), (14.52, "wide")],
        [(14.78, "main"), (14.96, "road")],
        [(15.40, "30", 1), (15.64, "feet"), (15.80, "wide")],
        [(16.06, "internal"), (16.54, "road")],
        [(17.08, "bijli", 1), (17.42, "paani", 1), (17.62, "ki"), (17.78, "suvidha")],
        [(18.26, "pakki"), (18.52, "wall"), (18.74, "boundary")],
        [(19.44, "aur"), (19.64, "street"), (19.96, "lights")],
        [(20.42, "main"), (20.66, "market")],
        [(21.16, "railway"), (21.46, "station")],
        [(21.78, "aur"), (21.96, "bus"), (22.16, "stand")],
        [(22.52, "sirf"), (22.80, "3 km", 1), (23.20, "door")],
        [(23.70, "site", 1), (24.16, "visit", 1)],
        [(24.66, "aur"), (24.76, "booking"), (25.04, "ke"), (25.22, "liye")],
        [(25.38, "abhi"), (25.50, "sampark"), (25.86, "karein")],
        [(26.06, "mahalaxmi", 1), (26.62, "properties", 1)],
    ]
    def out(s): return s if s < 7.90 else (s + OFF2 if s < 23.67 else s + OFF3)
    groups = []
    for g in G:
        groups.append([(out(w[0]), w[1], len(w) > 2) for w in g])
    return groups

def captions():
    groups = caption_words()
    ends = {9: 7.73 + 0.0}
    for gi, g in enumerate(groups):
        t0 = g[0][0] - 0.03
        last = g[-1][0]
        nxt = groups[gi + 1][0][0] - 0.03 if gi + 1 < len(groups) else last + 1.0
        t1 = min(nxt, last + 0.75)
        imgs = [text_p(w, "semi", 56, LIME if acc else (255, 255, 255), 0, (0, 4, 8, 0.7), 3, (10, 20, 12)) for (_, w, acc) in g]
        space = 16 - 2 * 20
        total = sum(i.shape[1] for i in imgs) + space * (len(imgs) - 1)
        def draw(c, t, g=g, imgs=imgs, total=total, t1=t1):
            x = W / 2 - total / 2
            op_g = clamp((t1 - t) * FPS / 3)
            for (wt, w, acc), im in zip(g, imgs):
                fr = (t - wt) * FPS
                if fr >= 0:
                    p = ease_out(fr / 4)
                    blit(c, im, x, 1400 - im.shape[0] / 2 + 8 * (1 - p), p * op_g)
                x += im.shape[1] + space
        el(t0, t1, "top", draw)

# ---- assets
def load_p(path, w=None, h=None):
    im = Image.open(path).convert("RGBA")
    if w: im = im.resize((w, h or int(im.height * w / im.width)), Image.LANCZOS)
    return pil_to_p(im)

def sticker_from_crop(path, size, r=34, border=10):
    im = Image.open(path).convert("RGB")
    s = (size - 2 * border) / max(im.size)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    bw, bh = im.width + 2 * border, im.height + 2 * border
    base = solid_p(rrect_mask(bw, bh, r), (255, 255, 255))
    inner = pil_to_p(im); inner[..., 3] = rrect_mask(im.width, im.height, r - border)
    inner[..., :3] = np.asarray(im).astype(np.float32) * (inner[..., 3:4] / 255.0)
    blit_p(base, inner, border, border)
    # gloss
    gl = np.clip(1 - np.linspace(0, 1, bh, dtype=np.float32) / 0.45, 0, 1)[:, None] * 0.22
    base[..., :3] += 255 * gl[..., None] * (base[..., 3:4] / 255.0)
    return add_shadow(base, 0, 10, 14, 0.45)

def badge_patta(size):
    ss = 3; D = size * ss
    im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, D - 1, D - 1), fill=(255, 255, 255))
    d.ellipse((10 * ss, 10 * ss, D - 10 * ss, D - 10 * ss), fill=(201, 150, 43))
    d.ellipse((18 * ss, 18 * ss, D - 18 * ss, D - 18 * ss), outline=(255, 236, 170), width=3 * ss)
    p = pil_to_p(im.resize((size, size), Image.LANCZOS))
    g = grad_img(size, size, GOLD1, GOLD2)
    inner = rrect_mask(size - 20, size - 20, (size - 20) // 2)
    gp = solid_p(inner, g[10:-10, 10:-10])
    blit_p(p, gp, 10, 10)
    ring = rrect_mask(size - 36, size - 36, (size - 36) // 2); ring2 = rrect_mask(size - 42, size - 42, (size - 42) // 2)
    rr = ring.copy(); rr[3:-3, 3:-3] -= ring2; blit_p(p, solid_p(np.clip(rr, 0, 255), (255, 240, 190)), 18, 18)
    t1 = text_p("पट्टासुदा", "deva", int(size * 0.2), (74, 40, 6), 0, None)
    t2 = text_p("योजना", "devas", int(size * 0.14), (74, 40, 6), 0, None)
    blit_p(p, t1, int(size / 2 - t1.shape[1] / 2), int(size * 0.47 - t1.shape[0] / 2 - 4))
    blit_p(p, t2, int(size / 2 - t2.shape[1] / 2), int(size * 0.66 - t2.shape[0] / 2))
    gl = np.clip(1 - np.linspace(0, 1, size, dtype=np.float32) / 0.5, 0, 1)[:, None] * 0.25
    p[..., :3] += 255 * gl[..., None] * (p[..., 3:4] / 255.0)
    return add_shadow(p, 0, 10, 14, 0.45)

def cover_card(width):
    im = cv2.cvtColor(cv2.imread(f"{S}/stills/cover_rot.jpg"), cv2.COLOR_BGR2RGB)
    srcq = np.float32([[240, 250], [1772, 122], [1874, 1478], [80, 1446]])
    ow, oh = 1240, 960
    M = cv2.getPerspectiveTransform(srcq, np.float32([[0, 0], [ow, 0], [ow, oh], [0, oh]]))
    flat = cv2.warpPerspective(im, M, (ow, oh), flags=cv2.INTER_CUBIC)
    flat = Image.fromarray(flat).resize((width, int(width * oh / ow)), Image.LANCZOS)
    b = 8
    base = solid_p(rrect_mask(flat.width + 2 * b, flat.height + 2 * b, 22), (255, 255, 255))
    inner = pil_to_p(flat); inner[..., 3] = rrect_mask(flat.width, flat.height, 16)
    inner[..., :3] = np.asarray(flat).astype(np.float32) * (inner[..., 3:4] / 255.0)
    blit_p(base, inner, b, b)
    return add_shadow(base, 0, 16, 20, 0.5)

def chip(text, emoji=None, size=40, bg=(255, 255, 255), fg=(20, 20, 20), fname="semi", grad_text=None, padx=34, pady=18):
    tp = text_p(text, fname, size, grad_text or fg, 0, None)
    ep = emoji_p(emoji, int(size * 1.15)) if emoji else None
    w = tp.shape[1] + 2 * padx + (ep.shape[1] + 14 if ep is not None else 0)
    h = max(tp.shape[0], ep.shape[0] if ep is not None else 0) + 2 * pady
    p = solid_p(rrect_mask(w, h, h // 2), bg)
    x = padx
    if ep is not None:
        blit_p(p, ep, x, (h - ep.shape[0]) // 2); x += ep.shape[1] + 14
    blit_p(p, tp, x, (h - tp.shape[0]) // 2)
    return add_shadow(p, 0, 8, 12, 0.35)

# ---------------------------------------------------------------- build element timeline
def build(phone):
    # S1 hook ------------------------------------------------------------------
    cy, hs = hero(0.20, 3.28, "agar", "JODHPUR", G_BLUE, maxsize=200)
    plot_word = text_p("PLOT", "black", 96, G_LIME, -0.02, (0, 6, 10, 0.4))
    pop_icon(0.86, 3.28, plot_word, W / 2 + hs[1] / 2 - 120, cy + hs[0] / 2 + 30, layer="back", tilt=6, float_amp=4)
    pop_icon(0.50, 3.28, add_shadow(emoji_p("🏡", 150), 0, 10, 12, 0.4), 905, 345, tilt=14)

    # S2 project name ------------------------------------------------------------
    cy2, hs2 = hero(3.54, 7.66, "MAHA LAXMI PROPERTY'S", "RAMDEV VATIKA II", G_BLUE, maxsize=150)
    graph(6.10, 7.66, "Profitable Plots")

    # light leak S2 -> S3
    leak(7.73, "blue"); SFX.append((7.58, "whoosh"))

    # S3 brochure ----------------------------------------------------------------
    cc = cover_card(600)
    def cover_draw(c, t, t0=7.82, t1=9.58):
        p = ease_out((t - t0) * FPS / 14); ex = clamp((t1 - t) * FPS / 6)
        fl = 8 * math.sin((t - t0) * math.pi)
        im = warp3d(cc, 0.7 + 0.3 * p, ry=-28 * (1 - p) + 10 * math.sin((t - t0) * 1.4), rx=8)
        blitc(c, im, W / 2, 520 + 120 * (1 - p) + fl, p * ex)
    el(7.82, 9.58, "front", cover_draw); SFX.append((7.82, "pop"))
    loc = chip("Banar, Jodhpur", "📍", 44)
    pop_icon(8.15, 9.58, loc, W / 2, 1290, tilt=4, float_amp=3)

    # S4 approvals ---------------------------------------------------------------
    st_jda = sticker_from_crop(f"{S}/stills/st_jda.png", 230)
    st_bank = sticker_from_crop(f"{S}/stills/st_bank.png", 230)
    st_patta = badge_patta(220)
    pop_icon(9.64, 15.22, st_jda, 210, 375, phase=0.0)
    pop_icon(10.70, 15.22, st_patta, 540, 375, phase=1.0)
    pop_icon(13.06, 15.22, st_bank, 870, 375, phase=2.0)
    hero(9.66, 10.64, "JDA", "APPROVED", G_BLUE)
    hero(10.70, 11.90, "plot", "पट्टासुदा", G_BLUE, maxsize=170)
    hero(11.94, 13.02, "clear", "DOCUMENTS", G_BLUE)
    hero(13.06, 14.50, "bank", "LOANABLE", G_BLUE)
    hero(14.54, 15.40, "aasan", "FINANCE", G_GOLD)

    # S5 roads + facilities -------------------------------------------------------
    hero(15.58, 16.99, "main road", "60 FT", G_BLUE, maxsize=210)
    hero(17.06, 18.47, "internal road", "30 FT", G_BLUE, layer="front", cy=760, maxsize=210)
    facilities(18.62, 22.02)

    # S6 distances ---------------------------------------------------------------
    dist_card(22.12, 23.62, "Main Market", "3 KM", "🛒", 285, 455)
    dist_card(22.86, 23.62, "Railway Station", "3 KM", "🚉", 795, 455, phase=1)
    dist_card(23.72, 25.30, "Bus Stand", "3 KM", "🚌", 285, 455)
    dist_card(23.86, 25.30, "Hospital · School", "4 KM", "🏥", 795, 455, phase=1)
    hero(24.48, 25.34, "sirf", "3 KM", G_LIME, maxsize=200)

    leak(25.36, "blue"); SFX.append((25.21, "whoosh"))
    # S7 site tour -----------------------------------------------------------------
    hero(25.50, 27.70, "30 ft gravel", "WIDE ROADS", G_BLUE, layer="front", cy=760)
    hero(27.84, 29.50, "hare bhare ped", "GREEN", G_LIME, layer="front", cy=700, maxsize=220)
    leak(29.56, "white"); SFX.append((29.41, "whoosh"))

    # S8 plots counter + layout ------------------------------------------------------
    counter(29.70, 33.30)
    layout_card(29.85, 33.30)
    pop_icon(31.95, 33.30, chip("20×40 ft", None, 40, fg=(20, 60, 30), fname="bold"), 175, 1090, tilt=5, float_amp=3)
    pop_icon(32.12, 33.30, chip("25×40 ft", None, 40, fg=(20, 60, 30), fname="bold"), 410, 1090, tilt=5, float_amp=3, phase=1)
    lab = text_p("plot sizes", "semi", 38, (255, 255, 255), 0, (0, 3, 8, 0.5))
    def lab_draw(c, t): blitc(c, lab, 290, 1000, clamp((t - 31.85) * FPS / 5) * clamp((33.3 - t) * FPS / 5))
    el(31.85, 33.30, "front", lab_draw)

    # S9 film burn + riser
    burn(33.40); SFX.append((31.65, "riser")); SFX.append((33.40, "impact"))

    # S10 CTA -----------------------------------------------------------------------
    hero(33.52, 35.06, "book your", "SITE VISIT", G_BLUE)
    lim = chip("LIMITED PLOTS AVAILABLE", None, 38, bg=(255, 255, 255), fname="pxb", grad_text=("grad", (214, 150, 20), (150, 95, 10)))
    pop_icon(35.10, 37.06, lim, W / 2, 330, tilt=4, float_amp=3)
    cta_text(35.22, 37.06)
    leak(37.10, "white"); SFX.append((36.95, "whoosh"))

    # END card -----------------------------------------------------------------------
    end_card(37.10, DUR, phone)
    captions()

def graph(t0, t1, label):
    pts = [(0.0, 0.85), (0.16, 0.66), (0.30, 0.74), (0.48, 0.48), (0.62, 0.56), (0.80, 0.26), (1.0, 0.08)]
    GW, GH, x0, y0 = 760, 230, (W - 760) / 2, 255
    P = [(x * GW, y * GH) for x, y in pts]
    segl = [math.dist(a, b) for a, b in zip(P, P[1:])]; L = sum(segl)
    pill = chip(label, None, 40, fname="pxb", grad_text=("grad", MAG, VIO))
    pill = None if pill is None else pill
    # horizontal gradient text for pill
    tp = text_p(label, "pxb", 40, (255, 255, 255), 0, None)
    g = grad_img(tp.shape[1], tp.shape[0], MAG, VIO, horizontal=True)
    tp = np.concatenate([g * (tp[..., 3:4] / 255.0), tp[..., 3:4]], axis=2)
    pw, ph = tp.shape[1] + 68, tp.shape[0] + 34
    pill = solid_p(rrect_mask(pw, ph, ph // 2), (255, 255, 255)); blit_p(pill, tp, 34, 17); pill = add_shadow(pill, 0, 8, 12, 0.35)
    SFX.append((t0, "swish"))
    def draw(c, t):
        p = ease_io((t - t0) * FPS / 20); ex = clamp((t1 - t) * FPS / 6)
        d = p * L; pts_d = [P[0]]; acc = 0
        for (a, b), sl in zip(zip(P, P[1:]), segl):
            if acc + sl <= d: pts_d.append(b); acc += sl
            else:
                f = (d - acc) / sl; pts_d.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); break
        ss = 2
        im = Image.new("L", (int(GW + 60) * ss, int(GH + 60) * ss), 0); dr = ImageDraw.Draw(im)
        q = [((x + 30) * ss, (y + 30) * ss) for x, y in pts_d]
        if len(q) > 1: dr.line(q, fill=255, width=5 * ss, joint="curve")
        tip = q[-1]
        dr.ellipse((tip[0] - 9 * ss, tip[1] - 9 * ss, tip[0] + 9 * ss, tip[1] + 9 * ss), fill=255)
        m = np.asarray(im.resize((int(GW + 60), int(GH + 60)), Image.LANCZOS)).astype(np.float32)
        glow = cv2.GaussianBlur(m, (0, 0), 8) * 0.8
        lay = solid_p(np.clip(glow, 0, 255), (150, 220, 255)); blit_p(lay, solid_p(m, (255, 255, 255)), 0, 0)
        blit(c, lay, x0 - 30, y0 - 30, ex)
        pf = (t - t0 - 0.30) * FPS
        if pf > 0:
            s = pop_scale(pf)
            blitc(c, scale_p(pill, max(s, 0.01)), W / 2, y0 + GH + 70, ex)
    el(t0, t1, "front", draw)

def facilities(t0, t1):
    cw, chh = 760, 470
    card, shape = glass_card(cw, chh)
    hdr = solid_p(rrect_mask(300, 64, 32), (14, 59, 36))
    ht = text_p("FACILITIES", "pxb", 34, LIME, 0.04, None)
    blit_p(hdr, ht, (300 - ht.shape[1]) // 2, (64 - ht.shape[0]) // 2)
    blit_p(card, hdr, 40, 32)
    rows = [(18.80, "⚡", "Bijli (Electricity)"), (19.14, "💧", "Paani (Water)"), (19.96, "🧱", "Pakki Boundary Wall"), (21.34, "💡", "Street Lights")]
    rimgs = []
    for (rt, e, tx) in rows:
        r = np.zeros((80, 680, 4), np.float32)
        ep = emoji_p(e, 54); blit_p(r, ep, 0, (80 - ep.shape[0]) // 2)
        tp = text_p(tx, "bold", 44, (12, 52, 30), 0, None); blit_p(r, tp, 80, (80 - tp.shape[0]) // 2)
        rimgs.append((rt, r))
        SFX.append((rt, "pop"))
    SFX.append((t0, "swish"))
    cx, cy = W / 2, 520
    def draw(c, t):
        p, op, ang = swing_in(t, t0, t1)
        cardt = card.copy()
        for i, (rt, r) in enumerate(rimgs):
            fr = (t - rt) * FPS
            if fr > 0:
                q = ease_out(fr / 6)
                blit_p(cardt, r, int(48 - 30 * (1 - q)), 120 + i * 84, q)
        draw_glass(c, cardt, shape, cx, cy, 0.92 + 0.08 * p, ry=ang, op=op)
    el(t0, t1, "front", draw)

def dist_card(t0, t1, title, val, emoji, cx, cy, phase=0):
    cw, chh = 450, 300
    card, shape = glass_card(cw, chh)
    hdr = np.zeros((84, cw, 4), np.float32)
    hm = rrect_mask(cw, 84 + 28, 28)[:84]
    blit_p(hdr, solid_p(hm, (14, 59, 36)), 0, 0)
    tsize = 36 if len(title) < 15 else 30
    tt = text_p(title, "pxb", tsize, LIME, 0, None)
    blit_p(hdr, tt, (cw - tt.shape[1]) // 2, (84 - tt.shape[0]) // 2)
    blit_p(card, hdr, 0, 0)
    ep = emoji_p(emoji, 92); blit_p(card, ep, 44, 84 + (chh - 84 - ep.shape[0]) // 2)
    vt = text_p(val, "black", 92, (12, 52, 30), -0.02, None)
    blit_p(card, vt, 44 + ep.shape[1] + 26, 84 + (chh - 84 - vt.shape[0]) // 2)
    SFX.append((t0, "pop"))
    def draw(c, t):
        p, op, ang = swing_in(t, t0, t1)
        fl = 6 * math.sin(2 * math.pi * (t - t0) / 2 + phase)
        draw_glass(c, card, shape, cx + (60 * (1 - p) if phase else -60 * (1 - p)), cy + fl, 0.9 + 0.1 * p,
                   ry=ang if phase else -ang, op=op)
    el(t0, t1, "front", draw)

def counter(t0, t1):
    R = 170; cx, cy = 290, 520
    t_count0, t_count1, t_sw = t0 + 0.12, t0 + 1.35, t0 + 1.70
    for k in range(18): SFX.append((t_count0 + k * (t_count1 - t_count0) / 18, "tick"))
    SFX.append((t_sw, "pop"))
    for k in range(10): SFX.append((t_sw + 0.05 + k * 0.07, "tick"))
    def draw(c, t):
        p_in = ease_out((t - t0) * FPS / 10); ex = clamp((t1 - t) * FPS / 6)
        op = p_in * ex
        if t < t_sw:
            q = ease_io((t - t_count0) / (t_count1 - t_count0)); val = int(round(152 * q)); frac = q
            col, num_fill, tag, lead = (124, 255, 58), (255, 255, 255), "PLOTS", "total"
        else:
            q = ease_io((t - t_sw) / 0.75); val = int(round(152 - 70 * q)); frac = 1 - 0.4605 * q
            col, num_fill, tag, lead = (255, 205, 90), G_GOLD, "AVAILABLE", "only"
        ss = 2; D = (R * 2 + 40) * ss
        im = Image.new("RGBA", (D, D), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        bb = (20 * ss, 20 * ss, D - 20 * ss, D - 20 * ss)
        dr.ellipse(bb, fill=(0, 0, 0, 90))
        dr.arc(bb, 0, 360, fill=(255, 255, 255, 60), width=16 * ss)
        if frac > 0.002: dr.arc(bb, -90, -90 + 360 * frac, fill=col + (255,), width=16 * ss)
        ring = pil_to_p(im.resize((D // ss, D // ss), Image.LANCZOS))
        s = 0.85 + 0.15 * p_in
        blitc(c, scale_p(ring, s), cx, cy, op)
        nt = text_p(str(val), "black", 120, num_fill, -0.02, (0, 6, 10, 0.45))
        blitc(c, scale_p(nt, s), cx, cy - 10, op)
        tg = text_p(tag, "pxb", 30, col, 0.06, (0, 3, 6, 0.5))
        blitc(c, tg, cx, cy + 75, op)
        ld = text_p(lead, "semi", 40, (255, 255, 255), 0, (0, 3, 8, 0.5))
        blitc(c, ld, cx, cy - R - 50, op)
        if t >= t_sw:
            big = text_p("ONLY 82 PLOTS", "black", 54, G_GOLD, -0.01, (0, 5, 10, 0.5))
            big2 = text_p("AVAILABLE", "black", 54, (255, 255, 255), -0.01, (0, 5, 10, 0.5))
            pp = ease_out((t - t_sw - 0.2) * FPS / 9)
            blitc(c, hblur(big, 30 * (1 - pp)), cx - 80 * (1 - pp) , cy + R + 85, op * pp)
            blitc(c, hblur(big2, 30 * (1 - pp)), cx - 80 * (1 - pp), cy + R + 150, op * pp)
        else:
            big = text_p("TOTAL 152 PLOTS", "black", 50, (255, 255, 255), -0.01, (0, 5, 10, 0.5))
            pp = ease_out((t - t0 - 0.3) * FPS / 9)
            blitc(c, hblur(big, 30 * (1 - pp)), cx - 80 * (1 - pp), cy + R + 85, op * pp * clamp((t_sw - t) * FPS / 3))
    el(t0, t1, "front", draw)

def layout_card(t0, t1):
    mp_ = Image.open(f"{S}/stills/map_crop.jpg")
    mw = 380; mh = int(mp_.height * mw / mp_.width)
    mimg = mp_.resize((mw, mh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 60, 2))
    pad = 22
    card, shape = glass_card(mw + 2 * pad, mh + 2 * pad + 70)
    mpp = pil_to_p(mimg); mpp[..., 3] = rrect_mask(mw, mh, 16)
    mpp[..., :3] = np.asarray(mimg.convert("RGB")).astype(np.float32) * (mpp[..., 3:4] / 255.0)
    blit_p(card, mpp, pad, pad)
    tt = text_p("60 FT MAIN ROAD", "pxb", 30, (12, 52, 30), 0.02, None)
    blit_p(card, tt, (card.shape[1] - tt.shape[1]) // 2, mh + 2 * pad + (70 - tt.shape[0]) // 2 - 10)
    road_y = pad + int(mh * 1590 / 1710); road_h = int(mh * 120 / 1710)
    cx, cy = 820, 790
    SFX.append((t0, "swish"))
    def draw(c, t):
        p, op, ang = swing_in(t, t0, t1, 14)
        ct = card.copy()
        pulse = 0.5 + 0.5 * math.sin((t - t0) * 2 * math.pi * 1.4)
        if t > t0 + 0.4:
            hm = np.zeros(ct.shape[:2], np.float32)
            cv2.rectangle(hm, (pad - 4, road_y - road_h // 2), (pad + mw + 4, road_y + road_h // 2), 255, 5)
            hm = np.maximum(hm, cv2.GaussianBlur(hm, (0, 0), 6) * 1.5)
            blit_p(ct, solid_p(np.clip(hm, 0, 255), (124, 255, 58)), 0, 0, 0.45 + 0.55 * pulse)
        draw_glass(c, ct, shape, cx, cy, 0.9 + 0.1 * p, ry=ang, op=op)
    el(t0, t1, "front", draw)

def cta_text(t0, t1):
    big = text_p("DM / CALL NOW", "black", 104, (255, 255, 255), -0.02, (0, 8, 14, 0.5))
    letters = "FOR SITE VISIT"
    lp = [text_p(ch if ch != " " else "i", "black", 70, G_LIME, 0, (0, 6, 10, 0.5)) for ch in letters]
    f = font("black", 70)
    adv = [f.getlength(ch) for ch in letters]; tot = sum(adv)
    SFX.append((t0, "swish"))
    def draw(c, t):
        p = ease_out((t - t0) * FPS / 9); ex = clamp((t1 - t) * FPS / 5)
        blitc(c, hblur(scale_p(big, 0.9 + 0.1 * p), 40 * (1 - p)), W / 2 - 120 * (1 - p), 470, p * ex)
        x = W / 2 - tot / 2
        for k, (ch, im, a) in enumerate(zip(letters, lp, adv)):
            fr = (t - t0 - 0.25) * FPS - k * 1.5
            if ch != " " and fr > 0:
                q = ease_out(fr / 5)
                blit(c, im, x + a / 2 - im.shape[1] / 2, 590 - im.shape[0] / 2 + 30 * (1 - q), q * ex)
            x += a
    el(t0, t1, "front", draw)

def end_card(t0, t1, phone):
    l1 = "MAHA LAXMI"; l2 = "PROPERTY'S"
    n1g = text_p(l1, "cinzel", 112, G_GOLD, 0.02, None); n2g = text_p(l2, "cinzel", 112, G_GOLD, 0.02, None)
    n1w = text_p(l1, "cinzel", 112, (255, 255, 255), 0.02, None); n2w = text_p(l2, "cinzel", 112, (255, 255, 255), 0.02, None)
    proj = text_p("RAMDEV VATIKA – II", "semi", 46, (255, 255, 255), 0.12, None)
    ph = text_p(phone, "bold", 58, (255, 255, 255), 0.02, None)
    loc = text_p("Khasra No. 195, Jajiwal Bishnoiyan, Banar, Jodhpur", "med", 30, (210, 210, 210), 0, None)
    e_ph = emoji_p("📞", 58); e_pin = emoji_p("📍", 34)
    row = [text_p("JDA Approved", "semi", 32, GOLD1, 0, None), text_p("Bank Loanable", "semi", 32, GOLD1, 0, None),
           text_p("पट्टासुदा", "devas", 32, GOLD1, 0, None)]
    SFX.append((t0, "shimmer"))
    def name_layer(t):
        k = 0.5 - 0.5 * math.cos((t - t0) / 2.2 * 2 * math.pi)  # 0 gold -> 1 white -> gold
        k *= 0.55
        out = []
        for g, w_ in ((n1g, n1w), (n2g, n2w)):
            out.append(g * (1 - k) + w_ * k)
        return out
    def draw(c, t):
        u = t - t0
        p = ease_out(u * FPS / 18)
        s = 0.9 + 0.1 * p
        n1, n2 = name_layer(t)
        for img, y in ((n1, 700), (n2, 830)):
            im = scale_p(img, s)
            glow = im.copy(); glow[..., 3] = cv2.GaussianBlur(im[..., 3], (0, 0), 18)
            glow[..., :3] = np.array(GOLD1, np.float32) * (glow[..., 3:4] / 255.0)
            blitc(c, glow, W / 2, y, 0.55 * p)
            blitc(c, im, W / 2, y, p)
        # gold rules
        q = ease_out((u - 0.25) * FPS / 12)
        if q > 0:
            lw = int(520 * q)
            c[598:601, int(W / 2 - lw / 2):int(W / 2 + lw / 2)] = np.array(GOLD2, np.float32)
            c[929:932, int(W / 2 - lw / 2):int(W / 2 + lw / 2)] = np.array(GOLD2, np.float32)
        q = ease_out((u - 0.45) * FPS / 9)
        blitc(c, proj, W / 2, 1000 + 20 * (1 - q), q)
        q = ease_out((u - 0.7) * FPS / 9)
        if q > 0:
            wtot = e_ph.shape[1] + 18 + ph.shape[1]
            x = W / 2 - wtot / 2
            blit(c, e_ph, x, 1130 - e_ph.shape[0] / 2 + 20 * (1 - q), q)
            blit(c, ph, x + e_ph.shape[1] + 18, 1130 - ph.shape[0] / 2 + 20 * (1 - q), q)
            wtot = e_pin.shape[1] + 10 + loc.shape[1]; x = W / 2 - wtot / 2
            blit(c, e_pin, x, 1222 - e_pin.shape[0] / 2 + 20 * (1 - q), q)
            blit(c, loc, x + e_pin.shape[1] + 10, 1222 - loc.shape[0] / 2 + 20 * (1 - q), q)
        q = ease_out((u - 0.95) * FPS / 9)
        if q > 0:
            sep = 50
            wtot = sum(r.shape[1] for r in row) + sep * 2
            x = W / 2 - wtot / 2
            for i, r in enumerate(row):
                blit(c, r, x, 1330 - r.shape[0] / 2, q)
                x += r.shape[1]
                if i < 2:
                    c[1316:1346, int(x + sep / 2 - 1):int(x + sep / 2 + 1)] = c[1316:1346, int(x + sep / 2 - 1):int(x + sep / 2 + 1)] * (1 - q) + np.array(GOLD2, np.float32) * q
                    x += sep
        fo = clamp((t1 - t) / 0.5)
        if fo < 1: c *= fo
    el(t0, t1, "top", draw)

# ---------------------------------------------------------------- transitions
LEAKS = []
def leak(tc, kind): LEAKS.append((tc, kind))
def burn(tc): LEAKS.append((tc, "burn"))

_lw, _lh = 270, 480
_gx, _gy = np.meshgrid(np.arange(_lw, dtype=np.float32), np.arange(_lh, dtype=np.float32))
def blob(cx, cy, r):
    return np.exp(-(((_gx - cx) ** 2 + (_gy - cy) ** 2) / (2 * r * r)))

def apply_leaks(c, t):
    for tc, kind in LEAKS:
        half = 0.30 if kind == "burn" else 0.17
        if not (tc - half <= t <= tc + half): continue
        p = (t - tc + half) / (2 * half)            # 0..1
        inten = math.sin(math.pi * p) ** 1.2
        sx = _lw * (1.25 - 1.5 * p)
        if kind == "burn":
            cols = [((255, 90, 30), blob(sx, _lh * 0.35, 120), 1.0), ((255, 180, 70), blob(sx + 60, _lh * 0.6, 90), 0.9),
                    ((255, 240, 210), blob(sx + 20, _lh * 0.5, 60), inten)]
        elif kind == "white":
            cols = [((200, 225, 255), blob(sx, _lh * 0.4, 110), 1.0), ((255, 255, 255), blob(sx + 30, _lh * 0.55, 70), 1.0)]
        else:
            cols = [((90, 170, 255), blob(sx, _lh * 0.4, 120), 1.0), ((235, 245, 255), blob(sx + 30, _lh * 0.55, 70), 1.0),
                    ((60, 120, 255), blob(sx + 80, _lh * 0.2, 90), 0.8)]
        L = np.zeros((_lh, _lw, 3), np.float32)
        for col, b, k in cols:
            L += b[..., None] * np.array(col, np.float32) * k
        L = np.clip(L * inten * 1.15, 0, 255)
        L = cv2.resize(L, (W, H), interpolation=cv2.INTER_LINEAR)
        c[:] = 255 - (255 - c) * (255 - L) / 255   # screen

# ---------------------------------------------------------------- main loop
def scene_at(t):
    for sc in SCENES:
        if sc[0] <= t < sc[1]: return sc
    return SCENES[-1]

def main():
    build(ARGS.phone)
    json.dump(dict(sfx=sorted(SFX), dur=DUR), open(f"{S}/work/sfx.json", "w"))
    frames = range(N)
    if ARGS.preview:
        frames = [int(float(x) * FPS) for x in ARGS.preview.split(",")]
    enc = None
    if not ARGS.preview:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-i", ARGS.audio,
                                "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-level", "4.2",
                                "-b:v", "14M", "-maxrate", "16M", "-bufsize", "24M", "-pix_fmt", "yuv420p",
                                "-g", "60", "-bf", "2", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                                "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", ARGS.out],
                               stdin=subprocess.PIPE)
    readers = {}
    for fi in frames:
        t = fi / FPS
        sc = scene_at(t)
        t0, t1, kind, pr = sc
        key = (t0, kind)
        mask = None
        if kind == "black":
            frame = np.zeros((H, W, 3), np.float32)
        else:
            if key not in readers:
                for k in list(readers): readers[k].close(); del readers[k]
                if kind == "pres":
                    readers[key] = Reader(PRES, t0 - pr["off"])
                else:
                    readers[key] = Reader(pr["path"], pr["src"])
            rd = readers[key]
            u = t - t0
            if kind == "ramp":
                si = RAMP_T[min(int(round(u * FPS)), len(RAMP_T) - 1)] * FPS
                cur, prev = rd.get(int(si))
                fr = cur.astype(np.float32)
                if ramp_speed(u) > 1.4 and prev is not None: fr = 0.6 * fr + 0.4 * prev.astype(np.float32)
            else:
                cur, _ = rd.get(int(round(u * FPS)))
                fr = cur.astype(np.float32)
            if "zoom" in pr:
                z0, z1 = pr["zoom"]; z = z0 + (z1 - z0) * ease_io(u / (t1 - t0))
                if z > 1.001:
                    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
                    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            frame = finish_footage(fr)
            if "dark" in pr: frame *= pr["dark"]
            if kind == "pres":
                src = t - pr["off"]
                mask = pres_mask(int(round(src * 30)))
        canvas = frame.copy()
        if mask is not None:
            bgb = cv2.GaussianBlur(frame, (0, 0), 2.2)
            canvas = bgb * (1 - mask) + frame * mask
        act = [e for e in ELS if e["t0"] <= t < e["t1"]]
        for e in act:
            if e["layer"] == "back": e["fn"](canvas, t)
        if mask is not None and any(e["layer"] == "back" for e in act):
            canvas = canvas * (1 - mask) + frame * mask
        for e in act:
            if e["layer"] == "front": e["fn"](canvas, t)
        for e in act:
            if e["layer"] == "top": e["fn"](canvas, t)
        apply_leaks(canvas, t)
        if t < 0.25: canvas *= ease_io(t / 0.25)
        out = np.clip(canvas, 0, 255).astype(np.uint8)
        if ARGS.preview:
            Image.fromarray(out).save(f"{S}/work/prev_{t:05.2f}.jpg", quality=88)
        else:
            enc.stdin.write(out.tobytes())
        if fi % 60 == 0: print(f"frame {fi}/{N}", flush=True)
    if enc:
        enc.stdin.close(); enc.wait()

main()
