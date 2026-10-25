"""Krishna Shringar Karwa Chauth reel: edit decision list, effects and frame renderer."""
import numpy as np, cv2, math, json, sys, os, subprocess
from gfx import *

V = '/root/.claude/uploads/72bc255f-5202-5cbe-bb9b-e101156314d2/a223cf04-copy_E9820242-9872-4BF7-A635-D83D49897C5E-compressed.mov'
WORK = f'{S}/work'
SRC_W, SRC_H = 864, 1536
BASE_K = W / SRC_W  # 1.25
END_CARD = 4.5
BRAND = 'KRISHNA SHRINGAR'
HANDLE = os.environ.get('HANDLE', '')  # e.g. "@krishnashringar" once supplied; empty -> shop name
WM_TEXT = HANDLE if HANDLE else BRAND

# ---------------------------------------------------------------- EDL
# name, src_in, src_out, framing scale (1.0 wide / 1.2 mid / 1.35 close)
PIECES = [
    ('A1', 0.15, 1.66, 1.06), ('A2', 1.66, 3.06, 1.25), ('A3', 3.06, 4.66, 1.10),
    ('B', 4.80, 6.22, 1.25),
    ('C1', 7.50, 8.35, 1.06), ('C2', 8.50, 10.92, 1.15),
    ('D1', 17.28, 19.25, 1.0), ('D2', 19.43, 19.97, 1.25), ('D3', 20.10, 21.28, 1.35),
    ('E1', 21.80, 23.27, 1.0), ('E2', 23.41, 25.10, 1.2),
    ('F1', 25.30, 25.78, 1.35), ('F2a', 25.91, 27.40, 1.0), ('F2b', 27.40, 28.72, 1.2),
    ('G1', 29.00, 30.10, 1.0), ('G2', 30.29, 31.38, 1.25), ('G3', 31.59, 33.30, 1.12), ('G4', 33.44, 34.52, 1.0),
    ('H1a', 34.75, 35.40, 1.2), ('H1b', 35.40, 37.25, 1.32), ('H2', 37.42, 38.32, 1.0),
    ('I1', 38.52, 39.12, 1.2), ('I2a', 39.28, 40.45, 1.35), ('I2b', 40.45, 42.20, 1.15),
]
STAB_END = 330  # handheld section (src frames)


class Piece:
    pass


def build_pieces():
    out, o = [], 0
    for name, a, b, s in PIECES:
        p = Piece(); p.name, p.s = name, s
        p.fin, p.fout = int(round(a * FPS)), int(round(b * FPS))
        p.n = p.fout - p.fin
        p.o0 = o; p.o1 = o + p.n; o += p.n
        p.a, p.b = a, b
        out.append(p)
    return out, o


PCS, TALK_FRAMES = build_pieces()
TOTAL_FRAMES = TALK_FRAMES + int(END_CARD * FPS)
PIECE_BY = {p.name: p for p in PCS}


def T(src_t):
    """source time -> output time (snaps forward if inside a removed gap)."""
    f = src_t * FPS
    for p in PCS:
        if f < p.fin:
            return p.o0 / FPS
        if p.fin <= f < p.fout:
            return (p.o0 + (f - p.fin)) / FPS
    return TALK_FRAMES / FPS


def cut_time(name):  # output time where piece `name` starts
    return PIECE_BY[name].o0 / FPS


# ---------------------------------------------------------------- source data
FR = np.load(f'{WORK}/frames.npy', mmap_mode='r')
MS = np.load(f'{WORK}/masks.npy', mmap_mode='r')
HEAD = np.load(f'{WORK}/head.npy')
STAB = np.load(f'{WORK}/stab.npy')


def piece_anchor_src(p):
    hs = HEAD[p.fin:p.fout]
    return float(np.median(hs[:, 0])), float(np.median(hs[:, 1]))


def frame_affine(p, j):
    """2x3 affine from source pixels to output pixels for local frame j of piece p."""
    cx, top = piece_anchor_src(p)
    prog = j / max(p.n - 1, 1)
    k = BASE_K * p.s
    k *= (1.02 - 0.02 * prog) if p.s >= 1.3 else (1 + 0.025 * prog)
    eye = top + 95
    tx = 540 - k * cx; ty = 768 - k * eye
    tx = min(0, max(W - k * SRC_W, tx)); ty = min(0, max(H - k * SRC_H, ty))
    A = np.array([[k, 0, tx], [0, k, ty]], np.float32)
    fi = p.fin + j
    if fi < STAB_END:
        dx, dy, da = STAB[min(fi, len(STAB) - 1)]
        dx = float(np.clip(dx, -38, 38)); dy = float(np.clip(dy, -38, 38)); da = float(np.clip(da, -0.03, 0.03))
        c, s = math.cos(da), math.sin(da)
        cxs, cys = SRC_W / 2, SRC_H / 2
        R = np.array([[c, -s, cxs - c * cxs + s * cys + dx], [s, c, cys - s * cxs - c * cys + dy], [0, 0, 1]], np.float32)
        A = (np.vstack([A, [0, 0, 1]]) @ R)[:2]
        # keep the frame covered after stabilisation
        A = cover(A)
    return A


def cover(A):
    corners = np.array([[0, 0, 1], [SRC_W, 0, 1], [0, SRC_H, 1], [SRC_W, SRC_H, 1]], np.float32) @ A.T
    sx = 1.0
    for _ in range(3):
        c = corners
        left = max(c[0, 0], c[2, 0]); right = min(c[1, 0], c[3, 0])
        top = max(c[0, 1], c[1, 1]); bot = min(c[2, 1], c[3, 1])
        if left <= 0 and top <= 0 and right >= W and bot >= H:
            break
        if right - left < W or bot - top < H:
            f = max(W / (right - left), H / (bot - top)) * 1.01
            A = np.vstack([[f, 0, (1 - f) * 540], [0, f, (1 - f) * 960]]) @ np.vstack([A, [0, 0, 1]])
            A = A.astype(np.float32)
        c = np.array([[0, 0, 1], [SRC_W, 0, 1], [0, SRC_H, 1], [SRC_W, SRC_H, 1]], np.float32) @ A.T
        left = max(c[0, 0], c[2, 0]); right = min(c[1, 0], c[3, 0])
        top = max(c[0, 1], c[1, 1]); bot = min(c[2, 1], c[3, 1])
        if left > 0: A[0, 2] -= left
        if right < W: A[0, 2] += W - right
        if top > 0: A[1, 2] -= top
        if bot < H: A[1, 2] += H - bot
        corners = np.array([[0, 0, 1], [SRC_W, 0, 1], [0, SRC_H, 1], [SRC_W, SRC_H, 1]], np.float32) @ A.T
    return A


def apply_pt(A, x, y):
    return A[0, 0] * x + A[0, 1] * y + A[0, 2], A[1, 0] * x + A[1, 1] * y + A[1, 2]


ANCH = {}
def anchor(p):
    """head anchor in output space for the first frame of a piece: (hx, htop, hs)."""
    if p.name not in ANCH:
        A = frame_affine(p, 0)
        cx, top = piece_anchor_src(p)
        hx, ht = apply_pt(A, cx, top)
        ANCH[p.name] = (hx, ht, 172 * A[0, 0])
    return ANCH[p.name]


# ---------------------------------------------------------------- static assets
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = 1 - 0.18 * np.clip(((((XX - 540) / 620) ** 2 + ((YY - 900) / 1100) ** 2) ** 0.5 - 0.55) / 0.6, 0, 1) ** 1.6
VIGNETTE = VIGNETTE[..., None].astype(np.float32)
SRC_RAMP = np.clip((1010 - np.arange(SRC_H, dtype=np.float32)) / 140, 0, 1)[:, None] * np.ones((1, SRC_W), np.float32)


def load_icon(name, size):
    im = cv2.imread(f'{WORK}/sprites/icon_{name}.png', cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    sc = size / 300.0
    im = cv2.resize(im, (int(420 * sc), int(420 * sc)), interpolation=cv2.INTER_AREA)
    spr = from_rgba8(im)
    spr.cx = 210 * sc; spr.cy = 200 * sc
    return spr


ICONS = {n: load_icon(n, 150) for n in ['diya', 'gift', 'moon', 'coin']}
ICON_COIN_BIG = load_icon('coin', 130)
ICON_PIN = load_icon('pin', 104)
STAR = star_sprite(26)
STAR_S = star_sprite(18)


def src_crop(fi, x0, y0, x1, y1, out_w, out_h):
    im = np.asarray(FR[fi][y0:y1, x0:x1], np.float32) / 255
    return cv2.resize(im, (out_w, out_h), interpolation=cv2.INTER_CUBIC)


def card_sprite(img, border=8, radius=16, shadow=True):
    h, w = img.shape[:2]
    bw, bh = w + 2 * border, h + 2 * border
    pad = 30
    m = rounded_rect_mask(bw, bh, radius)
    inner = rounded_rect_mask(w, h, max(radius - border, 4))
    rgba = np.zeros((bh + pad * 2, bw + pad * 2, 4), np.float32)
    if shadow:
        sh = np.zeros((bh + pad * 2, bw + pad * 2), np.float32); sh[pad:pad + bh, pad:pad + bw] = m
        sh = cv2.GaussianBlur(sh, (0, 0), 10); sh = np.roll(sh, 8, 0) * 0.45
        rgba[..., :3] = hexc('#2A0508') * sh[..., None]; rgba[..., 3] = sh
    reg = rgba[pad:pad + bh, pad:pad + bw]
    col = np.empty((bh, bw, 3), np.float32); col[:] = hexc(WARM)
    col[border:border + h, border:border + w] = img * inner[..., None] + hexc(WARM) * (1 - inner[..., None])
    reg[..., :3] = col * m[..., None] + reg[..., :3] * (1 - m[..., None])
    reg[..., 3] = m + reg[..., 3] * (1 - m)
    return Sprite(rgba)


# ---------------------------------------------------------------- elements
class El:
    layer = 'front'
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
    def active(self, t): return self.t0 - 1e-6 <= t < self.t1
    def draw(self, img, t, ctx): pass


def fr_since(t, t0): return (t - t0) * FPS


class WordLine:
    """Words of one caption line, each popping on its spoken time (Effect B)."""
    def __init__(self, words, fname='cap', size=56, fill=WARM, typed=False, gap=0.28):
        self.words, self.fname, self.size, self.fill, self.typed = words, fname, size, fill, typed
        self.spr = [text_sprite(w, fname, size, fill) for w, _ in words]
        self.space = font(fname, size).getlength(' ') * 1.0
        self.width = sum(s.iw for s in self.spr) + self.space * (len(self.spr) - 1)
        self.height = max(s.ih for s in self.spr)

    def draw(self, img, t, x, y_mid, t_end=None, exit_cut=True, alpha=1.0):
        """x = left edge, y_mid = vertical centre."""
        fe = None if t_end is None else fr_since(t, t_end - 3 / FPS)
        ex_a, ex_dy = 1.0, 0.0
        if fe is not None and fe >= 0 and not exit_cut:
            ex_a = clamp01(1 - fe / 3); ex_dy = -10 * clamp01(fe / 3)
        if self.typed:
            full = ' '.join(w for w, _ in self.words)
            f0 = fr_since(t, self.words[0][1])
            if f0 < 0: return
            nch = min(len(full), int(f0) + 1)
            spr = text_sprite(full[:nch], self.fname, self.size, self.fill)
            place(img, spr, x + spr.cx - spr.ink[0], y_mid + ex_dy, alpha=ex_a * alpha)
            return
        cx = x
        for (w, tw), spr in zip(self.words, self.spr):
            f = fr_since(t, tw)
            if f >= 0:
                sc = pop_scale(f, 5)
                a = clamp01(f / 3) * ex_a * alpha
                bl = 8 * (1 - clamp01(f / 5))
                place(img, spr, cx + spr.iw / 2, y_mid + ex_dy, scale=sc, alpha=a, blur=bl)
            cx += spr.iw + self.space


def fit_line(words, fname, size, maxw, **kw):
    while True:
        wl = WordLine(words, fname, size, **kw)
        if wl.width <= maxw or size <= 38:
            return wl
        size -= 4


class Hero(El):
    """Big gradient keyword. mode: 'slide' (from left, Effect A), 'pop', 'reveal' (letters from right)."""
    def __init__(self, t0, t1, lines, grad, layer='back', mode='slide', size=165, piece_anchor=True, exit_cut=True,
                 y_off=0.45, fname='hero', tracking=-0.02):
        super().__init__(t0, t1)
        self.layer, self.mode, self.exit_cut, self.y_off = layer, mode, exit_cut, y_off
        self.lines = lines if isinstance(lines, list) else [lines]
        maxw = W - 128
        while True:
            self.spr = [text_sprite(l, fname, size, grad, tracking=tracking) for l in self.lines]
            if max(s.iw for s in self.spr) <= maxw or size < 70: break
            size -= 6
        self.size, self.grad, self.fname, self.tracking = size, grad, fname, tracking
        self.lh = size * 0.98
        self.bw = max(s.iw for s in self.spr); self.bh = self.lh * (len(self.lines) - 1) + self.spr[0].ih

    def box(self, ctx):
        hx, ht, hs = ctx['anchor']
        cy = ht + self.y_off * hs
        cx = min(max(hx, self.bw / 2 + 64), W - 64 - self.bw / 2)
        return cx, cy

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0)
        cx, cy = self.box(ctx)
        fe = fr_since(t, self.t1 - 4 / FPS)
        a_exit, dx_exit = 1.0, 0.0
        if not self.exit_cut and fe >= 0:
            a_exit = clamp01(1 - fe / 4); dx_exit = 20 * clamp01(fe / 4)
        drift = 1.3 * f
        for i, spr in enumerate(self.spr):
            ly = cy - self.bh / 2 + spr.ih / 2 + i * self.lh
            if self.mode == 'slide':
                ff = f - i * 2
                if ff < 0: continue
                p = ff / 7
                off = -300 * (1 - ease_out(p, 4))
                vel = 300 * 4 * (1 - clamp01(p)) ** 3 / 7
                sc = 1.0 + 0.03 * (1 - ease_in_out((ff - 7) / 4)) if ff >= 7 else 1.03
                place(img, spr, cx + off + drift + dx_exit, ly, scale=sc, alpha=clamp01(ff / 2) * a_exit, mblur=(min(vel * 0.5, 60), 0))
            elif self.mode == 'pop':
                ff = f - i * 2
                if ff < 0: continue
                place(img, spr, cx + dx_exit + drift * 0.4, ly, scale=pop_scale(ff, 6), alpha=clamp01(ff / 3) * a_exit, blur=8 * (1 - clamp01(ff / 5)))
            elif self.mode == 'reveal':
                self._reveal(img, spr, self.lines[i], cx + drift * 0.6, ly, f - i * 6, a_exit)

    def _reveal(self, img, spr, text, cx, cy, f, a_exit):
        # letters revealed from the right, 1 letter / 2 frames, each fading in with 6px blur
        if f < 0: return
        n = len(text)
        fnt = font(self.fname, self.size)
        left = cx - spr.iw / 2
        xs = []
        for i in range(n):
            xs.append(fnt.getlength(text[:i]) + i * self.tracking * self.size)
        for i in range(n - 1, -1, -1):
            if text[i] == ' ': continue
            k = (n - 1 - i)
            lf = f - k * 2
            if lf < 0: continue
            ls = text_sprite(text[i], self.fname, self.size, self.grad, tracking=0)
            x = left - fnt.getbbox(text[0])[0] + xs[i] + fnt.getbbox(text[i])[0] + ls.iw / 2
            place(img, ls, x, cy, alpha=clamp01(lf / 4) * a_exit, blur=6 * (1 - clamp01(lf / 4)))


class Stack(El):
    """Mixed-size caption stack: small lead above-left, hero, small trail below-right.
    kind='head': hero behind the head (handled by a separate Hero element), lead/trail beside the face.
    kind='chest': everything in front, under the chin."""
    def __init__(self, t0, t1, lead=None, trail=None, hero=None, kind='head', exit_cut=True, trail_typed=True,
                 lead_size=54, trail_size=52, lead_fill=WARM, trail_fill=WARM, chest_dy=40):
        super().__init__(t0, t1)
        self.kind, self.exit_cut, self.hero, self.chest_dy = kind, exit_cut, hero, chest_dy
        self.lead = fit_line(lead, 'cap', lead_size, 560, fill=lead_fill) if lead else None
        self.trail = fit_line(trail, 'cap', trail_size, 470, fill=trail_fill, typed=trail_typed) if trail else None

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        te = None if self.exit_cut else self.t1
        if self.kind == 'head' and self.hero is not None:
            hcx, hcy = self.hero.box(ctx)
            top = hcy - self.hero.bh / 2; bot = hcy + self.hero.bh / 2
            left = hcx - self.hero.bw / 2; right = hcx + self.hero.bw / 2
            face_l = hx - 0.48 * hs; face_r = hx + 0.48 * hs
            if self.lead:
                x = max(64, left + 6)
                y = top - self.lead.height / 2 - 14
                self.lead.draw(img, t, x, y, te, self.exit_cut)
            if self.trail:
                w = self.trail.width
                x = min(max(face_r + 14, right - w), W - 64 - w)
                y = bot + self.trail.height / 2 + 14
                self.trail.draw(img, t, x, y, te, self.exit_cut)
        else:
            chin = ht + 1.22 * hs + self.chest_dy
            y = min(chin, H * 0.70)
            hero_h = self.hero.bh if self.hero is not None else 0
            if self.lead:
                lw = self.lead.width
                x = (540 - self.hero.bw / 2 + 6) if self.hero is not None else 540 - lw / 2 - 40
                x = max(64, min(x, W - 64 - lw))
                self.lead.draw(img, t, x, y, te, self.exit_cut)
                y += self.lead.height / 2 + 18
            if self.hero is not None:
                self.hero.chest_y = y + hero_h / 2
                if self.hero.active(t): self.hero.draw(img, t, ctx)
                y += hero_h + 14
            if self.trail:
                w = self.trail.width
                x = (540 + self.hero.bw / 2 - w) if self.hero is not None else 540 - w / 2 + 60
                x = max(64, min(x, W - 64 - w))
                self.trail.draw(img, t, x, y + self.trail.height / 2, te, self.exit_cut)


class ChestHero(Hero):
    """Front-layer hero placed by a chest Stack."""
    def __init__(self, *a, **k):
        k.setdefault('layer', 'front'); k.setdefault('mode', 'pop')
        super().__init__(*a, **k)
        self.chest_y = None

    def box(self, ctx):
        if self.chest_y is None:
            hx, ht, hs = ctx['anchor']
            return 540, min(ht + 1.22 * hs + 120, H * 0.72)
        return 540, self.chest_y


class Icons(El):
    """Effect C: glossy 3D icons dropping in above the head."""
    def __init__(self, t0, t1, names, exit_cut=False, dy=-112, single=None):
        super().__init__(t0, t1)
        self.names, self.exit_cut, self.dy, self.single = names, exit_cut, dy, single

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        n = len(self.names); gap = 174
        if self.single is not None:
            xs = [self.single[0]]; ys = [self.single[1]]
        else:
            x0 = min(max(hx, gap * (n - 1) / 2 + 100), W - 100 - gap * (n - 1) / 2)
            xs = [x0 + (i - (n - 1) / 2) * gap for i in range(n)]
            ys = [max(ht + self.dy, 230)] * n
        f = fr_since(t, self.t0)
        fe = fr_since(t, self.t1 - 9 / FPS)
        for i, name in enumerate(self.names):
            spr = ICONS[name] if name != 'coin_big' else ICON_COIN_BIG
            ff = f - i * 3
            if ff < 0: continue
            # drop 7 frames to +15px overshoot, settle 8 frames
            if ff < 7:
                y = -150 + (ys[i] + 15 + 150) * ease_out(ff / 7, 2) if self.single is None else ys[i] - 260 * (1 - ease_out(ff / 7, 2)) + 15 * ease_out(ff / 7, 2)
            else:
                y = ys[i] + 15 * (1 - ease_in_out((ff - 7) / 8))
            rot = (8 if i % 2 == 0 else -7) * (1 - ease_in_out(ff / 12))
            sc = 1.0
            if not self.exit_cut and fe >= 0:
                k = fe - (n - 1 - i) * 2
                sc = 1 - ease_in_out(k / 5) if k > 0 else 1.0
            # sparkle burst on landing
            fs = ff - 7
            if 0 <= fs < 8:
                for j in range(10):
                    ang = j / 10 * 2 * math.pi + i
                    r = 70 + 70 * ease_out(fs / 8, 2)
                    place(img, STAR if j % 2 else STAR_S, xs[i] + r * math.cos(ang), ys[i] + r * math.sin(ang), alpha=1 - fs / 8)
            place(img, spr, xs[i], y, scale=sc, rot=rot)


class CardRow(El):
    """Effect D: row of 3 post cards popping in on the spoken words, hovering, then shrinking away."""
    def __init__(self, t0, t1, cards, times, labels):
        super().__init__(t0, t1)
        self.cards, self.times, self.labels = cards, times, [text_sprite(l, 'capb', 40, LIME) for l in labels]

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        cy = max(ht - 190, 300)
        fe = fr_since(t, self.t1 - 6 / FPS)
        ex = 1 - ease_in_out(fe / 6) if fe > 0 else 1.0
        for i, (spr, tt, lab) in enumerate(zip(self.cards, self.times, self.labels)):
            f = fr_since(t, tt)
            if f < 0: continue
            x = 540 + (i - 1) * 300
            fl = 4 * math.sin(2 * math.pi * (t / 1.2) + i * 0.3 * 2 * math.pi / 1.2)
            sc = overshoot(f, 6, 0, 1.08) * ex
            rot = (-4, 2, 5)[i]
            place(img, spr, x, cy + fl, scale=sc, rot=rot, alpha=clamp01(f / 2) * ex)
            place(img, lab, x, cy + fl + 168 * sc, scale=sc, alpha=clamp01((f - 2) / 3) * ex)


class PhoneCards(El):
    """Effect D (phone version): tall 9:16 clips entering from the left/right edges with labels."""
    def __init__(self, t0, t1, specs):
        super().__init__(t0, t1)
        self.specs = specs  # list of (side, label, crop(x0,y0,x1,y1), src_start_frame, t_in)
        self.mask = rounded_rect_mask(240, 427, 30)
        self.labels = [text_sprite(s[1], 'capb', 44, LIME) for s in specs]

    def draw(self, img, t, ctx):
        fe = fr_since(t, self.t1 - 6 / FPS)
        ex = 1 - ease_in_out(fe / 6) if fe > 0 else 1.0
        for (side, label, crop, sf, tin), lab in zip(self.specs, self.labels):
            f = fr_since(t, tin)
            if f < 0: continue
            fi = sf + int(f) % 120
            clip = src_crop(fi, *crop, 234, 421)
            spr = card_sprite(clip, border=3, radius=30)
            p = ease_out(f / 8, 3)
            tx = 170 if side == 'L' else 830
            sx = -200 if side == 'L' else W + 200
            x = sx + (tx - sx) * p
            rot = -6 if side == 'L' else 6
            y = 1150 + 3 * math.sin(2 * math.pi * t / 1.4 + (0 if side == 'L' else 1.5))
            place(img, spr, x, y, rot=rot, scale=ex, alpha=ex)
            place(img, lab, x + (12 if side == 'L' else -12), y - 262, rot=rot * 0.5, scale=ex, alpha=clamp01((f - 4) / 3) * ex)


class Badge(El):
    """Effect E: logo badge rising from behind the head."""
    layer = 'back'
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        d = 220; pad = 40; n = d + pad * 2
        im = np.zeros((n, n), np.float32)
        cv2.circle(im, (n // 2, n // 2), d // 2, 1.0, -1, cv2.LINE_AA)
        circ = im
        sh = cv2.GaussianBlur(circ, (0, 0), 12); sh = np.roll(sh, 10, 0) * 0.45
        rgba = np.zeros((n, n, 4), np.float32)
        rgba[..., :3] = hexc('#2A0508') * sh[..., None]; rgba[..., 3] = sh
        ring = np.zeros((n, n), np.float32); cv2.circle(ring, (n // 2, n // 2), d // 2 - 3, 1.0, 6, cv2.LINE_AA)
        col = np.empty((n, n, 3), np.float32); col[:] = hexc('#FFFFFF')
        gold = grad_img(n, n, GOLD)
        col = col * (1 - ring[..., None]) + gold * ring[..., None]
        rgba[..., :3] = col * circ[..., None] + rgba[..., :3] * (1 - circ[..., None])
        rgba[..., 3] = circ + rgba[..., 3] * (1 - circ)
        self.base = Sprite(rgba)
        self.circ = circ
        self.ks = text_sprite('KS', 'hero', 104, ROSE, shadow=False)
        self.small = text_sprite('JODHPUR', 'capb', 20, '#B5179E', tracking=0.18, shadow=False)
        self.layer = 'back'

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        f = fr_since(t, self.t0)
        p = ease_out(f / 12, 3)
        y0, y1 = ht + 0.5 * hs, max(ht - 150, 210)
        y = y0 + (y1 - y0) * p
        sc = overshoot(f, 12, 0.4, 1.1)
        place(img, self.base, hx, y, scale=sc)
        place(img, self.ks, hx, y - 8 * sc, scale=sc)
        place(img, self.small, hx, y + 62 * sc, scale=sc)
        # highlight sweep after landing
        fs = f - 12
        if 0 <= fs <= 10:
            n = self.base.w
            bar = np.zeros((n, n, 4), np.float32)
            off = -n * 0.6 + n * 1.2 * fs / 10
            yy, xx = np.mgrid[0:n, 0:n]
            d = ((xx - n / 2) - (yy - n / 2) - off) / math.sqrt(2)
            a = np.clip(1 - np.abs(d) / 22, 0, 1) * 0.6 * self.circ
            bar[..., :3] = a[..., None]; bar[..., 3] = a
            place(img, Sprite(bar), hx, y, scale=sc)


class Glass(El):
    """Effect F: frosted glass location card with perspective tilt."""
    def __init__(self, t0, t1, lines_t):
        super().__init__(t0, t1)
        self.cw, self.ch = 760, 340
        self.lines_t = lines_t
        self.l1 = text_sprite(BRAND.title(), 'hero7', 54, WARM, shadow=False)
        self.l2 = text_sprite('Lotus Restaurant ke saamne', 'cap', 32, '#FFF1E2', shadow=False)
        self.l3 = text_sprite('Bhati Chauraha, Ratanada, Jodhpur', 'cap', 32, '#FFF1E2', shadow=False)
        self.tag = text_sprite('VISIT STORE', 'capb', 22, LIME, tracking=0.12, shadow=False)
        self.mask = rounded_rect_mask(self.cw, self.ch, 24)

    def content(self, t):
        cw, ch = self.cw, self.ch
        rgba = np.zeros((ch, cw, 4), np.float32)
        m = self.mask
        tint = hexc('#FFD8C2')
        rgba[..., :3] = tint * 0.18 * m[..., None]; rgba[..., 3] = 0.18 * m
        inner = cv2.GaussianBlur(m - cv2.erode(m, np.ones((15, 15), np.uint8)), (0, 0), 6) * 0.25
        rgba[..., :3] += inner[..., None] * (1 - rgba[..., 3:4]); rgba[..., 3] += inner * (1 - rgba[..., 3])
        border = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8)), 0, 1) * 0.35
        rgba[..., :3] = rgba[..., :3] * (1 - border[..., None]) + border[..., None]; rgba[..., 3] = border + rgba[..., 3] * (1 - border)
        tmp = np.zeros((ch, cw, 3), np.float32)
        a_acc = np.zeros((ch, cw), np.float32)
        # draw contents into tmp (premult) using place on an RGB buffer + alpha via a second pass
        lay = np.zeros((ch, cw, 4), np.float32)
        def put(spr, x, y, alpha=1.0, sc=1.0):
            buf = np.zeros((ch, cw, 3), np.float32); place(buf, spr, x, y, alpha=alpha, scale=sc)
            al = np.zeros((ch, cw, 3), np.float32)
            asp = Sprite(np.dstack([spr.a[..., 3:4].repeat(3, 2), spr.a[..., 3]])); asp.cx, asp.cy = spr.cx, spr.cy
            place(al, asp, x, y, alpha=alpha, scale=sc)
            a = al[..., 0]
            lay[..., :3] = buf + lay[..., :3] * (1 - a[..., None]); lay[..., 3] = a + lay[..., 3] * (1 - a)
        put(ICON_PIN, 104, ch / 2, sc=1.0)
        f = [fr_since(t, x) for x in self.lines_t]
        put(self.tag, 210 + self.tag.iw / 2, 82, alpha=clamp01(f[0] / 4))
        put(self.l1, 210 + self.l1.iw / 2, 140, alpha=clamp01(f[0] / 4))
        put(self.l2, 210 + self.l2.iw / 2, 205, alpha=clamp01(f[1] / 4))
        put(self.l3, 210 + self.l3.iw / 2, 255, alpha=clamp01(f[2] / 4))
        rgba[..., :3] = lay[..., :3] + rgba[..., :3] * (1 - lay[..., 3:4]); rgba[..., 3] = lay[..., 3] + rgba[..., 3] * (1 - lay[..., 3])
        return rgba

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        f = fr_since(t, self.t0); fe = fr_since(t, self.t1 - 8 / FPS)
        tx, ty = 540, 420
        if fe > 0:
            q = ease_in_out(fe / 8)
            p, rx, ry, alpha = 1 - q, 0, 0, 1 - q
            sc = 1 - 0.8 * q; cx = tx + (hx - tx) * q; cy = ty + (ht + 60 - ty) * q
        else:
            p = ease_out(f / 10, 3)
            sc = overshoot(f, 10, 0.2, 1.06)
            cx = hx + (tx - hx) * p; cy = ht + 60 + (ty - ht - 60) * p
            rx, ry = 10 + 1.0 * math.sin(t * 2.2), -8 + 1.0 * math.cos(t * 1.7)
            cy += 4 * math.sin(2 * math.pi * t / 1.6)
            alpha = clamp01(f / 3)
        cw, ch = self.cw, self.ch
        rgba = self.content(t)
        # perspective: rotate card corners in 3D
        def proj(x, y):
            X, Y, Z = x, y, 0.0
            a, b = math.radians(rx), math.radians(ry)
            Y, Z = Y * math.cos(a) - Z * math.sin(a), Y * math.sin(a) + Z * math.cos(a)
            X, Z = X * math.cos(b) + Z * math.sin(b), -X * math.sin(b) + Z * math.cos(b)
            d = 1600
            return cx + X * sc * d / (d + Z * sc), cy + Y * sc * d / (d + Z * sc)
        src = np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]])
        dst = np.float32([proj(-cw / 2, -ch / 2), proj(cw / 2, -ch / 2), proj(cw / 2, ch / 2), proj(-cw / 2, ch / 2)])
        x0, y0 = np.floor(dst.min(0)).astype(int) - 2; x1, y1 = np.ceil(dst.max(0)).astype(int) + 2
        X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if X1 <= X0 or Y1 <= Y0: return
        Hm = cv2.getPerspectiveTransform(src, (dst - [X0, Y0]).astype(np.float32))
        roi = cv2.warpPerspective(rgba, Hm, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR)
        mroi = cv2.warpPerspective(self.mask, Hm, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR) * alpha
        reg = img[Y0:Y1, X0:X1]
        # frosted backdrop + soft shadow
        blur = cv2.GaussianBlur(reg, (0, 0), 18)
        reg[:] = reg * (1 - mroi[..., None]) + blur * mroi[..., None]
        reg *= (1 - roi[..., 3:4] * alpha)
        reg += roi[..., :3] * alpha


class Chart(El):
    """Effect G: line chart draw-on with pill label."""
    def __init__(self, t0, t1, t_pill, pill_text):
        super().__init__(t0, t1)
        self.t_pill = t_pill
        tx = text_sprite(pill_text, 'capb', 44, MAGENTA, shadow=False)
        pw, ph = int(tx.iw + 64), int(tx.ih + 34)
        m = rounded_rect_mask(pw, ph, ph // 2)
        pad = 24
        rgba = np.zeros((ph + pad * 2, pw + pad * 2, 4), np.float32)
        sh = np.zeros(rgba.shape[:2], np.float32); sh[pad:pad + ph, pad:pad + pw] = m
        sh = np.roll(cv2.GaussianBlur(sh, (0, 0), 8), 5, 0) * 0.35
        rgba[..., :3] = hexc('#2A0508') * sh[..., None]; rgba[..., 3] = sh
        r = rgba[pad:pad + ph, pad:pad + pw]
        r[..., :3] = hexc('#FFFFFF') * m[..., None] + r[..., :3] * (1 - m[..., None]); r[..., 3] = m + r[..., 3] * (1 - m)
        rgb = rgba[..., :3]
        place(rgb, tx, rgba.shape[1] / 2, rgba.shape[0] / 2)
        self.pill = Sprite(rgba)
        self.pts = np.array([(312, 472), (390, 420), (455, 446), (535, 365), (605, 392), (690, 300), (770, 252)], np.float32)

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0); fe = fr_since(t, self.t1 - 6 / FPS)
        ex = 1 - ease_in_out(fe / 6) if fe > 0 else 1.0
        if ex <= 0: return
        ov = np.zeros((H, W), np.float32)
        x0, yt, yb, xr = 280, 230, 500, 812
        pv = ease_in_out(f / 3); ph = ease_in_out((f - 3) / 3)
        S_ = 2  # draw in 2x-subpixel via shift
        if pv > 0:
            cv2.line(ov, (x0, yb), (x0, int(yb - (yb - yt) * pv)), 1.0, 4, cv2.LINE_AA)
        if ph > 0:
            cv2.line(ov, (x0, yb), (int(x0 + (xr - x0) * ph), yb), 1.0, 4, cv2.LINE_AA)
        pl = ease_in_out((f - 6) / 15)
        dots = []
        if pl > 0:
            seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1); tot = seg.sum(); L = tot * pl
            path = [self.pts[0]]; acc = 0
            for i, sl in enumerate(seg):
                if acc + sl <= L:
                    path.append(self.pts[i + 1]); acc += sl
                    dots.append((self.pts[i + 1], f - 6 - 15 * (acc / tot)))
                else:
                    r = (L - acc) / sl; path.append(self.pts[i] + (self.pts[i + 1] - self.pts[i]) * r); break
            cv2.polylines(ov, [np.int32(np.array(path) * 4)], False, 1.0, 5, cv2.LINE_AA, shift=2)
            if pl >= 1:
                e = self.pts[-1]; d = self.pts[-1] - self.pts[-2]; d = d / np.linalg.norm(d)
                nrm = np.array([-d[1], d[0]])
                tri = np.array([e + d * 26, e - d * 6 + nrm * 16, e - d * 6 - nrm * 16])
                cv2.fillPoly(ov, [np.int32(tri * 4)], 1.0, cv2.LINE_AA, shift=2)
        glow = cv2.GaussianBlur(ov, (0, 0), 7) * 0.55
        over_full(img, hexc('#FFC34D'), glow * ex)
        over_full(img, hexc(WARM), ov * ex)
        for pt, df in dots:
            df = f - 6 - 15 * 0  # dots pop shortly after the line passes
        if pl > 0:
            seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()
            for pt, c in zip(self.pts[1:], cum[1:]):
                pf = (f - 6) - 15 * c
                if pf >= 0:
                    r = 7 * overshoot(pf, 3, 0, 1.3)
                    cv2.circle(img, (int(pt[0]), int(pt[1])), max(int(r), 1), tuple(map(float, hexc('#FFD25A'))), -1, cv2.LINE_AA)
        fp = fr_since(t, self.t_pill)
        if fp >= 0:
            place(img, self.pill, 546, 575, scale=overshoot(fp, 6, 0, 1.1) * ex, alpha=ex)


class Counter(El):
    """Effect H: number counter with gradient ring."""
    def __init__(self, t0, t1, target, t_label, label, count_frames=24):
        super().__init__(t0, t1)
        self.target, self.t_label, self.cf = target, t_label, count_frames
        self.label = text_sprite(label, 'hero', 74, GOLD)
        self.ringcols = grad_vals(RING, 361)

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0)
        p = ease_out(f / self.cf, 3)
        cx, cy, r = 540, 405, 180
        ov = np.zeros((H, W, 3), np.float32); a = np.zeros((H, W), np.float32)
        deg = int(360 * p)
        for d0 in range(0, deg, 3):
            col = self.ringcols[d0]
            cv2.ellipse(ov, (cx, cy), (r, r), -90, d0, min(d0 + 4, deg), tuple(map(float, col)), 14, cv2.LINE_AA)
            cv2.ellipse(a, (cx, cy), (r, r), -90, d0, min(d0 + 4, deg), 1.0, 14, cv2.LINE_AA)
        # faint track
        trk = np.zeros((H, W), np.float32); cv2.circle(trk, (cx, cy), r, 0.18, 14, cv2.LINE_AA)
        over_full(img, hexc(WARM), trk * (1 - a) * clamp01(f / 4))
        sl = (slice(cy - r - 20, cy + r + 20), slice(cx - r - 20, cx + r + 20))
        glow = cv2.GaussianBlur(a[sl], (0, 0), 8) * 0.5
        img[sl] = img[sl] * (1 - glow[..., None]) + cv2.GaussianBlur(ov[sl], (0, 0), 8) / np.maximum(cv2.GaussianBlur(a[sl], (0, 0), 8)[..., None], 1e-3) * glow[..., None]
        img[sl] = img[sl] * (1 - a[sl][..., None]) + ov[sl]
        v = int(round(self.target * p)) if f >= 0 else 0
        rate = self.target * 3 * (1 - clamp01(f / self.cf)) ** 2 / self.cf
        num = text_sprite(str(v), 'hero', 170, WARM)
        place(img, num, cx, cy, mblur=(0, min(rate * 10, 24)), alpha=clamp01(f / 3), scale=overshoot(f, 6, 0.6, 1.06))
        fl = fr_since(t, self.t_label)
        if fl >= 0:
            place(img, self.label, cx, cy + r + 78, scale=pop_scale(fl, 6), alpha=clamp01(fl / 3), blur=8 * (1 - clamp01(fl / 5)))

    def ticks(self):
        out, last = [], 0
        for f in range(self.cf + 1):
            v = int(round(self.target * ease_out(f / self.cf, 3)))
            if v != last: out.append(self.t0 + f / FPS); last = v
        return out


class MoonRise(El):
    layer = 'back'
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        n = 200
        m = np.zeros((n, n), np.float32)
        cv2.circle(m, (100, 100), 46, 1.0, -1, cv2.LINE_AA)
        cut = np.zeros((n, n), np.float32); cv2.circle(cut, (124, 86), 42, 1.0, -1, cv2.LINE_AA)
        m = np.clip(m - cut, 0, 1)
        g = cv2.GaussianBlur(m, (0, 0), 14) * 1.2
        a = np.clip(m + g * (1 - m), 0, 1)
        rgba = np.zeros((n, n, 4), np.float32); rgba[..., :3] = hexc('#FFF4D6') * a[..., None]; rgba[..., 3] = a
        self.spr = Sprite(rgba)

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        f = fr_since(t, self.t0); dur = (self.t1 - self.t0) * FPS
        a = clamp01(f / 9) * clamp01((dur - f) / 9)
        place(img, self.spr, min(hx + 250, W - 120), 0.18 * H - 40 * (f / 60), alpha=a)


class Spotlight(El):
    """Effect L: glow outline traced around a held product (+ sparkles)."""
    def __init__(self, t0, t1, region, mode='red'):
        super().__init__(t0, t1)
        self.region, self.mode = region, mode

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0); dur = (self.t1 - self.t0) * FPS
        a = clamp01(f / 3) * clamp01((dur - f) / 3)
        if a <= 0: return
        fi, A = ctx['src_fi'], ctx['A']
        x0, y0, x1, y1 = self.region
        sub = np.asarray(FR[fi][y0:y1, x0:x1], np.int16)
        R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
        red = (R > 135) & (R - G > 60) & (B < 120)
        gold = (R > 170) & (G > 120) & (B < 120) & (R - B > 80)
        m = ((red | gold) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((17, 17), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        if n < 2: return
        k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        m = (lab == k).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        full = np.zeros((SRC_H, SRC_W), np.float32)
        cv2.drawContours(full, [c + [x0, y0] for c in cnts], -1, 1.0, -1)
        # fade near the bottom of the search region (where it meets the table)
        fade = np.clip((y1 - np.arange(SRC_H)) / 60, 0, 1)[:, None]
        mo = cv2.warpAffine(full, A, (W, H))
        fo = cv2.warpAffine(np.repeat(fade, SRC_W, 1).astype(np.float32), A, (W, H))
        dil = cv2.dilate(mo, np.ones((13, 13), np.uint8))
        edge = np.clip(dil - mo, 0, 1) * fo
        glow = cv2.GaussianBlur(edge, (0, 0), 12) * 1.6
        over_full(img, hexc('#FFE9A8'), np.clip(glow, 0, 1) * a * 0.9)
        over_full(img, hexc(WARM), cv2.GaussianBlur(edge, (0, 0), 1.2) * a)
        ys, xs = np.nonzero(edge > 0.5)
        if len(xs):
            rng = np.random.RandomState(7)
            idx = rng.choice(len(xs), 8, replace=False) if len(xs) > 8 else range(len(xs))
            for j, i in enumerate(idx):
                tw = 0.5 + 0.5 * math.sin(f * 0.9 + j * 1.7)
                place(img, STAR, xs[i] + rng.randint(-20, 20), ys[i] + rng.randint(-20, 20), alpha=a * tw, scale=0.8 + 0.5 * tw)


class HeartGlow(El):
    """Effect L: designed heart outline glowing around the held heart thaalposh (keyframed to the footage)."""
    def __init__(self, t0, t1, keys):
        super().__init__(t0, t1); self.keys = keys  # [(src_t, cx, cy, w, h, rot)]
        tt = np.linspace(0, 2 * np.pi, 240)
        x = 16 * np.sin(tt) ** 3
        y = -(13 * np.cos(tt) - 5 * np.cos(2 * tt) - 2 * np.cos(3 * tt) - np.cos(4 * tt))
        x = (x - x.min()) / (x.max() - x.min()) - 0.5; y = (y - y.min()) / (y.max() - y.min()) - 0.5
        self.path = np.stack([x, y], 1)

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0); dur = (self.t1 - self.t0) * FPS
        a = clamp01(f / 3) * clamp01((dur - f) / 3)
        if a <= 0: return
        st = ctx['src_t']; ks = self.keys
        if st <= ks[0][0]: k = ks[0][1:]
        elif st >= ks[-1][0]: k = ks[-1][1:]
        else:
            for k0, k1 in zip(ks, ks[1:]):
                if k0[0] <= st <= k1[0]:
                    r = (st - k0[0]) / (k1[0] - k0[0]); k = [u + (v - u) * r for u, v in zip(k0[1:], k1[1:])]; break
        cx, cy, w, h, rot = k
        th = math.radians(rot); c, s_ = math.cos(th), math.sin(th)
        pts = self.path * [w * 1.18, h * 1.18]
        pts = pts @ np.array([[c, s_], [-s_, c]]) + [cx, cy]
        A = ctx['A']
        po = np.stack([A[0, 0] * pts[:, 0] + A[0, 1] * pts[:, 1] + A[0, 2], A[1, 0] * pts[:, 0] + A[1, 1] * pts[:, 1] + A[1, 2]], 1)
        ov = np.zeros((H, W), np.float32)
        cv2.polylines(ov, [np.int32(po * 4)], True, 1.0, 5, cv2.LINE_AA, shift=2)
        over_full(img, hexc('#FFC34D'), np.clip(cv2.GaussianBlur(ov, (0, 0), 14) * 2.4, 0, 1) * a)
        over_full(img, hexc(WARM), ov * a)
        for j in range(8):
            q = po[(j * 30 + int(f * 2)) % len(po)]
            tw = 0.5 + 0.5 * math.sin(f * 0.9 + j * 1.7)
            place(img, STAR, q[0], q[1], alpha=a * tw, scale=0.8 + 0.6 * tw)


class BoxGlow(El):
    def __init__(self, t0, t1, center, size):
        super().__init__(t0, t1); self.c, self.sz = center, size

    def draw(self, img, t, ctx):
        f = fr_since(t, self.t0); dur = (self.t1 - self.t0) * FPS
        a = clamp01(f / 3) * clamp01((dur - f) / 4)
        A = ctx['A']
        cx, cy = apply_pt(A, *self.c); k = A[0, 0]
        w, h = self.sz[0] * k, self.sz[1] * k
        ov = np.zeros((H, W), np.float32)
        cv2.rectangle(ov, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)), 1.0, 5, cv2.LINE_AA)
        ov = cv2.GaussianBlur(ov, (0, 0), 2)
        over_full(img, hexc('#FFE9A8'), np.clip(cv2.GaussianBlur(ov, (0, 0), 14) * 2.2, 0, 1) * a)
        over_full(img, hexc(WARM), ov * a)
        for j in range(7):
            ang = j / 7 * 2 * math.pi + f * 0.05
            tw = 0.5 + 0.5 * math.sin(f * 0.8 + j * 2.1)
            place(img, STAR, cx + (w / 2 + 30) * math.cos(ang), cy + (h / 2 + 30) * math.sin(ang), alpha=a * tw, scale=0.9 + 0.4 * tw)


class CTA(El):
    """CTA: bold condensed caps appearing word by word; last word in Saffron Gold."""
    def __init__(self, t0, t1, lines, last_grad=SAFFRON, size=104, y=None):
        super().__init__(t0, t1)
        self.lines = []
        for ln in lines:
            row = []
            for i, (w, tw, grad) in enumerate(ln):
                row.append((text_sprite(w, 'cta', size, grad if grad else WARM, tracking=0.02), tw))
            self.lines.append(row)
        self.size, self.y = size, y

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        y = self.y if self.y else min(ht + 1.25 * hs + 40, 0.55 * H)
        sp = self.size * 0.28
        for li, row in enumerate(self.lines):
            tw_ = sum(s.iw for s, _ in row) + sp * (len(row) - 1)
            x = 540 - tw_ / 2
            yy = y + li * self.size * 1.05
            for s, tw in row:
                f = fr_since(t, tw)
                if f >= 0:
                    place(img, s, x + s.iw / 2, yy, scale=pop_scale(f, 5, 0.7, 1.08), alpha=clamp01(f / 3), blur=8 * (1 - clamp01(f / 5)))
                x += s.iw + sp


class Ornament(El):
    """Faint Devanagari accent behind the opening hero."""
    layer = 'back'
    def __init__(self, t0, t1, text, hero):
        super().__init__(t0, t1); self.spr = text_sprite(text, 'dev', 76, GOLD, shadow=False); self.hero = hero

    def draw(self, img, t, ctx):
        cx, cy = self.hero.box(ctx)
        f = fr_since(t, self.t0)
        place(img, self.spr, cx + self.hero.bw / 2 - self.spr.iw / 2 - 10, cy - self.hero.bh / 2 - 46, alpha=0.6 * clamp01(f / 6))


class Watermark(El):
    def __init__(self, t0, t1, moves):
        super().__init__(t0, t1)
        g = ig_glyph_mask(28)
        self.glyph = mask_sprite(g, WARM, shadow=True)
        self.txt = text_sprite(WM_TEXT, 'cap', 24, WARM, tracking=0.08)
        self.moves = moves  # list of (t, 'TR'/'BL')
        self.w = 28 + 10 + self.txt.iw

    def pos(self, where):
        if where == 'TR': return (W - 64 - self.w, 120)
        return (64, 1400)

    def draw(self, img, t, ctx):
        cur = self.pos(self.moves[0][1])
        for i in range(1, len(self.moves)):
            tm, wh = self.moves[i]
            if t >= tm:
                prev = self.pos(self.moves[i - 1][1]); nxt = self.pos(wh)
                q = ease_in_out((t - tm) * FPS / 10)
                cur = (prev[0] + (nxt[0] - prev[0]) * q, prev[1] + (nxt[1] - prev[1]) * q)
        x, y = cur
        place(img, self.glyph, x + 14, y, alpha=0.85)
        place(img, self.txt, x + 38 + self.txt.iw / 2, y, alpha=0.85)


class Flash(El):
    """Effect I: diagonal light-leak burst (bottom-right -> top-left), full white at the cut."""
    layer = 'post'
    def __init__(self, tc, warm=False):
        super().__init__(tc - 7 / FPS, tc + 8 / FPS)
        self.tc, self.warm = tc, warm
        lw, lh = 270, 480
        yy, xx = np.mgrid[0:lh, 0:lw].astype(np.float32)
        self.u = ((xx / lw) + (yy / lh)) / 2  # 0 TL .. 1 BR
        self.streak_y = np.random.RandomState(3 if warm else 5).rand(5) * lh
        self.dust = np.random.RandomState(11).rand(14, 3)

    def draw(self, img, t, ctx):
        f = (t - self.t0) * FPS  # 0..15
        p = f / 15
        front = 1.25 - 1.7 * p
        core = np.clip((self.u - front) / 0.35, 0, 1)
        edge = np.exp(-((self.u - front) / 0.12) ** 2)
        lw, lh = 270, 480
        if self.warm:
            c_edge = [hexc('#FF8A00'), hexc('#FF4F7B'), hexc('#C2185B')]
        else:
            c_edge = [hexc('#FFB000'), hexc('#FFE9A8'), hexc('#FFD25A')]
        yy = np.linspace(0, 1, lh)[:, None]
        ecol = (c_edge[0] * (1 - yy)[..., None] + c_edge[2] * yy[..., None]) * 0.6 + c_edge[1] * 0.4
        ecol = np.broadcast_to(ecol, (lh, lw, 3))
        white = np.ones(3, np.float32)
        a_edge = np.clip(edge * 0.9, 0, 1); a_core = core
        col = ecol * (a_edge * (1 - a_core))[..., None] + white * a_core[..., None]
        a = np.clip(a_edge * (1 - a_core) + a_core, 0, 1)
        # anamorphic streaks
        for sy in self.streak_y:
            band = np.exp(-((np.arange(lh)[:, None] - sy) / 1.6) ** 2) * edge * 0.8
            col = col * (1 - band[..., None]) + white * band[..., None]; a = np.maximum(a, band)
        peak = 1.0 if 6 <= f <= 8.5 else (clamp01(f / 6) ** 3 * 0.7 if f < 6 else clamp01((15 - f) / 6.5) ** 2)
        col = col * (1 - peak) + white * peak; a = np.maximum(a, peak) if f <= 8.5 else np.clip(a * clamp01((15 - f) / 7) + peak, 0, 1)
        colF = cv2.resize(col.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        aF = cv2.resize(a.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        img *= (1 - aF[..., None]); img += colF * aF[..., None]
        # gold dust
        for i, (dx, dy, ph) in enumerate(self.dust):
            x = W * (dx + 0.25 - 0.5 * p); y = H * (dy + 0.25 - 0.5 * p)
            place(img, STAR_S, x, y, alpha=0.9 * math.sin(math.pi * clamp01(p)) * (0.5 + 0.5 * math.sin(ph * 6 + f)))


# ---------------------------------------------------------------- timeline
def W_(words):
    """[('word', src_t)] -> output times (clamped into the piece where the word is heard)."""
    return [(w, T(s)) for w, s in words]


def build_timeline():
    E = []
    ct = cut_time
    end_talk = TALK_FRAMES / FPS

    # --- A1: brand behind the head on frame 1
    h = Hero(0, ct('A2'), ['KRISHNA', 'SHRINGAR'], GOLD, size=170, y_off=0.40)
    E.append(h)
    E.append(Ornament(0, ct('A2'), 'शुभ', h))
    E.append(Stack(0, ct('A2'), lead=W_([('gautam', .15), ('bhai,', .52), ('aap', .72)]),
                   trail=[('JODHPUR', T(.25))], hero=h, trail_fill=LIME, trail_size=56, trail_typed=False))
    E.append(Stack(T(1.04), ct('A2'), lead=W_([('karwa', 1.04), ('chauth', 1.38), ('ke', 1.50), ('liye', 1.58)]), kind='chest', chest_dy=60))
    # --- A2
    h = Hero(T(2.32), ct('A3'), 'COLLECTION', GOLD, size=165)
    E.append(h)
    E.append(Stack(ct('A2'), ct('A3'), lead=W_([('itna', 1.76), ('achha', 1.88), ('achha', 2.18)]),
                   trail=W_([('leke', 2.62), ('aaye', 2.80)]), hero=h))
    # --- A3: icons + Karwa Chauth + moon
    E.append(Icons(ct('A3'), ct('B'), ['diya', 'gift', 'moon'], exit_cut=True, dy=-118))
    h = Hero(T(3.38), ct('B'), ['KARWA', 'CHAUTH'], GOLD, size=165, y_off=0.42)
    E.append(h)
    E.append(MoonRise(T(3.38), ct('B')))
    E.append(Stack(ct('A3'), ct('B'), lead=W_([('is', 3.12), ('baar', 3.20)]),
                   trail=W_([('pe', 3.90), ('kya', 4.0), ('laaye', 4.2), ('ho?', 4.5)]), hero=h))
    # --- B
    hb = ChestHero(T(5.57), ct('C1'), 'LEKE AAYE', MAGENTA, size=128)
    E.append(Stack(ct('B'), ct('C1'), lead=W_([('aapke', 4.80), ('liye', 5.33)]), trail=W_([('hain', 5.95)]),
                   hero=hb, kind='chest', trail_typed=False))
    # --- C1 / C2
    h = Hero(T(8.50), T(9.37), ['ALAG ALAG'], GOLD, size=165, exit_cut=False)
    E.append(h)
    E.append(Stack(ct('C1'), T(9.37), lead=W_([('karwa', 7.50), ('chauth', 7.75), ('par', 8.03)]),
                   trail=W_([('prakar', 8.93), ('ki', 9.21)]), hero=h, exit_cut=False))
    cards = [card_sprite(src_crop(600, 405, 930, 675, 1200, 224, 224)),
             card_sprite(src_crop(600, 350, 1100, 610, 1360, 224, 224)),
             card_sprite(src_crop(600, 40, 1060, 320, 1340, 224, 224))]
    E.append(CardRow(T(9.39), ct('D1'), cards, [T(9.39), T(9.87), T(10.41)], ['THAALI', 'LOTA', 'CHHALNI']))
    E.append(Stack(T(9.39), ct('D1'), lead=W_([('thaali,', 9.39), ('lota', 9.87), ('aur', 10.21), ('chhalni', 10.41)]), kind='chest', chest_dy=50))
    # --- D1: badge + brand reveal
    E.append(Stack(ct('D1'), ct('D2'), lead=W_([('jiske', 17.28), ('liye', 17.57), ('aapko', 17.75)]),
                   trail=W_([('aana', 17.97), ('hoga', 18.17)]), kind='chest', chest_dy=30, trail_typed=False))
    E.append(Badge(T(18.41), ct('D2')))
    E.append(Hero(T(18.41), ct('D2'), ['KRISHNA', 'SHRINGAR'], ROSE, mode='reveal', size=150, y_off=0.42))
    # --- D2/D3: glass location card
    E.append(Glass(ct('D2'), ct('E1'), [ct('D2'), T(19.64), T(20.10)]))
    hb = ChestHero(T(20.10), ct('E1'), 'BHATI CHAURAHA', MAGENTA, size=104)
    E.append(Stack(ct('D2'), ct('E1'), lead=W_([('jo', 19.43), ('hai', 19.64)]),
                   trail=W_([('ratanada,', 20.71), ('jodhpur', 21.13)]), hero=hb, kind='chest', chest_dy=10))
    # --- E1
    hb = ChestHero(T(22.21), ct('E2'), 'SAATH SAATH', WARM, size=118)
    E.append(Stack(ct('E1'), ct('E2'), lead=W_([('uske', 21.97)]), trail=W_([('aapko', 22.85)]), hero=hb, kind='chest', trail_typed=False))
    # --- E2: phone cards + KARWE behind
    E.append(PhoneCards(ct('E2'), ct('F1'), [('L', 'KARWE', (180, 880, 400, 1270), 372, ct('E2')),
                                             ('R', 'LOTA', (370, 1050, 590, 1440), 380, ct('E2') + 4 / FPS)]))
    h = Hero(T(24.20), ct('F1'), 'KARWE', GOLD, size=170)
    E.append(h)
    E.append(Stack(ct('E2'), ct('F1'), lead=W_([('alag', 23.41), ('alag', 23.66), ('prakar', 23.82), ('ke', 24.08)]),
                   trail=W_([('bhi', 24.50), ('milenge', 24.64)]), hero=h))
    # --- F1 / F2a
    h = Hero(T(26.68), ct('F2b'), ['ALAG ALAG'], GOLD, size=165)
    E.append(h)
    E.append(Stack(ct('F1'), ct('F2a'), lead=W_([('aapko', 25.30)]), kind='chest', chest_dy=40))
    E.append(Stack(ct('F2a'), ct('F2b'), lead=W_([('thaali', 25.91), ('pe', 26.18), ('rakhne', 26.30), ('ke', 26.56)]),
                   trail=W_([('prakar', 27.04), ('ke', 27.36)]), hero=h))
    # --- F2b: thaalposh + spotlight on the heart
    hb = ChestHero(T(27.46), ct('G1'), 'THAALPOSH', WARM, size=112)
    E.append(Stack(ct('F2b'), ct('G1'), trail=W_([('bhi', 28.12), ('milenge', 28.24)]), hero=hb, kind='chest', trail_typed=False, chest_dy=60))
    E.append(HeartGlow(T(28.30), ct('G1'), [(28.30, 470, 895, 320, 300, 8), (28.40, 546, 865, 310, 326, 0), (28.60, 501, 928, 378, 284, -15), (28.72, 488, 945, 385, 280, -18)]))
    # --- G1-G3: chart + chunri
    E.append(Chart(ct('G1'), T(32.55), T(31.59), 'alag alag chunri'))
    E.append(Stack(ct('G1'), ct('G2'), lead=W_([('saath', 29.21), ('hi', 29.73), ('saath', 29.85)]), kind='chest', chest_dy=30))
    E.append(Stack(ct('G2'), ct('G3'), lead=W_([('alag', 30.29), ('alag', 30.56), ('prakar', 30.74), ('ki', 31.08)]), kind='chest', chest_dy=30))
    h = Hero(T(31.59), T(32.55), 'CHUNRI', GOLD, size=175, exit_cut=False)
    E.append(h)
    E.append(Stack(ct('G3'), T(32.55), trail=W_([('bhi', 31.92), ('aapko', 32.06), ('milegi', 32.26)]), hero=h, exit_cut=False))
    E.append(Stack(T(32.64), ct('G4'), lead=W_([('iske', 32.64), ('saath', 32.78), ('hi', 33.08)]), kind='chest', chest_dy=30))
    # --- G4: counter
    cnt = Counter(ct('G4'), ct('H1a'), 16, T(33.75), 'SOLAH SHRINGAR')
    E.append(cnt)
    E.append(Stack(ct('G4'), ct('H1a'), lead=W_([('aapko', 33.44)]), kind='chest', chest_dy=50))
    # --- H1a/H1b: CTA build-up (warm flash at the cut into H1a)
    E.append(Stack(ct('H1a'), T(35.30), lead=W_([('bhi', 34.75), ('milega', 35.02)]), kind='chest', chest_dy=20))
    E.append(_Typed(T(35.30), ct('H2'), [('ISKO', T(35.30)), ('AAPKO', T(35.96))], [('LENE', T(36.24)), ('KE', T(36.46)), ('LIYE', T(36.58))],
                    W_([('aana', 36.70), ('hoga', 36.84)])))
    E.append(BoxGlow(ct('H1b'), ct('H1b') + 0.55, (330, 948), (250, 175)))
    # --- H2: Krishna Shringar hero + coin
    h = Hero(T(37.57), ct('I1'), ['KRISHNA', 'SHRINGAR'], GOLD, size=160, y_off=0.42)
    E.append(h)
    E.append(_CoinNext(T(37.57) + 2 / FPS, ct('I1'), h))
    # --- I1/I2: CTA
    E.append(Stack(ct('I1'), ct('I2a'), lead=W_([('jo', 38.52), ('hai', 38.73)]), kind='chest', chest_dy=30, lead_size=62))
    E.append(CTA(ct('I2a'), end_talk, [[('LOTUS', T(39.28), None)], [('RESTAURANT', T(39.53), None)], [('KE', T(39.93), None), ('SAAMNE', T(40.09), SAFFRON)]], y=1000))
    E.append(_Address(T(40.53), end_talk))
    # --- flashes
    E.append(Flash(ct('C1'))); E.append(Flash(ct('D1'))); E.append(Flash(ct('F1'))); E.append(Flash(ct('H1a'), warm=True))
    # --- watermark + end card
    E.append(Watermark(0, TOTAL_FRAMES / FPS + 1, [(0, 'TR'), (ct('D1'), 'BL'), (ct('G1'), 'TR')]))
    E.append(EndCard(end_talk, TOTAL_FRAMES / FPS + 1))
    return E, cnt


class _Typed(El):
    """Big Warm White bold lines typing on word by word, small trail to the right."""
    def __init__(self, t0, t1, line1, line2, trail):
        super().__init__(t0, t1)
        self.l1 = WordLine(line1, 'hero', 112); self.l2 = WordLine(line2, 'hero', 112)
        self.tr = WordLine(trail, 'cap', 52, typed=True)

    def draw(self, img, t, ctx):
        hx, ht, hs = ctx['anchor']
        y = min(ht + 1.22 * hs + 40, 0.62 * H)
        x = 540 - max(self.l1.width, self.l2.width) / 2
        self.l1.draw(img, t, x, y)
        self.l2.draw(img, t, x, y + 112)
        self.tr.draw(img, t, min(x + self.l2.width - self.tr.width, W - 64 - self.tr.width), y + 112 + 92)


class _CoinNext(El):
    def __init__(self, t0, t1, hero):
        super().__init__(t0, t1); self.hero = hero; self.ic = Icons(t0, t1, ['coin_big'], exit_cut=True)

    def draw(self, img, t, ctx):
        cx, cy = self.hero.box(ctx)
        self.ic.single = (max(cx - self.hero.bw / 2 - 20, 90), cy - self.hero.bh / 2 - 40)
        self.ic.draw(img, t, ctx)


class _Address(El):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.wl = WordLine([('bhati', T(40.53)), ('chauraha,', T(40.83))], 'cap', 46)
        self.wl2 = WordLine([('ratanada,', T(41.21)), ('jodhpur', T(41.67))], 'cap', 46)
        self.pin = mask_sprite(self._pin(), LIME[0][1])

    def _pin(self):
        n = 120; im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
        d.ellipse((30, 10, 90, 70), fill=255); d.polygon([(34, 52), (86, 52), (60, 110)], fill=255); d.ellipse((50, 30, 70, 50), fill=0)
        return np.asarray(im.resize((36, 36), Image.LANCZOS), np.float32) / 255

    def draw(self, img, t, ctx):
        x = W - 64 - max(self.wl.width, self.wl2.width) - 10
        y = 880
        f = fr_since(t, self.t0)
        place(img, self.pin, x - 30, y, alpha=clamp01(f / 3), scale=pop_scale(f, 5))
        self.wl.draw(img, t, x, y); self.wl2.draw(img, t, x, y + 54)


class EndCard(El):
    layer = 'post'
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.g = ig_glyph_mask(220)
        self.grad = grad_img(220, 220, IG, 'd')
        self.txt = text_sprite(HANDLE.upper() if HANDLE else BRAND, 'cap', 40, WARM, tracking=0.10)
        self.sub = text_sprite('BHATI CHAURAHA  •  RATANADA  •  JODHPUR', 'cap', 26, WARM, tracking=0.08)
        self.sub2 = text_sprite('Lotus Restaurant ke saamne', 'cap', 26, WARM)

    def draw(self, img, t, ctx):
        img[:] = 0
        tt = t - self.t0; f = tt * FPS
        mix = 0.5 - 0.5 * math.cos(2 * math.pi * tt / 2.0)
        col = np.ones((220, 220, 3), np.float32) * (1 - mix) + self.grad * mix
        rgba = np.dstack([col * self.g[..., None], self.g]).astype(np.float32)
        place(img, Sprite(rgba), 540, 860, scale=overshoot(f, 9, 0.8, 1.04))
        ft = f - 12
        if ft >= 0:
            q = ease_out(ft / 12, 3)
            place(img, self.txt, 540, 1040 + 30 * (1 - q), alpha=q)
            place(img, self.sub, 540, 1100 + 30 * (1 - q), alpha=q * 0.6)
            place(img, self.sub2, 540, 1146 + 30 * (1 - q), alpha=q * 0.6)


# ---------------------------------------------------------------- renderer
ELEMENTS, COUNTER = build_timeline()


def piece_for(k):
    for p in PCS:
        if p.o0 <= k < p.o1: return p
    return None


def render_frame(k):
    t = k / FPS
    p = piece_for(k)
    img = np.zeros((H, W, 3), np.float32)
    ctx = {'t': t}
    if p is not None:
        j = k - p.o0
        fi = p.fin + j
        A = frame_affine(p, j)
        # freeze-zoom 3% during the heart spotlight
        if p.name == 'F2b' and t >= T(28.30):
            z = 1 + 0.03 * ease_out((t - T(28.30)) * FPS / 6, 2)
            A = (np.array([[z, 0, (1 - z) * 560], [0, z, (1 - z) * 1100], [0, 0, 1]], np.float32) @ np.vstack([A, [0, 0, 1]]))[:2]
        src = np.asarray(FR[fi], np.float32) / 255
        msk = np.asarray(MS[fi], np.float32) / 255
        base = cv2.warpAffine(src, A, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        m = cv2.warpAffine(msk, A, (W, H), flags=cv2.INTER_LINEAR)
        ramp = cv2.warpAffine(SRC_RAMP, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # sharpen the upscale a touch
        bl = cv2.GaussianBlur(base, (0, 0), 1.4)
        base = np.clip(base + 0.45 * (base - bl), 0, 1)
        # fake shallow DoF on the shelves only (not the table / products)
        wbg = np.clip((1 - m) * ramp, 0, 1)
        far = cv2.GaussianBlur(base, (0, 0), 4.5)
        base = base * (1 - wbg[..., None]) + far * wbg[..., None]
        # bloom on speculars
        lum = base.mean(2)
        hl = np.clip((lum - 0.82) / 0.18, 0, 1)[..., None] * base
        base = np.clip(base + 0.10 * cv2.GaussianBlur(hl, (0, 0), 14), 0, 1)
        base *= VIGNETTE
        # top-corner distractions (TV / CCTV / AC) dimmed 20%
        base *= DIM
        ctx.update(anchor=anchor(p), A=A, src_fi=fi, piece=p.name, src_t=fi / FPS)
        back = base.copy()
        for e in ELEMENTS:
            if e.layer == 'back' and e.active(t) or (isinstance(e, Hero) and e.layer == 'back' and e.active(t)):
                e.draw(back, t, ctx)
        img = base * m[..., None] + back * (1 - m[..., None])
        for e in ELEMENTS:
            if e.layer == 'front' and e.active(t):
                e.draw(img, t, ctx)
    else:
        ctx.update(anchor=(540, 700, 220), A=np.eye(2, 3, dtype=np.float32), src_fi=0, piece='END')
    for e in ELEMENTS:
        if e.layer == 'post' and e.active(t):
            e.draw(img, t, ctx)
    # watermark always on top (except under a full white flash it is simply covered)
    return np.clip(img, 0, 1)


DIM = np.ones((H, W, 1), np.float32)
_d = np.zeros((H, W), np.float32)
cv2.rectangle(_d, (0, 0), (W, 230), 1.0, -1)
_d = cv2.GaussianBlur(_d, (0, 0), 60)
DIM[..., 0] = 1 - 0.2 * _d


def reorder():
    # watermark must render after flashes? keep it under flashes but above everything else
    wm = [e for e in ELEMENTS if isinstance(e, Watermark)]
    rest = [e for e in ELEMENTS if not isinstance(e, Watermark)]
    fronts = [e for e in rest if e.layer != 'post']; posts = [e for e in rest if e.layer == 'post']
    ec = [e for e in posts if isinstance(e, EndCard)]; fl = [e for e in posts if not isinstance(e, EndCard)]
    for w in wm: w.layer = 'post'
    ELEMENTS[:] = fronts + ec + wm + fl


reorder()


def sfx_events():
    """(time, kind) list for the audio mix."""
    ev = []
    for e in ELEMENTS:
        if isinstance(e, Flash): ev.append((e.tc, 'whoosh_warm' if e.warm else 'whoosh'))
        elif isinstance(e, Icons): ev += [(e.t0 + (i * 3 + 7) / FPS, 'pop') for i in range(len(e.names))]
        elif isinstance(e, _CoinNext): ev.append((e.t0 + 7 / FPS, 'pop'))
        elif isinstance(e, CardRow): ev += [(tt, 'pop') for tt in e.times]
        elif isinstance(e, PhoneCards): ev += [(s[4] + 2 / FPS, 'swoosh_s') for s in e.specs]
        elif isinstance(e, Badge): ev.append((e.t0 + 6 / FPS, 'pop_big'))
        elif isinstance(e, Glass): ev.append((e.t0 + 3 / FPS, 'pop_big'))
        elif isinstance(e, Chart): ev += [(e.t0 + 6 / FPS, 'swoosh'), (e.t_pill, 'pop')]
        elif isinstance(e, Counter): ev += [(x, 'tick') for x in e.ticks()] + [(e.t_label, 'pop')]
        elif isinstance(e, (Spotlight, BoxGlow, HeartGlow)): ev.append((e.t0, 'sparkle'))
        elif isinstance(e, MoonRise): ev.append((e.t0, 'bells'))
        elif isinstance(e, EndCard): ev.append((e.t0 + 2 / FPS, 'pop_big'))
    return sorted(ev)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'info':
        for p in PCS: print(p.name, p.o0 / FPS, p.o1 / FPS, p.s)
        print('talk', TALK_FRAMES / FPS, 'total', TOTAL_FRAMES / FPS)
    elif mode == 'stills':
        os.makedirs(f'{WORK}/stills', exist_ok=True)
        for tt in sys.argv[2:]:
            k = int(float(tt) * FPS)
            im = (render_frame(k) * 255).astype(np.uint8)
            cv2.imwrite(f'{WORK}/stills/f_{float(tt):05.2f}.jpg', cv2.cvtColor(im, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    elif mode == 'chunk':
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '10', '-pix_fmt', 'yuv444p', out], stdin=subprocess.PIPE)
        for k in range(a, b):
            im = (render_frame(k) * 255 + 0.5).astype(np.uint8)
            enc.stdin.write(im.tobytes())
            if (k - a) % 30 == 0: print(out, k, flush=True)
        enc.stdin.close(); enc.wait()
    elif mode == 'events':
        json.dump({'pieces': [(p.name, p.a, p.b, p.o0, p.o1) for p in PCS], 'talk': TALK_FRAMES / FPS, 'total': TOTAL_FRAMES / FPS,
                   'sfx': sfx_events()}, open(f'{WORK}/events.json', 'w'), indent=1)
