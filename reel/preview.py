"""Render the approval stills for shots 1 (flash + landed), 9 and 16.

usage: python3 preview.py <route.mov> <out_dir>
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

import look
import masks
import typo

SRC, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
EDL = json.loads((Path(__file__).parent / "edl.json").read_text())
SHOT = {s["shot"]: s for s in EDL["shots"]}


def src_frame(n):
    """Frame n of the source conformed to 30 fps CFR (duplication, no blending)."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"fps=30,select=eq(n\\,{n})",
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(978, 550, 3)


def plate(shot, edit_frame, push=True):
    """Graded 1080x1920 plate for an edit frame, plus a function that maps
    source-res masks into the same (upscaled, pushed-in) space."""
    s = SHOT[shot]
    k = edit_frame - s["edit_in_frame"]
    n = s["source_in_frame"] + round(k * s["speed_pct"] / 100)
    raw = src_frame(n)
    # slow push-in 100 -> 106% across the clip masks residual bounce
    z = 1 + 0.06 * k / s["duration_frames"] if push else 1.0
    up = look.push_in(look.upscale(raw), z)
    bg = look.grade(up)
    to_out = lambda m: look.push_in(masks.resize_mask(m, (look.W, look.H)), z, cv2.INTER_LINEAR)
    return raw, bg, to_out, n


def save(name, x, seed):
    x = look.finish(x, seed)
    cv2.imwrite(str(OUT / name), cv2.cvtColor((x * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR))
    return OUT / name


def bottom_of(m):
    rows = np.where(m.max(axis=1) > 0.5)[0]
    return rows.min() if len(rows) else None


out = []

# ---- Shot 1a: frame 1, white-silhouette flash -------------------------------
raw, bg, to_out, n = plate(1, 0)
body = masks.point_mask(raw, [(0.43, 0.595), (0.42, 0.635), (0.415, 0.655)], box=(0.37, 0.56, 0.48, 0.685))
head = masks.point_mask(raw, [(0.437, 0.583)], box=(0.42, 0.565, 0.455, 0.60))
sil = to_out(np.maximum(body, head))
flash = bg * (1 - sil[..., None]) + sil[..., None]
out.append(save("shot01a_flash_f0000.png", flash, 1))

# ---- Shot 1b: SEARCHING landed ----------------------------------------------
cue = {t["text"]: t for t in SHOT[1]["text"]}
f = cue["SEARCHING"]["lands_frame"]
raw, bg, to_out, n = plate(1, f)
vis = to_out(masks.sky_mask(raw))
cx, top, fr = typo.auto_place(["SEARCHING"], 1 - vis, 780, range(470, 551, 10), range(300, 661, 15), (540, 520))
print("shot1", cx, top, fr.round(2))
hero, (x0, y0, x1, y1) = typo.hero(["SEARCHING"], cx, top, 780)
x = typo.composite(bg, hero, vis)
x = typo.composite(x, typo.small("Stop", x0 + 6, y0 - 98))
out.append(save(f"shot01b_searching_f{f:04d}.png", x, 2))

# ---- Shot 9: STRAIGHT behind the rider --------------------------------------
cue = {t["text"]: t for t in SHOT[9]["text"]}
f = cue["STRAIGHT"]["lands_frame"]
raw, bg, to_out, n = plate(9, f)
rider = masks.point_mask(raw, [(0.37, 0.47), (0.37, 0.56), (0.38, 0.68)], box=(0.18, 0.40, 0.60, 0.82))
px = masks.find_pole_x(raw)
pole = masks.point_mask(raw, [(px, 0.12), (px, 0.30)], box=(px - 0.015, 0.0, px + 0.015, 0.62))
occ = to_out(np.maximum(rider, pole))
head_top = bottom_of(to_out(rider))
cx, top, fr = typo.auto_place(["STRAIGHT"], occ, 780, range(440, 551, 5),
                              range(head_top - 190, head_top - 60, 10), (540, head_top - 113), max_hidden=0.35, min_total=0.06)
print("shot9 pole", round(px, 3), cx, top, fr.round(2))
hero, (x0, y0, x1, y1) = typo.hero(["STRAIGHT"], cx, top, 780)
x = typo.composite(bg, hero, 1 - occ)
x = typo.composite(x, typo.small("keep", x0 + 6, y0 - 98))
out.append(save(f"shot09_straight_f{f:04d}.png", x, 9))

# ---- Shot 16: YELLOW / SIGN behind the pole + signboard ----------------------
cue = {t["text"]: t for t in SHOT[16]["text"]}
f = cue["YELLOW / SIGN"]["lands_frame"]
raw, bg, to_out, n = plate(16, f)
sign = masks.point_mask(raw, [(0.62, 0.40)], box=(0.52, 0.28, 0.78, 0.52))
pole = masks.point_mask(raw, [(0.62, 0.15), (0.62, 0.62), (0.62, 0.85)], box=(0.57, 0.0, 0.70, 1.0))
occ = to_out(np.maximum(sign, pole))
for fit in ("width", "cap"):
    cx, top, fr = typo.auto_place(["YELLOW", "SIGN"], occ, 780, range(400, 551, 5), range(320, 1100, 20),
                                  (540, 320), fit=fit, max_hidden=0.40)
    print("shot16", fit, cx, top, fr.round(2))
    hero, (x0, y0, x1, y1) = typo.hero(["YELLOW", "SIGN"], cx, top, 780, fit=fit)
    x = typo.composite(bg, hero, 1 - occ)
    x = typo.composite(x, typo.small("look for the", x0 + 6, y0 - 98))
    out.append(save(f"shot16_yellow_sign_fit-{fit}_f{f:04d}.png", x, 16))

for p in out:
    print(p)
