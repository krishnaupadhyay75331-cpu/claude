# Audio: tighten pauses (same KEEP list as picture), clean voice, music bed with ducking, SFX, loudness
# usage: python3 mix.py SRC.mov out.wav
import os
import sys
import subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound as S
import plan as P

SRC, OUT = sys.argv[1], sys.argv[2]
SR = S.SR
work = os.path.dirname(os.path.abspath(OUT))

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.float32).reshape(-1, 2)

# ---- tighten pauses: concat kept ranges with 8 ms equal-power crossfades
xf = int(0.008 * SR)
parts = []
segs = []
o = 0.0
for s, e in P.KEEP:
    seg = a[int(s * SR):int(e * SR)].copy()
    segs.append((s, e, o))
    o += e - s
    parts.append(seg)
voice = parts[0]
for p in parts[1:]:
    fo = np.cos(np.linspace(0, np.pi / 2, xf))[:, None]
    fi = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
    voice = np.concatenate([voice[:-xf], voice[-xf:] * fo + p[:xf] * fi, p[xf:]])
AROLL_END = o
TOTAL = AROLL_END + P.FREEZE
voice = np.concatenate([voice, np.zeros((int(TOTAL * SR) - len(voice) + SR, 2), np.float32)])[:int(TOTAL * SR)]


def s2o(t):
    for s, e, oo in segs:
        if t < s:
            return oo
        if t <= e:
            return oo + t - s
    return AROLL_END


# ---- voice chain (ffmpeg): HPF 80, light denoise/room reduction, de-ess, 3:1 comp
vin = os.path.join(work, "_voice_in.f32")
vout = os.path.join(work, "_voice_out.f32")
voice.astype(np.float32).tofile(vin)
chain = ("highpass=f=80,afftdn=nr=8:nf=-42,deesser=i=0.35:m=0.5:f=0.5,"
         "volume=-8dB,acompressor=threshold=-24dB:ratio=3:attack=8:release=120:makeup=4dB")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", vin, "-af", chain,
                "-f", "f32le", "-ar", str(SR), "-ac", "2", vout], check=True)
voice = np.fromfile(vout, np.float32).reshape(-1, 2)[:int(TOTAL * SR)]

# ---- music bed
m = S.music(TOTAL, swell_at=s2o(P.MUSIC["swell"]), happy_at=s2o(P.MUSIC["happy"]), cta_at=s2o(P.MUSIC["cta"]))
m = m[:len(voice)]
if len(m) < len(voice):
    m = np.concatenate([m, np.zeros((len(voice) - len(m), 2), np.float32)])
# sidechain duck: -8 dB while she speaks (smoothed envelope of the voice)
env = np.abs(voice).mean(1)
win = int(0.05 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
speaking = (env > 10 ** (-38 / 20)).astype(np.float32)
att, rel = int(0.03 * SR), int(0.35 * SR)
g = np.zeros_like(speaking)
cur = 0.0
for i in range(0, len(speaking), 64):
    tgt = speaking[i]
    k = att if tgt > cur else rel
    cur += (tgt - cur) * min(1, 64 / k)
    g[i:i + 64] = cur
duck = 10 ** ((-8 * g) / 20)
# music bed ~ -22 dB under voice (relative), applied as peak-normalised level
m = S.norm(m, -20.0) * duck[:, None]

# ---- SFX
fx = np.zeros_like(voice)
lib = dict(whoosh=S.whoosh, flash=S.flash_hit, shimmer=S.shimmer, neon=S.neon_buzz, bell=S.temple_bell,
           pop=S.pop, bloop=S.bloop, swell=S.swell, riser=S.riser, boom=S.sub_boom, whip=S.tape_whip, sparkle=S.sparkle)
for (t_src, name, dt, peak) in P.SFX:
    clip = S.norm(lib[name](), peak)
    st = int((s2o(t_src) + dt) * SR)
    if st < 0:
        clip = clip[-st:]
        st = 0
    n = min(len(clip), len(fx) - st)
    if n > 0:
        fx[st:st + n] += clip[:n]

mixd = voice + m + fx
tmp = os.path.join(work, "_mix.f32")
mixd.astype(np.float32).tofile(tmp)
# two-pass loudnorm to -14 LUFS / -1 dBTP
p1 = subprocess.run(["ffmpeg", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp, "-af",
                     "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
import json
js = json.loads(p1[p1.rfind("{"):p1.rfind("}") + 1])
flt = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
       f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,"
       f"alimiter=limit=0.89:level=false")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp, "-af", flt,
                "-ar", str(SR), "-c:a", "pcm_s24le", OUT], check=True)
for f in (vin, vout, tmp):
    os.remove(f)
print("audio", TOTAL)
