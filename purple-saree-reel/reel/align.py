# Word timing: syllable-weighted spread inside each pause-bounded chunk, snapped to audio onsets.
# usage: python3 align.py a16.wav transcript.json words.json
import sys
import json
import re
import wave
import numpy as np

wav, tr, out = sys.argv[1:4]
w = wave.open(wav)
sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

hop, win = 160, 512
frames = np.lib.stride_tricks.sliding_window_view(np.pad(a, (0, win)), win)[::hop] * np.hanning(win)
mag = np.abs(np.fft.rfft(frames, axis=1))
logm = np.log1p(mag * 50)
flux = np.maximum(0, np.diff(logm, axis=0, prepend=logm[:1])).sum(1)
flux = np.convolve(flux, np.ones(3) / 3, mode="same")
flux /= flux.max()
fps = sr / hop


def syl(word):
    wd = re.sub(r"[^a-z]", "", word.lower())
    n = len(re.findall(r"[aeiou]+", wd))
    if wd.endswith("y") and not wd.endswith("ay"):
        n += 1
    return max(1, n)


def onset_near(t, lo, hi, rad=0.09):
    i0 = int(max(lo, t - rad) * fps)
    i1 = int(min(hi, t + rad) * fps) + 1
    if i1 <= i0:
        return t
    seg = flux[i0:i1]
    # prefer strong onsets but penalise distance
    dist = np.abs(np.arange(i0, i1) / fps - t)
    score = seg - dist * 2.0
    return (i0 + int(np.argmax(score))) / fps


chunks = json.load(open(tr))
res = []
for ch in chunks:
    s, e = ch["s"], ch["e"]
    words = ch["text"].split()
    weights = np.array([syl(x) + 0.35 for x in words], float)
    cum = np.concatenate([[0], np.cumsum(weights)]) / weights.sum()
    starts = s + cum[:-1] * (e - s)
    snapped = []
    prev = s - 0.01
    for i, t0 in enumerate(starts):
        if i == 0:
            t = s
        else:
            t = onset_near(t0, prev + 0.08, e - 0.05)
        t = max(t, prev + 0.07)
        snapped.append(t)
        prev = t
    for i, x in enumerate(words):
        en = snapped[i + 1] if i + 1 < len(words) else e
        res.append({"w": x, "s": round(float(snapped[i]), 3), "e": round(float(en), 3), "chunk": [s, e]})
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
for r in res:
    print(f"{r['s']:6.2f} {r['w']}")
