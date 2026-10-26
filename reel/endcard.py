"""End card (§5): drifting cream silk + placeholder three-circle logo."""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from look import W, H
from typo import FONTS, hexrgb

MONT_L = f"{FONTS}/Montserrat-Light.ttf"
DEVA = f"{FONTS}/NotoSansDevanagari-Light.ttf"


def silk(t):
    """Soft diagonal folds. t in 0..1 drives ~2% scale/position drift."""
    h, w = H // 4, W // 4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    z = 1 + 0.02 * t
    u = ((xx - w / 2) / z + w / 2 + 0.02 * w * t) / w
    v = ((yy - h / 2) / z + h / 2 - 0.01 * h * t) / h
    d = u * 0.80 + v * 0.60  # fold direction, ~37 deg
    e = u * -0.60 + v * 0.80
    f = (0.55 * np.sin(d * 9.0 + 1.3 * np.sin(e * 3.1) + 0.4)
         + 0.30 * np.sin(d * 17.0 + 2.0 * np.sin(e * 2.3 + 1.0))
         + 0.15 * np.sin(d * 31.0 + e * 4.0))
    f = cv2.GaussianBlur(f, (0, 0), 2.0)
    shade = np.clip(0.5 + 0.5 * f, 0, 1) ** 1.3
    hi, lo = hexrgb("#FBF3E4"), hexrgb("#E9D9BE")
    img = lo + (hi - lo) * shade[..., None]
    # faint saffron sheen along the fold crests
    crest = np.clip((f - 0.55) / 0.35, 0, 1)[..., None]
    img = img * (1 - 0.06 * crest) + hexrgb("#F2B233") * 0.06 * crest
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC)


def _tracked(draw, cx, y, text, font, tracking, fill):
    """Draw text centred on cx with extra letter-spacing (tracking in em/1000)."""
    sp = font.size * tracking / 1000
    widths = [font.getlength(c) for c in text]
    total = sum(widths) + sp * (len(text) - 1)
    x = cx - total / 2
    for c, wd in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += wd + sp
    return cx - total / 2, cx + total / 2


def logo_rgba():
    """Placeholder logo, RGBA uint8 full frame."""
    S = 2  # supersample for clean thin lines
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r, gap, cy = 78 * S, 34 * S, 800 * S
    cols = ["#C9A227", "#7A1E2C", "#1A1A1A"]
    xs = [W * S / 2 + k * (2 * r + gap) for k in (-1, 0, 1)]
    lw = 4 * S
    for x, c in zip(xs, cols):
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=c)
    # Om
    om = ImageFont.truetype(DEVA, 96 * S)
    d.text((xs[0], cy + 6 * S), "ॐ", font=om, fill="white", anchor="mm")
    # sun: ring + 8 rays
    x = xs[1]
    d.ellipse([x - 24 * S, cy - 24 * S, x + 24 * S, cy + 24 * S], outline="white", width=lw)
    for k in range(8):
        a = k * np.pi / 4
        d.line([x + 36 * S * np.cos(a), cy + 36 * S * np.sin(a),
                x + 52 * S * np.cos(a), cy + 52 * S * np.sin(a)], fill="white", width=lw)
    # star (outline) with crescent
    x = xs[2]
    pts = []
    for k in range(10):
        a = -np.pi / 2 + k * np.pi / 5
        rr = 40 * S if k % 2 == 0 else 17 * S
        pts.append((x + rr * np.cos(a), cy + 4 * S + rr * np.sin(a)))
    d.line(pts + [pts[0]], fill="white", width=lw, joint="curve")

    name = ImageFont.truetype(MONT_L, 38 * S)
    small = ImageFont.truetype(MONT_L, 25 * S)
    grey = "#6E6A64"
    y = cy + r + 70 * S
    _tracked(d, W * S / 2, y, "MAA CHAMUNDA", name, 400, grey)
    _tracked(d, W * S / 2, y + 62 * S, "JYOTISH", name, 400, grey)
    ty = y + 160 * S
    x0, x1 = _tracked(d, W * S / 2, ty, "ASTROLOGY • KUNDLI • VASTU", small, 200, grey)
    d.line([x0, ty + 44 * S, x1, ty + 44 * S], fill=grey, width=S)
    _tracked(d, W * S / 2, ty + 74 * S, "JODHPUR, RAJASTHAN", small, 200, grey)
    im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


_LOGO = None


def frame(k, n_total, with_logo=True):
    """End-card frame k of n_total (k=0 is the first frame after the dissolve)."""
    global _LOGO
    bg = silk(k / max(1, n_total - 1))
    if not with_logo:
        return bg
    if _LOGO is None:
        _LOGO = logo_rgba()
    p = min(1.0, (k + 1) / 8)  # 8-frame fade, 95% -> 100%
    p = 1 - (1 - p) ** 3
    s = 0.95 + 0.05 * p
    M = cv2.getRotationMatrix2D((W / 2, 900), 0, s)
    lg = cv2.warpAffine(_LOGO, M, (W, H), flags=cv2.INTER_CUBIC)
    a = lg[..., 3:4] * p
    return bg * (1 - a) + lg[..., :3] * a
