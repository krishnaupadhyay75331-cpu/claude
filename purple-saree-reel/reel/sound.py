# Procedural music bed + SFX library (44.1 kHz stereo float32)
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.01, d=0.2, s=0.6, r=0.3):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, np.float32)
    e[:a] = np.linspace(0, 1, a)
    e[a:a + d] = np.linspace(1, s, len(e[a:a + d]))
    if r > 0:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def lp(x, cutoff):
    # one-pole low-pass, cutoff may be an array
    a = np.exp(-2 * np.pi * np.asarray(cutoff, float) / SR) * np.ones(len(x))
    y = np.empty_like(x)
    z = 0.0
    for i in range(len(x)):
        z = (1 - a[i]) * x[i] + a[i] * z
        y[i] = z
    return y


def lp_fast(x, cutoff):
    # FFT brick-ish low-pass for constant cutoff
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def hp_fast(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (cutoff / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X, len(x))


def bp_sweep_noise(d, f0, f1, q=3.0):
    # noise through a moving band (STFT-domain), for whooshes / risers
    n = int(d * SR)
    x = rng.standard_normal(n)
    hop, win = 256, 1024
    out = np.zeros(n + win)
    w = np.hanning(win)
    frames = range(0, n - win, hop)
    for k, i in enumerate(frames):
        fc = f0 * (f1 / f0) ** (i / max(1, n - win))
        X = np.fft.rfft(x[i:i + win] * w)
        f = np.fft.rfftfreq(win, 1 / SR)
        X *= np.exp(-0.5 * ((np.log2(np.maximum(f, 1) / fc)) * q) ** 2)
        out[i:i + win] += np.fft.irfft(X, win) * w
    return out[:n] / (np.abs(out).max() + 1e-9)


def stereo(x, width=0.0, pan=0.0):
    l = x * np.sqrt(0.5 * (1 - pan))
    r = x * np.sqrt(0.5 * (1 + pan))
    if width:
        dly = int(0.011 * SR)
        r = np.concatenate([np.zeros(dly), r[:-dly]]) * (1 - width) + r * width
    return np.stack([l, r], 1).astype(np.float32)


def norm(x, peak_db):
    return x / (np.abs(x).max() + 1e-9) * 10 ** (peak_db / 20)


# ---------------- SFX ----------------
def whoosh(d=0.45, up=True):
    x = bp_sweep_noise(d, 300 if up else 3000, 3000 if up else 300, 2.2)
    e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    return stereo(x * e, 0.6)


def flash_hit():
    d = 0.5
    t = t_(d)
    click = rng.standard_normal(len(t)) * np.exp(-t * 90)
    shutter = hp_fast(rng.standard_normal(len(t)), 2500) * np.exp(-t * 25) * 0.6
    body = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 18) * 0.5
    return stereo(click + shutter + body, 0.4)


def shimmer(d=1.2):
    t = t_(d)
    x = np.zeros_like(t)
    for k, f in enumerate([2093, 2637, 3136, 4186, 5274]):
        st = k * 0.045
        tt = np.clip(t - st, 0, None)
        x += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3.5) * (t >= st) * (0.8 ** k)
    return stereo(x, 0.7)


def neon_buzz(d=0.45):
    t = t_(d)
    x = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.3 + np.sin(2 * np.pi * 240 * t) * 0.3
    flick = (rng.random(len(t) // 600 + 1) > 0.35).repeat(600)[:len(t)]
    x = lp_fast(x * flick, 2500) * np.exp(-t * 3)
    return stereo(x, 0.2)


def temple_bell(d=2.5, f=880):
    t = t_(d)
    partials = [(1.0, 1.0, 1.6), (2.0, 0.55, 2.4), (2.76, 0.4, 3.0), (5.4, 0.25, 5), (8.9, 0.12, 8)]
    x = sum(a * np.sin(2 * np.pi * f * r * t + 0.3 * r) * np.exp(-t * dc) for r, a, dc in partials)
    x *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    return stereo(x, 0.6)


def pop():
    t = t_(0.12)
    f = 900 * np.exp(-t * 30) + 250
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    return stereo(x, 0.1)


def bloop():
    t = t_(0.25)
    f = 300 + 500 * (1 - np.exp(-t * 25))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16) + lp_fast(rng.standard_normal(len(t)), 1200) * np.exp(-t * 40) * 0.3
    return stereo(x, 0.3)


def swell(d=1.6):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (220, 277.2, 329.6, 440))
    x += lp_fast(rng.standard_normal(len(t)), 1800) * 0.4
    e = (t / d) ** 2 * np.minimum(1, (d - t) * 6)
    return stereo(x * e, 0.8)


def riser(d=1.2):
    x = bp_sweep_noise(d, 200, 6000, 2.0)
    t = t_(d)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 800 * (t / d) ** 2) / SR) * 0.4
    e = (t / d) ** 2.2
    return stereo((x + tone) * e, 0.7)


def sub_boom():
    t = t_(1.3)
    f = 55 + 70 * np.exp(-t * 12)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    x += rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.2
    return stereo(x, 0.0)


def tape_whip():
    t = t_(0.5)
    f = 1200 * np.exp(-t * 6) + 60
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + bp_sweep_noise(0.5, 4000, 200, 2) * 0.7
    return stereo(x * np.exp(-t * 4), 0.5)


def sparkle():
    t = t_(0.9)
    x = np.zeros_like(t)
    for k in range(9):
        st = rng.uniform(0, 0.35)
        f = rng.uniform(3000, 7000)
        tt = np.clip(t - st, 0, None)
        x += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 14) * (t >= st)
    return stereo(x, 0.9)


# ---------------- music ----------------
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def hz(name, octv):
    return 440 * 2 ** ((NOTE[name] + 12 * (octv + 1) - 69) / 12)


def piano(f, d, vel=1.0):
    t = t_(d)
    x = np.zeros_like(t)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 12000:
            break
        x += np.sin(2 * np.pi * fk * t) * (1 / k ** 1.4) * np.exp(-t * (0.9 + 0.7 * k))
    x *= np.minimum(1, t / 0.004)
    x[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return x * vel


def pad(freqs, d):
    t = t_(d)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            ff = f * 2 ** (det / 12)
            x += np.sin(2 * np.pi * ff * t + rng.uniform(0, 6)) + 0.25 * np.sin(4 * np.pi * ff * t)
    x = lp_fast(x, 1400)
    e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
    return x * e / len(freqs)


def flute(f, d):
    t = t_(d)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    x += lp_fast(rng.standard_normal(len(t)), 3000) * 0.04
    return x * env_adsr(len(t), 0.18, 0.3, 0.75, min(0.5, d * 0.4))


def reverb(x, decay=2.2, mix=0.3):
    n = int(decay * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 6.9 / decay)
    ir = lp_fast(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    L = len(x) + n
    nf = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[:len(x)]
    return x * (1 - mix) + y * mix * 3


def _add(buf, s, x):
    if s >= len(buf):
        return
    n = min(len(x), len(buf) - s)
    buf[s:s + n] += x[:n]


def music(total, swell_at, happy_at, cta_at):
    """Dm-Bb-F-C melancholic bed -> swell -> warm Bb-C-F resolution."""
    out = np.zeros(int(total * SR) + SR)
    bpm = 70
    beat = 60 / bpm
    bar = 4 * beat
    sad = [("D", "F", "A"), ("A#", "D", "F"), ("F", "A", "C"), ("C", "E", "G")]
    happy = [("A#", "D", "F"), ("C", "E", "G"), ("F", "A", "C"), ("D", "F", "A"), ("A#", "D", "F"), ("C", "E", "G")]
    pads = np.zeros_like(out)
    pianos = np.zeros_like(out)
    flutes = np.zeros_like(out)
    t0 = 0.0
    i = 0
    melody_sad = [("A", 4), ("F", 4), ("E", 4), ("D", 4), ("C", 4), ("D", 4), ("F", 4), ("E", 4)]
    while t0 < total:
        sec_happy = t0 >= happy_at - 0.3
        chords = happy if sec_happy else sad
        ch = chords[i % len(chords)]
        root = ch[0]
        ns = int(t0 * SR)
        p = pad([hz(n, 3) for n in ch] + [hz(root, 2)], bar + 1.2)
        lvl = 0.5 if t0 < swell_at else 0.75
        _add(pads, ns, p * lvl)
        # arpeggio: sparse in the sad section, fuller later
        patt = [0, 2, 1, 2] if t0 < swell_at else [0, 1, 2, 1, 0, 2, 1, 2]
        step = bar / len(patt)
        for k, ix in enumerate(patt):
            n = ch[ix]
            o = 4 if ix else 3
            s = int((t0 + k * step) * SR)
            note = piano(hz(n, o), 2.5, 0.55 if k else 0.8)
            _add(pianos, s, note)
        bn = piano(hz(root, 2), 3.0, 0.6)
        _add(pianos, ns, bn)
        # flute phrase every other bar
        if i % 2 == 1 and t0 < total - 2:
            if sec_happy:
                mel = [(ch[2], 5), (ch[1], 5), (ch[0], 5)]
            else:
                mel = [melody_sad[(i + j) % len(melody_sad)] for j in range(2)]
            for j, (n, o) in enumerate(mel):
                s = int((t0 + j * bar / len(mel)) * SR)
                fl = flute(hz(n, o), bar / len(mel) * 1.1)
                _add(flutes, s, fl * 0.35)
        t0 += bar
        i += 1
        if not sec_happy and t0 > happy_at - 0.3:
            t0 = happy_at  # land the resolution exactly on the happy-ending cut
            i = 0
    tt = np.arange(len(out)) / SR
    dyn = 0.55 + 0.45 * np.clip((tt - swell_at) / 4, 0, 1)
    dyn *= 1 - 0.25 * np.clip((tt - cta_at) / 1.0, 0, 1)
    mix = (pads * 0.35 + pianos * 0.5 + flutes) * dyn
    mix = reverb(mix, 2.6, 0.35)
    fade = np.clip((total - tt) / 1.2, 0, 1) * np.clip(tt / 0.6, 0, 1)
    mix *= fade
    return stereo(mix[:int(total * SR)], 0.8)
