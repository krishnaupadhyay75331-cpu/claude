"""Voice cleanup + original synthesized music bed + synthesized SFX + final mix.

usage: python3 audio.py SOURCE.mov build/video_only.mp4 out/reel.mp4
Needs build/sfx_events.json (written by render.py).
"""
import json
import os
import subprocess
import sys

import numpy as np

from timeline import END, FPS, SEGS

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
N = int(round(END * SR))
rng = np.random.default_rng(5)


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                         stdin=subprocess.PIPE)
    p.communicate(pcm.tobytes())


def read_wav(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ar", str(SR), "-ac", "2", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    return float(j["input_i"]), float(j["input_tp"])


def db(x):
    return 10 ** (x / 20)


# ---------------------------------------------------------------- voice
def voice(src):
    parts, labels = [], []
    for i, (a, b) in enumerate(SEGS):
        t0, t1 = a / FPS, b / FPS
        parts.append(f"[0:a]atrim={t0:.4f}:{t1:.4f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.012,afade=t=out:st={t1 - t0 - 0.012:.4f}:d=0.012[s{i}]")
        labels.append(f"[s{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(SEGS)}:v=0:a=1," \
        "aresample=48000,highpass=f=80,afftdn=nr=8:nf=-44,deesser=i=0.3,alimiter=limit=0.89:level=false[v]"
    out = os.path.join(BUILD, "voice.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[v]", "-ac", "2", "-ar", str(SR), out])
    x = read_wav(out)
    y = np.zeros((N, 2), np.float32)
    y[:min(N, len(x))] = x[:N]
    return y


# ---------------------------------------------------------------- music
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(freq, dur, vel):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for k in range(1, 7):
        x += (1 / k ** 1.4) * np.sin(2 * np.pi * freq * k * (1 + 0.0004 * k) * t) * np.exp(-t * (1.2 + 0.9 * k))
    x *= np.minimum(1, t / 0.004) * vel
    return x


def pad_voice(freq, dur, att=0.9, rel=1.4):
    t = np.arange(int((dur + rel) * SR)) / SR
    env = np.minimum(1, t / att) * np.where(t > dur, np.exp(-(t - dur) / (rel / 3)), 1)
    l = np.sin(2 * np.pi * freq * 0.9985 * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t + 1)
    r = np.sin(2 * np.pi * freq * 1.0015 * t) + 0.25 * np.sin(2 * np.pi * freq * 2.001 * t)
    trem = 1 + 0.06 * np.sin(2 * np.pi * 0.35 * t)
    return np.stack([l, r], 1) * (env * trem)[:, None]


CH = {
    "Am": [45, 52, 59, 60, 64], "F": [41, 48, 57, 64, 67], "C": [36, 43, 52, 60, 64],
    "G": [43, 50, 59, 62, 67], "Am2": [45, 52, 57, 60, 71],
}


def music(ev):
    lift = ev["music_lift"]
    swell = ev["music_swell"]
    res = ev["music_resolve"]
    prog = [(0.0, "Am", 0.5), (3.2, "F", 0.5), (6.4, "Am", 0.5), (8.4, "F", 0.55),
            (lift, "C", 0.7), (lift + 2.4, "G", 0.7), (lift + 4.8, "Am2", 0.7), (lift + 7.2, "F", 0.72),
            (swell, "F", 1.0), (swell + 1.4, "G", 1.0), (res, "C", 0.9)]
    out = np.zeros((N + SR * 3, 2))
    for i, (t0, name, g) in enumerate(prog):
        t1 = prog[i + 1][0] if i + 1 < len(prog) else END + 0.5
        for m in CH[name][:4]:
            pv = pad_voice(midi(m), max(0.3, t1 - t0)) * g * 0.05
            a = int(t0 * SR)
            out[a:a + len(pv)] += pv[:len(out) - a]
        # piano arpeggio
        notes = [m + 12 for m in CH[name][1:]]
        step = 0.8 if t0 < lift else 0.4
        if name == "C" and t0 >= res - 1e-6:  # resolve: one block chord on the last word
            for j, m in enumerate([48, 55, 60, 64, 67, 72]):
                p = piano(midi(m), 3.0, 0.16)
                a = int((t0 + 0.012 * j) * SR)
                pan = 0.5 + 0.3 * (j / 5 - 0.5)
                out[a:a + len(p), 0] += p[:len(out) - a] * (1 - pan) * 2
                out[a:a + len(p), 1] += p[:len(out) - a] * pan * 2
            continue
        t, j = t0, 0
        while t < t1 - 0.05:
            m = notes[[0, 2, 1, 3, 2, 1][j % 6] % len(notes)]
            if t0 >= swell:
                m += 12 if j % 2 else 0
            vel = (0.13 if t0 < lift else 0.15) * (1.0 if j % 2 == 0 else 0.75)
            p = piano(midi(m), 2.2, vel)
            a = int(t * SR)
            pan = rng.uniform(0.35, 0.65)
            out[a:a + len(p), 0] += p[:len(out) - a] * (1 - pan) * 2
            out[a:a + len(p), 1] += p[:len(out) - a] * pan * 2
            t += step
            j += 1
    out = reverb(out, 2.4, 0.35)
    out = out[:N]
    fade = int(0.04 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out.astype(np.float32)


def reverb(x, secs, wet):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / secs)[:, None]
    ir[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    ir /= np.sqrt((ir ** 2).sum(0))
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[:len(x)]
                  for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 0.9


# ---------------------------------------------------------------- sfx
def onepole_lp(x, cut):
    """Time-varying one-pole lowpass; cut = array of cutoff Hz."""
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.zeros_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def norm_peak(x, dbfs):
    return x / (np.abs(x).max() + 1e-9) * db(dbfs)


def whoosh():
    pre, post = 0.38, 0.32
    n = int((pre + post) * SR)
    t = np.arange(n) / SR
    q = t / (pre + post)
    cut = 300 + 5200 * np.sin(np.pi * q) ** 2
    env = np.where(t < pre, (t / pre) ** 2, np.exp(-(t - pre) / 0.1))
    x = np.stack([onepole_lp(rng.standard_normal(n), cut) - onepole_lp(rng.standard_normal(n), cut * 0.15)
                  for _ in range(2)], 1) * env[:, None]
    return norm_peak(x, -18), pre


def shimmer():
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    x = np.zeros((n, 2))
    for i, f in enumerate([2093, 2637, 3136, 3951, 4186]):
        d = 0.05 * i
        env = np.where(t > d, np.exp(-(t - d) / 0.35), 0) * np.minimum(1, np.maximum(0, t - d) / 0.01)
        s = np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 5 * t)) * env
        x[:, i % 2] += s
        x[:, (i + 1) % 2] += s * 0.4
    return norm_peak(x, -26)


def neon(frames_on=(1, 0, 1, 0, 1)):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    saw = 2 * ((120 * t) % 1) - 1
    hum = onepole_lp(saw, np.full(n, 900.0)) + 0.5 * np.sin(2 * np.pi * 60 * t)
    gate = np.zeros(n)
    for k, on in enumerate(frames_on):
        a, b = int(k / FPS * SR), int((k + 1) / FPS * SR)
        gate[a:b] = on
    gate[int(len(frames_on) / FPS * SR):] = np.exp(-(t[int(len(frames_on) / FPS * SR):] - len(frames_on) / FPS) / 0.25)
    zap = rng.standard_normal(n) * (gate > 0.9) * np.exp(-t / 0.05) * 0.6
    x = (hum * gate + zap)
    return norm_peak(np.stack([x, x * 0.9], 1), -26)


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.004) + rng.standard_normal(n) * np.exp(-t / 0.002) * 0.4)
    return norm_peak(np.stack([x, x], 1), -30)


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 650 * np.exp(-t / 0.04) + 180
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.04)
    return norm_peak(np.stack([x, x], 1), -24)


def riser(d=0.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    q = t / d
    f = 180 + 800 * q ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + onepole_lp(rng.standard_normal(n), 400 + 4000 * q) * 0.8
    x *= q ** 2
    return norm_peak(np.stack([x, x * 0.95], 1), -22)


def place(buf, clip, t):
    a = int(round(t * SR))
    if a < 0:
        clip, a = clip[-a:], 0
    b = min(len(buf), a + len(clip))
    if b > a:
        buf[a:b] += clip[:b - a]


def sfx(events):
    buf = np.zeros((N, 2), np.float32)
    W_, pre = whoosh()
    SH = shimmer()
    for kind, t in events:
        if kind in ("whoosh", "burn"):
            place(buf, W_, t - pre)
            place(buf, SH, t - 0.03)
        elif kind == "neon":
            place(buf, neon(), t)
        elif kind == "neon_small":
            place(buf, neon() * 0.6, t)
        elif kind == "tick":
            place(buf, tick(), t)
        elif kind == "pop":
            place(buf, pop(), t)
        elif kind == "riser":
            place(buf, riser(), t)
    return buf


def loudnorm_file(inp, out, I, TP, extra=()):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", inp, "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    af = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", inp, "-af", af + ",aresample=48000", *extra, out])


def main(src, video, out):
    events = json.load(open(os.path.join(BUILD, "sfx_events.json")))
    ev = {k: t for k, t in events}
    v = voice(src)
    m = music(ev)
    write_wav(os.path.join(BUILD, "music_raw.wav"), m * 0.5)
    mi, _ = loudness(os.path.join(BUILD, "music_raw.wav"))
    m = m * 0.5 * db(-23 - mi)  # music bed at ~-23 LUFS
    s = sfx(events)
    write_wav(os.path.join(BUILD, "music.wav"), m)
    write_wav(os.path.join(BUILD, "sfx.wav"), s)
    mix = v + m + s
    write_wav(os.path.join(BUILD, "mix_pre.wav"), mix * 0.8)
    loudnorm_file(os.path.join(BUILD, "mix_pre.wav"), os.path.join(BUILD, "mix.wav"), -14, -1.0)
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", os.path.join(BUILD, "mix.wav"), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    for name in ("voice.wav", "music.wav", "sfx.wav", "mix.wav"):
        print(name, loudness(os.path.join(BUILD, name)))


if __name__ == "__main__":
    main(*sys.argv[1:4])
