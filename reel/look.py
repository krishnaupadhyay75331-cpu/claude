"""Upscale, grade, sharpen, grain and vignette per the brief (§0, §1)."""
import cv2
import numpy as np

W, H = 1080, 1920


def upscale(rgb):
    # Lanczos fallback (no AI upscaler available in this environment)
    return cv2.resize(rgb, (W, H), interpolation=cv2.INTER_LANCZOS4)


def push_in(img, scale, interp=cv2.INTER_LANCZOS4):
    """Centre digital push-in (scale >= 1) on an image or mask."""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
    return cv2.warpAffine(img, M, (w, h), flags=interp, borderMode=cv2.BORDER_REFLECT)


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def grade(rgb, interior=False, vignette=True):
    x = rgb.astype(np.float32) / 255.0
    lum = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)

    # highlights -20: compress the top end (sky, white walls)
    x -= 0.10 * _smooth(0.55, 1.0, lum)[..., None] * x
    # shadows +15: open the hard noon shadows
    x += 0.09 * (1 - _smooth(0.0, 0.45, lum))[..., None] * (1 - x)
    # airy, low contrast
    x = 0.5 + (x - 0.5) * 0.93
    # black point ~4.5 IRE
    x = 0.045 + x * (1 - 0.045)
    if interior:  # mixed fluorescent -> warm, lifted ivory
        x *= np.array([1.05, 1.0, 0.92], np.float32)
        x += 0.04 * (1 - x)
    # warm whites (+5 temp, +2 tint to magenta)
    x *= np.array([1.03, 0.99, 0.955], np.float32)
    x = np.clip(x, 0, 1)

    hsv = cv2.cvtColor(x, cv2.COLOR_RGB2HSV)  # H 0..360, S/V 0..1
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # sky: -10% sat, pull hue away from cyan toward powder blue
    sky = ((h > 185) & (h < 235) & (v > 0.55)).astype(np.float32)
    sky = cv2.GaussianBlur(sky, (0, 0), 2)
    h += sky * (214 - h) * 0.35
    s *= 1 - 0.10 * sky
    # maroon / oxblood railings, gates, doors: +10 sat
    maroon = (((h < 14) | (h > 336)) & (s > 0.30)).astype(np.float32)
    s *= 1 + 0.12 * maroon
    # saffron signboard: +8 sat
    saff = ((h > 38) & (h < 56) & (s > 0.40)).astype(np.float32)
    s *= 1 + 0.10 * saff
    # sandstone: warm glow
    sand = ((h >= 14) & (h <= 36) & (s > 0.18) & (s < 0.65)).astype(np.float32)
    s *= 1 + 0.06 * sand
    v *= 1 + 0.03 * sand
    # tame green autos / foliage (-15%), nudge toward olive
    green = ((h > 70) & (h < 170)).astype(np.float32)
    s *= 1 - 0.15 * green
    h -= green * np.clip(h - 80, 0, 40) * 0.12
    hsv = np.dstack([np.mod(h, 360), np.clip(s, 0, 1), np.clip(v, 0, 1)])
    x = cv2.cvtColor(hsv.astype(np.float32), cv2.COLOR_HSV2RGB)

    if vignette:  # -8, feather 80
        yy, xx = np.mgrid[0:x.shape[0], 0:x.shape[1]].astype(np.float32)
        d = np.sqrt(((xx / x.shape[1]) - 0.5) ** 2 + ((yy / x.shape[0]) - 0.5) ** 2) / 0.7071
        x *= (1 - 0.08 * _smooth(0.2, 1.0, d))[..., None]
    return np.clip(x, 0, 1)


def finish(x, seed=0):
    """Unsharp (amount 0.35, radius 0.8) + 2.5% fine mono grain. float in/out."""
    blur = cv2.GaussianBlur(x, (0, 0), 0.8)
    x = x + 0.35 * (x - blur)
    rng = np.random.default_rng(seed)
    grain = cv2.GaussianBlur(rng.normal(0, 1, x.shape[:2]).astype(np.float32), (0, 0), 0.6)
    x = x + 0.025 * grain[..., None] * 0.6
    return np.clip(x, 0, 1)
