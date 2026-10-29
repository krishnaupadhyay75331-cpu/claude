"""Builds the reel soundtrack: tightened + processed voice, synthesized piano/pad bed, SFX, -14 LUFS master.

Usage: python3 audio.py <workdir>   -> writes <workdir>/mix_master.wav
All music and SFX are synthesized here (royalty-free by construction).
"""
import json, os, subprocess, sys
import numpy as np

WD = sys.argv[1]
sys.argv = ["render", WD]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R   # cut frames, transitions, word frames

SR = 48000
FPS = 30
P = json.load(open(os.path.join(WD, "plan.json")))
NTOT = P["total"]
DUR = NTOT / FPS
NS = int(round(DUR * SR))
rng = np.random.default_rng(11)

def ff_read(path, sr, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch)

def ff_write(path, x, sr):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(x.shape[1]), "-i", "-", "-c:a", "pcm_f32le", path], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(x, np.float32).tobytes()); p.stdin.close(); p.wait()

# ------------------------------------------------------------ 1. voice: splice at the same frame boundaries as the picture
src = ff_read(os.path.join(WD, "src.mov"), SR, 1)[:, 0]
spf = SR // FPS
xf = int(0.008 * SR)
ramp = np.linspace(0, 1, xf, dtype=np.float32)
voice = np.zeros(0, np.float32)
for a, b in P["segs"]:
    seg = src[a * spf: b * spf + xf].copy()   # each segment carries xf extra samples that overlap the next one
    if len(voice):
        voice[-xf:] = voice[-xf:] * (1 - ramp) + seg[:xf] * ramp
        seg = seg[xf:]
    voice = np.concatenate([voice, seg])
voice = np.pad(voice, (0, max(0, NS - len(voice))))[:NS]
voice[:int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))
ff_write(os.path.join(WD, "voice_raw.wav"), voice[:, None], SR)
chain = ("afftdn=nr=10:nf=-50:tn=1,highpass=f=80,equalizer=f=3500:t=q:w=1.2:g=2,"
         "deesser=i=0.35:m=0.5:f=0.5,acompressor=threshold=-18dB:ratio=3.5:attack=4:release=90:makeup=3,"
         "acompressor=threshold=-10dB:ratio=6:attack=1:release=60")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WD, "voice_raw.wav"), "-af", chain, "-c:a", "pcm_f32le", os.path.join(WD, "voice_proc.wav")], check=True)
vp = ff_read(os.path.join(WD, "voice_proc.wav"), SR, 1)[:, 0][:NS]
vp = np.pad(vp, (0, NS - len(vp)))

# voice activity envelope (for ducking) from word timings in output frames
act = np.zeros(NS, np.float32)
for w in P["words"]:
    a = int(w["of"] / FPS * SR); b = int((max(w["oe"], w["of"] + 3)) / FPS * SR)
    act[max(a - 2400, 0):min(b + 4800, NS)] = 1
k = np.ones(int(.12 * SR), np.float32) / int(.12 * SR)
act = np.convolve(act, k, "same")
speech_rms = np.sqrt(np.mean(vp[act > .5] ** 2))
vdb = 20 * np.log10(speech_rms)

# ------------------------------------------------------------ 2. music bed: 72 BPM ambient piano + pad
t_all = np.arange(NS) / SR
def midi_hz(m): return 440 * 2 ** ((m - 69) / 12)
CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [48, 52, 55], "G": [55, 59, 62], "Fadd9": [53, 57, 60, 67], "Cmaj": [48, 55, 60, 64]}
bar = 60 / 72 * 4
lift_t = R.OF[61] / FPS          # B5 method/solution starts (pills)
swell_t = R.c17 / FPS            # B7 happy ending
resolve_t = R.c18 / FPS          # B8 CTA
prog = []
t = 0.0
seq = ["Am", "F", "C", "G"]
i = 0
while t < swell_t - .01:
    nxt = min(t + bar, swell_t)
    prog.append((t, nxt, seq[i % 4])); t = nxt; i += 1
prog += [(swell_t, swell_t + (resolve_t - swell_t) * .55, "Fadd9"), (swell_t + (resolve_t - swell_t) * .55, resolve_t, "G"), (resolve_t, DUR + 1, "Cmaj")]

def piano_note(f, dur, vel):
    n = int(dur * SR); tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for h in range(1, 9):
        fh = f * h * (1 + 0.0004 * h * h)
        if fh > 9000: break
        out += (vel / h ** 1.6) * np.exp(-tt * (0.9 + 0.55 * h)) * np.sin(2 * np.pi * fh * tt + rng.uniform(0, 6))
    att = np.clip(tt / .006, 0, 1)
    rel = np.clip((dur - tt) / .25, 0, 1)
    return out * att * rel

def place(buf, x, t0, gain=1.0, pan=0.0):
    a = int(t0 * SR)
    if a >= len(buf): return
    x = x[:len(buf) - a]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[a:a + len(x), 0] += x * gain * l * 1.41
    buf[a:a + len(x), 1] += x * gain * r * 1.41

music = np.zeros((NS, 2), np.float32)
beat = bar / 4
for (t0, t1, name) in prog:
    notes = CH[name]
    # piano: soft broken chord on every beat, low root on the downbeat
    bt = t0; j = 0
    while bt < t1 - 1e-3:
        if bt >= resolve_t:   # resolve: one held chord
            for m in notes: place(music, piano_note(midi_hz(m + 12), DUR - bt + .3, .22), bt, pan=rng.uniform(-.3, .3))
            place(music, piano_note(midi_hz(notes[0] - 12), DUR - bt + .3, .3), bt)
            break
        m = notes[[0, 2, 1, 2][j % 4]] + 12
        place(music, piano_note(midi_hz(m), 1.8, .18 if j % 4 else .24), bt, pan=[-.25, .2, -.1, .3][j % 4])
        if j % 4 == 0: place(music, piano_note(midi_hz(notes[0] - 12), 2.6, .22), bt)
        if bt >= lift_t:      # hopeful lift: gentle eighth-note arpeggio an octave up
            for e in range(2):
                mm = notes[(j * 2 + e) % len(notes)] + 24
                place(music, piano_note(midi_hz(mm), .9, .06 if bt < swell_t else .09), bt + e * beat / 2, pan=.4 - .8 * e)
        bt += beat; j += 1
    # pad: detuned saw stack, slow attack
    n = int((t1 - t0 + 1.2) * SR); tt = np.arange(n) / SR
    pad = np.zeros(n, np.float32)
    for m in notes:
        for det in (-.12, 0, .11):
            f = midi_hz(m + det)
            ph = (f * tt + rng.uniform()) % 1.0
            pad += (2 * ph - 1) * .05
    # one-pole low-pass, brighter from the lift, warm swell on the happy ending
    cutoff = 900 if t0 < lift_t else 1500 if t0 < swell_t else 2400
    a = np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter  # noqa
    pad = lfilter([1 - a], [1, -a], lfilter([1 - a], [1, -a], pad)).astype(np.float32)
    env = np.clip(tt / 1.0, 0, 1) * np.clip((t1 - t0 + 1.2 - tt) / 1.2, 0, 1)
    g = .55 if t0 < lift_t else .7 if t0 < swell_t else 1.25
    if name == "Cmaj": env = np.clip(tt / .25, 0, 1)
    place(music, pad * env, t0, g * .6, -.15); place(music, np.roll(pad, 300) * env, t0, g * .6, .15)

# reverb: stereo exponentially-decaying noise IR
from scipy.signal import fftconvolve
ir_n = int(2.6 * SR); irt = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-irt * 2.6); irR = rng.standard_normal(ir_n) * np.exp(-irt * 2.6)
irL[:int(.012 * SR)] = 0; irR[:int(.017 * SR)] = 0
wet = np.stack([fftconvolve(music[:, 0], irL)[:NS], fftconvolve(music[:, 1], irR)[:NS]], 1)
wet /= np.max(np.abs(wet)) + 1e-9
music = music / (np.max(np.abs(music)) + 1e-9) * .7 + wet * .45
# arc: swell into the happy ending, hard stop at the last frame (10 ms de-click)
arc = np.ones(NS, np.float32)
sw = (t_all >= swell_t - 1.5) & (t_all < resolve_t)
arc[sw] = 1 + .9 * np.clip((t_all[sw] - (swell_t - 1.5)) / 1.5, 0, 1)
arc[t_all >= resolve_t] = 1.5
music *= arc[:, None]
music[-int(.01 * SR):] *= np.linspace(1, 0, int(.01 * SR))[:, None]
m_rms = np.sqrt(np.mean(music[t_all < swell_t] ** 2))
music *= 10 ** ((vdb - 12) / 20) / m_rms
duck = 10 ** (-4 * act / 20)
music *= duck[:, None]

# ------------------------------------------------------------ 3. SFX (synthesized)
from scipy.signal import butter, sosfilt
def bp_noise(n, lo, hi):
    return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), rng.standard_normal(n)).astype(np.float32)
def whoosh(d=.55):
    n = int(d * SR); tt = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k, (lo, hi) in enumerate([(200, 900), (600, 2500), (1500, 6000)]):
        x += bp_noise(n, lo, hi) * (1 - k * .25)
    env = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 1.5
    return x * env / (np.max(np.abs(x * env)) + 1e-9)
def shimmer(d=.9):
    n = int(d * SR); tt = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * (1 + .5 * np.sin(2 * np.pi * rng.uniform(9, 15) * tt)) for f in (2637, 3136, 3951, 4699, 5274))
    env = np.exp(-tt * 3.2) * np.clip(tt / .03, 0, 1)
    return (x * env / 5).astype(np.float32)
def pop():
    n = int(.12 * SR); tt = np.arange(n) / SR
    f = 900 * np.exp(-tt * 25) + 180
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 38)).astype(np.float32)
def tick():
    n = int(.03 * SR); tt = np.arange(n) / SR
    return (bp_noise(n, 2500, 7000) * np.exp(-tt * 250)).astype(np.float32)
def buzz(d=.5, flick=True):
    n = int(d * SR); tt = np.arange(n) / SR
    x = sum(np.sign(np.sin(2 * np.pi * 120 * h * tt)) / h ** 1.3 for h in (1, 2, 3)) * .3
    x = sosfilt(butter(2, [150, 3000], "bandpass", fs=SR, output="sos"), x)
    env = np.ones(n)
    if flick:
        for (a, b, v) in ((0, .033, 1), (.033, .066, .1), (.066, .1, .7), (.1, .133, .2)):
            env[int(a * SR):int(b * SR)] = v
    env *= np.clip((d - tt) / .2, 0, 1)
    return (x * env).astype(np.float32)
def hit():
    n = int(.35 * SR); tt = np.arange(n) / SR
    th = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 9) + 45) / SR) * np.exp(-tt * 11)
    return (th * .9 + np.pad(whoosh(.25), (0, n - int(.25 * SR))) * .6).astype(np.float32)
def riser(d=1.6):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 200 * (1 + 6 * (tt / d) ** 2)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * .4 + bp_noise(n, 800, 8000) * .5 * (tt / d)
    return (x * (tt / d) ** 2).astype(np.float32)

sfx = np.zeros((NS, 2), np.float32)
ref = 10 ** (vdb / 20)
def add(x, frame, db, pan=0.0):
    pk = np.max(np.abs(x)) + 1e-9
    place(sfx, x / pk, frame / FPS, ref * 2.2 * 10 ** (db / 20), pan)
events = []
for c, kind in R.TRANS:
    add(whoosh(), c - 6, -8, -.2); add(shimmer(), c, -14, .2); events.append((c - 6, f"whoosh+shimmer ({kind})"))
for (n0, sz) in ((R.c1 * 0 + 8, 0), (R.c1 + 6, 0)):   # neon "?" flicker-on (S1 and card A)
    add(buzz(.9), n0, -18, .1); events.append((n0, "neon buzz/flicker"))
add(pop(), R.c2 + 6, -10, -.3); events.append((R.c2 + 6, "thought-bubble pop"))
for s in R.SNAPS: add(hit(), s, -10); events.append((s, "whoosh-hit (snap zoom)"))
add(shimmer(1.1), R.OF[54] + 4, -12, .3); events.append((R.OF[54] + 4, "gold sparkle shimmer"))
add(riser(1.6), R.c17 - 6 - 48, -12); events.append((R.c17 - 54, "riser into happy ending"))
pill_words = [(61, "Kundli Vishleshan"), (63, "Face Reading"), (65, "Prashna Kundli"), (68, "Vastu"), (101, "consultation")]
for wi, text in pill_words:
    for k in range(len(text)):
        add(tick(), R.OF[wi] + 4 + k * 1.5, -24, .15)
    events.append((R.OF[wi] + 4, f"typewriter ticks: {text}"))
add(tick(), R.c18 + 7, -24); events.append((R.c18 + 3, "CTA pill"))
json.dump(sorted(events), open(os.path.join(WD, "sfx_events.json"), "w"))

# ------------------------------------------------------------ 4. mix + master
mix = vp[:, None] * np.ones((1, 2), np.float32) + music + sfx
mix[-int(.005 * SR):] *= np.linspace(1, 0, int(.005 * SR))[:, None]
ff_write(os.path.join(WD, "mix_pre.wav"), mix, SR)
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", os.path.join(WD, "mix_pre.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=4:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
js = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=4:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,alimiter=limit=0.85:level=false")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WD, "mix_pre.wav"), "-af", ln, "-ar", "48000", "-c:a", "pcm_f32le", os.path.join(WD, "mix_master.wav")], check=True)
print("voice speech rms dB", round(vdb, 1), "measured", js["input_i"], js["input_lra"])
