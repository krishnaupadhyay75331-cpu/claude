# Graphics library: sprites, compositing and procedural overlays (float32 RGB 0..1 frames)
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get("REEL_FONTS", os.path.join(HERE, "..", "fonts"))


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


PAL = dict(plum="#14061A", deep="#5B1A6E", orchid="#A645B8", lilac="#D9B8E8", rani="#E8318A",
           neon="#FF4FD8", neoncore="#FFE1F7", gold="#E2B65A", goldl="#F7DFA0", sindoor="#C8102E",
           cream="#F3E9DA", haze="#E7C6EE", tintp="#8E3FA8", bokehpink="#FF8FC8", halo="#FFE7B0")
C = {k: hexc(v) for k, v in PAL.items()}


# ---------------- easing ----------------
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return 3 * x * x - 2 * x * x * x


def overshoot(x):
    # 0 -> 1.2 -> 1.0
    x = clamp01(x)
    if x < 0.6:
        return 1.2 * ease_out(x / 0.6)
    return 1.2 - 0.2 * ease_in_out((x - 0.6) / 0.4)


# ---------------- fonts / text sprites ----------------
_font_cache = {}


def font(name, size, weight=None):
    key = (name, size, weight)
    if key not in _font_cache:
        path = os.path.join(FONTS, name)
        f = ImageFont.truetype(path, int(size))
        if weight is not None:
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
        _font_cache[key] = f
    return _font_cache[key]


def QS(size):
    return font("Quicksand[wght].ttf", size, 700)


def SCRIPT(size):
    return font("GreatVibes-Regular.ttf", size)


def THIN(size):
    return font("JosefinSans[wght].ttf", size, 100)


def COND(size):
    return font("Antonio[wght].ttf", size, 100)


def text_sprite(txt, fnt, fill=(255, 255, 255), alpha=1.0, tracking=0):
    """RGBA float sprite tightly bounding the glyphs plus padding; returns (img, baseline_y)."""
    pad = int(fnt.size * 0.35) + 30
    asc, desc = fnt.getmetrics()
    if tracking:
        widths = [fnt.getlength(ch) + tracking for ch in txt]
        tw = int(sum(widths) - tracking)
    else:
        tw = int(fnt.getlength(txt))
    w, h = tw + 2 * pad, asc + desc + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, cw in zip(txt, widths):
            d.text((x, pad), ch, font=fnt, fill=fill + (255,))
            x += cw
    else:
        d.text((pad, pad), txt, font=fnt, fill=fill + (255,))
    a = np.asarray(im).astype(np.float32) / 255
    a[..., 3] *= alpha
    return a, pad + asc, pad


def gradient_text_sprite(txt, fnt, stops, alpha=0.85, tracking=0):
    spr, base, pad = text_sprite(txt, fnt, tracking=tracking)
    h = spr.shape[0]
    ys = np.linspace(0, 1, h)
    # stops: list of (pos, rgb)
    cols = np.zeros((h, 3), np.float32)
    for c in range(3):
        cols[:, c] = np.interp(ys, [p for p, _ in stops], [col[c] for _, col in stops])
    spr[..., :3] = cols[:, None, :]
    spr[..., 3] *= alpha
    return spr, base, pad


# ---------------- compositing ----------------
def over(dst, spr, x, y, opacity=1.0, mode="normal"):
    """Alpha-composite RGBA sprite (float) onto dst at integer top-left (x,y)."""
    sh, sw = spr.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    x1, y1 = max(0, x0), max(0, y0)
    x2, y2 = min(dst.shape[1], x0 + sw), min(dst.shape[0], y0 + sh)
    if x2 <= x1 or y2 <= y1 or opacity <= 0:
        return dst
    s = spr[y1 - y0:y2 - y0, x1 - x0:x2 - x0]
    a = s[..., 3:4] * opacity
    region = dst[y1:y2, x1:x2]
    if mode == "screen":
        res = 1 - (1 - region) * (1 - s[..., :3] * a)
        dst[y1:y2, x1:x2] = res
    elif mode == "add":
        dst[y1:y2, x1:x2] = np.minimum(1, region + s[..., :3] * a)
    else:
        dst[y1:y2, x1:x2] = region * (1 - a) + s[..., :3] * a
    return dst


def transform(spr, scale=1.0, blur=0.0, rot=0.0):
    out = spr
    if abs(scale - 1) > 1e-3 or abs(rot) > 1e-3:
        h, w = spr.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
        nw, nh = int(w * max(scale, 1) + 2), int(h * max(scale, 1) + 2)
        M[0, 2] += (nw - w) / 2
        M[1, 2] += (nh - h) / 2
        out = cv2.warpAffine(spr, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if blur > 0.3:
        # premultiplied blur so colour doesn't bleed to black
        pm = out.copy()
        pm[..., :3] *= pm[..., 3:4]
        k = int(blur * 3) | 1
        pm = cv2.GaussianBlur(pm, (k, k), blur)
        a = pm[..., 3:4]
        pm[..., :3] = np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0)
        out = pm
    return out


def shadow_of(spr, color, alpha, blur):
    sh = np.zeros_like(spr)
    sh[..., :3] = color
    sh[..., 3] = spr[..., 3] * alpha
    k = int(blur * 3) | 1
    sh[..., 3] = cv2.GaussianBlur(sh[..., 3], (k, k), blur)
    return sh


def glow_of(spr, color, radius, strength=1.0):
    g = np.zeros_like(spr)
    g[..., :3] = color
    k = int(radius * 2) | 1
    g[..., 3] = np.clip(cv2.GaussianBlur(spr[..., 3], (k, k), radius / 2) * strength, 0, 1)
    return g


def pad_sprite(spr, p):
    return np.pad(spr, ((p, p), (p, p), (0, 0)))


# ---------------- frame-level effects ----------------
def vignette_mask(strength=0.28):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
    v = np.clip((d - 0.55) / 0.6, 0, 1) ** 1.6 * strength
    return v[..., None]


def bottom_gradient():
    ys = np.arange(H, dtype=np.float32) / H
    a = np.clip((ys - 0.62) / 0.38, 0, 1) ** 1.2 * 0.88
    return a[:, None, None] * np.ones((1, W, 1), np.float32)


_grain_bank = None


def grain(frame, idx, amount=0.08):
    global _grain_bank
    if _grain_bank is None:
        r = np.random.default_rng(3)
        _grain_bank = [cv2.GaussianBlur(r.standard_normal((H, W)).astype(np.float32), (3, 3), 0.6) for _ in range(6)]
    g = _grain_bank[idx % 6][..., None]
    lum = frame.mean(2, keepdims=True)
    return np.clip(frame + g * amount * 0.35 * (0.4 + 0.6 * (1 - np.abs(lum - 0.5) * 2)), 0, 1)


def tint(frame, color, opacity):
    return frame * (1 - opacity) + (frame * color * 1.6) * opacity


def flash(frame, color, amount):
    return frame * (1 - amount) + color[None, None, :] * amount


def lowfreq_noise(seed, w, h, scale, octaves=3):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp = 1.0
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        n = r.random((max(2, h // (w // s) if w // s else 2), s)).astype(np.float32)
        acc += cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        amp *= 0.5
    acc -= acc.min()
    return acc / (acc.max() + 1e-6)


_paper = None


def paper_white():
    global _paper
    if _paper is None:
        r = np.random.default_rng(11)
        base = np.ones((H, W, 3), np.float32) * np.array([0.985, 0.98, 0.975], np.float32)
        fib = lowfreq_noise(5, W, H, 40, 4)
        base -= (fib[..., None] - 0.5) * 0.035
        specks = np.zeros((H, W), np.float32)
        for _ in range(140):
            x, y = r.integers(0, W), r.integers(0, H)
            cv2.circle(specks, (int(x), int(y)), int(r.integers(1, 4)), float(r.uniform(0.15, 0.5)), -1)
        for _ in range(25):
            x, y = r.integers(0, W), r.integers(0, H)
            ang = r.uniform(0, np.pi)
            L = r.integers(8, 30)
            cv2.line(specks, (int(x), int(y)), (int(x + L * np.cos(ang)), int(y + L * np.sin(ang))), float(r.uniform(0.1, 0.3)), 1)
        specks = cv2.GaussianBlur(specks, (3, 3), 0.7)
        _paper = np.clip(base - specks[..., None] * 0.5, 0, 1)
    return _paper


_haze_tex = None


def haze_layer(progress):
    """Lilac-rose smoke clearing: returns alpha map (H,W,1) and colour."""
    global _haze_tex
    if _haze_tex is None:
        _haze_tex = (lowfreq_noise(21, W // 4, H // 4, 3, 4), lowfreq_noise(22, W // 4, H // 4, 5, 3))
    a, b = _haze_tex
    shift = int(progress * 60)
    n = np.roll(a, shift, axis=1) * 0.6 + np.roll(b, -shift, axis=0) * 0.4
    thr = progress * 1.1
    al = np.clip((n - thr) * 3 + (1 - progress) * 0.6, 0, 1)
    al = cv2.resize(al.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return al


def bokeh_layer(seed, progress, density=60):
    r = np.random.default_rng(seed)
    lay = np.zeros((H // 2, W // 2, 3), np.float32)
    for i in range(density):
        x = r.uniform(0, W / 2)
        y = r.uniform(0, H / 2)
        rad = r.uniform(12, 55)
        col = C["goldl"] if r.random() < 0.6 else C["bokehpink"]
        delay = r.uniform(0, 0.5)
        p = clamp01((progress - delay) / 0.5)
        if p <= 0:
            continue
        y -= p * r.uniform(10, 50)
        cv2.circle(lay, (int(x), int(y)), int(rad * (0.6 + 0.4 * p)), (col * r.uniform(0.4, 0.9) * p).tolist(), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 3)
    return cv2.resize(lay, (W, H))


def light_leak(t, palette=("goldl", "rani"), seed=0, strength=0.6, sweep=None):
    """Organic leak as additive colour layer (H,W,3). sweep in 0..1 moves it across frame."""
    r = np.random.default_rng(seed)
    small = np.zeros((H // 8, W // 8, 3), np.float32)
    yy, xx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32)
    for k in range(4):
        col = C[palette[k % len(palette)]]
        cx = (r.uniform(-0.2, 1.2) if sweep is None else (-0.4 + 1.8 * sweep + r.uniform(-0.15, 0.15))) * W / 8
        cx += np.sin(t * (0.7 + k * 0.3) + k) * 12
        cy = r.uniform(0.1, 0.9) * H / 8 + np.cos(t * (0.5 + k * 0.2) + k) * 18
        rad = r.uniform(25, 70)
        g = np.exp(-(((xx - cx) / rad) ** 2 + ((yy - cy) / (rad * 1.6)) ** 2))
        flick = 0.75 + 0.25 * np.sin(t * (7 + k * 3.1)) * np.sin(t * (3.3 + k))
        small += g[..., None] * col * flick
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC) * strength


def screen(frame, layer):
    return 1 - (1 - frame) * (1 - np.clip(layer, 0, 1))


def zoom_blur(frame, amount, center=(W / 2, H * 0.45)):
    if amount < 0.01:
        return frame
    acc = frame.copy()
    n = 8
    for i in range(1, n):
        s = 1 + amount * i / n
        M = cv2.getRotationMatrix2D(center, 0, s)
        acc += cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / n


# ---------------- specific sprites ----------------
def neon_qmark(size=330):
    f = QS(size)
    spr, _, _ = text_sprite("?", f)
    a = spr[..., 3]
    er = cv2.erode(a, np.ones((9, 9), np.uint8))
    outline = np.clip(a - er, 0, 1)
    outline = cv2.GaussianBlur(outline, (3, 3), 0.8)
    p = 70
    outline = np.pad(outline, p)
    core = np.zeros(outline.shape + (4,), np.float32)
    core[..., :3] = C["neoncore"]
    core[..., 3] = outline
    inner = glow_of(core, C["neon"], 8, 1.6)
    outer = glow_of(core, C["neon"], 40, 2.2)
    res = np.zeros_like(core)
    for layer in (outer, inner, core):
        a2 = layer[..., 3:4]
        res[..., :3] = res[..., :3] * (1 - a2) + layer[..., :3] * a2
        res[..., 3:4] = res[..., 3:4] + a2 * (1 - res[..., 3:4])
    return res


def star4(size=60, color=None):
    color = C["goldl"] if color is None else color
    s = size * 3
    im = np.zeros((s, s), np.float32)
    c = s / 2
    pts = []
    for k in range(8):
        ang = k * np.pi / 4 - np.pi / 2
        rr = size / 2 if k % 2 == 0 else size / 9
        pts.append((c + rr * np.cos(ang), c + rr * np.sin(ang)))
    cv2.fillPoly(im, [np.array(pts, np.int32)], 1.0, cv2.LINE_AA)
    spr = np.zeros((s, s, 4), np.float32)
    spr[..., :3] = color
    spr[..., 3] = im
    g = glow_of(spr, color, size / 3, 1.5)
    out = g.copy()
    a = spr[..., 3:4]
    out[..., :3] = out[..., :3] * (1 - a) + spr[..., :3] * a
    out[..., 3:4] = np.clip(out[..., 3:4] + a, 0, 1)
    return out


def halo_sprite(r=230):
    s = int(r * 4.2)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / r
    core = np.clip(1 - d, 0, 1) ** 0.6
    ring = np.exp(-((d - 0.92) / 0.08) ** 2)
    bloom = np.exp(-(d / 1.15) ** 4) * 0.55
    spr = np.zeros((s, s, 4), np.float32)
    col = C["halo"][None, None] * core[..., None] + C["gold"][None, None] * (ring[..., None] + bloom[..., None] * (1 - core[..., None]))
    spr[..., :3] = np.clip(col / np.maximum(core + ring + bloom * (1 - core), 1e-3)[..., None], 0, 1)
    spr[..., 3] = np.clip(core * 0.95 + ring + bloom, 0, 1)
    return spr


def rounded_rect(w, h, rad, fill, stroke=None, sw=1.5, ss=3):
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fc = tuple(int(c * 255) for c in fill) + (255,)
    oc = tuple(int(c * 255) for c in stroke) + (255,) if stroke is not None else None
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], rad * ss, fill=fc, outline=oc, width=int(sw * ss) if stroke is not None else 0)
    im = im.resize((w, h), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255


def pill_sprite(txt, size=52, padx=18, pady=10):
    f = QS(size)
    tw = int(f.getlength(txt))
    asc, desc = f.getmetrics()
    h = asc + desc + pady * 2 - int(size * 0.18)
    w = tw + padx * 2
    box = rounded_rect(w, h, 10, C["deep"], C["gold"], 1.5)
    t, base, pad = text_sprite(txt, f)
    # place text
    out = np.zeros((h + 40, w + 40, 4), np.float32)
    out[20:20 + h, 20:20 + w] = box
    ty = 20 + pady - pad - int(size * 0.08)
    tx = 20 + padx - pad
    over_rgba(out, t, tx, ty)
    return out


def over_rgba(dst, spr, x, y):
    sh, sw = spr.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(dst.shape[1], x + sw), min(dst.shape[0], y + sh)
    s = spr[y1 - y:y2 - y, x1 - x:x2 - x]
    d = dst[y1:y2, x1:x2]
    a = s[..., 3:4]
    da = d[..., 3:4]
    oa = a + da * (1 - a)
    d[..., :3] = np.where(oa > 0, (s[..., :3] * a + d[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-5), 0)
    d[..., 3:4] = oa
    return dst


def callout_tag(txt, size=44):
    f = QS(size)
    tw = int(f.getlength(txt))
    asc, desc = f.getmetrics()
    bh = asc + desc + 16
    bw = int((tw + 44) / 0.75)
    bar = np.zeros((bh, bw, 4), np.float32)
    bar[..., :3] = C["rani"]
    xs = np.arange(bw) / bw
    bar[..., 3] = np.clip((1 - xs) / 0.4, 0, 1)[None, :]
    p = 40
    bar = pad_sprite(bar, p)
    glow = glow_of(bar, C["neon"], 25, 0.5)
    res = glow.copy()
    over_rgba(res, bar, 0, 0)
    t, base, pad = text_sprite(txt, f)
    over_rgba(res, t, p + 22 - pad, p + 8 - pad - int(size * 0.06))
    return res


def blob_mask(w, h, seed, n=6):
    """Irregular watercolour cloud built from n blobs; returns list of per-blob masks."""
    r = np.random.default_rng(seed)
    blobs = []
    for i in range(n):
        m = np.zeros((h, w), np.float32)
        cx = w * (0.2 + 0.6 * (i + 0.5) / n) + r.uniform(-30, 30)
        cy = h * 0.5 + r.uniform(-h * 0.18, h * 0.18)
        rad = r.uniform(0.22, 0.32) * min(w, h)
        pts = []
        for k in range(24):
            ang = k / 24 * 2 * np.pi
            rr = rad * (1 + 0.18 * np.sin(3 * ang + r.uniform(0, 6)) + 0.08 * r.standard_normal())
            pts.append((cx + rr * np.cos(ang), cy + rr * 0.8 * np.sin(ang)))
        cv2.fillPoly(m, [np.array(pts, np.int32)], 1.0, cv2.LINE_AA)
        m = cv2.GaussianBlur(m, (0, 0), 6)
        blobs.append(m)
    return blobs


def phone_cutout(kind="heart", h=760):
    """B&W stylised smartphone showing a social-post icon (vector-drawn cut-out)."""
    w = int(h * 0.5)
    ss = 2
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], 60 * ss, fill=(30, 30, 30, 255), outline=(235, 235, 235, 255), width=7 * ss)
    m = 26 * ss
    d.rounded_rectangle([m, m * 2, w * ss - m, h * ss - m * 2], 30 * ss, fill=(215, 215, 215, 255))
    d.rounded_rectangle([w * ss // 2 - 50 * ss, 22 * ss, w * ss // 2 + 50 * ss, 38 * ss], 8 * ss, fill=(10, 10, 10, 255))
    # post image area
    d.rectangle([m + 20 * ss, m * 2 + 90 * ss, w * ss - m - 20 * ss, m * 2 + 90 * ss + int(w * 0.8) * ss], fill=(160, 160, 160, 255))
    # avatar + name lines
    d.ellipse([m + 20 * ss, m * 2 + 25 * ss, m + 70 * ss, m * 2 + 75 * ss], fill=(110, 110, 110, 255))
    d.rounded_rectangle([m + 85 * ss, m * 2 + 38 * ss, m + 230 * ss, m * 2 + 58 * ss], 8 * ss, fill=(120, 120, 120, 255))
    cy = m * 2 + 90 * ss + int(w * 0.8) * ss + 50 * ss
    cx = m + 50 * ss
    if kind == "heart":
        r = 26 * ss
        d.ellipse([cx - r, cy - r, cx, cy], fill=(20, 20, 20, 255))
        d.ellipse([cx, cy - r, cx + r, cy], fill=(20, 20, 20, 255))
        d.polygon([(cx - r, cy - r // 2 + 4), (cx + r, cy - r // 2 + 4), (cx, cy + r)], fill=(20, 20, 20, 255))
    else:
        d.rounded_rectangle([cx - 30 * ss, cy - 24 * ss, cx + 30 * ss, cy + 22 * ss], 10 * ss, outline=(20, 20, 20, 255), width=5 * ss)
        d.ellipse([cx - 12 * ss, cy - 12 * ss, cx + 12 * ss, cy + 12 * ss], outline=(20, 20, 20, 255), width=5 * ss)
    for k in range(3):
        d.rounded_rectangle([m + 20 * ss, cy + (50 + 34 * k) * ss, w * ss - m - (40 + 60 * k) * ss, cy + (66 + 34 * k) * ss], 8 * ss, fill=(140, 140, 140, 255))
    im = im.resize((w, h), Image.LANCZOS)
    spr = np.asarray(im).astype(np.float32) / 255
    spr = pad_sprite(spr, 40)
    sh = shadow_of(spr, np.zeros(3, np.float32), 0.55, 18)
    res = sh.copy()
    over_rgba(res, spr, 0, 0)
    return res
