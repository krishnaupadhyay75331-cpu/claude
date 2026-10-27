# Reel renderer: A-roll grade + framing, B-roll, captions, overlays, transitions -> raw frames to ffmpeg
# usage: python3 render.py SRC.mov masks.npy out_video.mp4 [start_s end_s]   (times = output time, for previews)
import os
import sys
import json
import subprocess
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx
from gfx import W, H, FPS, C
import plan as P

SRC, MASKS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PREV = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else None
SW, SH = 756, 1344
SRC_FPS = 30
BROLL_DIR = os.environ.get("BROLL_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "broll"))

# ---------------- time mapping (source <-> output) ----------------
KEEP = P.KEEP  # list of [s,e] in source seconds
segs = []
o = 0.0
for s, e in KEEP:
    segs.append((s, e, o))
    o += e - s
AROLL_END = o
TOTAL = AROLL_END + P.FREEZE


def s2o(t):
    """source time -> output time (times inside a removed gap snap to the next kept start)."""
    for s, e, oo in segs:
        if t < s:
            return oo
        if t <= e:
            return oo + t - s
    return AROLL_END


def o2s(t):
    if t >= AROLL_END:
        return KEEP[-1][1] - 1 / SRC_FPS
    for s, e, oo in segs:
        if t < oo + (e - s):
            return s + (t - oo)
    return KEEP[-1][1]


# ---------------- face track from masks ----------------
masks = np.load(MASKS)
NM = len(masks)


def head_point(m):
    mh, mw = m.shape
    rows = np.where(m.max(1) > 128)[0]
    if len(rows) == 0:
        return 0.4, 0.38
    top = rows[0]
    band = m[top:top + int(mh * 0.16)] > 128
    ys, xs = np.nonzero(band)
    cx = xs.mean() / mw
    cy = (top + mh * 0.105) / mh
    return cx, cy


track = np.array([head_point(masks[i]) for i in range(NM)])
# smooth (centred moving average), but never across the reframe
reframe_i = int(P.REFRAME * SRC_FPS)
sm = track.copy()
for a, b in ((0, reframe_i), (reframe_i, NM)):
    seg = track[a:b]
    k = 31
    pad = np.pad(seg, ((k // 2, k // 2), (0, 0)), mode="edge")
    ker = np.ones(k) / k
    sm[a:b] = np.stack([np.convolve(pad[:, j], ker, mode="valid") for j in range(2)], 1)
track = sm


# ---------------- A-roll grade ----------------
def unsharp(img, sigma, amount):
    bl = cv2.GaussianBlur(img, (0, 0), sigma)
    return np.clip(img + (img - bl) * amount, 0, 1)


SHADOW_TINT = gfx.hexc("#2A0F33")
VIG = gfx.vignette_mask(0.28)
VIGCOL = C["plum"]
BOTG = gfx.bottom_gradient()


def grade_aroll(rgb_u8, mask_small):
    f = cv2.resize(rgb_u8, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    f = unsharp(f, 1.1, 0.45)
    m = cv2.resize(mask_small.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_LINEAR)
    m = np.clip((m - 0.35) / 0.4, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 3.0)[..., None]  # ~6 px feather
    # background: -0.8 EV, -40% sat, plum shadows, blur
    bg = f * 0.44
    lum = bg.mean(2, keepdims=True)
    bg = lum + (bg - lum) * 0.6
    sh = np.clip(1 - lum * 3.0, 0, 1)
    bg = bg * (1 - sh * 0.5) + (np.maximum(bg, SHADOW_TINT)) * sh * 0.5
    bg = cv2.GaussianBlur(bg, (0, 0), 8)
    # subject: recover highlights / whites, warm WB, vibrance, local contrast
    s = f.copy()
    l2 = s.max(2, keepdims=True)
    hl = np.clip((l2 - 0.6) / 0.4, 0, 1)
    s = s - (s - 0.6) * hl * 0.30
    s = np.minimum(s, 0.94 + (s - 0.94) * 0.5)
    s = s * np.array([1.025, 1.0, 0.975], np.float32)
    hsv = cv2.cvtColor(np.clip(s, 0, 1), cv2.COLOR_RGB2HSV)
    hue, sat = hsv[..., 0], hsv[..., 1]
    purple = ((hue > 255) & (hue < 320)).astype(np.float32)
    skin = ((hue > 8) & (hue < 45) & (sat < 0.7)).astype(np.float32)
    hsv[..., 1] = np.clip(sat * (1 - 0.05 * purple) * (1 + 0.12 * skin * (1 - sat)), 0, 1)
    s = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    s = unsharp(s, 12, 0.12)
    out = bg * (1 - m) + s * m
    return out


def finish(frame, gidx, grade_bottom=True):
    frame = frame * (1 - VIG) + VIGCOL * VIG
    if grade_bottom:
        frame = frame * (1 - BOTG) + VIGCOL * BOTG
    return frame


# ---------------- framing ----------------
def frame_affine(kind, prog, face, push=(1.02, 1.06), tilt=0.0):
    fx, fy = face[0] * W, face[1] * H
    if kind == "wide":
        z = push[0] + (push[1] - push[0]) * gfx.ease_in_out(prog)
        tx, ty, fx, fy = W / 2, H / 2, W / 2, H / 2
    elif kind == "med":
        z = 1.20 + 0.02 * prog
        tx, ty = W / 2, H * 0.31
    elif kind == "close":
        z = 1.35
        tx, ty = W * 0.36, H * 0.33
        tilt = 1.5
    elif kind == "tight":  # after the source reframe
        z = push[0] + (push[1] - push[0]) * gfx.ease_in_out(prog)
        tx, ty, fx, fy = W / 2, H / 2, W / 2, H / 2
    else:
        raise ValueError(kind)
    # keep crop window inside frame
    fx = np.clip(fx, tx / z, W - (W - tx) / z)
    fy = np.clip(fy, ty / z, H - (H - ty) / z)
    M = cv2.getRotationMatrix2D((fx, fy), tilt, z)
    M[0, 2] += tx - fx
    M[1, 2] += ty - fy
    return M


def apply_affine(img, M, extra_scale=1.0):
    if extra_scale != 1.0:
        E = cv2.getRotationMatrix2D((W / 2, H / 2), 0, extra_scale)
        M = np.vstack([E, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]])
        M = M[:2]
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------- B-roll ----------------
_broll_cache = {}
CUR = {"M": None, "extra": 1.0, "mask": None}


def to_out(pos, space):
    """normalised position -> output pixels; 'src' positions follow the current A-roll framing."""
    x, y = pos[0] * W, pos[1] * H
    if space == "src" and CUR["M"] is not None:
        M = np.vstack([CUR["M"], [0, 0, 1]])
        E = np.vstack([cv2.getRotationMatrix2D((W / 2, H / 2), 0, CUR["extra"]), [0, 0, 1]])
        v = E @ M @ np.array([x, y, 1.0])
        return v[0], v[1]
    return x, y


def broll_source(n):
    if n in _broll_cache:
        return _broll_cache[n]
    src = None
    for ext in (".jpg", ".png", ".jpeg", ".webp"):
        p = os.path.join(BROLL_DIR, f"b{n}{ext}")
        if os.path.exists(p):
            im = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
            ih, iw = im.shape[:2]
            sc = max(W / iw, H / ih) * 1.0
            im = cv2.resize(im, (int(iw * sc + 1), int(ih * sc + 1)), interpolation=cv2.INTER_LANCZOS4)
            y0 = (im.shape[0] - H) // 2
            x0 = (im.shape[1] - W) // 2
            src = im[y0:y0 + H, x0:x0 + W]
            # warm tungsten film-still grade
            src = np.clip(src * np.array([1.04, 1.0, 0.93], np.float32), 0, 1)
            break
    if src is None:
        src = placeholder_slate(n)
    _broll_cache[n] = src
    return src


def placeholder_slate(n):
    info = P.BROLL[n]
    r = np.random.default_rng(100 + n)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    base = gfx.hexc("#2A0F33") * (1 - yy) + C["plum"] * yy
    img = np.ones((H, W, 3), np.float32) * base
    # warm window light + bokeh, so the slate reads as an interior
    lay = np.zeros((H // 4, W // 4, 3), np.float32)
    for _ in range(26):
        col = C["goldl"] if r.random() < 0.65 else C["bokehpink"]
        cv2.circle(lay, (int(r.uniform(0, W / 4)), int(r.uniform(0, H / 4))), int(r.uniform(6, 22)), (col * r.uniform(0.15, 0.45)).tolist(), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 2.5)
    img = gfx.screen(img, cv2.resize(lay, (W, H)))
    img = gfx.screen(img, gfx.light_leak(0.3 * n, ("goldl", "rani"), seed=n, strength=0.22))
    # silhouette of the scene's character (abstract): head + shoulders
    sil = np.zeros((H, W), np.float32)
    cx, cy = int(W * info.get("cx", 0.5)), int(H * info.get("cy", 0.5))
    cv2.ellipse(sil, (cx, cy), (95, 120), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    cv2.ellipse(sil, (cx, cy + 330), (260, 220), 0, 180, 360, 1.0, -1, cv2.LINE_AA)
    cv2.rectangle(sil, (cx - 260, cy + 330), (cx + 260, H), 1.0, -1)
    sil = cv2.GaussianBlur(sil, (0, 0), 3)[..., None]
    img = img * (1 - sil * 0.55) + gfx.hexc("#3B1446") * sil * 0.55
    # label
    lab, _, _ = gfx.text_sprite(f"B-ROLL #{info['label']}", gfx.QS(46), fill=(247, 223, 160))
    gfx.over(img, lab, (W - lab.shape[1]) / 2, H * 0.115, 0.9)
    y = H * 0.115 + 70
    for line in info["desc"]:
        sp, _, _ = gfx.text_sprite(line, gfx.QS(30), fill=(230, 215, 235))
        gfx.over(img, sp, (W - sp.shape[1]) / 2, y, 0.75)
        y += 44
    return img


def broll_frame(n, prog, drift):
    src = broll_source(n)
    info = P.BROLL[n]
    z = 1.0 + 0.08 * gfx.ease_in_out(prog)
    zin = info.get("zoom_in_from")
    if zin:
        q = gfx.ease_out(min(1, prog * info.get("dur", 2.0) / 0.67))
        z = zin + (1.0 - zin) * q
    dx = drift * gfx.ease_in_out(prog)
    dy = info.get("drift_y", 0) * gfx.ease_in_out(prog)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    M[0, 2] += dx
    M[1, 2] += dy
    f = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return f


# ---------------- captions ----------------
SMALL = 32
HERO = 132
SHADOW = dict(color=C["plum"], alpha=0.45, blur=12)


class Stack:
    def __init__(self, d):
        self.d = d
        words = d["words"]
        self.hero_i = d["hero"]
        self.y = d.get("y", 0.72) * H
        self.t_words = [s2o(w[1][0] if isinstance(w[1], (list, tuple)) else w[1]) for w in words]
        self.t_end = s2o(d["end"]) if "end" in d else None
        hero_txt = words[self.hero_i][0]
        hero_t = words[self.hero_i][1]
        hero_parts = hero_txt.split(" ")
        hero_times = hero_t if isinstance(hero_t, (list, tuple)) else [hero_t] * len(hero_parts)
        hs = d.get("hero_size", HERO)
        f = gfx.QS(hs)
        while f.getlength(hero_txt) > 960 and hs > 60:
            hs -= 4
            f = gfx.QS(hs)
        col = (200, 16, 46) if d.get("red") else (255, 255, 255)
        hero_spr, hbase, hpad = gfx.text_sprite(hero_txt, f, fill=col, tracking=-int(hs * 0.01))
        hw = f.getlength(hero_txt) - int(hs * 0.01) * (len(hero_txt) - 1)
        xh = f.getbbox("x")
        xheight = xh[3] - xh[1]
        hx = (W - hw) / 2
        self.items = []  # (sprite, x, y, t, is_hero)
        self.items_by_idx = {}
        self.hero_extra = []
        if len(hero_parts) == 1:
            self.items_by_idx[self.hero_i] = (hero_spr, hx - hpad, self.y - hbase, True)
        else:
            # multi-word hero: each word is its own sprite, revealed on its own spoken time
            xx = hx
            for k, (part, pt) in enumerate(zip(hero_parts, hero_times)):
                spr, b, p = gfx.text_sprite(part, f, fill=col, tracking=-int(hs * 0.01))
                if k == 0:
                    self.items_by_idx[self.hero_i] = (spr, xx - p, self.y - b, True)
                else:
                    self.hero_extra.append((spr, xx - p, self.y - b, s2o(pt)))
                xx += f.getlength(part + " ")
        sf = gfx.QS(d.get("small_size", SMALL))
        lead = " ".join(w[0] for w in words[:self.hero_i])
        trail = " ".join(w[0] for w in words[self.hero_i + 1:])
        # lead words: above-right, baseline touching top of hero x-height
        if lead:
            lw = sf.getlength(lead)
            lx = min(hx + hw - lw, W - 60 - lw)
            lx = max(lx, hx + hw * 0.25)
            lx = min(lx, W - 60 - lw)
            ly_base = self.y - xheight - 6
            x = lx
            for i, w in enumerate(words[:self.hero_i]):
                spr, b, p = gfx.text_sprite(w[0], sf, alpha=0.9)
                self.items_by_idx[i] = (spr, x - p, ly_base - b, False)
                x += sf.getlength(w[0] + " ")
        if trail:
            tw = sf.getlength(trail)
            tx = max(60, hx + 6)
            ty_base = self.y + sf.size * 1.25
            x = tx
            for j, w in enumerate(words[self.hero_i + 1:]):
                i = self.hero_i + 1 + j
                spr, b, p = gfx.text_sprite(w[0], sf, alpha=0.9)
                self.items_by_idx[i] = (spr, x - p, ty_base - b, False)
                x += sf.getlength(w[0] + " ")
        for i in sorted(self.items_by_idx):
            spr, x, y, hero = self.items_by_idx[i]
            sh = gfx.shadow_of(spr, SHADOW["color"], SHADOW["alpha"], SHADOW["blur"])
            self.items.append((spr, sh, x, y, self.t_words[i], hero))
        for spr, x, y, tt in self.hero_extra:
            sh = gfx.shadow_of(spr, SHADOW["color"], SHADOW["alpha"], SHADOW["blur"])
            self.items.append((spr, sh, x, y, tt, True))

    def draw(self, frame, t, t_out):
        if t < self.t_words[0] - 0.01 or t > t_out + 1e-6:
            return
        out_p = gfx.clamp01((t - (t_out - 4 / FPS)) / (4 / FPS))
        for spr, sh, x, y, tw, hero in self.items:
            if t < tw - 1e-6:
                continue
            n = 8 if hero else 6
            p = gfx.ease_out((t - tw) * FPS / n)
            blur = 25 * (1 - p) / 2.5 + 20 * out_p / 2.5
            op = p * (1 - out_p)
            sc = (1.12 - 0.12 * p) if hero else 1.0
            rise = 8 * (1 - p)
            s1 = gfx.transform(spr, sc, blur)
            s2 = gfx.transform(sh, sc, blur)
            dx = (s1.shape[1] - spr.shape[1]) / 2
            dy = (s1.shape[0] - spr.shape[0]) / 2
            gfx.over(frame, s2, x - dx, y - dy + rise, op)
            gfx.over(frame, s1, x - dx, y - dy + rise, op)


# ---------------- build timeline objects ----------------
STACKS = [Stack(d) for d in P.STACKS]
for i, st in enumerate(STACKS):
    nxt = STACKS[i + 1].t_words[0] if i + 1 < len(STACKS) else TOTAL
    end = st.t_end if st.t_end is not None else (max(st.t_words) + 0.6)
    st.t_out = min(end, nxt - 1 / FPS)

SHOTS = []
for sh in P.SHOTS:
    d = dict(sh)
    d["o0"] = s2o(sh["t0"]) if sh.get("t0") is not None else 0.0
    d["o1"] = TOTAL if sh.get("t1") in (None, "END") else s2o(sh["t1"])
    SHOTS.append(d)
SHOTS[-1]["o1"] = TOTAL


def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s["o0"] - 1e-6 <= t < s["o1"]:
            return i, s
    return len(SHOTS) - 1, SHOTS[-1]


EV = []
for e in P.EVENTS:
    d = dict(e)
    d["o"] = s2o(e["t"]) + e.get("dt", 0.0)
    if "t_end" in e:
        d["oe"] = s2o(e["t_end"]) + e.get("dt_end", 0.0)
    EV.append(d)

# sprites
QM = gfx.neon_qmark(300)
STAR = gfx.star4(64)
HALO = gfx.halo_sprite(230)
PHONES = (gfx.phone_cutout("heart", 780), gfx.phone_cutout("camera", 780))
_cache = {}
CUR = {"M": None, "extra": 1.0, "mask": None}


def to_out(pos, space):
    """normalised position -> output pixels; 'src' positions follow the current A-roll framing."""
    x, y = pos[0] * W, pos[1] * H
    if space == "src" and CUR["M"] is not None:
        M = np.vstack([CUR["M"], [0, 0, 1]])
        E = np.vstack([cv2.getRotationMatrix2D((W / 2, H / 2), 0, CUR["extra"]), [0, 0, 1]])
        v = E @ M @ np.array([x, y, 1.0])
        return v[0], v[1]
    return x, y


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ---------------- overlays ----------------
def draw_events(frame, t, layer, shot):
    for e in EV:
        k = e["kind"]
        if e.get("layer", "top") != layer:
            continue
        lt = t - e["o"]
        dur = e.get("oe", e["o"] + e.get("dur", 2)) - e["o"]
        if lt < -0.5 or lt > dur + 0.6:
            continue
        fn = OVERLAYS.get(k)
        if fn:
            fn(frame, e, lt, dur, t, shot)


def ov_qmark(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    f = lt * FPS
    sc = gfx.overshoot(f / 10)
    flick = [1, 0.2, 1, 0.4, 1]
    op = flick[int(f)] if f < 5 else 1.0
    tail = dur - lt
    if tail < 0.3:
        op *= [0, 0.6, 0.1, 0.8, 0.2, 1, 1, 1, 1, 1][int(tail * FPS)]
    pos = e["pos_broll"] if shot["type"] == "broll" else e["pos_aroll"]
    bob = 10 * np.sin(2 * np.pi * lt / 1.5)
    s = gfx.transform(QM, max(0.01, sc * e.get("scale", 1.0)), 0)
    gfx.over(frame, s, pos[0] * W - s.shape[1] / 2, pos[1] * H - s.shape[0] / 2 + bob, op, mode="screen")


def ov_phones(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur + 0.2:
        return
    p = gfx.ease_out(lt * FPS / 12)
    out = gfx.clamp01((lt - dur) / 0.2)
    for side, spr in ((-1, PHONES[0]), (1, PHONES[1])):
        x_final = W * (0.02 if side < 0 else 0.98) - (spr.shape[1] if side > 0 else 0) + side * 40
        x_start = -spr.shape[1] if side < 0 else W
        x = x_start + (x_final - x_start) * p
        s = gfx.transform(spr, 1.0, 20 * out / 2.5, rot=-8 * side)
        gfx.over(frame, s, x, H * 0.26, (1 - out) * 0.92)


def ov_sparkle(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > 0.45:
        return
    p = lt / 0.4
    r = np.random.default_rng(e.get("seed", 1))
    cx, cy = to_out(e["pos"], e.get("space"))
    for k in range(8):
        ang = r.uniform(0, 2 * np.pi)
        dist = r.uniform(60, 190) * gfx.ease_out(p)
        sc = r.uniform(0.35, 0.9) * np.sin(np.pi * gfx.clamp01(p * 1.1 - r.uniform(0, 0.15)))
        if sc <= 0.02:
            continue
        s = gfx.transform(STAR, sc, 0, rot=r.uniform(0, 45))
        gfx.over(frame, s, cx + np.cos(ang) * dist - s.shape[1] / 2, cy + np.sin(ang) * dist - s.shape[0] / 2, 1.0, mode="screen")


def ov_pill(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    spr = cached(("pill", e["text"], e.get("size", 52)), lambda: gfx.pill_sprite(e["text"], e.get("size", 52)))
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    if "wipe_until" in e:
        p = gfx.clamp01(lt * FPS / max(1, (s2o(e["wipe_until"]) - e["o"]) * FPS))
    else:
        p = gfx.ease_out(lt * FPS / 8)
    w = int(spr.shape[1] * p)
    if w < 2:
        return
    x = (W - spr.shape[1]) / 2 + e.get("x", 0)
    y = e["y"] * H
    s = gfx.transform(spr, 1.0, 20 * out / 2.5)
    s = s.copy()
    s[:, w:, 3] = 0
    gfx.over(frame, s, x, y, 1 - out)
    if e.get("script"):
        sc = cached(("scr", e["script"], e.get("script_size", 72)), lambda: gfx.text_sprite(e["script"], gfx.SCRIPT(e.get("script_size", 72)), fill=e.get("script_rgb", (255, 255, 255)))[0])
        ps = gfx.ease_out((lt - 0.15) * FPS / 8)
        if ps > 0:
            s2 = gfx.transform(sc, 1.0, 20 * (1 - ps) / 2.5 + 20 * out / 2.5)
            gfx.over(frame, s2, (W - sc.shape[1]) / 2 + e.get("x", 0) + e.get("script_dx", -60), y - sc.shape[0] + 62, ps * (1 - out))


def ov_depth(frame, e, lt, dur, t, shot, layer_mask=None):
    if lt < 0 or lt > dur:
        return
    spr = cached(("depth", e["text"]), lambda: gfx.gradient_text_sprite(e["text"], gfx.THIN(300), [(0.25, C["orchid"]), (0.55, C["lilac"]), (0.85, np.ones(3, np.float32))], 0.85, tracking=4)[0])
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    p = gfx.ease_out(lt * FPS / 10)
    s = gfx.transform(spr, 1.0, 20 * out / 2.5).copy()
    s[:, int(s.shape[1] * p):, 3] = 0
    gfx.over(frame, s, (W - s.shape[1]) / 2, e.get("y", 0.12) * H, 1 - out)


def ov_depth_words(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    for i, (w, wt, x, y) in enumerate(e["words"]):
        p = gfx.ease_out((t - s2o(wt)) * FPS / 6)
        if p <= 0:
            continue
        spr = cached(("dw", w), lambda: gfx.text_sprite(w, gfx.QS(40), alpha=0.95)[0])
        s = gfx.transform(spr, 1.0, 25 * (1 - p) / 2.5 + 20 * out / 2.5)
        sh = gfx.shadow_of(s, C["plum"], 0.45, 12)
        gfx.over(frame, sh, x * W, y * H + 8 * (1 - p), p * (1 - out))
        gfx.over(frame, s, x * W, y * H + 8 * (1 - p), p * (1 - out))


def ov_bubble(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    bw, bh = 640, 430
    blobs = cached(("blobs", e.get("seed", 4)), lambda: gfx.blob_mask(bw, bh, e.get("seed", 4), 6))
    mem = cached(("mem",), lambda: memory_image(bw, bh))
    acc = np.zeros((bh, bw), np.float32)
    bleed = gfx.clamp01((lt - (dur - 0.4)) / 0.4)
    for i, b in enumerate(blobs):
        p = gfx.ease_out((lt - i * 3 / FPS) * FPS / 5)
        if p <= 0:
            continue
        bb = b
        if bleed > 0:
            bb = cv2.GaussianBlur(b, (0, 0), 1 + 22 * bleed)
            M = cv2.getRotationMatrix2D((bw / 2, bh / 2), 0, 1 + 0.25 * bleed)
            bb = cv2.warpAffine(bb, M, (bw, bh))
        acc = np.maximum(acc, bb * p)
    acc *= 1 - bleed
    spr = np.zeros((bh, bw, 4), np.float32)
    # watercolour rim: lilac / grey-purple wash around a photo core
    core = np.clip((acc - 0.35) / 0.4, 0, 1)
    rim = np.clip(acc - core, 0, 1)
    wash = C["lilac"] * 0.7 + gfx.hexc("#8C7A99") * 0.3
    spr[..., :3] = mem * core[..., None] + wash * (1 - core[..., None])
    spr[..., 3] = np.clip(acc * 0.95, 0, 1)
    gfx.over(frame, spr, e["pos"][0] * W - bw / 2, e["pos"][1] * H - bh / 2, 1.0)


def memory_image(bw, bh):
    p = os.path.join(BROLL_DIR, "memory.jpg")
    if os.path.exists(p):
        im = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        ih, iw = im.shape[:2]
        sc = max(bw / iw, bh / ih)
        im = cv2.resize(im, (int(iw * sc + 1), int(ih * sc + 1)))
        y0, x0 = (im.shape[0] - bh) // 2, (im.shape[1] - bw) // 2
        return im[y0:y0 + bh, x0:x0 + bw]
    yy = np.linspace(0, 1, bh, dtype=np.float32)[:, None, None]
    im = C["goldl"] * (1 - yy) + C["bokehpink"] * yy * 0.8 + 0.1
    im = np.ones((bh, bw, 3), np.float32) * im
    sp, _, _ = gfx.text_sprite("memory photo", gfx.QS(30), fill=(90, 40, 100))
    gfx.over(im, sp, (bw - sp.shape[1]) / 2, bh / 2 - 30, 0.7)
    return np.clip(im, 0, 1)


def ov_halo(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    p = gfx.ease_out(lt * FPS / 15)
    pulse = 1 + 0.03 * np.sin(2 * np.pi * max(0, lt - 0.5) / 2.0)
    s = gfx.transform(HALO, max(0.01, p * pulse), 0)
    gfx.over(frame, s, e["pos"][0] * W - s.shape[1] / 2, e["pos"][1] * H - s.shape[0] / 2, 0.95, mode="screen")


def ov_wall_leak(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    p = gfx.clamp01(lt / 0.4) * gfx.clamp01((dur - lt) / 0.2 + 0.3)
    lay = gfx.light_leak(t, ("goldl", "rani", "gold"), seed=9, strength=0.6 * p)
    frame[:] = gfx.screen(frame, lay)


def ov_tags(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    for i, (txt, y, anchor) in enumerate(e["tags"]):
        tl = lt - i * 6 / FPS
        if tl < 0:
            continue
        spr = cached(("tag", txt), lambda: gfx.callout_tag(txt))
        p = gfx.ease_out(tl * FPS / 8)
        x_final = e.get("x", 0.06) * W
        x = -spr.shape[1] + (x_final + spr.shape[1]) * p
        mb = 18 * (1 - p)
        s = spr
        if mb > 1:
            k = int(mb) | 1
            s = cv2.blur(spr, (k * 2 + 1, 1))
        s = gfx.transform(s, 1.0, 20 * out / 2.5)
        gfx.over(frame, s, x, y * H, 1 - out)
        # leader line draws on after the tag lands
        lp = gfx.clamp01((tl - 8 / FPS) * FPS / 6)
        if lp > 0:
            x0 = x_final + spr.shape[1] * 0.55
            y0 = y * H + spr.shape[0] / 2
            x1 = x0 + (anchor[0] * W - x0) * lp
            y1 = y0 + (anchor[1] * H - y0) * lp
            ov = frame.copy()
            cv2.line(ov, (int(x0), int(y0)), (int(x1), int(y1)), (1, 1, 1), 3, cv2.LINE_AA)
            if lp >= 1:
                cv2.circle(ov, (int(x1), int(y1)), 7, (1, 1, 1), -1, cv2.LINE_AA)
            frame[:] = frame * (1 - 0.9 * (1 - out)) + ov * 0.9 * (1 - out)


def ov_stat(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    spr = cached(("stat", e["text"]), lambda: gfx.text_sprite(e["text"], gfx.COND(e.get("size", 330)), tracking=2)[0])
    if spr.shape[1] > W - 120:
        spr = cached(("stat_s", e["text"]), lambda: gfx.transform(spr, (W - 120) / spr.shape[1], 0))
    p = gfx.ease_out(lt * FPS / 10)
    s = gfx.transform(spr, 1.0, 20 * out / 2.5).copy()
    s[:, int(s.shape[1] * p):, 3] = 0
    y = e.get("y", 0.075) * H
    sh = gfx.shadow_of(s, C["plum"], 0.45, 12)
    gfx.over(frame, sh, (W - s.shape[1]) / 2, y, 1 - out)
    gfx.over(frame, s, (W - s.shape[1]) / 2, y, 1 - out)
    if e.get("script"):
        sc = cached(("sscr", e["script"]), lambda: gfx.text_sprite(e["script"], gfx.SCRIPT(84), fill=(247, 223, 160))[0])
        ps = gfx.ease_out((lt - 0.2) * FPS / 8)
        if ps > 0:
            s2 = gfx.transform(sc, 1.0, 25 * (1 - ps) / 2.5 + 20 * out / 2.5)
            gfx.over(frame, s2, (W - sc.shape[1]) / 2, y - sc.shape[0] * 0.55 + 40, ps * (1 - out))


def ov_cta(frame, e, lt, dur, t, shot):
    if lt < 0:
        return
    words = e["words"]
    f = gfx.QS(e.get("size", 80))
    line = " ".join(words)
    tot = f.getlength(line)
    if tot > W - 120:
        f = gfx.QS(int(e.get("size", 80) * (W - 120) / tot))
        tot = f.getlength(line)
    x = (W - tot) / 2
    y = e["y"] * H
    for i, w in enumerate(words):
        p = gfx.ease_out((lt - i * e.get("gap", 0.18)) * FPS / 6)
        ww = f.getlength(w + " ")
        if p > 0:
            spr, b, pad = cached(("cta", w, f.size), lambda: gfx.text_sprite(w, f))
            s = gfx.transform(spr, 1.0, 25 * (1 - p) / 2.5)
            sh = gfx.shadow_of(s, C["plum"], 0.5, 12)
            gfx.over(frame, sh, x - pad, y - b + 8 * (1 - p), p)
            gfx.over(frame, s, x - pad, y - b + 8 * (1 - p), p)
        x += ww


def ov_words(frame, e, lt, dur, t, shot):
    if lt < 0 or lt > dur:
        return
    words = e["words"]  # [(text, src_time)]
    style = e.get("style", "script")
    size = e.get("size", 90)
    f = gfx.SCRIPT(size) if style == "script" else gfx.QS(size)
    rgb = tuple(e.get("rgb", (255, 255, 255)))
    line = " ".join(w for w, _ in words)
    tot = f.getlength(line)
    if tot > W - 140:
        size = int(size * (W - 140) / tot)
        f = gfx.SCRIPT(size) if style == "script" else gfx.QS(size)
        tot = f.getlength(line)
    x = (W - tot) / 2
    y = e["y"] * H
    out = gfx.clamp01((lt - (dur - 4 / FPS)) / (4 / FPS))
    for w, wt in words:
        p = gfx.ease_out((t - s2o(wt)) * FPS / 6)
        if p > 0:
            spr, b, pad = cached(("w", w, style, size, rgb), lambda: gfx.text_sprite(w, f, fill=rgb))
            s1 = gfx.transform(spr, 1.0, 25 * (1 - p) / 2.5 + 20 * out / 2.5)
            sh = gfx.shadow_of(s1, C["plum"], 0.5, 12)
            gfx.over(frame, sh, x - pad, y - b + 8 * (1 - p), p * (1 - out))
            gfx.over(frame, s1, x - pad, y - b + 8 * (1 - p), p * (1 - out))
        x += f.getlength(w + " ")


OVERLAYS = dict(qmark=ov_qmark, phones=ov_phones, sparkle=ov_sparkle, pill=ov_pill, depth=ov_depth,
                depth_words=ov_depth_words, bubble=ov_bubble, halo=ov_halo, wall_leak=ov_wall_leak,
                tags=ov_tags, stat=ov_stat, cta=ov_cta, words=ov_words)


# ---------------- transitions (applied around shot boundaries) ----------------
def apply_transitions(frame, t):
    for i, s in enumerate(SHOTS[:-1]):
        tr = s.get("out", "hard")
        cut = s["o1"]
        d = (t - cut) * FPS  # frames relative to cut (negative = before)
        if d < -10 or d > 22:
            continue
        if tr == "white":
            if -3 <= d < 2:
                frame[:] = gfx.paper_white()
            elif 2 <= d < 10:
                p = (d - 2) / 8
                al = gfx.haze_layer(p)
                hz = C["haze"]
                frame[:] = frame * (1 - al) + (gfx.paper_white() * (1 - p) + hz * p) * al
        elif tr == "cream":
            if 0 <= d < 2:
                frame[:] = C["cream"]
        elif tr == "bokeh":
            if -4 <= d < 0:
                frame[:] = gfx.screen(frame, gfx.bokeh_layer(i, (d + 4) / 4) * 1.4)
            elif 0 <= d < 2:
                frame[:] = gfx.flash(frame, np.ones(3, np.float32), 0.95)
            elif 2 <= d < 8:
                p = (d - 2) / 6
                frame[:] = gfx.screen(frame, gfx.bokeh_layer(i, 1.0) * (1 - p))
                frame[:] = gfx.flash(frame, np.ones(3, np.float32), 0.6 * (1 - p))
        elif tr in ("burn", "pinkleak"):
            pal = ("gold", "goldl", "rani") if tr == "burn" else ("rani", "neon", "bokehpink")
            if -9 <= d < 9:
                p = (d + 9) / 18
                peak = 1 - abs(d) / 9
                lay = gfx.light_leak(t, pal, seed=30 + i, strength=0.5 + 1.6 * peak, sweep=p)
                frame[:] = gfx.screen(frame, lay)
                if abs(d) < 2.5:
                    frame[:] = gfx.flash(frame, C["bokehpink"] * 0.4 + 0.6 if tr == "pinkleak" else np.array([1, 0.97, 0.9], np.float32), 0.85 - abs(d) * 0.2)
        elif tr == "flare":
            if -8 <= d < 0:
                p = (d + 8) / 8
                yy, xx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32)
                g = np.exp(-(((xx - W / 8) ** 2 + (yy - H / 8) ** 2) / (2 * (10 + 260 * p ** 2) ** 2)))
                lay = cv2.resize(g, (W, H))[..., None] * (np.array([1, 0.93, 0.78], np.float32)) * (0.5 + 1.5 * p)
                frame[:] = gfx.screen(frame, lay)
            elif 0 <= d < 5:
                frame[:] = gfx.flash(frame, np.array([1, 0.97, 0.9], np.float32), 1 - d / 5)
        elif tr == "whip":
            if -4 <= d < 0:
                frame[:] = gfx.zoom_blur(frame, 0.12 * (d + 5))
            elif 0 <= d < 3:
                frame[:] = gfx.zoom_blur(frame, 0.3 * (1 - d / 3))
    return frame


# ---------------- main loop ----------------
def main():
    n_frames = int(round(TOTAL * FPS))
    f0, f1 = 0, n_frames
    if PREV:
        f0, f1 = int(PREV[0] * FPS), min(n_frames, int(PREV[1] * FPS))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    src_idx = -1
    src_frame = None
    graded = {}
    for fi in range(f0, f1):
        t = fi / FPS
        st = o2s(t)
        need = min(NM - 1, int(round(st * SRC_FPS)))
        if t >= AROLL_END:
            need = min(need, NM - 1)
        while src_idx < need:
            b = dec.stdout.read(SW * SH * 3)
            if len(b) < SW * SH * 3:
                break
            src_idx += 1
            src_frame = b
        si, shot = shot_at(t)
        prog = gfx.clamp01((t - shot["o0"]) / max(1e-3, shot["o1"] - shot["o0"]))
        if shot["type"] == "aroll":
            key = src_idx
            if key not in graded:
                graded.clear()
                rgb = np.frombuffer(src_frame, np.uint8).reshape(SH, SW, 3)
                graded[key] = grade_aroll(rgb, masks[min(src_idx, NM - 1)])
            base = graded[key]
            face = track[min(src_idx, NM - 1)]
            M = frame_affine(shot["frame"], prog, face, push=tuple(shot.get("push", (1.02, 1.06))))
            extra = 1.0
            # freeze push-in
            if t >= AROLL_END:
                extra *= 1.0 + 0.04 * gfx.ease_in_out((t - AROLL_END) / P.FREEZE)
            # whip entrance zoom-out 180% -> 100%
            if shot.get("enter") == "zoomout":
                q = gfx.ease_out((t - shot["o0"]) * FPS / 20)
                extra *= 1.8 - 0.8 * q
            # micro-shake bump on hero words
            for (bt, bdur) in P.BUMPS_O:
                lf = (t - bt) * FPS
                if 0 <= lf < bdur:
                    extra *= 1 + 0.03 * np.sin(np.pi * lf / bdur)
            frame = apply_affine(base, M, extra)
            CUR["M"] = M
            CUR["extra"] = extra
            CUR["mask"] = None
            if any(e.get("layer") == "under" and -0.1 <= t - e["o"] <= e.get("oe", e["o"] + e.get("dur", 2)) - e["o"] + 0.3 for e in EV):
                mk = cv2.resize(masks[min(src_idx, NM - 1)].astype(np.float32) / 255, (W, H))
                mk = cv2.GaussianBlur(np.clip((mk - 0.35) / 0.4, 0, 1), (0, 0), 3)
                CUR["mask"] = apply_affine(mk, M, extra)[..., None]
            if shot.get("enter") == "haze":
                lf = (t - shot["o0"]) * FPS
                if lf < 8:
                    bl = cv2.GaussianBlur(frame, (0, 0), 14 * (1 - lf / 8) + 0.1)
                    frame = gfx.screen(bl, C["haze"] * 0.35 * (1 - lf / 8))
            frame = finish(frame, fi)
        else:
            CUR["M"] = None
            CUR["mask"] = None
            frame = broll_frame(shot["n"], prog, shot.get("drift", 0))
            if shot.get("enter") == "zoomout":
                q = gfx.ease_out((t - shot["o0"]) * FPS / 20)
                Mz = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1.8 - 0.8 * q)
                frame = cv2.warpAffine(frame, Mz, (W, H), borderMode=cv2.BORDER_REFLECT)
            frame = finish(frame, fi, grade_bottom=shot.get("bottom", True))
        frame = np.ascontiguousarray(frame, dtype=np.float32)
        # tint pops on the first frames of marked shots
        if shot.get("pop"):
            lf = (t - shot["o0"]) * FPS
            if 0 <= lf < 3:
                col = C["tintp"] if shot["pop"] == "purple" else C["rani"]
                frame = frame * (1 - (0.6 if shot["pop"] == "purple" else 0.55)) + (gfx.screen(frame, col[None, None] * 0.8)) * (0.6 if shot["pop"] == "purple" else 0.55)
        for (pt, pc) in P.POPS_O:
            lf = (t - pt) * FPS
            if 0 <= lf < 3:
                col = C["tintp"] if pc == "purple" else C["rani"]
                frame = frame * 0.45 + gfx.screen(frame, col[None, None] * 0.8) * 0.55
        if CUR.get("mask") is not None and shot["type"] == "aroll":
            under = frame.copy()
            draw_events(under, t, "under", shot)
            frame = under * (1 - CUR["mask"]) + frame * CUR["mask"]
        else:
            draw_events(frame, t, "under", shot)
        for i, stck in enumerate(STACKS):
            stck.draw(frame, t, stck.t_out)
        draw_events(frame, t, "top", shot)
        frame = apply_transitions(frame, t)
        if t > TOTAL - 6 / FPS:
            frame = frame * max(0.0, (TOTAL - t) / (6 / FPS))
        frame = gfx.grain(frame, fi, 0.08)
        enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{f1}", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.kill()


P.BUMPS_O = [(s2o(b), 6) for b in P.BUMPS]
P.POPS_O = [(s2o(b) + dt, c) for b, c, dt in P.POPS]

if __name__ == "__main__":
    json.dump({"aroll_end": AROLL_END, "total": TOTAL, "segs": segs}, open(OUT + ".timing.json", "w"))
    main()
