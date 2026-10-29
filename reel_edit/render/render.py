"""Frame compositor for the Maa Chamunda Jyotish reel.

Usage: python3 render.py <workdir> <start_frame> <end_frame> [out.mp4]
workdir must contain plan.json, src_rgb.raw (720x1280 rgb24), matte.npy.
Expert-only edit: one locked-off take cut into WIDE / MEDIUM / CLOSE punch-ins.
"""
import json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.expanduser("~/.fonts")
OW, OH, FPS = 1080, 1920, 30
SW, SH = 720, 1280

def hexc(h): h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255
ROSE, ROSE_GLOW = hexc("E2566C"), hexc("F27A8C")
SAGE, SAGE_DEEP, SAGE_LIGHT = hexc("A9B596"), hexc("6F7D5E"), hexc("B9C6A4")
NEON_CORE, NEON_GLOW = hexc("FFE3E8"), hexc("FF6F8E")
GOLD, GOLD_LIGHT = hexc("C9A24A"), hexc("F1D58C")
WALNUT, WALNUT_MID = hexc("1E1412"), hexc("5C4139")
WARM_WHITE, CREAM_FLASH = hexc("FFF8F0"), hexc("FFF6EC")
GRAD_TOP, GRAD_BOT = hexc("F4A3B0"), hexc("8E2F45")
GRAD_BOT_VIS = GRAD_TOP * 0.35 + GRAD_BOT * 0.65   # stop the rose->walnut ramp at 65% so the word stays legible on dark grounds

def font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if wght: f.set_variation_by_axes([wght])
    return f

# ---------------------------------------------------------------- easing
def clamp01(t): return max(0.0, min(1.0, t))
def ease_out_cubic(t): t = clamp01(t); return 1 - (1 - t) ** 3
def ease_in_out(t): t = clamp01(t); return t * t * (3 - 2 * t)
def ease_out_back(t, s=1.70158): t = clamp01(t) - 1; return 1 + (s + 1) * t ** 3 + s * t ** 2

# ---------------------------------------------------------------- compositing (premultiplied float32)
def over(dst, rgb, a, x, y, opacity=1.0):
    """Composite premultiplied patch (rgb,a) onto dst at integer top-left (x,y)."""
    h, w = a.shape
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x0 >= x1 or y0 >= y1 or opacity <= 0: return
    pa = a[y0 - y:y1 - y, x0 - x:x1 - x, None] * opacity
    prgb = rgb[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
    dst[y0:y1, x0:x1] = prgb + dst[y0:y1, x0:x1] * (1 - pa)

def screen(dst, rgb, a, x, y, opacity=1.0):
    h, w = a.shape
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x0 >= x1 or y0 >= y1: return
    src = rgb[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
    d = dst[y0:y1, x0:x1]
    dst[y0:y1, x0:x1] = 1 - (1 - d) * (1 - np.clip(src, 0, 1))

def from_pil(im):
    arr = np.asarray(im.convert("RGBA"), np.float32) / 255
    a = arr[..., 3]
    return arr[..., :3] * a[..., None], a

def transform_patch(rgb, a, scale=1.0, blur=0.0):
    if abs(scale - 1) > 1e-3:
        h, w = a.shape
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
        a = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR)
    if blur > 0.3:
        k = 0
        rgb = cv2.GaussianBlur(rgb, (k, k), blur)
        a = cv2.GaussianBlur(a, (k, k), blur)
    return rgb, a

def place_center(dst, rgb, a, cx, cy, opacity=1.0, mode="over"):
    h, w = a.shape
    (over if mode == "over" else screen)(dst, rgb, a, int(round(cx - w / 2)), int(round(cy - h / 2)), opacity)

# ---------------------------------------------------------------- text
_TCACHE = {}
def text_patch(text, f, color=WARM_WHITE, gradient=None, shadow=True, pad=48, stretch_x=1.0):
    """Returns (rgb, a, ink_box) where ink_box=(x0,y0,x1,y1) of the glyphs inside the patch."""
    key = (text, f.path, f.size, getattr(f, "_wght", None), tuple(color), None if gradient is None else tuple(map(tuple, gradient)), shadow, stretch_x)
    if key in _TCACHE: return _TCACHE[key]
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255)
    if stretch_x != 1.0:
        m = m.resize((int(w * stretch_x), h), Image.LANCZOS); w = m.size[0]
    ma = np.asarray(m, np.float32) / 255
    if gradient is not None:
        t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        t = np.clip((t * h - pad) / max(1, h - 2 * pad), 0, 1)
        col = gradient[0] * (1 - t) + gradient[1] * t
        col = np.broadcast_to(col, (h, w, 3))
    else:
        col = np.broadcast_to(color, (h, w, 3))
    rgb, a = col * ma[..., None], ma
    if shadow:
        sa = cv2.GaussianBlur(np.roll(ma, 3, axis=0), (0, 0), 6) * 0.6
        out_a = a + sa * (1 - a)
        rgb = rgb + (WALNUT * sa[..., None]) * (1 - a[..., None])
        a = out_a
    ink = (pad, pad, w - pad, h - pad)
    _TCACHE[key] = (rgb.astype(np.float32), a.astype(np.float32), ink)
    return _TCACHE[key]

# ---------------------------------------------------------------- plan & timing
WD = sys.argv[1] if len(sys.argv) > 1 else "."
P = json.load(open(os.path.join(WD, "plan.json")))
WORDS = P["words"]; SEGS = P["segs"]; NTOT = P["total"]
OF = [w["of"] for w in WORDS]
SRC_IDX = []
for a, b in SEGS: SRC_IDX += list(range(a, b))

def cut_before(i): return OF[i] - 1
SEG_BOUNDS = np.cumsum([b - a for a, b in SEGS]).tolist()
c1 = cut_before(8)      # -> WIDE + neon "?" "ya future"
c2 = cut_before(15)     # -> CLOSE "jiska"
c3 = SEG_BOUNDS[0]      # tightening cut before "kabhi kabhi"
c4 = cut_before(29)     # -> CLOSE "humein"
c5 = cut_before(33)     # -> WIDE "ek naye perspective"
c6 = cut_before(39)     # -> MEDIUM "jiske liye"
c8 = cut_before(49)     # -> WIDE credibility "jinhe"
c9 = SEG_BOUNDS[1]      # tightening cut before "chahe"
c10 = cut_before(61)    # -> MEDIUM pills "kundli"
c11 = SEG_BOUNDS[2]     # tightening cut before "prashna"
c12 = cut_before(73)    # -> MEDIUM "Maa Chamunda"
c13 = cut_before(81)    # -> WIDE "according"
c14 = cut_before(89)    # -> CLOSE "agar"
c15 = cut_before(96)    # -> MEDIUM CTA "toh abhi"
c16 = cut_before(104)   # -> WIDE "hamari team"
c17 = cut_before(109)   # -> CLOSE "consultation process"
c18 = SEG_BOUNDS[3]     # source jump cut -> MEDIUM punch-in "Maa Chamunda"
c19 = cut_before(120)   # -> CLOSE "aapke sawaal"

FR = dict(WIDE=(1.00, 0.04, 0.50, 0.50, False), MEDIUM=(1.22, 0.03, 0.54, 0.507, False), CLOSE=(1.32, 0.03, 0.57, 0.515, True))
# Expert-only cut (no B-roll): every tightening cut and the source jump cut land on a framing change.
SHOTS = [  # (start, end, kind, extra)
    (0, c1, "MEDIUM", {}), (c1, c2, "WIDE", {"neon": True}), (c2, c3, "CLOSE", {}), (c3, c4, "MEDIUM", {}),
    (c4, c5, "CLOSE", {}), (c5, c6, "WIDE", {}), (c6, c8, "MEDIUM", {}), (c8, c9, "WIDE", {"cardC": True}),
    (c9, c10, "CLOSE", {}), (c10, c11, "MEDIUM", {}), (c11, c12, "WIDE", {}), (c12, c13, "MEDIUM", {}),
    (c13, c14, "WIDE", {}), (c14, c15, "CLOSE", {}), (c15, c16, "MEDIUM", {"cta": True}), (c16, c17, "WIDE", {}),
    (c17, c18, "CLOSE", {}), (c18, c19, "MEDIUM", {}), (c19, NTOT, "CLOSE", {}),
]
SNAPS = [OF[45], OF[54], OF[99]]   # "Pushpa", "21", "DM"
# transitions: (cut frame, kind) -- flash only into the CTA and over the source jump cut
TRANS = [(c15, "std"), (c18, "std")]

def shot_at(n):
    for s in SHOTS:
        if s[0] <= n < s[1]: return s
    return SHOTS[-1]

# ---------------------------------------------------------------- source / grade
RAW = np.memmap(os.path.join(WD, "src_rgb.raw"), np.uint8, "r").reshape(-1, SH, SW, 3)
MATTE = np.load(os.path.join(WD, "matte.npy"), mmap_mode="r")

def build_lut():
    x = np.arange(256, dtype=np.float32) / 255
    # gentle S-curve, blacks down ~4%, whites held creamy (no crush)
    y = np.interp(x, [0, .08, .25, .5, .75, .92, 1], [0, .04, .215, .5, .775, .915, .965])
    r = np.clip(y * 1.02 + .006 * x, 0, 1)
    g = np.clip(y + .016 * (1 - x) ** 2, 0, 1)          # hint of sage in the shadows
    b = np.clip(y * .965 + .010 * (1 - x) ** 2, 0, 1)   # warmer/creamier highlights
    return [(c * 255).astype(np.uint8) for c in (r, g, b)]
LUT = build_lut()

def grade_expert(fr):
    out = np.dstack([cv2.LUT(fr[..., i], LUT[i]) for i in range(3)]).astype(np.float32) / 255
    l = out @ np.array([.299, .587, .114], np.float32)
    return np.clip(l[..., None] + (out - l[..., None]) * 1.08, 0, 1)

def guided(I, p, r=8, eps=1e-3):
    mI = cv2.boxFilter(I, -1, (r, r)); mp = cv2.boxFilter(p, -1, (r, r))
    cov = cv2.boxFilter(I * p, -1, (r, r)) - mI * mp
    var = cv2.boxFilter(I * I, -1, (r, r)) - mI * mI
    a = cov / (var + eps); b = mp - a * mI
    return np.clip(cv2.boxFilter(a, -1, (r, r)) * I + cv2.boxFilter(b, -1, (r, r)), 0, 1)

def expert_frame(n, shot, need_matte):
    kind = shot[2]; base, push, cx, cy, dof = FR[kind]
    t = (n - shot[0]) / max(1, shot[1] - shot[0] - 1)
    z = base * (1 + push * ease_in_out(t))
    for s in SNAPS:
        if shot[0] <= s < shot[1] and n >= s: z *= 1 + 0.08 * ease_out_cubic((n - s) / 4)
    src = SRC_IDX[min(n, len(SRC_IDX) - 1)]
    fr = grade_expert(RAW[src])
    cw, chh = SW / z, SH / z
    x0 = min(max(cx * SW - cw / 2, 0), SW - cw); y0 = min(max(cy * SH - chh / 2, 0), SH - chh)
    s = OW / cw
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    img = cv2.warpAffine(fr, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(img, (0, 0), 1.0)
    img = np.clip(img + 0.35 * (img - bl), 0, 1)
    alpha = None
    if need_matte or dof:
        m = MATTE[src].astype(np.float32) / 255
        Mm = np.float32([[s * 2, 0, -x0 * s], [0, s * 2, -y0 * s]])
        small = (OW // 2, OH // 2)
        Ms = Mm.copy(); Ms[:, :] *= 0.5
        a_s = cv2.warpAffine(m, Ms, small, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        I_s = cv2.cvtColor(cv2.resize(img, small, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        a_s = guided(I_s, a_s, 6, 2e-3)
        alpha = cv2.resize(a_s, (OW, OH), interpolation=cv2.INTER_LINEAR)
    if dof:   # fake shallow depth of field: normalized background blur so the subject doesn't bleed
        bgw = (1 - alpha)[..., None]
        num = cv2.GaussianBlur(img * bgw, (0, 0), 8); den = cv2.GaussianBlur(bgw, (0, 0), 8)[..., None] + 1e-4
        img = img * alpha[..., None] + (num / den) * (1 - alpha[..., None])
    return img, alpha, z

# ---------------------------------------------------------------- persistent layers
YY = np.linspace(0, 1, OH, dtype=np.float32)[:, None]
XX = np.linspace(0, 1, OW, dtype=np.float32)[None, :]
VIGNETTE = (1 - 0.15 * np.clip(((XX - .5) ** 2 * 1.4 + (YY - .45) ** 2) * 2.6, 0, 1) ** 1.3)[..., None].astype(np.float32)
gy = np.clip((np.arange(OH, dtype=np.float32) - 1250) / (OH - 1250), 0, 1)
CAP_GRAD = (ease_in_out(0) + gy ** 1.15 * 0.8)[:, None, None].astype(np.float32)

def apply_cap_gradient(img, strength=1.0):
    a = CAP_GRAD * strength
    img[:] = img * (1 - a) + WALNUT * a

# ---------------------------------------------------------------- overlays
def neon_question(size=230):
    key = ("neonq", size)
    if key in _TCACHE: return _TCACHE[key]
    f = font("Poppins-Light.ttf", size)
    pad = 80; bb = f.getbbox("?")
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    st = Image.new("L", (w, h)); ImageDraw.Draw(st).text((pad - bb[0], pad - bb[1]), "?", font=f, fill=255, stroke_width=7, stroke_fill=255)
    fi = Image.new("L", (w, h)); ImageDraw.Draw(fi).text((pad - bb[0], pad - bb[1]), "?", font=f, fill=255)
    outline = np.asarray(st, np.float32) / 255
    outline = np.clip(outline - cv2.erode(np.asarray(fi, np.float32) / 255, np.ones((9, 9))), 0, 1)
    core = cv2.GaussianBlur(outline, (0, 0), 1.2)
    g1 = cv2.GaussianBlur(outline, (0, 0), 10); g2 = cv2.GaussianBlur(outline, (0, 0), 26)
    _TCACHE[key] = (core, np.clip(g1 * 1.6 + g2 * 1.2, 0, 1))
    return _TCACHE[key]

def draw_neon_q(img, cx, cy, n, n0, size=230):
    k = n - n0
    if k < 0: return
    flick = [0, 1, .3, 1][k] if k < 4 else 1
    pulse = .85 + .15 * math.sin((k - 4) / (1.5 * FPS) * 2 * math.pi) if k >= 4 else 1
    core, glow = neon_question(size)
    gl = glow * (.7 + .3 * pulse) * flick
    rgb = NEON_GLOW * gl[..., None]
    screen(img, rgb, gl, int(cx - glow.shape[1] / 2), int(cy - glow.shape[0] / 2), 1.0)
    over(img, NEON_CORE * (core * flick)[..., None], core * flick, int(cx - glow.shape[1] / 2), int(cy - glow.shape[0] / 2))

def sparkle(img, cx, cy, k):
    if not (0 <= k < 12): return
    t = k / 11; s = math.sin(t * math.pi)
    L = int(70 * s) + 2
    canvas = np.zeros((200, 200), np.float32)
    ang = t * .8
    for th in (ang, ang + math.pi / 2):
        for sgn in (1, -1):
            x2 = 100 + sgn * math.cos(th) * L; y2 = 100 + sgn * math.sin(th) * L
            cv2.line(canvas, (100, 100), (int(x2), int(y2)), 1.0, 3, cv2.LINE_AA)
    for (dx, dy, sz) in ((-40, 30, .5), (35, -38, .4)):
        cv2.circle(canvas, (100 + dx, 100 + dy), max(1, int(6 * s * sz * 2)), 1.0, -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(canvas, (0, 0), 6) * 1.5 + canvas
    rgb = GOLD_LIGHT * np.clip(glow, 0, 1)[..., None]
    screen(img, rgb, np.clip(glow, 0, 1), int(cx - 100), int(cy - 100), s)

def chevron(img, cx, cy, opacity):
    c = np.zeros((90, 120), np.float32)
    cv2.polylines(c, [np.int32([[20, 25], [60, 65], [100, 25]])], False, 1.0, 9, cv2.LINE_AA)
    g = np.clip(cv2.GaussianBlur(c, (0, 0), 5) + c, 0, 1)
    over(img, GOLD_LIGHT * g[..., None], g, int(cx - 60), int(cy - 45), opacity)

# ---------------------------------------------------------------- pills
def pill_patch(text, fill, chars=None):
    f = font("Poppins-Medium.ttf", 42)
    full_w = int(f.getlength(text)) + 72
    h = 86; pad = 40
    W = full_w + 2 * pad; H = h + 2 * pad
    shape = Image.new("L", (W, H)); ImageDraw.Draw(shape).rounded_rectangle((pad, pad, pad + full_w, pad + h), h // 2, fill=255)
    sa = np.asarray(shape, np.float32) / 255
    glow = cv2.GaussianBlur(sa, (0, 0), 12) * .35
    tm = Image.new("L", (W, H))
    shown = text if chars is None else text[:chars]
    ImageDraw.Draw(tm).text((pad + 36, pad + h / 2), shown, font=f, fill=255, anchor="lm")
    ta = np.asarray(tm, np.float32) / 255
    rgb = ROSE_GLOW * glow[..., None]
    a = glow
    rgb = fill * sa[..., None] + rgb * (1 - sa[..., None]); a = sa + a * (1 - sa)
    rgb = WARM_WHITE * ta[..., None] + rgb * (1 - ta[..., None]); a = np.maximum(a, ta)
    return rgb.astype(np.float32), a.astype(np.float32), full_w

def draw_pill(img, text, fill, x_left, cy, n, n0, centered=False):
    k = n - n0
    if k < 0: return
    t = k / 8
    dx = -40 * (1 - ease_out_back(t))
    op = ease_out_cubic(t)
    chars = min(len(text), int(max(0, k - 4) / 1.5) + 1) if k >= 4 else 0
    rgb, a, fw = pill_patch(text, fill, chars)
    x = (OW - fw) / 2 if centered else x_left
    over(img, rgb, a, int(x - 40 + dx), int(cy - 43 - 40), op)

# ---------------------------------------------------------------- captions
F_HERO = "Poppins-Medium.ttf"; F_HELP = "Poppins-Light.ttf"
YC = 1430
def Wd(i): return OF[i]
PHRASES = [
    dict(hero=[("Kya", 0)], h1=[("aapke", 1), ("mind", 2), ("mein", 3), ("bhi", 4)], grad=True),
    dict(hero=[("Shaadi", 5)]),
    dict(hero=[("Career", 6)]),
    dict(hero=[("Future", 8)], h1=[("ya", 7)], h2=[("ko", 9), ("lekar", 10)]),
    dict(hero=[("Sawaal", 13)], h1=[("koi", 11), ("aisa", 12)], h2=[("hai", 14)]),
    dict(hero=[("Jawab", 16)], h1=[("jiska", 15)], h2=[("aap", 17), ("kaafi", 18), ("time", 19), ("se", 20)]),
    dict(hero=[("Dhoondh", 21)], h2=[("rahe", 22), ("ho", 23)]),
    dict(hero=[("Zaroorat", 26)], h1=[("kabhi", 24), ("kabhi", 25)], h2=[("hoti", 27), ("hai", 28)]),
    dict(hero=[("Perspective", 35)], h1=[("ek", 33), ("naye", 34)], h2=[("se", 36), ("samajhne", 37), ("ki", 38)]),
    dict(hero=[("Mil", 42)], h1=[("jiske", 39), ("liye", 40), ("aap", 41)], h2=[("sakte", 43), ("hain", 44)]),
    dict(hero=[("Pushpa", 45), ("ji", 47)], h2=[("se", 48)], end=c8),
    dict(hero=[("Guidance", 71)], h1=[("se", 69), ("related", 70)], h2=[("chahiye", 72)], end=c12),
    dict(hero=[("Maa", 73), ("Chamunda", 74)], h2=[("Jyotish", 75), ("mein", 76)]),
    dict(hero=[("Zaroorat", 79)], h1=[("aap", 77), ("apni", 78)], h2=[("ke", 80)]),
    dict(hero=[("Consultation", 82)], h1=[("according", 81)], h2=[("ke", 83), ("baare", 84), ("mein", 85), ("jaan", 86), ("sakte", 87), ("hain", 88)], letters=True),
    dict(hero=[("Consultation", 92)], h1=[("agar", 89), ("aap", 90), ("bhi", 91)], h2=[("lena", 93), ("chahte", 94), ("hain", 95)], end=c15),
    dict(hero=[("Appointment", 107)], h1=[("hamari", 104), ("team", 105), ("aapko", 106)], h2=[("aur", 108)]),
    dict(hero=[("Process", 110)], h1=[("consultation", 109)], h2=[("ki", 111), ("poori", 112)]),
    dict(hero=[("Details", 113)], h2=[("share", 114), ("kar", 115), ("degi", 116)]),
    dict(hero=[("Maa", 117), ("Chamunda", 118)], h2=[("Jyotish", 119)]),
    dict(hero=[("Sawaal", 121)], h1=[("aapke", 120)], h2=[("ko", 122), ("samajhne", 123), ("ki", 124)]),
    dict(hero=[("Shuruaat", 127)], h1=[("ek", 125), ("nayi", 126)], end=NTOT),
]
for p in PHRASES:
    p["start"] = min(Wd(i) for _, i in p.get("hero", []) + p.get("h1", []) + p.get("h2", []))
for i, p in enumerate(PHRASES):
    if "end" not in p: p["end"] = PHRASES[i + 1]["start"] if i + 1 < len(PHRASES) else NTOT

def layout_phrase(p):
    """Returns list of items: (rgb, a, x_left_of_ink, y_top_of_ink, onset, letters_flag)."""
    if "items" in p: return p["items"]
    items = []
    hero_text = " ".join(t for t, _ in p["hero"])
    if p.get("grad"):
        size = 130; fh = font(F_HELP, size)
    else:
        size = 112
        while True:
            fh = font(F_HERO, size)
            if fh.getlength(hero_text) <= 820 or size <= 60: break
            size -= 4
    sp = fh.getlength(" ")
    total = fh.getlength(hero_text)
    bb_all = fh.getbbox(hero_text)
    hx0 = OW / 2 - total / 2
    asc_top = YC - (bb_all[3] + bb_all[1]) / 2   # y of text origin so the ink box centres on YC
    grad = (GRAD_TOP, GRAD_BOT_VIS) if p.get("grad") else None
    x = hx0
    for t, wi in p["hero"]:
        if p.get("letters"):
            xs = x
            for k, ch in enumerate(t):
                rgb, a, ink = text_patch(ch, fh, gradient=grad)
                cb = fh.getbbox(ch)
                items.append((rgb, a, xs + fh.getlength(t[:k]) + cb[0], asc_top + cb[1], Wd(wi) + 2 * k, ink))
        else:
            rgb, a, ink = text_patch(t, fh, gradient=grad)
            cb = fh.getbbox(t)
            items.append((rgb, a, x + cb[0], asc_top + cb[1], Wd(wi), ink))
        x += fh.getlength(t) + sp
    hero_l, hero_r = hx0 + bb_all[0], hx0 + bb_all[2]
    hero_t, hero_b = asc_top + bb_all[1], asc_top + bb_all[3]
    fs = font(F_HELP, 29)
    for key, side in (("h1", "above"), ("h2", "below")):
        ws = p.get(key, [])
        if not ws: continue
        line = " ".join(t for t, _ in ws)
        L = fs.getlength(line)
        lx = hero_r - L if side == "above" else hero_l
        lx = min(max(lx, 90), 990 - L)
        lb = fs.getbbox(line)
        oy = (hero_t - 12 - lb[3]) if side == "above" else (hero_b + 12 - lb[1])
        cx = lx
        for t, wi in ws:
            rgb, a, ink = text_patch(t, fs)
            cb = fs.getbbox(t)
            items.append((rgb, a, cx + cb[0], oy + cb[1], Wd(wi) - (0 if key == "h1" and wi > p["hero"][0][1] else 0), ink))
            cx += fs.getlength(t + " ")
    p["items"] = items
    return items

def draw_item(img, it, n, fade=1.0):
    rgb, a, x, y, onset, ink = it
    k = n - onset
    if k < 0: return
    t = ease_out_cubic(k / 6)
    op = t * fade
    if op <= 0: return
    scale = 1.05 - .05 * t; blur = 6 * (1 - t)   # 12px blur radius ~ sigma 6
    r2, a2 = transform_patch(rgb, a, scale, blur)
    cx_ink = x + (ink[2] - ink[0]) / 2; cy_ink = y + (ink[3] - ink[1]) / 2
    ox = cx_ink - ((ink[0] + ink[2]) / 2 - a.shape[1] / 2) * scale
    oy = cy_ink - ((ink[1] + ink[3]) / 2 - a.shape[0] / 2) * scale
    over(img, r2, a2, int(round(ox - a2.shape[1] / 2)), int(round(oy - a2.shape[0] / 2)), op)

def draw_captions(img, n):
    for i, p in enumerate(PHRASES):
        if not (p["start"] <= n < p["end"] + 3): continue
        fade = 1.0 if n < p["end"] else 1 - (n - p["end"] + 1) / 3
        for it in layout_phrase(p): draw_item(img, it, n, fade)

def caption_rows():
    rows = []
    for i, p in enumerate(PHRASES):
        rows.append(dict(n=i + 1, start=p["start"], end=p["end"], hero=" ".join(t for t, _ in p["hero"]),
                         h1=" ".join(t for t, _ in p.get("h1", [])), h2=" ".join(t for t, _ in p.get("h2", [])),
                         special="gradient hero" if p.get("grad") else "letter-by-letter" if p.get("letters") else ""))
    return rows

# ---------------------------------------------------------------- card C (credibility, text behind subject)
def card_c_number():
    key = ("num",)
    if key in _TCACHE: return _TCACHE[key]
    f = font("Antonio.ttf", 400, 100)
    rgb, a, ink = text_patch("21 SAAL", f, color=WARM_WHITE, shadow=False, pad=60, stretch_x=0.86)
    sh = cv2.GaussianBlur(a, (0, 0), 15) * .25
    rgb2 = rgb * .95 + (WALNUT * sh[..., None]) * (1 - a[..., None]); a2 = a * .95 + sh * (1 - a * .95)
    _TCACHE[key] = (rgb2.astype(np.float32), a2.astype(np.float32))
    return _TCACHE[key]

def draw_card_c_behind(img, alpha, n):
    """Number composited behind the presenter's matte."""
    k = n - OF[54]
    if k < 0: return
    t = ease_out_cubic(k / 10)
    rgb, a = card_c_number()
    layer = img.copy()
    place_center(layer, rgb, a, OW / 2, 575 + 40 * (1 - t), t)
    al = alpha[..., None]
    img[:] = img * al + layer * (1 - al)

def write_on(img, text, f, color, cx, cy, n, n0, frames=12):
    k = n - n0
    if k < 0: return
    rgb, a, ink = text_patch(text, f, color=color)
    t = clamp01(k / frames)
    reveal = int(ink[0] + (ink[2] - ink[0]) * ease_in_out(t)) + 6
    mask = np.zeros_like(a); mask[:, :reveal] = 1
    mask = cv2.GaussianBlur(mask, (0, 0), 6) if t < 1 else np.ones_like(a)
    place_center(img, rgb * mask[..., None], a * mask, cx, cy, 1.0)

# ---------------------------------------------------------------- transitions
RNG = np.random.default_rng(7)
BOKEH_SETS = {}
def bokeh_set(c):
    if c in BOKEH_SETS: return BOKEH_SETS[c]
    rng = np.random.default_rng(c)
    s = []
    for _ in range(int(rng.integers(15, 26))):
        side = rng.integers(4)
        ex = [rng.uniform(0, OW), rng.uniform(0, OW), -60, OW + 60][side]
        ey = [-60, OH + 60, rng.uniform(0, OH), rng.uniform(0, OH)][side]
        s.append(dict(ex=ex, ey=ey, tx=rng.uniform(OW * .2, OW * .8), ty=rng.uniform(OH * .25, OH * .75),
                      r=rng.uniform(30, 140), col=[ROSE_GLOW, SAGE_LIGHT, GOLD_LIGHT][rng.integers(3)], op=rng.uniform(.4, .7)))
    BOKEH_SETS[c] = s
    return s

def draw_bokeh(img, c, p, grow):
    for b in bokeh_set(c):
        x = b["ex"] + (b["tx"] - b["ex"]) * p; y = b["ey"] + (b["ty"] - b["ey"]) * p
        r = b["r"] * grow
        R = int(r + 8)
        yy, xx = np.ogrid[-R:R, -R:R]
        d = np.sqrt(xx ** 2 + yy ** 2).astype(np.float32)
        disk = np.clip((r - d) / 5, 0, 1) * (0.75 + 0.25 * np.clip(d / max(r, 1), 0, 1))
        screen(img, b["col"] * disk[..., None], disk, int(x - R), int(y - R), b["op"])

def trans_state(n):
    for c, kind in TRANS:
        if c - 6 <= n < c + 6: return c, kind, n - (c - 6) + 1   # frame 1..12
    return None

def apply_transition(img, n, c, kind, f):
    if kind == "std":
        if f <= 4:
            p = f / 4
            img *= 2 ** (1.5 * p); np.clip(img, 0, 1, out=img)
            draw_bokeh(img, c, ease_out_cubic(p), .4 + .8 * p)
        elif f <= 9:
            img[:] = CREAM_FLASH
        else:
            p = (f - 9) / 3
            img *= 2 ** (1.5 * (1 - p)); np.clip(img, 0, 1, out=img)
            img[:] = img * p + CREAM_FLASH * (1 - p) * .9 + img * (1 - p) * .1
            draw_bokeh(img, c + 1, 1 - .3 * p, 1.2 - .2 * p)

# ---------------------------------------------------------------- frame
def render(n):
    shot = shot_at(n)
    extra = shot[3]
    img, alpha, z = expert_frame(n, shot, extra.get("cardC"))
    if extra.get("cardC"):
        draw_card_c_behind(img, alpha, n)
    img *= VIGNETTE
    apply_cap_gradient(img)
    if extra.get("neon"):
        draw_neon_q(img, 625, 465, n, shot[0] + 6, 210)
        k = n - (shot[0] + 6)
        if 0 <= k < 2: img[:] = 1 - (1 - img) * (1 - ROSE_GLOW * .35)

    # graphics layer
    if c10 <= n < c12:
        pills = [("Kundli Vishleshan", ROSE, 61), ("Face Reading", SAGE_DEEP, 63), ("Prashna Kundli", ROSE, 65), ("Vastu", SAGE_DEEP, 68)]
        for i, (t, col, wi) in enumerate(pills):
            draw_pill(img, t, col, 120, 880 + i * 110, n, OF[wi])
    if extra.get("cardC"):
        write_on(img, "Jyotish ki field mein", font("GreatVibes-Regular.ttf", 74), GOLD_LIGHT, OW / 2, 330, n, OF[49])
        write_on(img, "ka experience", font("GreatVibes-Regular.ttf", 84), WARM_WHITE, OW / 2, 1420, n, OF[56])
        sparkle(img, 870, 480, n - OF[54] - 4)
    if extra.get("cta"):
        fq = font(F_HERO, 66)
        words = [("“DM", 99), ("mein", 100), ("likhkar", 102), ("bhejiye”", 103)]
        line = " ".join(w for w, _ in words); L = fq.getlength(line); x = OW / 2 - L / 2
        bb = fq.getbbox(line); top = 1380 - (bb[1] + bb[3]) / 2
        for w, wi in words:
            rgb, a, ink = text_patch(w, fq); cb = fq.getbbox(w)
            draw_item(img, (rgb, a, x + cb[0], top + cb[1], OF[wi], ink), n)
            x += fq.getlength(w + " ")
        fs = font(F_HELP, 29)
        hx = OW / 2 + L / 2 - fs.getlength("toh abhi hume")
        for w, wi in (("toh", 96), ("abhi", 97), ("hume", 98)):
            rgb, a, ink = text_patch(w, fs); cb = fs.getbbox(w)
            draw_item(img, (rgb, a, hx + cb[0], top + bb[1] - 44 + cb[1], OF[wi], ink), n)
            hx += fs.getlength(w + " ")
        draw_pill(img, "consultation", ROSE, 0, 1500, n, OF[101], centered=True)
    if n >= c18:   # persistent CTA reminder after the jump cut
        draw_pill(img, "DM “consultation”", ROSE, 0, 1250, n, c18 + 3, centered=True)
        k = n - (NTOT - 18)
        if k >= 0:
            bounce = abs(math.sin(k / 18 * 3 * math.pi)) * 22
            chevron(img, OW / 2, 1585 + bounce - 11, ease_out_cubic(k / 4))
    if not (extra.get("cardC") or extra.get("cta")):
        draw_captions(img, n)

    ts = trans_state(n)
    if ts: apply_transition(img, n, *ts)
    return np.clip(img, 0, 1)

if __name__ == "__main__":
    a, b = int(sys.argv[2]), int(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else None
    if out is None:
        for n in range(a, b):
            cv2.imwrite(os.path.join(WD, "frames", f"f{n:04d}.jpg"), cv2.cvtColor((render(n) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    else:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for n in range(a, b):
            enc.stdin.write((render(n) * 255 + .5).astype(np.uint8).tobytes())
        enc.stdin.close(); enc.wait()
