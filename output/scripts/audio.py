# Builds the reel soundtrack: processed presenter voice (re-timed), synthesized corporate-pop bed, SFX.
import json, subprocess, sys, numpy as np
from scipy.signal import butter, sosfilt
S = sys.argv[1]; PRES = sys.argv[2]; OUT = sys.argv[3]
SR = 48000
ev = json.load(open(f"{S}/work/sfx.json")); DUR = ev["dur"]
NS = int(DUR * SR)
rng = np.random.default_rng(7)

def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)
def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i] * g
def midi(n): return 440 * 2 ** ((n - 69) / 12)

# ---------------- voice
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", PRES, "-vn", "-ac", "1", "-ar", str(SR), "-af",
                      "highpass=f=90,lowpass=f=13000,afftdn=nf=-28,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=5dB",
                      "-f", "f32le", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
voice = np.zeros(NS)
VSEG = [(0.0, 7.90, 0.0), (7.90, 23.67, 1.72), (23.67, 27.60, 9.49)]
for a, b, off in VSEG:
    seg = v[int(a * SR):int(b * SR)].astype(np.float64)
    f = int(0.02 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    add(voice, seg, a + off)
voice /= np.max(np.abs(voice)) + 1e-9; voice *= 0.9
vact = np.zeros(NS)
for a, b, off in VSEG: vact[int((a + off) * SR):int((b + off) * SR)] = 1

# ---------------- music: 120 bpm, I-V-vi-IV in C, one chord per bar
BPM = 120; beat = 60 / BPM; bar = 4 * beat
chords = [[48, 55, 60, 64, 67], [43, 50, 59, 62, 67], [45, 52, 57, 60, 64], [41, 48, 57, 60, 65]]
roots = [36, 31, 33, 29]
music = np.zeros((NS, 2))
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; ph = (f * (1 + det)) * t
    return 2 * (ph - np.floor(ph + 0.5))
nbars = int(DUR / bar) + 1
END_T = 37.10
def section(t):  # energy 0..1
    if t < 3.4: return 0.35
    if t < 31.6: return 1.0
    if t < 33.4: return 0.6
    if t < END_T: return 1.0
    return 0.3
for b_ in range(nbars):
    t0 = b_ * bar; ci = b_ % 4; n = int(bar * SR)
    # pad
    pad = np.zeros(n)
    for m in chords[ci][1:]:
        for d in (-0.004, 0.0, 0.005): pad += saw(midi(m + 12), n, d)
    pad = lp(pad, 2200) * 0.018
    e = np.minimum(np.arange(n) / (0.08 * SR), 1) * np.minimum((n - np.arange(n)) / (0.05 * SR), 1)
    pad *= e
    add(music[:, 0], pad, t0); add(music[:, 1], np.roll(pad, 240), t0)
    en = section(t0 + 0.01)
    for s16 in range(16):
        ts = t0 + s16 * beat / 4
        if ts >= DUR: break
        en = section(ts)
        # pluck arpeggio 16ths
        if en > 0.3:
            note = chords[ci][1:][[0, 2, 3, 1, 2, 3, 0, 3][s16 % 8]] + 24
            nn = int(0.22 * SR); tt = np.arange(nn) / SR
            pl = (np.sin(2 * np.pi * midi(note) * tt) + 0.35 * np.sin(4 * np.pi * midi(note) * tt)) * np.exp(-tt / 0.07)
            pan = 0.35 if s16 % 2 else -0.35
            g = 0.05 * (0.6 if en < 1 else 1.0)
            add(music[:, 0], pl, ts, g * (1 - pan)); add(music[:, 1], pl, ts, g * (1 + pan))
        if en < 0.5: continue
        # kick on beats
        if s16 % 4 == 0 and en >= 1.0:
            nn = int(0.35 * SR); tt = np.arange(nn) / SR
            f = 45 + 90 * np.exp(-tt / 0.03); ph = 2 * np.pi * np.cumsum(f) / SR
            k = np.sin(ph) * np.exp(-tt / 0.16); k[:200] += rng.normal(0, 0.3, 200) * np.linspace(1, 0, 200)
            add(music[:, 0], k, ts, 0.5); add(music[:, 1], k, ts, 0.5)
        # clap on 2 & 4
        if s16 in (4, 12) and en >= 1.0:
            nn = int(0.2 * SR); c = bp(rng.normal(0, 1, nn), 900, 3500) * env_ad(nn, 0.002, 0.05)
            add(music[:, 0], c, ts, 0.22); add(music[:, 1], c, ts + 0.008, 0.22)
        # hats: offbeat 8ths loud, 16ths soft
        nn = int(0.06 * SR); hh = hp(rng.normal(0, 1, nn), 7000) * env_ad(nn, 0.001, 0.015)
        g = 0.10 if s16 % 4 == 2 else 0.035
        add(music[:, 0], hh, ts, g * 0.8); add(music[:, 1], hh, ts, g)
        # bass offbeat 8ths
        if s16 % 2 == 1 and en >= 1.0 or (en < 1 and s16 % 4 == 2):
            nn = int(0.22 * SR); tt = np.arange(nn) / SR
            bs = np.tanh(1.8 * np.sin(2 * np.pi * midi(roots[ci]) * tt)) * env_ad(nn, 0.005, 0.12)
            add(music[:, 0], bs, ts, 0.16); add(music[:, 1], bs, ts, 0.16)
music[:, 0] = hp(music[:, 0], 30); music[:, 1] = hp(music[:, 1], 30)
# outro: let it ring then fade
fo = np.ones(NS); i0 = int((DUR - 2.2) * SR); fo[i0:] = np.linspace(1, 0, NS - i0) ** 1.5
music *= fo[:, None]

# ---------------- sfx
sfx = np.zeros((NS, 2))
def mono(x, t, g, pan=0.0): add(sfx[:, 0], x, t, g * (1 - pan)); add(sfx[:, 1], x, t, g * (1 + pan))
for t, k in ev["sfx"]:
    if k == "pop":
        nn = int(0.09 * SR); tt = np.arange(nn) / SR
        f = 500 + 900 * np.minimum(tt / 0.04, 1); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(nn, 0.002, 0.03)
        mono(x, t, 0.25)
    elif k == "tick":
        nn = int(0.02 * SR); x = hp(rng.normal(0, 1, nn), 4000) * env_ad(nn, 0.0005, 0.004)
        mono(x, t, 0.25)
    elif k in ("whoosh", "swish"):
        L = 0.45 if k == "whoosh" else 0.3; nn = int(L * SR); tt = np.arange(nn) / SR
        noise = rng.normal(0, 1, nn); out = np.zeros(nn); blk = 1024
        for i in range(0, nn, blk):
            u = i / nn; c = 400 + 4000 * np.sin(np.pi * u)
            out[i:i + blk] = bp(noise[max(0, i - 2048):i + blk], c * 0.6, c * 1.4)[-len(out[i:i + blk]):]
        e = np.sin(np.pi * tt / L) ** 2
        g = 0.35 if k == "whoosh" else 0.15
        add(sfx[:, 0], out * e, t, g * 1.2); add(sfx[:, 1], out * e[::-1] if False else out * e, t + 0.01, g)
    elif k == "riser":
        L = 1.75; nn = int(L * SR); tt = np.arange(nn) / SR
        f = 200 * 2 ** (tt / L * 3); x = 0.4 * saw(1, 1) if False else np.sin(2 * np.pi * np.cumsum(f) / SR)
        n2 = hp(rng.normal(0, 1, nn), 1500) * 0.5
        x = (x * 0.5 + n2) * (tt / L) ** 2
        mono(x, t, 0.25)
    elif k == "impact":
        nn = int(1.2 * SR); tt = np.arange(nn) / SR
        x = np.sin(2 * np.pi * (40 + 40 * np.exp(-tt / 0.05)) * tt) * np.exp(-tt / 0.35) + lp(rng.normal(0, 1, nn), 800) * np.exp(-tt / 0.15) * 0.5
        mono(x, t, 0.45)
    elif k == "shimmer":
        nn = int(2.5 * SR); tt = np.arange(nn) / SR; x = np.zeros(nn)
        for m in (72, 76, 79, 84, 88):
            x += np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt / 0.9) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * tt))
        mono(x, t, 0.05)
# opening boom
nn = int(1.5 * SR); tt = np.arange(nn) / SR
boom = np.sin(2 * np.pi * (38 + 30 * np.exp(-tt / 0.08)) * tt) * np.exp(-tt / 0.5)
mono(boom, 0.0, 0.5)

# ---------------- mix with ducking: music ~-18 dB under voice, up in gaps
k = int(0.15 * SR); ker = np.ones(k) / k
duck = np.convolve(vact, ker, "same")
gain = 10 ** ((-19 * duck + -7 * (1 - duck)) / 20)
mix = music * gain[:, None] + sfx * (0.55 + 0.45 * (1 - duck))[:, None] + voice[:, None] * 0.85
mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.8
mix.astype(np.float32).tofile(f"{S}/work/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{S}/work/mix.f32",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), "-c:a", "pcm_s16le", OUT], check=True)
print("ok")
