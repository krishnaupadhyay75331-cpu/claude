"""Small 2D motion-graphics toolkit: sprites, gradients, premultiplied compositing."""
import numpy as np, cv2, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

S = '/tmp/claude-0/-home-user-claude/72bc255f-5202-5cbe-bb9b-e101156314d2/scratchpad'
W, H = 1080, 1920
FPS = 30

FONT_FILES = {
    'hero': f'{S}/fonts/Poppins_wght_800.ttf',
    'hero7': f'{S}/fonts/Poppins_wght_700.ttf',
    'cap': f'{S}/fonts/Inter_wght_600.ttf',
    'capb': f'{S}/fonts/Inter_wght_800.ttf',
    'cta': f'{S}/fonts/Montserrat_wght_800.ttf',
    'dev': f'{S}/fonts/Tiro_Devanagari_Hindi.ttf',
}

GOLD = [(0, '#FFE9A8'), (0.40, '#F7B733'), (0.47, '#FFE08A'), (0.53, '#F2A516'), (1, '#D98E04')]
LIME = [(0, '#D4FF4F'), (1, '#57D45A')]
ROSE = [(0, '#FFB199'), (0.5, '#FF4F7B'), (1, '#D1104A')]
MAGENTA = [(0, '#FF5FA2'), (1, '#B5179E')]
SAFFRON = [(0, '#FFD25A'), (1, '#FF8A00')]
RING = [(0, '#FFE08A'), (0.5, '#FF9F1C'), (1, '#E0217A')]
IG = [(0, '#FEDA75'), (0.25, '#FA7E1E'), (0.5, '#D62976'), (0.75, '#962FBF'), (1, '#4F5BD5')]
WARM = '#FFF8EE'


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def grad_vals(stops, n):
    pos = np.array([s[0] for s in stops]); cols = np.stack([hexc(s[1]) for s in stops])
    x = np.linspace(0, 1, n)
    return np.stack([np.interp(x, pos, cols[:, c]) for c in range(3)], 1).astype(np.float32)


def grad_img(w, h, stops, direction='v'):
    if direction == 'v':
        g = grad_vals(stops, h)[:, None, :]
        return np.repeat(g, w, 1)
    if direction == 'h':
        g = grad_vals(stops, w)[None, :, :]
        return np.repeat(g, h, 0)
    # diagonal bottom-left -> top-right
    yy, xx = np.mgrid[0:h, 0:w]
    t = ((xx / max(w - 1, 1)) + (1 - yy / max(h - 1, 1))) / 2
    g = grad_vals(stops, 256)
    return g[(t * 255).astype(int)]


@lru_cache(maxsize=None)
def font(name, size):
    return ImageFont.truetype(FONT_FILES[name], int(size), layout_engine=ImageFont.Layout.RAQM)


class Sprite:
    """Premultiplied RGBA float32 image with a reference point (cx, cy)."""
    def __init__(self, rgba, cx=None, cy=None):
        self.a = rgba
        self.h, self.w = rgba.shape[:2]
        self.cx = self.w / 2 if cx is None else cx
        self.cy = self.h / 2 if cy is None else cy


def text_mask(text, fname, size, tracking=0.0, pad=40):
    f = font(fname, size)
    if tracking == 0:
        l, t, r, b = f.getbbox(text)
        im = Image.new('L', (r - l + pad * 2, b - t + pad * 2), 0)
        ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=255)
    else:
        adv = [f.getlength(ch) + tracking * size for ch in text]
        tw = int(sum(adv) - tracking * size) + 4
        asc, desc = f.getmetrics()
        im = Image.new('L', (tw + pad * 2, asc + desc + pad * 2), 0)
        d = ImageDraw.Draw(im); x = pad
        for ch, a in zip(text, adv):
            d.text((x, pad), ch, font=f, fill=255); x += a
        bb = im.getbbox()
        if bb:
            im = im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), bb[2] + pad, bb[3] + pad))
    return np.asarray(im, np.float32) / 255


def finish(mask, color, shadow=True, inner_stroke=False, shadow_alpha=0.35, glow=None):
    """mask (h,w) + color (h,w,3) -> premultiplied sprite with maroon drop shadow."""
    h, w = mask.shape
    col = color
    if inner_stroke:
        er = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)
        edge = np.clip(mask - er, 0, 1)[..., None] * 0.4
        col = col * (1 - edge) + hexc('#7A1020') * edge
    out = np.zeros((h, w, 4), np.float32)
    if glow is not None:
        gc, ga, gs = glow
        g = cv2.GaussianBlur(mask, (0, 0), gs) * ga
        out[..., :3] = hexc(gc) * g[..., None]; out[..., 3] = g
    if shadow:
        sh = cv2.GaussianBlur(mask, (0, 0), 6)
        M = np.float32([[1, 0, 0], [0, 1, 4]])
        sh = cv2.warpAffine(sh, M, (w, h)) * shadow_alpha
        out[..., :3] = out[..., :3] * (1 - sh[..., None]) + hexc('#2A0508') * sh[..., None]
        out[..., 3] = sh + out[..., 3] * (1 - sh)
    a = mask[..., None]
    out[..., :3] = col * a + out[..., :3] * (1 - a)
    out[..., 3] = mask + out[..., 3] * (1 - mask)
    return out


_tcache = {}
def text_sprite(text, fname, size, fill=WARM, tracking=0.0, shadow=True, inner_stroke=None, glow=None, direction='v'):
    key = (text, fname, size, str(fill), tracking, shadow, inner_stroke, str(glow), direction)
    if key in _tcache:
        return _tcache[key]
    m = text_mask(text, fname, size, tracking)
    h, w = m.shape
    if isinstance(fill, str):
        col = np.empty((h, w, 3), np.float32); col[:] = hexc(fill)
    else:
        ys = np.where(m.max(1) > 0.1)[0]; xs = np.where(m.max(0) > 0.1)[0]
        col = np.empty((h, w, 3), np.float32)
        if direction == 'v' and len(ys):
            y0, y1 = ys[0], ys[-1] + 1
            g = grad_vals(fill, y1 - y0)
            col[:y0] = g[0]; col[y1:] = g[-1]; col[y0:y1] = g[:, None, :]
        elif len(xs):
            x0, x1 = xs[0], xs[-1] + 1
            g = grad_vals(fill, x1 - x0)
            col[:, :x0] = g[0]; col[:, x1:] = g[-1]; col[:, x0:x1] = g[None, :, :]
    if inner_stroke is None:
        inner_stroke = not isinstance(fill, str)
    spr = Sprite(finish(m, col, shadow, inner_stroke, glow=glow))
    # visible ink bbox (for layout)
    ys = np.where(m.max(1) > 0.2)[0]; xs = np.where(m.max(0) > 0.2)[0]
    spr.ink = (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1) if len(xs) else (0, 0, w, h)
    spr.cx = (spr.ink[0] + spr.ink[2]) / 2; spr.cy = (spr.ink[1] + spr.ink[3]) / 2
    spr.iw = spr.ink[2] - spr.ink[0]; spr.ih = spr.ink[3] - spr.ink[1]
    _tcache[key] = spr
    return spr


def from_rgba8(arr):
    a = arr.astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return Sprite(a)


def place(dst, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, blur=0.0, mblur=(0.0, 0.0), clip=None):
    """Composite sprite so that its reference point lands at (cx, cy). dst float32 RGB (H,W,3)."""
    if alpha <= 0.003 or scale <= 0.01:
        return
    th = math.radians(rot)
    c, s = math.cos(th) * scale, math.sin(th) * scale
    A = np.array([[c, -s], [s, c]], np.float32)
    corners = np.array([[0, 0], [spr.w, 0], [0, spr.h], [spr.w, spr.h]], np.float32) - [spr.cx, spr.cy]
    pts = corners @ A.T + [cx, cy]
    pad = int(abs(mblur[0]) + abs(mblur[1]) + blur * 3 + 2)
    x0 = int(math.floor(pts[:, 0].min())) - pad; x1 = int(math.ceil(pts[:, 0].max())) + pad
    y0 = int(math.floor(pts[:, 1].min())) - pad; y1 = int(math.ceil(pts[:, 1].max())) + pad
    Hd, Wd = dst.shape[:2]
    X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x1, Wd), min(y1, Hd)
    if X1 <= X0 or Y1 <= Y0:
        return
    t = np.array([cx - X0, cy - Y0], np.float32) - A @ np.array([spr.cx, spr.cy], np.float32)
    M = np.hstack([A, t[:, None]]).astype(np.float32)
    roi = cv2.warpAffine(spr.a, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if blur > 0.3:
        roi = cv2.GaussianBlur(roi, (0, 0), blur)
    L = math.hypot(*mblur)
    if L > 1.5:
        n = int(L) | 1
        k = np.zeros((n, n), np.float32)
        ang = math.atan2(mblur[1], mblur[0])
        for i in range(n):
            d = i - n // 2
            k[int(round(n // 2 + d * math.sin(ang))), int(round(n // 2 + d * math.cos(ang)))] = 1
        roi = cv2.filter2D(roi, -1, k / k.sum())
    if clip is not None:
        roi = roi * clip[Y0:Y1, X0:X1, None]
    roi = roi * alpha
    d = dst[Y0:Y1, X0:X1]
    d *= (1 - roi[..., 3:4])
    d += roi[..., :3]


def over_full(dst, rgb, a):
    """Composite full-frame colour rgb (H,W,3 or (3,)) with alpha a (H,W)."""
    dst *= (1 - a[..., None]); dst += np.asarray(rgb) * a[..., None]


# ---------- easing ----------
def clamp01(x): return max(0.0, min(1.0, x))
def ease_out(p, k=4): p = clamp01(p); return 1 - (1 - p) ** k
def ease_in_out(p): p = clamp01(p); return p * p * (3 - 2 * p)
def smooth(p): return ease_in_out(p)


def pop_scale(fr, total=5, s0=0.7, peak=1.05):
    """70% -> 105% -> 100% over `total` frames."""
    if fr < 0: return 0.0
    p = fr / total
    if p >= 1: return 1.0
    mid = 0.5
    if p < mid: return s0 + (peak - s0) * ease_out(p / mid, 2)
    return peak + (1 - peak) * ease_in_out((p - mid) / (1 - mid))


def overshoot(fr, total, s0, peak, s1=1.0, mid=0.6):
    if fr < 0: return s0
    p = fr / total
    if p >= 1: return s1
    if p < mid: return s0 + (peak - s0) * ease_out(p / mid, 3)
    return peak + (s1 - peak) * ease_in_out((p - mid) / (1 - mid))


# ---------- shapes ----------
def rounded_rect_mask(w, h, r, ss=2):
    im = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255


def star_sprite(size=26, color='#FFE9A8'):
    n = size * 4
    im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
    c = n / 2; r1 = n * 0.48; r2 = n * 0.09
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=255)
    m = np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255
    glow = cv2.GaussianBlur(m, (0, 0), size / 6) * 0.8
    a = np.clip(m + glow * (1 - m), 0, 1)
    rgba = np.zeros((size, size, 4), np.float32)
    rgba[..., :3] = hexc(color) * a[..., None]; rgba[..., 3] = a
    return Sprite(rgba)


def ig_glyph_mask(size, ss=3):
    n = size * ss
    im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
    sw = n * 0.085
    d.rounded_rectangle((sw / 2, sw / 2, n - sw / 2, n - sw / 2), n * 0.28, outline=255, width=int(sw))
    r = n * 0.215
    d.ellipse((n / 2 - r, n / 2 - r, n / 2 + r, n / 2 + r), outline=255, width=int(sw))
    rd = n * 0.055; cx, cy = n * 0.755, n * 0.245
    d.ellipse((cx - rd, cy - rd, cx + rd, cy + rd), fill=255)
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255


def mask_sprite(mask, color, shadow=False):
    h, w = mask.shape
    col = np.empty((h, w, 3), np.float32)
    col[:] = hexc(color) if isinstance(color, str) else color
    return Sprite(finish(mask, col, shadow=shadow))
