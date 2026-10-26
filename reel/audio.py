"""Music bed (112.5 BPM Indian-fusion), SFX and street ambience for the reel.

usage: python3 audio.py <route.mov> <out.wav>
The bed has a 3-beat pickup so bar 1 lands on beat 3, and its hard final hit
lands on the frame the logo settles (end-card in + 8 frames).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
HERE = Path(__file__).parent
EDL = json.loads((HERE / "edl.json").read_text())
FPS = EDL["fps"]
BEAT = 60 / EDL["music_bpm"]
TOTAL = EDL["total_frames"] / FPS
SHOTS = {s["shot"]: s for s in EDL["shots"]}
END_HIT = (SHOTS[28]["edit_in_frame"] + 8) / FPS
INTERIOR = {20, 21, 22, 23, 24, 26}  # no street ambience indoors
rng = np.random.default_rng(7)


def t_of(n):
    return np.arange(int(n * SR)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- instruments
def kick():
    t = t_of(0.35)
    f = 45 + 95 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.9


def snare():
    t = t_of(0.22)
    n = bp(rng.normal(0, 1, len(t)), 900, 7000) * np.exp(-t * 22)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (0.55 * n + 0.45 * tone) * 0.7


def clap():
    t = t_of(0.25)
    env = sum(np.exp(-np.clip(t - d, 0, None) * 60) * (t >= d) for d in (0, 0.011, 0.022))
    env += np.exp(-t * 14) * 0.5
    return bp(rng.normal(0, 1, len(t)), 1000, 4500) * env * 0.35


def hat(open_=False):
    t = t_of(0.18 if open_ else 0.05)
    return hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t * (18 if open_ else 90)) * 0.16


def tabla(kind):
    """'na' = bright ringing treble stroke, 'ge' = bass bend."""
    if kind == "na":
        t = t_of(0.4)
        f0 = 420
        x = sum(a * np.sin(2 * np.pi * f0 * m * t) for m, a in ((1, 1), (2.0, 0.4), (3.0, 0.2)))
        x = x * np.exp(-t * 11) + bp(rng.normal(0, 1, len(t)), 2000, 6000) * np.exp(-t * 80) * 0.3
        return x * 0.22
    t = t_of(0.5)
    f = 80 + 40 * (1 - np.exp(-t * 10))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.45


def sitar(note, dur=0.9, vel=1.0):
    """Karplus-Strong pluck + jawari-style buzz and sympathetic shimmer."""
    f = midi(note)
    n = int(dur * SR)
    p = int(round(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = 0.998 * 0.5 * (buf[j] + buf[(j + 1) % p])
    out = np.tanh(out * 2.2) * 0.6 + out * 0.4  # buzz
    t = t_of(dur)[:n]
    out *= np.exp(-t * 2.2)
    sym = sum(np.sin(2 * np.pi * f * m * t) * np.exp(-t * 1.2) * a for m, a in ((2, 0.05), (3, 0.03), (4.01, 0.02)))
    return hp(out + sym, 120) * 0.42 * vel


def flute(note, dur, vel=1.0):
    t = t_of(dur)
    f = midi(note) * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t * 2, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    breath = bp(rng.normal(0, 1, len(t)), midi(note) * 1.5, midi(note) * 4) * 0.12
    env = np.clip(t / 0.06, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    return (x + breath) * env * 0.16 * vel


def bass(note, dur):
    t = t_of(dur)
    f = midi(note)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.clip(t / 0.01, 0, 1) * np.exp(-t * 1.6) * np.clip((dur - t) / 0.03, 0, 1)
    return lp(x, 400) * env * 0.42


def pad(notes, dur):
    t = t_of(dur)
    x = sum(np.sin(2 * np.pi * midi(n) * (1 + d) * t) for n in notes for d in (-0.003, 0.003))
    env = np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 0.4, 0, 1)
    return lp(x, 1800) * env * 0.035


def tanpura(dur):
    t = t_of(dur)
    x = np.zeros(len(t))
    for k, n in enumerate((50, 57, 62, 62)):  # D, A, D', D' (Sa-Pa-Sa-Sa)
        f = midi(n)
        for m, a in ((1, 1), (2, 0.5), (3, 0.35), (4, 0.25), (5, 0.18), (6, 0.1)):
            x += a * np.sin(2 * np.pi * f * m * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.4 + 0.1 * k) * t + m))
    return lp(x, 2500) * 0.012


# ---------------------------------------------------------------- arrangement
class Track:
    def __init__(self, seconds):
        self.x = np.zeros((int(seconds * SR) + SR, 2))

    def add(self, sig, at, gain=1.0, pan=0.0):
        i = int(round(at * SR))
        if i < 0:
            sig, i = sig[-i:], 0
        n = min(len(sig), len(self.x) - i)
        if n <= 0:
            return
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.x[i:i + n, 0] += sig[:n] * gain * l * 1.414
        self.x[i:i + n, 1] += sig[:n] * gain * r * 1.414


def reverb(x, secs=1.6, mix=0.18):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t * 6.9 / secs)[:, None]
    ir[:, 0], ir[:, 1] = lp(ir[:, 0], 6000), lp(ir[:, 1], 5500)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], axis=1)
    return x + wet * mix


def music():
    tr = Track(TOTAL + 2)
    beats_total = int(round(END_HIT / BEAT))  # final hit index
    bar0 = 3  # 3-beat pickup
    # D major: I - vi - IV - V (D, Bm, G, A)
    prog = [(50, [62, 66, 69]), (47, [59, 62, 66]), (43, [55, 59, 62]), (45, [57, 61, 64])]
    riff = [74, 76, 78, 81, 78, 76, 74, 71]  # D-major pentatonic hook on 8ths
    riff_b = [81, 78, 76, 74, 76, 78, 74, None]
    tr.add(tanpura(END_HIT + 0.1), 0, 1.0)
    # pickup: tabla roll + rising sitar
    for k in range(6):
        tr.add(tabla("na"), k * BEAT / 2, 0.8 + 0.1 * k, pan=0.2)
    for k, nte in enumerate((69, 71, 74)):
        tr.add(sitar(nte, 0.6), k * BEAT, 0.8, pan=-0.2)
    interior_start = SHOTS[21]["edit_in_frame"] / FPS
    interior_end = SHOTS[25]["edit_in_frame"] / FPS
    for b in range(bar0, beats_total):
        t = b * BEAT
        bar, beat = divmod(b - bar0, 4)
        chord = prog[bar % 4]
        calm = interior_start <= t < interior_end
        # drums
        if not calm:
            if beat in (0, 2) or (beat == 3 and bar % 2 == 1):
                tr.add(kick(), t, 1.0)
            if beat == 2 and bar % 4 == 3:
                tr.add(kick(), t + BEAT / 2, 0.7)
            if beat in (1, 3):
                tr.add(snare(), t, 0.8)
                tr.add(clap(), t, 0.9, pan=0.1)
        else:
            if beat == 0:
                tr.add(kick(), t, 0.6)
        for h in range(2):
            tr.add(hat(open_=(h == 1 and beat == 3)), t + h * BEAT / 2, 0.9 if h else 0.6, pan=0.35)
        if beat in (1, 3):
            tr.add(tabla("na"), t + BEAT / 2, 0.9, pan=-0.3)
        if beat == 0 and bar % 2 == 0:
            tr.add(tabla("ge"), t + 0.75 * BEAT, 0.8, pan=-0.2)
        # bass + pad
        if beat == 0:
            tr.add(pad(chord[1], 4 * BEAT), t, 1.0)
        if not calm or beat == 0:
            tr.add(bass(chord[0] - 12, BEAT * (0.9 if beat != 3 else 0.45)), t, 1.0)
            if beat == 3 and not calm:
                tr.add(bass(chord[0] - 12, BEAT * 0.4), t + BEAT / 2, 0.8)
        # sitar hook: bars alternate hook / answer, every 4th bar rests for the flute
        mel = riff if bar % 2 == 0 else riff_b
        if bar % 4 != 3:
            for h in range(2):
                nte = mel[beat * 2 + h]
                if nte is not None and not (calm and h == 1):
                    tr.add(sitar(nte - (12 if calm else 0), 0.7, 0.9 if h == 0 else 0.7),
                           t + h * BEAT / 2, 1.0, pan=-0.25)
        elif beat == 0:
            tr.add(flute(81, 2.6 * BEAT), t, 1.0, pan=0.25)
            tr.add(flute(78, 1.2 * BEAT), t + 2.8 * BEAT, 1.0, pan=0.25)
        if calm and beat == 0:
            tr.add(flute(chord[1][2] + 12, 3.6 * BEAT, 0.8), t, 1.0, pan=0.25)
    # hard final hit on the logo: kick + clap + full chord strum + bass, then let it ring
    t = END_HIT
    tr.add(kick(), t, 1.2)
    tr.add(clap(), t, 1.0)
    for k, nte in enumerate((62, 66, 69, 74, 78)):
        tr.add(sitar(nte, 2.4, 1.0), t + k * 0.012, 0.9, pan=-0.3 + 0.15 * k)
    tr.add(bass(38, 1.6), t, 1.2)
    x = reverb(tr.x, 1.8, 0.16)
    # nothing but the ring-out after the hit
    i = int(t * SR)
    x[i + int(2.2 * SR):] = 0
    return x


# ---------------------------------------------------------------- sfx
def whoosh(dur=0.5, hi=6000, lo=400, rev=False):
    t = t_of(dur)
    n = rng.normal(0, 1, len(t))
    out = np.zeros(len(t))
    seg = 256
    for i in range(0, len(t), seg):
        u = i / len(t)
        u = 1 - u if rev else u
        fc = hi * (lo / hi) ** u
        out[i:i + seg] = bp(n[max(0, i - 2048):i + seg], fc * 0.7, min(fc * 1.4, SR / 2 - 100))[-len(n[i:i + seg]):]
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return out * env


def flash():
    t = t_of(0.6)
    ping = sum(np.sin(2 * np.pi * f * t) for f in (2093, 3136, 4186)) * np.exp(-t * 9) * 0.15
    return whoosh(0.6, 8000, 600) * 0.55 + ping


def creak(dur=1.1):
    """Stick-slip door creak: irregular pulse train through wooden resonances."""
    t = t_of(dur)
    rate = 38 + 22 * np.sin(2 * np.pi * 0.9 * t) + 8 * rng.normal(0, 1, len(t)).cumsum() / np.sqrt(len(t))
    ph = np.cumsum(rate) / SR
    pulses = np.diff(np.floor(ph), prepend=0) * (0.6 + 0.4 * rng.random(len(t)))
    x = sum(bp(pulses, f * 0.9, f * 1.1) * a for f, a in ((420, 1), (850, 0.8), (1700, 0.5), (2900, 0.25)))
    env = np.clip(t / 0.08, 0, 1) * np.clip((dur - t) / 0.2, 0, 1)
    return x * env * 6


def shimmer():
    t = t_of(1.8)
    x = np.zeros(len(t))
    for k, n in enumerate((86, 90, 93, 98, 102)):
        d = k * 0.06
        tt = np.clip(t - d, 0, None)
        x += np.sin(2 * np.pi * midi(n) * tt) * np.exp(-tt * 3) * (t >= d)
    return x * 0.06


def sfx():
    tr = Track(TOTAL + 2)
    tr.add(flash(), 0, 0.9)
    # swishes on 4 hero entrances (not all of them), ending on the landing frame
    for shot in (2, 8, 16, 25):
        h = [t for t in SHOTS[shot]["text"] if t["layer"] in "BC"][0]
        tr.add(whoosh(0.32, 7000, 1500) * 0.5, h["lands_frame"] / FPS - 0.30, 1.0, pan=0.2)
    tr.add(creak(), SHOTS[19]["edit_in_frame"] / FPS + 0.05, 0.35, pan=0.3)
    tr.add(shimmer(), SHOTS[28]["edit_in_frame"] / FPS, 1.0)
    return reverb(tr.x, 1.2, 0.12)


def ambience(src):
    """Original street sound under the road shots, very low."""
    tr = Track(TOTAL + 2)
    for s in EDL["shots"]:
        if "source_in_frame" not in s or s["shot"] in INTERIOR:
            continue
        a, b = s["source_in_frame"] / FPS, s["source_out_frame"] / FPS
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-vn",
                              "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
        dur = s["duration_frames"] / FPS
        if len(x) == 0:
            continue
        # time-map to the edit duration (speed changes) by resampling
        idx = np.linspace(0, len(x) - 1, int(dur * SR))
        x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
        fade = np.clip(np.minimum(np.arange(len(x)), len(x) - np.arange(len(x))) / (0.01 * SR), 0, 1)[:, None]
        i = int(s["edit_in_frame"] / FPS * SR)
        tr.x[i:i + len(x)] += x * fade
    return tr.x


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    m, fx, amb = music(), sfx(), ambience(src)
    n = int(TOTAL * SR)
    m, fx, amb = m[:n], fx[:n], amb[:n]
    # street ambience sits ~28 dB under the music bed
    amb *= 10 ** ((rms_db(m) - 28 - rms_db(amb[amb != 0])) / 20)
    mix = m + fx * 0.8 + amb
    mix /= np.abs(mix).max() / 0.7
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out, f"{len(mix) / SR:.2f}s")
