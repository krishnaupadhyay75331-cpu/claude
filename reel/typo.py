"""Typography layers A-D (§2) rendered as premultiplied RGBA float layers."""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from look import W, H

FONTS = os.environ.get("REEL_FONTS", "fonts")
BEBAS = f"{FONTS}/BebasNeue.ttf"
MONT_SB = f"{FONTS}/Montserrat-SemiBold.ttf"
ARIAL = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # Arial-metric


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


GOLD = [(0.0, "#FFF6D5"), (0.40, "#F1D58A"), (0.75, "#D4A93A"), (1.0, "#C9A227")]
BRAND = [(0.0, "#7A1E2C"), (0.33, "#B8322E"), (0.66, "#E8742A"), (1.0, "#F2B233")]


def ramp(stops, t):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t - p0) / (p1 - p0))[..., None]
        out[m] = (hexrgb(c0) * (1 - k) + hexrgb(c1) * k)[m]
    return out


def ease(p):  # cubic-bezier(0.2, 0.8, 0.2, 1) approximated by a strong ease-out
    p = np.clip(p, 0, 1)
    return 1 - (1 - p) ** 3.2


class Layer:
    """Full-frame premultiplied RGBA float layer."""

    def __init__(self):
        self.rgb = np.zeros((H, W, 3), np.float32)
        self.a = np.zeros((H, W), np.float32)

    def over(self, rgb, a):
        self.rgb = rgb * a[..., None] + self.rgb * (1 - a[..., None])
        self.a = a + self.a * (1 - a)

    def transform(self, scale, dy, opacity, cx, cy):
        if scale != 1 or dy:
            M = cv2.getRotationMatrix2D((cx, cy), 0, scale)
            M[1, 2] += dy
            self.rgb = cv2.warpAffine(self.rgb, M, (W, H), flags=cv2.INTER_CUBIC)
            self.a = cv2.warpAffine(self.a, M, (W, H), flags=cv2.INTER_CUBIC)
        self.rgb *= opacity
        self.a *= opacity
        return self


def ink(text, font_path, size):
    """Alpha mask of the text with its ink bbox: (alpha, (x0, y0, x1, y1))."""
    f = ImageFont.truetype(font_path, size)
    x0, y0, x1, y1 = f.getbbox(text)
    pad = 4
    im = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=f, fill=255)
    return np.asarray(im, np.float32) / 255, pad


def place(alpha, pad, x, y):
    """Paste an ink alpha so its ink top-left lands on (x, y)."""
    out = np.zeros((H, W), np.float32)
    x, y = int(round(x - pad)), int(round(y - pad))
    h, w = alpha.shape
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    dx1, dy1 = min(W, x + w), min(H, y + h)
    out[dy0:dy1, dx0:dx1] = alpha[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    return out


def shadow(a, opacity, dist, blur):
    s = cv2.GaussianBlur(a, (0, 0), blur / 2)
    M = np.float32([[1, 0, dist * 0.35], [0, 1, dist]])
    return cv2.warpAffine(s, M, (W, H)) * opacity


def layout(lines, cx, top, width, fit="width", align="center"):
    """Per-line ink alphas for a hero block.

    fit="width": every line fitted to `width` px (the brief's rule).
    fit="cap":   first line fitted to `width`, later lines share its cap height
                 (used only where width-fitting a short word breaks the safe area).
    Returns list of (alpha, pad, x, y, letter_label) and the line (y0, y1) boxes.
    """
    ems = []
    for i, txt in enumerate(lines):
        probe = ImageFont.truetype(BEBAS, 1000).getbbox(txt)
        em = int(round(1000 * width / (probe[2] - probe[0])))
        ems.append(ems[0] if (fit == "cap" and i) else em)
    out, boxes, y = [], [], top
    for i, (txt, em) in enumerate(zip(lines, ems)):
        a, pad = ink(txt, BEBAS, em)
        cap = a.shape[0] - 2 * pad
        x = cx - (a.shape[1] - 2 * pad) / 2 if align == "center" else cx - width / 2
        out.append((a, pad, x, y, letter_labels(txt, em, a.shape, pad)))
        boxes.append((y, y + cap))
        if i + 1 < len(lines):
            # line-height 0.88: the inter-line gap is what's left of 0.88 em after the cap
            y += cap + (0.88 - 0.72) * min(em, ems[i + 1])
    return out, boxes


def letter_labels(txt, em, shape, pad):
    """Label image: pixel -> index of the letter whose advance box it falls in."""
    f = ImageFont.truetype(BEBAS, em)
    x0 = f.getbbox(txt)[0]
    lab = np.full(shape, -1, np.int32)
    edges = [f.getlength(txt[:i]) - x0 + pad for i in range(len(txt) + 1)]
    for i, ch in enumerate(txt):
        if ch != " ":
            lab[:, max(0, int(edges[i])):int(edges[i + 1])] = i
    return lab


def hidden_fractions(lay, occ):
    """Fraction of each letter's ink hidden by `occ` (1 = occluder) for a layout."""
    fr = []
    for a, pad, x, y, lab in lay:
        X, Y = int(round(x - pad)), int(round(y - pad))
        h, w = a.shape
        o = np.zeros_like(a)
        sx0, sy0, dx0, dy0 = max(0, -X), max(0, -Y), max(0, X), max(0, Y)
        dx1, dy1 = min(W, X + w), min(H, Y + h)
        o[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0] = occ[dy0:dy1, dx0:dx1]
        o[(sy0 + dy1 - dy0):, :] = 1  # off-frame counts as hidden
        o[:, (sx0 + dx1 - dx0):] = 1
        for i in np.unique(lab[lab >= 0]):
            m = (lab == i) * a
            fr.append(float((m * o).sum() / max(m.sum(), 1)))
    return np.array(fr)


def auto_place(lines, occ, width, cxs, tops, prefer, fit="width", max_hidden=0.30, min_total=0.03,
               x_safe=(50, W - 140), y_max=1560, align="center"):
    """Pick (cx, top) so the occluder clips letters (depth) without erasing any:
    every letter <= max_hidden covered, total coverage >= min_total, block inside
    the Reels safe area, nearest to `prefer`."""
    best = None
    for cx in cxs:
        for top in tops:
            lay, boxes = layout(lines, cx, top, width, fit, align)
            xs = [(x, x + a.shape[1] - 2 * pad) for a, pad, x, _, _ in lay]
            if min(x for x, _ in xs) < x_safe[0] or max(x for _, x in xs) > x_safe[1] or boxes[-1][1] > y_max:
                continue
            fr = hidden_fractions(lay, occ)
            ok = fr.max() <= max_hidden and fr.mean() >= min_total
            # least-erased letter first, then closeness to the preferred spot
            cost = (0 if ok else 10) + fr.max() + abs(cx - prefer[0]) / 1000 + abs(top - prefer[1]) / 1000
            if best is None or cost < best[0]:
                best = (cost, cx, top, fr)
    return best[1], best[2], best[3]


def hero(lines, cx, top, width, kind="gold", progress=1.0, fit="width", align="center"):
    """Layer B (gold) or C (brand). Returns (Layer, (x0, y0, x1, y1) of the landed block)."""
    lay, line_boxes = layout(lines, cx, top, width, fit, align)
    alphas = [place(a, pad, x, y) for a, pad, x, y, _ in lay]
    A = np.clip(sum(alphas), 0, 1)
    x0 = min(x for _, _, x, _, _ in lay)
    x1 = max(x + a.shape[1] - 2 * pad for a, pad, x, _, _ in lay)
    y0, y1 = line_boxes[0][0], line_boxes[-1][1]

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if kind == "gold":
        fill = np.zeros((H, W, 3), np.float32)
        for (ly0, ly1), la in zip(line_boxes, alphas):
            t = (yy - ly0) / (ly1 - ly0)
            g = ramp(GOLD, t)
            # faint inner sheen: soft-light white band ~20% down each line
            band = np.exp(-(((t - 0.20) / 0.05) ** 2))[..., None] * 0.20
            g = g + band * ((2 * g - g * g) - g)
            fill = np.where(la[..., None] > 0, g, fill)
        # 1 px inner edge #A8841F @ 20% so the ivory tops don't melt into the sky
        edge = np.clip(A - cv2.erode(A, np.ones((3, 3), np.uint8)), 0, 1)[..., None] * 0.20
        fill = fill * (1 - edge) + hexrgb("#A8841F") * edge
        sh = shadow(A, 0.30, 4, 18)
        glow = None
    else:
        ang = np.deg2rad(20)
        d = (xx - x0) * np.cos(ang) + (yy - y0) * np.sin(ang)
        span = (x1 - x0) * np.cos(ang) + (y1 - y0) * np.sin(ang)
        fill = ramp(BRAND, d / span)
        sh = shadow(A, 0.30, 4, 18)
        glow = cv2.GaussianBlur(cv2.dilate(A, np.ones((5, 5), np.uint8)), (0, 0), 3) * 0.25

    L = Layer()
    L.over(np.zeros((H, W, 3), np.float32), sh)
    if glow is not None:
        L.over(np.broadcast_to(hexrgb("#FFF6D5"), (H, W, 3)), glow)
    L.over(fill, A)
    p = ease(progress)
    cy = (y0 + y1) / 2
    # 5-frame entrance: 110% -> 100%, 0 -> 100% opacity, 14 px upward drift
    L.transform(1.10 - 0.10 * p, 14 * (1 - p), min(1, p * 1.25), cx, cy)
    return L, (x0, y0, x1, y1)


def small_width(text):
    a, pad = ink(text, MONT_SB, 78)
    return a.shape[1] - 2 * pad


def small(text, x, y, progress=1.0):
    """Layer A: Montserrat SemiBold white, ~55 px cap height; (x, y) = ink top-left."""
    a, pad = ink(text, MONT_SB, 78)
    A = place(a, pad, x, y)
    L = Layer()
    L.over(np.zeros((H, W, 3), np.float32), shadow(A, 0.45, 3, 10))
    L.over(np.ones((H, W, 3), np.float32), A)
    p = ease(progress)
    cx, cy = x + (a.shape[1] - 2 * pad) / 2, y + (a.shape[0] - 2 * pad) / 2
    return L.transform(0.90 + 0.10 * p, 0, p, cx, cy)


def subtitle(words, lit, size=47):
    """Layer D: full phrase in 30% white, words[:lit] full white. Baseline y=1520."""
    f = ImageFont.truetype(ARIAL, size)
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    x = max(40, min((W - total) / 2, W - 140 - total))  # centred, clear of right 140 px
    im = Image.new("L", (W, H), 0)
    dim = Image.new("L", (W, H), 0)
    d, dd = ImageDraw.Draw(im), ImageDraw.Draw(dim)
    for i, (w, wd) in enumerate(zip(words, widths)):
        (d if i < lit else dd).text((x, 1520), w, font=f, fill=255, anchor="ls")
        x += wd + space
    lit_a = np.asarray(im, np.float32) / 255
    dim_a = np.asarray(dim, np.float32) / 255
    L = Layer()
    L.over(np.zeros((H, W, 3), np.float32), shadow(lit_a + dim_a, 0.55, 3, 10))
    L.over(np.ones((H, W, 3), np.float32), lit_a + dim_a * 0.30)
    return L


def composite(bg, layer, visible=None):
    """bg float RGB; visible = 1 where the layer may show (0 under occluders)."""
    a = layer.a if visible is None else layer.a * visible
    rgb = layer.rgb if visible is None else layer.rgb * visible[..., None]
    return bg * (1 - a[..., None]) + rgb
