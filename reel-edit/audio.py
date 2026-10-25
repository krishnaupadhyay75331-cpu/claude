"""Voice clean-up + cut, synthesised festive beat, SFX, mix to -14 LUFS."""
import numpy as np, subprocess, json, wave, math

S = '/tmp/claude-0/-home-user-claude/72bc255f-5202-5cbe-bb9b-e101156314d2/scratchpad'
WK = f'{S}/work'
V = '/root/.claude/uploads/72bc255f-5202-5cbe-bb9b-e101156314d2/a223cf04-copy_E9820242-9872-4BF7-A635-D83D49897C5E-compressed.mov'
SR = 48000
ev = json.load(open(f'{WK}/events.json'))
TOTAL, TALK = ev['total'], ev['talk']
rng = np.random.RandomState(42)


def rd(path):
    w = wave.open(path); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a


def wr(path, a):
    a = np.clip(a, -1, 1)
    w = wave.open(path, 'wb'); w.setnchannels(a.shape[1] if a.ndim > 1 else 1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()


# ---------------- voice
chain = ('highpass=f=80,afftdn=nf=-32:nr=10,equalizer=f=3500:t=q:w=1.2:g=2,'
         'deesser=i=0.35,acompressor=threshold=0.1:ratio=3:attack=8:release=120:makeup=1.6')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', V, '-vn', '-ac', '1', '-ar', str(SR), '-af', chain, f'{WK}/voice_full.wav'], check=True)
vf = rd(f'{WK}/voice_full.wav')
FPS = 30
voice = np.zeros(int(TOTAL * SR) + SR, np.float32)
pieces = ev['pieces']
# per-piece level matching (question voice vs shopkeeper)
def rms(x): return math.sqrt(float(np.mean(x ** 2)) + 1e-12)
lv = []
for name, a, b, o0, o1 in pieces:
    seg = vf[int(round(a * FPS)) * SR // FPS:int(round(b * FPS)) * SR // FPS]
    act = seg[np.abs(seg) > 0.01]
    lv.append(rms(act) if len(act) > 100 else None)
ref = np.median([x for x in lv if x])
prev_end = None
for (name, a, b, o0, o1), l in zip(pieces, lv):
    s0 = int(round(a * FPS)) * SR // FPS; s1 = int(round(b * FPS)) * SR // FPS
    seg = vf[s0:s1].copy()
    g = np.clip(ref / l, 0.6, 1.8) if l else 1.0
    seg *= g
    contiguous = prev_end is not None and prev_end == s0
    fl = int(0.006 * SR)
    if not contiguous: seg[:fl] *= np.linspace(0, 1, fl)
    seg[-fl:] *= np.linspace(1, 0, fl) if True else 1
    d0 = o0 * SR // FPS
    voice[d0:d0 + len(seg)] += seg
    prev_end = s1
# undo the tail fade on contiguous joins (re-add the missing part smoothly is negligible at 6ms)

# speech envelope for ducking
env = np.abs(voice)
k = int(0.25 * SR)
envs = np.convolve(env, np.ones(k) / k, 'same')
speech = np.clip((envs - 0.004) / 0.01, 0, 1)

# ---------------- music (116 BPM festive fusion groove, original synthesis)
BPM = 116; beat = 60 / BPM; s16 = beat / 4
N = len(voice); t_all = np.arange(N) / SR
mus = np.zeros((N, 2), np.float32)


def add(buf, start, sig, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= len(buf): return
    sig = sig[:len(buf) - i] * gain
    l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.414 / 2 * 2 ** .5
    buf[i:i + len(sig), 1] += sig * r * 1.414 / 2 * 2 ** .5


def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))


def dhol_low(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 58 + 60 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env_exp(n, 0.16) + 0.25 * np.sin(2 * ph) * env_exp(n, 0.05)
    s[:int(0.004 * SR)] += rng.randn(int(0.004 * SR)) * 0.4
    return s * 0.9


def dhol_high(dur=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 410 * t) * env_exp(n, 0.05) + 0.5 * np.sin(2 * np.pi * 690 * t) * env_exp(n, 0.03)
    nz = rng.randn(n) * env_exp(n, 0.012)
    nz = np.convolve(nz, [1, -0.9], 'same')
    return (tone * 0.5 + nz * 0.35)


def tabla_na(f0=520, dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f0 * m * t) * env_exp(n, 0.09 / m) for a, m in [(1, 1), (0.5, 2.02), (0.3, 3.1)])
    return s * 0.35


def shaker(dur=0.06):
    n = int(dur * SR)
    nz = rng.randn(n)
    nz = nz - np.convolve(nz, np.ones(6) / 6, 'same')
    return nz * env_exp(n, 0.015) * 0.18


def pluck(freq, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    saw = 2 * ((freq * t) % 1) - 1
    sq = np.sign(np.sin(2 * np.pi * freq * 2 * t)) * 0.2
    s = (saw + sq) * env_exp(n, 0.08)
    # one-pole lowpass with decaying cutoff
    out = np.zeros(n); y = 0.0
    a = np.exp(-2 * np.pi * (600 + 3500 * np.exp(-t / 0.05)) / SR)
    for i in range(n):
        y = (1 - a[i]) * s[i] + a[i] * y; out[i] = y
    return out * 0.35


def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    e = np.minimum(1, t / 0.01) * env_exp(n, dur * 0.7)
    return s * e * 0.45


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.003, 0.003):
            s += np.sin(2 * np.pi * f * (1 + d) * t + rng.rand() * 6)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return s * e * 0.05


def note(n): return 440 * 2 ** ((n - 69) / 12)

# D major: D Bm G A  (I vi IV V), one bar each
chords = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]]
roots = [38, 35, 31, 33]
arp = [0, 1, 2, 1, 2, 0, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1]
bar = beat * 4
nbars = int(TOTAL / bar) + 2
for b in range(nbars):
    t0 = b * bar
    ch = chords[b % 4]
    add(mus, t0, pad([note(x) for x in ch], bar), 0, 1.0)
    for i in range(16):
        tt = t0 + i * s16
        if i in (0, 6, 8, 11):
            add(mus, tt, dhol_low(), 0, 0.9)
        if i in (4, 12):
            add(mus, tt, dhol_high(), 0.1, 0.8)
        if i in (2, 10, 14):
            add(mus, tt, tabla_na(520 if i != 14 else 610), -0.25, 0.6)
        add(mus, tt, shaker(), 0.35, 0.9 if i % 4 == 2 else 0.5)
        if i % 2 == 0:
            add(mus, tt, pluck(note(ch[arp[i]] + 12)), -0.3 if i % 4 else 0.3, 0.55)
        if i in (0, 3, 6, 8, 10, 14):
            add(mus, tt, bass(note(roots[b % 4]), s16 * 2.5), 0, 0.9)
# intro: filter-ish fade in over first 0.4s
fi = int(0.4 * SR); mus[:fi] *= np.linspace(0.3, 1, fi)[:, None]
mus /= np.max(np.abs(mus)) + 1e-9

# music level: about -24 dB under voice, -3 dB extra ducking on speech, -18 dB on end card
def db(x): return 10 ** (x / 20)
gain = np.full(N, db(-20.5), np.float32)
gain *= (1 - speech * (1 - db(-3)))
endc = t_all >= TALK
ramp = np.clip((t_all - TALK) / 0.25, 0, 1)
gain = gain * (1 - ramp) + db(-13.0) * ramp
tail = np.clip((TOTAL - t_all) / 1.2, 0, 1)
gain *= tail
mus *= gain[:, None]

# ---------------- SFX
sfx = np.zeros((N, 2), np.float32)


def whoosh(dur=0.6, warm=False):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.randn(n)
    out = np.zeros(n)
    fc = 300 * (12 ** (t / dur))
    y1 = y2 = 0.0
    for i in range(n):  # 2-pole resonant bandpass sweep
        w = 2 * np.pi * fc[i] / SR; r = 0.97
        y = nz[i] * (1 - r) + 2 * r * np.cos(w) * y1 - r * r * y2
        y2, y1 = y1, y; out[i] = y
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    s = out * e
    if warm:
        s += 0.2 * np.sin(2 * np.pi * 180 * t) * e
    return s / (np.max(np.abs(s)) + 1e-9) * 0.5


def pop(f0=900, f1=300, dur=0.09, g=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.015)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.025)
    s[:60] += rng.randn(60) * 0.3
    return s * g


def tick():
    n = int(0.02 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * env_exp(n, 0.003) + rng.randn(n) * env_exp(n, 0.0015) * 0.3) * 0.35


def sparkle():
    out = np.zeros(int(0.9 * SR))
    for j in range(7):
        f = rng.choice([2093, 2637, 3136, 3520, 4186]) * (1 + rng.rand() * 0.01)
        n = int(0.5 * SR); t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.12) * 0.12
        i = int(j * 0.06 * SR); out[i:i + n] += s[:len(out) - i]
    return out


def bells():
    out = np.zeros(int(1.0 * SR))
    for j in range(16):
        n = int(0.25 * SR); t = np.arange(n) / SR
        f = 3000 + rng.rand() * 3500
        s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * env_exp(n, 0.04) * 0.06
        i = int(rng.rand() * 0.6 * SR); out[i:i + n] += s[:len(out) - i]
    return out


def swoosh(): return whoosh(0.35) * 0.7


for tt, kind in ev['sfx']:
    if kind.startswith('whoosh'):
        add(sfx, tt - 0.42, whoosh(0.6, kind == 'whoosh_warm'), 0.0, db(-15))
    elif kind == 'pop':
        add(sfx, tt - 0.01, pop(), rng.uniform(-.3, .3), db(-17))
    elif kind == 'pop_big':
        add(sfx, tt - 0.01, pop(700, 220, 0.14, 0.6), 0, db(-16))
    elif kind == 'tick':
        add(sfx, tt, tick(), 0.2, db(-19))
    elif kind == 'sparkle':
        add(sfx, tt, sparkle(), 0.2, db(-16))
    elif kind == 'bells':
        add(sfx, tt, bells(), -0.2, db(-17))
    elif kind in ('swoosh', 'swoosh_s'):
        add(sfx, tt - 0.12, swoosh(), -0.4 if kind == 'swoosh_s' else 0, db(-17))

mix = mus + sfx + voice[:, None]
mix = mix[:int(TOTAL * SR)]
wr(f'{WK}/mix_raw.wav', mix * 0.7)
# 2-pass loudnorm to -14 LUFS / -1 dBTP
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{WK}/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True)
js = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{WK}/mix_raw.wav', '-af', af, '-ar', '48000', f'{WK}/mix.wav'], check=True)
print('measured', js['input_i'], '->', 'done')
