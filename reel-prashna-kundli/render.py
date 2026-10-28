"""Frame renderer: A-roll framing + grade, B-roll slots, kinetic captions, pills,
neon "?", bokeh/cream flashes, film burn, credibility card, CTA, grain.

usage: python3 render.py SOURCE.mov OUT_video.mp4
Writes build/sfx_events.json for audio.py.
"""
import glob
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from timeline import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

SFX = []  # (kind, new_time)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name + ".ttf"), int(round(size)))


def c01(rgb):
    return np.array(rgb, np.float32) / 255.0


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- compositing
def over(frame, spr, x, y, op=1.0):
    """Alpha-over a premultiplied RGBA float sprite at integer (x, y)."""
    if spr is None or op <= 0:
        return
    h, w = spr.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4] * op
    region = frame[y0:y1, x0:x1]
    region *= 1 - a
    region += s[..., :3] * op


def screen(frame, spr, x, y, op=1.0):
    """Screen-blend a premultiplied RGBA sprite (used for light: neon, bokeh, leaks)."""
    if spr is None or op <= 0:
        return
    h, w = spr.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x, :3] * op
    region = frame[y0:y1, x0:x1]
    region[:] = 1 - (1 - region) * (1 - np.clip(s, 0, 1))


def premult(rgb, alpha):
    a = alpha.astype(np.float32)[..., None]
    col = np.broadcast_to(c01(rgb) if np.ndim(rgb) == 1 or isinstance(rgb, tuple) else rgb, a.shape[:2] + (3,))
    return np.concatenate([col * a, a], axis=2).astype(np.float32)


def blur_sprite(spr, sigma, pad=0):
    if pad:
        spr = np.pad(spr, ((pad, pad), (pad, pad), (0, 0)))
    if sigma > 0.3:
        spr = cv2.GaussianBlur(spr, (0, 0), sigma)
    return spr


# ---------------------------------------------------------------- text sprites
MARGIN = 48


class TextSprite:
    """Text with baked walnut drop shadow. ax/ay = baseline-left anchor in the sprite."""

    def __init__(self, text, fnt, fill=(255, 255, 255), shadow=True, gradient=None, glow=None):
        self.text = text
        self.font = fnt
        asc, desc = fnt.getmetrics()
        self.adv = fnt.getlength(text)
        bb = fnt.getbbox(text, anchor="ls")
        w = int(max(self.adv, bb[2]) - min(0, bb[0])) + 2 * MARGIN
        h = asc + desc + 2 * MARGIN
        self.ax, self.ay = MARGIN - min(0, bb[0]), MARGIN + asc
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).text((self.ax, self.ay), text, font=fnt, fill=255, anchor="ls")
        m = np.asarray(mask, np.float32) / 255.0
        cap = fnt.getbbox("H", anchor="ls")
        self.cap = -cap[1]
        self.top = bb[1]  # relative to baseline (negative)
        if gradient is not None:  # vertical gradient across the glyph box
            top_y, bot_y = self.ay + bb[1], self.ay + bb[3]
            t = np.clip((np.arange(h, dtype=np.float32) - top_y) / max(1, bot_y - top_y), 0, 1)[:, None, None]
            col = c01(gradient[0]) * (1 - t) + c01(gradient[1]) * t
            col = np.broadcast_to(col, (h, w, 3))
        else:
            col = np.broadcast_to(c01(fill), (h, w, 3))
        txt = np.concatenate([col * m[..., None], m[..., None]], 2)
        out = np.zeros((h, w, 4), np.float32)
        if shadow:
            sh = np.zeros_like(m)
            sh[4:, 4:] = m[:-4, :-4]
            sh = cv2.GaussianBlur(sh, (0, 0), 7) * 0.6
            out = premult(WALNUT, sh)
        if glow is not None:
            g = np.clip(cv2.GaussianBlur(m, (0, 0), glow[1]) * 3.0, 0, 1) * glow[2]
            gl = premult(glow[0], g)
            out = gl + out * (1 - gl[..., 3:4])
        out = txt + out * (1 - m[..., None])
        self.spr = out.astype(np.float32)
        self._anim = {}

    def frame(self, k, n=6, blur=12, scale0=1.05):
        """Blur-in state for age k frames (k >= n -> settled). Returns (sprite, ax, ay)."""
        if k >= n:
            return self.spr, self.ax, self.ay
        k = max(k, 0)
        if k not in self._anim:
            q = ease_out((k + 1) / (n + 1))
            s = scale0 + (1 - scale0) * q
            spr = self.spr
            h, w = spr.shape[:2]
            spr = cv2.resize(spr, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_LINEAR)
            spr = blur_sprite(spr, blur / 2 * (1 - q))
            spr = spr * min(1.0, 0.15 + q)
            self._anim[k] = (spr, self.ax * s, self.ay * s)
        return self._anim[k]


def draw_text(frame, ts, x, y, age, op=1.0, n=6, blur=12):
    """Place TextSprite so its baseline-left lands on (x, y), with blur-in by age."""
    if age < 0:
        return
    spr, ax, ay = ts.frame(age, n, blur)
    # scale about the glyph centre so the word settles in place
    cx = x + ts.adv / 2
    cy = y - ts.cap / 2
    s = spr.shape[1] / ts.spr.shape[1]
    over(frame, spr, cx - (ts.ax + ts.adv / 2) * s, cy - (ts.ay - ts.cap / 2) * s, op)


# ---------------------------------------------------------------- caption layout
HERO_BASE = int(0.68 * H)          # 1306
HERO_CAP = 110
HELPER_CAP = 30
F_HERO = "Poppins-Medium"
F_HELP = "Poppins-Light"


def cap_size(name, cap):
    f = font(name, 100)
    c = -f.getbbox("H", anchor="ls")[1]
    return 100 * cap / c


HERO_SIZE = cap_size(F_HERO, HERO_CAP)
HELP_SIZE = cap_size(F_HELP, HELPER_CAP)
GRAD_SIZE = cap_size("Poppins-Light", 130)


def fit_size(name, size, text, maxw=980):
    f = font(name, size)
    w = f.getlength(text)
    return size * min(1.0, maxw / w)


def n_frame(t_raw):
    return int(round(r2n(t_raw) * FPS))


class Phrase:
    def __init__(self, d):
        self.d = d
        style = d.get("style", "normal")
        self.style = style
        text, t = d["hero"]
        self.t_hero = n_frame(t)
        self.t_end = n_frame(d["end"])
        self.t_start = min([n_frame(tt) for _, tt in d["before"]] + [self.t_hero])
        if style == "gradient":
            fz = fit_size("Poppins-Light", GRAD_SIZE, text)
            self.hero = TextSprite(text, font("Poppins-Light", fz), gradient=(MAUVE, ROSE_DEEP),
                                   glow=(CREAM, 9, 0.95))
        else:
            fz = fit_size(F_HERO, HERO_SIZE, text)
            self.hero = TextSprite(text, font(F_HERO, fz))
        self.base = HERO_BASE
        self.x0 = (W - self.hero.adv) / 2
        self.x1 = self.x0 + self.hero.adv
        self.letters = []
        if style == "letters":
            f = font(F_HERO, fz)
            for i, ch in enumerate(text):
                if ch == " ":
                    continue
                self.letters.append((i, TextSprite(ch, f), self.x0 + f.getlength(text[:i])))
        hf = font(F_HELP, HELP_SIZE)
        sp = hf.getlength(" ")
        top = self.base + self.hero.top  # top of hero ink

        def line(words, right=None, left=None, base=0):
            sprites = [TextSprite(w.lower(), hf, fill=CREAM) for w, _ in words]
            total = sum(s.adv for s in sprites) + sp * max(0, len(sprites) - 1)
            x = right - total if right is not None else left
            out = []
            for (w, tt), s in zip(words, sprites):
                out.append((n_frame(tt), s, x, base))
                x += s.adv + sp
            return out

        self.helpers = line(d["before"], right=self.x1, base=top - 20) + \
            line(d["after"], left=self.x0, base=self.base + 20 + HELPER_CAP + 12)
        self.underline = d.get("ul", False)
        if self.letters:
            self.t_settled = self.t_hero + 2 * (len(self.letters) - 1) + 6
        else:
            self.t_settled = self.t_hero + 6

    def draw(self, frame, n):
        if n < self.t_start or n > self.t_end + 3:
            return
        op = 1.0 if n <= self.t_end else 1 - (n - self.t_end) / 3
        for tt, s, x, b in self.helpers:
            draw_text(frame, s, x, b, n - tt, op)
        if self.letters:
            for j, (_, s, x) in enumerate(self.letters):
                draw_text(frame, s, x, self.base, n - (self.t_hero + 2 * j), op)
        else:
            draw_text(frame, self.hero, self.x0, self.base, n - self.t_hero, op)
        if self.underline and n >= self.t_settled:
            p = ease_out((n - self.t_settled + 1) / 8)
            y = self.base + 18
            x1 = self.x0 + (self.x1 - self.x0) * p
            blend_rect(frame, self.x0, y, x1, y + 3, GOLD, op)


def blend_rect(frame, x0, y0, x1, y1, rgb, op):
    x0, x1 = int(x0), int(x1)
    if x1 <= x0:
        return
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - op) + c01(rgb) * op


# ---------------------------------------------------------------- pills
class Pill:
    def __init__(self, text, size=None):
        self.text = text
        f = font("Poppins-SemiBold", size or cap_size("Poppins-SemiBold", 33))
        self.font = f
        tw = f.getlength(text)
        cap = -f.getbbox("H", anchor="ls")[1]
        self.h = int(cap + 2 * 14 + 22)
        self.w = int(tw + 2 * 28 + 10)
        ss = 4
        g = 40  # glow pad
        big = Image.new("L", ((self.w + 2 * g) * ss, (self.h + 2 * g) * ss), 0)
        d = ImageDraw.Draw(big)
        d.rounded_rectangle([g * ss, g * ss, (g + self.w) * ss, (g + self.h) * ss], radius=self.h * ss // 2, fill=255)
        shape = np.asarray(big.resize((self.w + 2 * g, self.h + 2 * g), Image.LANCZOS), np.float32) / 255
        big2 = Image.new("L", big.size, 0)
        ImageDraw.Draw(big2).rounded_rectangle([g * ss, g * ss, (g + self.w) * ss, (g + self.h) * ss],
                                               radius=self.h * ss // 2, outline=255, width=2 * ss)
        stroke = np.asarray(big2.resize(shape.shape[::-1], Image.LANCZOS), np.float32) / 255
        hh, ww = shape.shape
        t = np.clip((np.arange(ww, dtype=np.float32) - g) / self.w, 0, 1)[None, :, None]
        grad = c01(ROSE) * (1 - t) + c01(ROSE_DEEP) * t
        body = np.concatenate([grad * shape[..., None], shape[..., None]], 2)
        glow = premult(ROSE, cv2.GaussianBlur(shape, (0, 0), 12) * 0.35)
        out = body + glow * (1 - shape[..., None])
        st = premult(GOLD, stroke * 0.6)
        out = st + out * (1 - st[..., 3:4])
        self.base = out.astype(np.float32)
        self.g = g
        self.tx = g + 28 + 5
        self.ty = g + self.h / 2 + cap / 2
        self._txt = {}

    def text_sprite(self, n):
        if n not in self._txt:
            self._txt[n] = TextSprite(self.text[:n], self.font, shadow=False) if n > 0 else None
        return self._txt[n]

    def draw(self, frame, cx, top, age, op=1.0, slide=0):
        """age in frames since the pill starts: 0-7 wipe, then 1 char per frame."""
        if age < 0:
            return
        x = cx - self.w / 2 - self.g + slide * (1 - ease_out((age + 1) / 8))
        y = top - self.g
        p = ease_out((age + 1) / 8)
        spr = self.base
        cut = int(self.g + (self.w + self.g) * p)
        over(frame, spr[:, :cut], x, y, op)
        nchar = max(0, age - 7)
        ts = self.text_sprite(min(nchar, len(self.text)))
        if ts is not None:
            over(frame, ts.spr, x + self.tx - ts.ax, y + self.ty - ts.ay, op)

    def tick_times(self, start_frame):
        out = []
        for i in range(1, len(self.text) + 1):
            if i % 3 == 1 and self.text[i - 1] != " ":
                out.append((start_frame + 7 + i) / FPS)
        return out


# ---------------------------------------------------------------- neon "?"
def neon_sprite(height):
    f = font("Poppins-Medium", 400)
    bb = f.getbbox("?", anchor="ls")
    s = height / (bb[3] - bb[1])
    f = font("Poppins-Medium", 400 * s)
    bb = f.getbbox("?", anchor="ls")
    pad = 90
    w, h = int(bb[2] - bb[0]) + 2 * pad, int(bb[3] - bb[1]) + 2 * pad
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), "?", font=f, fill=255, anchor="ls")
    m = (np.asarray(im) > 127).astype(np.uint8)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    sc = height / 260
    tube = (cv2.dilate(m, k(max(2, int(5 * sc)))) - cv2.erode(m, k(max(2, int(5 * sc))))).astype(np.float32)
    tube = cv2.GaussianBlur(tube, (0, 0), 1.0)
    core = (cv2.dilate(m, k(1)) - cv2.erode(m, k(1))).astype(np.float32)
    core = cv2.GaussianBlur(core, (0, 0), 0.8)
    rgb = np.zeros((h, w, 3), np.float32)
    g1 = cv2.GaussianBlur(tube, (0, 0), 12 * sc)[..., None] * 1.1
    g2 = cv2.GaussianBlur(tube, (0, 0), 34 * sc)[..., None] * 0.9
    rgb += c01(NEON) * np.clip(g1 + g2, 0, 1)
    rgb = rgb * (1 - tube[..., None]) + c01(NEON) * tube[..., None]
    rgb = rgb * (1 - core[..., None]) + c01(NEON_IN) * core[..., None]
    a = np.clip(rgb.max(2), 0, 1)
    return np.concatenate([np.clip(rgb, 0, 1), a[..., None]], 2).astype(np.float32)


NEON_BIG = neon_sprite(260)
NEON_SMALL = neon_sprite(140)


def neon_op(age):
    if age < 0:
        return 0
    if age < 5:
        return [1, 0, 1, 0, 1][age]
    return 0.85 + 0.15 * (0.5 + 0.5 * math.cos(2 * math.pi * (age - 5) / 45))


# ---------------------------------------------------------------- bokeh / flashes
def disc_sprite(r, rgb):
    d = 2 * r + 16
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32) - (d - 1) / 2
    rr = np.sqrt(xx ** 2 + yy ** 2) / r
    body = np.clip((1 - rr) * r / 3, 0, 1)
    rim = np.exp(-((rr - 0.92) ** 2) / 0.004) * 0.35
    a = np.clip(body * 0.75 + rim, 0, 1)
    a = cv2.GaussianBlur(a, (0, 0), 1.5)
    return premult(rgb, a)


class Bokeh:
    def __init__(self, seed, n=18):
        rng = np.random.default_rng(seed)
        self.discs = []
        for i in range(n):
            r = int(rng.uniform(20, 110))
            col = ROSE if rng.random() < 0.55 else GOLD
            edge = rng.integers(4)
            if edge == 0:
                x, y = rng.uniform(-60, 160), rng.uniform(200, H)
            elif edge == 1:
                x, y = rng.uniform(W - 160, W + 60), rng.uniform(200, H)
            else:
                x, y = rng.uniform(0, W), rng.uniform(H - 400, H + 60)
            self.discs.append(dict(spr=disc_sprite(r, col), x=x, y=y, r=r, a=rng.uniform(0.4, 0.7),
                                   vy=rng.uniform(140, 380), drift=rng.uniform(0.15, 0.4), d=rng.uniform(0, 3)))

    def draw(self, frame, k, env):
        for d in self.discs:
            t = (k + d["d"]) / 14
            x = d["x"] + (W / 2 - d["x"]) * d["drift"] * t
            y = d["y"] - d["vy"] * t
            sz = d["spr"].shape[0]
            screen(frame, d["spr"], x - sz / 2, y - sz / 2, d["a"] * env)


def flash_state(n, centre_frame):
    """k in 0..13 for the 14-frame transition (cut at k == 7), else None."""
    k = n - centre_frame + 7
    return k if 0 <= k < 14 else None


# ---------------------------------------------------------------- misc overlays
def walnut_gradient():
    g = np.zeros((H, W, 4), np.float32)
    y0 = int(H * (1 - 0.38))
    t = np.clip((np.arange(H) - y0) / (H - y0), 0, 1)
    a = (smooth_arr(t) * 0.8).astype(np.float32)[:, None]
    g[..., 3] = a
    g[..., :3] = c01(WALNUT) * a[..., None]
    return g


def smooth_arr(t):
    return t * t * (3 - 2 * t)


WALNUT_GRAD = walnut_gradient()


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    t = np.clip((r - 0.3) / 0.7, 0, 1)
    return (1 - 0.12 * 1.6 * smooth_arr(t))[..., None].astype(np.float32)


VIGNETTE = vignette()


def story_grade(f):
    """Golden-hour B-roll look: darker, amber highlights, mauve-leaning shadows."""
    lum = (f[..., 0] * 0.3 + f[..., 1] * 0.59 + f[..., 2] * 0.11)[..., None]
    f = f * 0.9
    f = f + (c01(MAUVE) - 0.55) * 0.10 * (1 - lum)
    f = f + (np.array([1.0, 0.72, 0.38], np.float32) - 0.7) * 0.10 * lum
    f = 0.5 + (f - 0.5) * 1.08
    return np.clip(f, 0, 1)


def leak_blob(rw, rh, rgb):
    yy, xx = np.mgrid[0:rh, 0:rw].astype(np.float32)
    d = ((xx - rw / 2) / (rw / 2)) ** 2 + ((yy - rh / 2) / (rh / 2)) ** 2
    a = np.clip(np.exp(-d * 2.2), 0, 1)
    return premult(rgb, a)


LEAK_A = leak_blob(900, 700, (255, 150, 60))
LEAK_B = leak_blob(700, 520, GOLD)
LEAK_C = leak_blob(520, 380, (255, 210, 140))


def flare_sprite():
    s = 1400
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
    r = np.sqrt(xx ** 2 + yy ** 2) / (s / 2)
    core = np.exp(-r * r * 10)
    halo = np.exp(-r * r * 2.2) * 0.55
    streak = np.exp(-(yy / 10) ** 2) * np.exp(-np.abs(xx) / 420) * 0.8
    a = np.clip(core + halo + streak, 0, 1)
    return premult((255, 214, 150), a)


FLARE = flare_sprite()


def sparkle_sprite(r):
    d = 8 * r
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32) - d / 2
    rr = np.sqrt(xx ** 2 + yy ** 2)
    a = np.exp(-(rr / r) ** 2) + 0.5 * np.exp(-(rr / (3 * r)) ** 2) * 0.5
    cross = (np.exp(-(xx / 1.2) ** 2) + np.exp(-(yy / 1.2) ** 2)) * np.exp(-rr / (2.5 * r)) * 0.6
    return premult((255, 225, 160), np.clip(a + cross, 0, 1))


SPARKLES = []
_rng = np.random.default_rng(7)
for i in range(9):
    SPARKLES.append(dict(spr=sparkle_sprite(int(_rng.uniform(2, 5))), x=_rng.uniform(200, 880),
                         y=_rng.uniform(1080, 1500), vy=_rng.uniform(50, 120), ph=_rng.uniform(0, 6.28),
                         sw=_rng.uniform(10, 30)))


def arrow_sprite():
    w, h = 90, 90
    ss = 4
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    d.line([(45 * ss, 6 * ss), (45 * ss, 76 * ss)], fill=255, width=7 * ss)
    d.line([(16 * ss, 50 * ss), (45 * ss, 80 * ss), (74 * ss, 50 * ss)], fill=255, width=7 * ss, joint="curve")
    m = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255
    sh = cv2.GaussianBlur(np.roll(np.roll(m, 4, 0), 4, 1), (0, 0), 5) * 0.6
    out = premult(WALNUT, sh)
    g = premult(GOLD, m)
    return g + out * (1 - m[..., None])


ARROW = arrow_sprite()

# ---------------------------------------------------------------- framing
FACE = {"A": (495, 830), "B": (570, 840)}


def framing(shot, p):
    """Return (scale, x0, y0) crop origin in source pixels."""
    fr = shot["frame"]
    fx, fy = FACE[shot["setup"]]
    if fr == "wide":
        s, ax, ay, ox, oy = 1.00 + 0.04 * p, 540, 960, 540, 960
    elif fr == "tight":
        s, ax, ay, ox, oy = 1.38 + 0.04 * p, fx, fy, 540, 640
    elif fr == "hook_kb":
        s, ax, ay, ox, oy = 1.10 + 0.16 * p, 470 + 50 * p, 860, 540, 780
    elif fr == "tight_story":
        s, ax, ay, ox, oy = 1.38 + 0.08 * p, fx, fy, 540, 640
    elif fr == "mid_story":
        s, ax, ay, ox, oy = 1.15 + 0.07 * p, fx, 860, 540, 820
    elif fr == "card":
        s, ax, ay, ox, oy = 1.22 + 0.03 * p, fx, fy, 540, 720
    elif fr == "b_story":
        s, ax, ay, ox, oy = 1.06 + 0.06 * p, fx, 900, 540, 900
    elif fr == "cta":
        s, ax, ay, ox, oy = 1.18 + 0.07 * p, fx, fy, 540, 700
    else:
        raise ValueError(fr)
    x0 = min(max(ax - ox / s, 0), W - W / s)
    y0 = min(max(ay - oy / s, 0), H - H / s)
    return s, x0, y0


def apply_framing(img, s, x0, y0, sharpen=False):
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if sharpen:
        bl = cv2.GaussianBlur(out, (0, 0), 1.6)
        out = cv2.addWeighted(out, 1.6, bl, -0.6, 0)
    return out


# ---------------------------------------------------------------- B-roll drop-ins
def find_asset(base):
    for ext in (".mp4", ".mov", ".png", ".jpg", ".jpeg", ".webp"):
        p = os.path.join(HERE, base + ext)
        if os.path.exists(p):
            return p
    return None


def cover(img):
    h, w = img.shape[:2]
    s = max(W / w, H / h)
    img = cv2.resize(img, (int(math.ceil(w * s)), int(math.ceil(h * s))), interpolation=cv2.INTER_AREA)
    y = (img.shape[0] - H) // 2
    x = (img.shape[1] - W) // 2
    return img[y:y + H, x:x + W]


class Slot:
    def __init__(self, path, kenburns):
        self.path = path
        self.kb = kenburns
        self.frames = None
        if path.endswith((".mp4", ".mov")):
            cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf",
                   f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
            raw = subprocess.run(cmd, capture_output=True, check=True).stdout
            self.frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        else:
            self.img = cover(np.asarray(Image.open(path).convert("RGB")))

    def get(self, i, p):
        if self.frames is not None:
            img = self.frames[min(i, len(self.frames) - 1)]
            s, dx = 1.0 + 0.03 * p, 0
        else:
            img = self.img
            if self.kb == "hook":
                s, dx = 1.0 + 0.15 * p, 40 * p
            else:
                s, dx = 1.0 + 0.10 * p, 0
        x0 = (W - W / s) / 2 + dx / s
        y0 = (H - H / s) / 2
        x0 = min(max(x0, 0), W - W / s)
        return apply_framing(img, s, x0, y0)


# ---------------------------------------------------------------- subject masks
_sess = None


def subject_mask(rgb_u8, key):
    """ISNet subject matte (from @imgly/background-removal-node's bundled model)."""
    global _sess
    path = os.path.join(BUILD, "masks", f"{key}.png")
    if os.path.exists(path):
        return np.asarray(Image.open(path), np.float32) / 255
    if _sess is None:
        import onnxruntime as ort
        _sess = ort.InferenceSession(os.environ.get("ISNET_ONNX", os.path.join(BUILD, "isnet_medium.onnx")),
                                     providers=["CPUExecutionProvider"])
    x = cv2.resize(rgb_u8, (1024, 1024), interpolation=cv2.INTER_AREA).astype(np.float32)
    x = ((x - 128) / 256).transpose(2, 0, 1)[None]
    y = _sess.run(["output"], {"input": x})[0][0, 0]
    m = np.clip(cv2.resize(y, (W, H), interpolation=cv2.INTER_LINEAR), 0, 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray((m * 255).astype(np.uint8)).save(path)
    return m


# ---------------------------------------------------------------- thought bubble
def bubble_sprite(photo_path, w=460, h=360):
    rng = np.random.default_rng(3)
    pad = 60
    cw, ch = w + 2 * pad, h + 2 * pad + 120
    ss = 2
    im = Image.new("L", (cw * ss, ch * ss), 0)
    d = ImageDraw.Draw(im)
    cx, cy = cw / 2, pad + h / 2
    for i in range(14):
        a = 2 * math.pi * i / 14
        r = rng.uniform(70, 110)
        x = cx + math.cos(a) * (w / 2 - 70)
        y = cy + math.sin(a) * (h / 2 - 70)
        d.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=255)
    d.ellipse([(cx - w / 2 + 60) * ss, (cy - h / 2 + 60) * ss, (cx + w / 2 - 60) * ss, (cy + h / 2 - 60) * ss], fill=255)
    for (dx, dy, r) in [(-120, h / 2 + 40, 28), (-170, h / 2 + 95, 16)]:  # trailing puffs
        d.ellipse([(cx + dx - r) * ss, (cy + dy - r) * ss, (cx + dx + r) * ss, (cy + dy + r) * ss], fill=255)
    m = np.asarray(im.resize((cw, ch), Image.LANCZOS), np.float32) / 255
    # torn-paper edge: perturb the edge with noise
    noise = cv2.GaussianBlur(rng.random((ch, cw)).astype(np.float32), (0, 0), 1.2)
    edge = cv2.GaussianBlur(m, (0, 0), 3)
    m = np.clip((edge - 0.5 + (noise - 0.5) * 0.35) * 8 + 0.5, 0, 1)
    paper = premult((255, 255, 255), m)
    sh = premult(WALNUT, cv2.GaussianBlur(np.roll(np.roll(m, 6, 0), 6, 1), (0, 0), 10) * 0.5)
    out = paper + sh * (1 - m[..., None])
    photo = cover_to(np.asarray(Image.open(photo_path).convert("RGB")), w - 150, h - 130)
    pm = np.zeros((h - 130, w - 150), np.float32)
    cv2.ellipse(pm, ((w - 150) // 2, (h - 130) // 2), ((w - 150) // 2 - 2, (h - 130) // 2 - 2), 0, 0, 360, 1, -1)
    pm = cv2.GaussianBlur(pm, (0, 0), 1.5)
    ph = np.concatenate([photo.astype(np.float32) / 255 * pm[..., None], pm[..., None]], 2)
    py, px = int(cy - (h - 130) / 2), int(cx - (w - 150) / 2)
    reg = out[py:py + h - 130, px:px + w - 150]
    reg[:] = ph + reg * (1 - ph[..., 3:4])
    return out


def cover_to(img, w, h):
    s = max(w / img.shape[1], h / img.shape[0])
    img = cv2.resize(img, (int(math.ceil(img.shape[1] * s)), int(math.ceil(img.shape[0] * s))))
    y = (img.shape[0] - h) // 2
    x = (img.shape[1] - w) // 2
    return img[y:y + h, x:x + w]


def couple_sprite(path, height):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im, np.float32) / 255
    g = (a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11)
    s = height / a.shape[0]
    rgb = np.repeat(g[..., None], 3, 2)
    al = a[..., 3]
    rgb = cv2.resize(rgb, (int(a.shape[1] * s), int(height)), interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_AREA)
    pad = 40
    rgb = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)))
    al = np.pad(al, pad)
    body = np.concatenate([rgb * al[..., None], al[..., None]], 2)
    glow = premult(CREAM, np.clip(cv2.GaussianBlur(al, (0, 0), 10) * 1.4, 0, 1) * 0.9)
    return body + glow * (1 - al[..., None])


# ---------------------------------------------------------------- main
def main(src, out_path):
    shots = SHOTS
    phrases = [Phrase(d) for d in PHRASES]

    slots = {}
    for sh in shots:
        if sh.get("slot"):
            p = find_asset(sh["slot"])
            if p:
                slots[sh["name"]] = Slot(p, "hook" if "hook" in sh["slot"] else "push")
                print("B-roll slot filled:", sh["name"], "<-", p)
    couple_path = find_asset("broll/6_couple")
    couple = couple_sprite(couple_path, 0.45 * H) if couple_path and couple_path.endswith(".png") else None
    photo_path = find_asset("broll/5_happy_couple")
    bubble = bubble_sprite(photo_path) if photo_path else None

    # pills
    pill_draws = []
    for g in PILL_GROUPS:
        t0 = n_frame(g["t"])
        y = g["y"]
        for i, txt in enumerate(g["items"]):
            pl = Pill(txt)
            st = t0 + 8 * i
            pill_draws.append(dict(pill=pl, start=st, end=n_frame(g["end"]), top=y, slide=-40))
            for tt in pl.tick_times(st):
                SFX.append(("tick", tt))
            y += pl.h + 18
        hf = font(F_HELP, HELP_SIZE)
        x = (W - pill_draws[-1]["pill"].w) / 2
        sp = hf.getlength(" ")
        for w_, tt in g["helper"]:
            ts = TextSprite(w_, hf, fill=CREAM)
            pill_draws.append(dict(text=ts, x=x, base=y + 10 + HELPER_CAP, start=n_frame(tt), end=n_frame(g["end"])))
            x += ts.adv + sp

    # credibility card
    card = CARD
    c0, c1 = n_frame(card["t0"]), n_frame(card["t1"])
    num_size = cap_size("Antonio-Thin", 300)
    num_size = fit_size("Antonio-Thin", num_size, card["number"], 1000)
    card_num = TextSprite(card["number"], font("Antonio-Thin", num_size), fill=CREAM)
    card_script = TextSprite(card["script_top"], font("GreatVibes", 110), fill=GOLD)
    card_script2 = TextSprite(card["script_bottom"], font("GreatVibes", 84), fill=CREAM)
    card_pill = Pill(card["pill"])
    for tt in card_pill.tick_times(c0 + 12):
        SFX.append(("tick", tt))

    # CTA
    cta_line_t = n_frame(CTA["line_t"])
    cta_pill_t = n_frame(CTA["pill_t"])
    cta_arrow_t = n_frame(CTA["arrow_t"])
    cta_line = TextSprite(CTA["line"], font(F_HERO, cap_size(F_HERO, 64)))
    cta_pill = Pill(CTA["pill"])
    for tt in cta_pill.tick_times(cta_pill_t):
        SFX.append(("tick", tt))

    bokehs = {i: Bokeh(100 + i) for i in range(len(FLASHES))}
    flash_frames = [int(round(c * FPS)) for c in FLASHES]
    burn_frame = int(round(GOLD_BURN * FPS))
    for c in FLASHES:
        SFX.append(("whoosh", c))
    SFX.append(("riser", GOLD_BURN - 0.6))
    SFX.append(("burn", GOLD_BURN))
    neon_t = n_frame(PHRASES[0]["hero"][1])
    SFX.append(("neon", neon_t / FPS))
    small_neon_t = int(round(B1 * FPS)) + 9
    SFX.append(("neon_small", small_neon_t / FPS))
    if bubble is not None:
        SFX.append(("pop", B2 + 0.25))
    SFX.append(("music_lift", r2n(PILL_GROUPS[0]["t"])))
    SFX.append(("music_swell", B9))
    SFX.append(("music_resolve", r2n(25.06)))
    SFX.append(("end", END))
    json.dump(SFX, open(os.path.join(BUILD, "sfx_events.json"), "w"), indent=1)

    grade = ("curves=all='0/0.04 0.2/0.18 0.5/0.5 0.8/0.79 0.93/0.88 1/0.92',"
             "colorbalance=rs=0.02:bs=-0.03:rm=0.035:gm=-0.012:bm=-0.04:rh=0.025:gh=-0.008:bh=-0.03,"
             "eq=saturation=1.05,huesaturation=saturation=-0.05:colors=y,huesaturation=saturation=0.08:colors=m")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", grade + ",format=rgb24",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["cat"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) if os.environ.get("PREVIEW") else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-profile:v", "high", "-preset", "slow",
                            "-b:v", "18M", "-maxrate", "20M", "-bufsize", "36M", "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)

    keep = set()
    for a, b in SEGS:
        keep.update(range(a, b))
    raw_i = 0
    n = 0
    rng = np.random.default_rng(11)
    fsz = W * H * 3
    preview = set(int(v) for v in os.environ.get("PREVIEW", "").split(",") if v)
    if preview:
        os.makedirs(os.path.join(BUILD, "preview"), exist_ok=True)
    while n < NEW_FRAMES:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        ri = raw_i
        raw_i += 1
        if ri not in keep:
            continue
        if preview and n not in preview:
            n += 1
            continue
        src_img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        t = n / FPS
        shot = next(s for s in shots if s["t0"] - 1e-6 <= t < s["t1"] - 1e-6) if t < END else shots[-1]
        p = (t - shot["t0"]) / max(1e-6, shot["t1"] - shot["t0"])
        si = n - int(round(shot["t0"] * FPS))

        s, x0, y0 = framing(shot, p)
        if shot["name"] in slots:
            img = slots[shot["name"]].get(si, p)
            f = story_grade(img.astype(np.float32) / 255)
        else:
            img = apply_framing(src_img, s, x0, y0, sharpen=s >= 1.3)
            f = img.astype(np.float32) / 255
            if shot.get("story"):
                f = story_grade(f)
        a_roll_px = img if shot["name"] not in slots else None

        # behind-subject layers ------------------------------------------------
        behind = None
        if shot["name"].startswith("2") and couple is not None:
            behind = np.zeros((H, W, 3), np.float32)
            behind[:] = f
            over(behind, couple, 40, int(0.22 * H), 0.85)
        if c0 <= n < c1 and shot["frame"] == "card":
            behind = f.copy()
            age = n - c0
            top_base = 670
            nx = (W - card_num.adv) / 2
            draw_text(behind, card_num, nx, top_base, age, 1.0)
            draw_text(behind, card_script, nx + 10, top_base - card_num.cap - 6, age - 4, 1.0)
        if behind is not None and a_roll_px is not None:
            m = subject_mask(a_roll_px, f"n{n:04d}")[..., None]
            f = behind * (1 - m) + f * m

        if shot.get("mauve_flash") and 9 <= si + 7 < 11:  # first frames after the flash clears
            f = f * (1 - 0.4 + 0.4 * c01(MAUVE))

        over(f, WALNUT_GRAD, 0, 0)
        f *= VIGNETTE

        # story overlays -----------------------------------------------------
        if shot["name"].startswith("1 "):
            sz = NEON_BIG.shape
            screen(f, NEON_BIG, 560 - sz[1] / 2, 230 - 90 + 20 * math.sin(t * 2), neon_op(n - neon_t))
        if shot["name"].startswith("2"):
            sz = NEON_SMALL.shape
            screen(f, NEON_SMALL, 800 - sz[1] / 2, 560, neon_op(n - small_neon_t))
        if shot["name"].startswith("3"):
            for sp_ in SPARKLES:
                yy = sp_["y"] - sp_["vy"] * (t - shot["t0"])
                xx = sp_["x"] + sp_["sw"] * math.sin(t * 2 + sp_["ph"])
                tw = 0.55 + 0.45 * math.sin(t * 9 + sp_["ph"])
                sz = sp_["spr"].shape[0]
                screen(f, sp_["spr"], xx - sz / 2, yy - sz / 2, tw)
            if bubble is not None:
                age = si - 6
                if age >= 0:
                    sc = 0.0 if age < 0 else (1.12 * ease_out(age / 6) if age < 6 else 1.12 - 0.12 * smooth((age - 6) / 4))
                    if sc > 0.02:
                        b = cv2.resize(bubble, (int(bubble.shape[1] * sc), int(bubble.shape[0] * sc)))
                        over(f, b, 70 + (bubble.shape[1] - b.shape[1]) / 2, 240 + (bubble.shape[0] - b.shape[0]) / 2)
        if shot["name"].startswith("9"):
            fl = si / 18
            if fl < 1:
                screen(f, FLARE, 820 - 700, 260 - 700, (1 - smooth(fl)) * 0.95)
                f[:] = 1 - (1 - f) * (1 - c01(GOLD) * 0.55 * (1 - smooth(fl)))

        # captions ----------------------------------------------------------
        for ph in phrases:
            ph.draw(f, n)
        for pd in pill_draws:
            if pd["start"] <= n <= pd["end"] + 3:
                op = 1.0 if n <= pd["end"] else 1 - (n - pd["end"]) / 3
                if "pill" in pd:
                    pd["pill"].draw(f, W / 2, pd["top"], n - pd["start"], op, pd["slide"])
                else:
                    draw_text(f, pd["text"], pd["x"], pd["base"], n - pd["start"], op)
        if c0 <= n < c1 + 3:
            op = 1.0 if n < c1 else 1 - (n - c1 + 1) / 3
            age = n - c0
            x2 = (W - card_script2.adv) / 2
            draw_text(f, card_script2, x2, 1150, age - 8, op)
            card_pill.draw(f, W / 2, 1180, age - 12, op)
        if n >= cta_line_t:
            draw_text(f, cta_line, (W - cta_line.adv) / 2, int(0.64 * H), n - cta_line_t)
            cta_pill.draw(f, W / 2, int(0.64 * H) + 44, n - cta_pill_t)
            if n >= cta_arrow_t:
                k = (n - cta_arrow_t) / FPS
                bounce = abs(math.sin(math.pi * k / 0.26)) * 22 if k < 0.78 else 0
                op = min(1, (n - cta_arrow_t + 1) / 4)
                over(f, ARROW, W / 2 - 45, int(0.64 * H) + 44 + cta_pill.h + 22 + bounce, op)

        # transitions -------------------------------------------------------
        for i, cf in enumerate(flash_frames):
            k = flash_state(n, cf)
            if k is None:
                continue
            if k <= 4:
                f *= 1 + 0.23 * (k + 1) / 5
                np.clip(f, 0, 1, out=f)
                bokehs[i].draw(f, k, smooth((k + 1) / 5))
            elif k <= 8:
                fa = 1.0 if 5 <= k <= 8 else 0
                f[:] = f * (1 - fa) + c01(FLASH) * fa
            else:
                fa = 1 - (k - 8) / 6
                bokehs[i].draw(f, k, fa)
                f[:] = f * (1 - fa) + c01(FLASH) * fa
        # golden film burn into shot 6
        lk = n - burn_frame
        if -36 <= lk < 7:
            if lk < 0:
                q = (lk + 36) / 36
                env = smooth(q)
                for spr, x_s, x_e, yy, a in ((LEAK_A, -500, 700, -150, 0.9), (LEAK_B, -300, 900, 80, 0.8),
                                             (LEAK_C, 1100, 200, 300, 0.7)):
                    screen(f, spr, x_s + (x_e - x_s) * q - spr.shape[1] / 2 + 300, yy, a * env)
                if lk >= -8:
                    g = smooth((lk + 8) / 6)
                    f[:] = 1 - (1 - f) * (1 - c01(GOLD) * g)
                if lk >= -2:
                    f[:] = c01(FLASH)
            else:
                fa = 1 - lk / 7 if lk >= 2 else 1.0
                f[:] = f * (1 - fa) + c01(FLASH) * fa

        # grain ---------------------------------------------------------------
        g = rng.standard_normal((H // 2, W // 2)).astype(np.float32) * 0.03
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        f += g * 0.6
        out = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if preview:
            Image.fromarray(out).save(os.path.join(BUILD, "preview", f"{n:04d}.jpg"), quality=88)
        else:
            enc.stdin.write(out.tobytes())
        n += 1
        if n % 30 == 0:
            print(f"frame {n}/{NEW_FRAMES}  shot {shot['name']}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.wait()
    print("wrote", out_path, n, "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
