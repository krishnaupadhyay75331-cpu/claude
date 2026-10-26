"""Full render of the "Find Us" reel: stabilise, grade, mask, type, export.

usage: python3 render.py <route30.mp4> <work_dir> [shot numbers...]
Writes <work_dir>/shots/sNN_text.mp4 and sNN_clean.mp4 (near-lossless) per shot.
"""
import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

import endcard
import look
import masks
import typo

SRC = sys.argv[1]
WORK = Path(sys.argv[2])
HERE = Path(__file__).parent
EDL = json.loads((HERE / "edl.json").read_text())
SHOTS = {s["shot"]: s for s in EDL["shots"]}
FPS = EDL["fps"]
INTERIOR = {21, 22, 23, 24, 26}
WORD_STEP = round(FPS / 2.2)  # ~2.2 words per second

# Occlusion + placement per hero shot. Points are normalized on the landing frame.
#   vis: "sky"  -> text shows only over sky (roofs, poles, wires, flags occlude)
#   occ: list of ("pts", [(x, y)...], box) | ("foliage",)
#   tops/prefer: search range and preferred (cx, top) for auto placement
UPPER = dict(tops=range(320, 900, 15), prefer=(540, 380))
CFG = {
    1: dict(vis="sky", **UPPER),
    2: dict(vis="sky", **UPPER),
    4: dict(vis="sky", **UPPER),
    5: dict(vis="sky", **UPPER),
    6: dict(occ=[("foliage",)], tops=range(320, 1300, 20), prefer=(540, 420)),
    8: dict(vis="sky", **UPPER),
    9: dict(occ=[("pts", [(0.37, 0.47), (0.37, 0.56), (0.38, 0.68)], (0.18, 0.40, 0.60, 0.82)), ("pole",)],
            tops=range(560, 760, 10), prefer=(540, 740), min_total=0.06, max_hidden=0.35),
    11: dict(vis="sky", **UPPER),
    12: dict(occ=[("foliage", 0.45)], tops=range(320, 1100, 20), prefer=(540, 400), fit="cap", max_hidden=0.35),
    13: dict(vis="sky", tops=range(320, 900, 15), prefer=(540, 380)),
    16: dict(occ=[("pts", [(0.62, 0.40)], (0.52, 0.28, 0.78, 0.52)),
                  ("pts", [(0.62, 0.15), (0.62, 0.62), (0.62, 0.85)], (0.57, 0.0, 0.70, 1.0))],
             tops=range(320, 1100, 20), prefer=(540, 940), fit="cap", align="left", max_hidden=0.40),
    18: dict(occ=[("pts", [(0.13, 0.25)], (0.03, 0.17, 0.25, 0.36)),
                  ("pts", [(0.27, 0.25)], (0.24, 0.0, 0.31, 0.5))],
             tops=range(320, 800, 15), prefer=(540, 380)),
    19: dict(occ=[("pts", [(0.47, 0.30), (0.60, 0.40)], (0.35, 0.05, 0.85, 0.95))],
             tops=range(320, 1100, 20), prefer=(540, 480), max_hidden=0.25),
    21: dict(occ=[("pts", [(0.24, 0.29)], (0.15, 0.20, 0.33, 0.38))],
             tops=range(320, 900, 15), prefer=(540, 380)),
    22: dict(occ=[("pts", [(0.24, 0.27), (0.35, 0.27)], (0.15, 0.18, 0.45, 0.36))],
             tops=range(320, 900, 15), prefer=(540, 380)),
    23: dict(occ=[("pts", [(0.25, 0.25)], (0.18, 0.15, 0.33, 0.40))],
             tops=range(320, 900, 15), prefer=(540, 380)),
    24: dict(occ=[("pts", [(0.62, 0.62)], (0.48, 0.48, 0.78, 0.80)),
                  ("pts", [(0.18, 0.86)], (0.0, 0.65, 0.45, 1.0))],
             tops=range(320, 1400, 15), prefer=(540, 1150), max_hidden=0.20),
    25: dict(vis="sky", tops=range(360, 900, 15), prefer=(540, 380)),
    26: dict(occ=[("pts", [(0.24, 0.27)], (0.15, 0.18, 0.33, 0.36))],
             tops=range(320, 900, 15), prefer=(540, 380)),
    # CTA: the brand name must read, so only the signboard edge sits in front
    27: dict(occ=[("pts", [(0.62, 0.40)], (0.52, 0.28, 0.78, 0.52))],
             tops=range(320, 700, 20), prefer=(540, 400), max_hidden=0.30),
}
FLASH_PTS = ([(0.43, 0.595), (0.42, 0.635), (0.415, 0.655)], (0.37, 0.56, 0.48, 0.685))
HERO_W = 780


def stabilised(shot):
    """Stabilised source frames [source_in, source_out) at 550x978 (vid.stab, two pass)."""
    s = SHOTS[shot]
    a, b = s["source_in_frame"], s["source_out_frame"]
    trf = WORK / f"s{shot:02d}.trf"
    trim = f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vf",
                    f"{trim},vidstabdetect=shakiness=7:accuracy=15:result={trf}", "-f", "null", "-"],
                   check=True)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", SRC, "-vf",
         f"{trim},vidstabtransform=input={trf}:smoothing=12:optzoom=1:maxshift=30:maxangle=0.04:"
         f"interpol=bicubic", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    return list(np.frombuffer(raw, np.uint8).reshape(-1, 978, 550, 3))


def occluder(spec, rgb, pts):
    if spec[0] == "foliage":
        m = masks.foliage_mask(rgb)
        if len(spec) > 1:  # only the canopy above this fraction of the height
            m[int(spec[1] * m.shape[0]):] = 0
        return m
    if spec[0] == "pole":
        px = masks.find_pole_x(rgb)
        return masks.point_mask(rgb, [(px, 0.12), (px, 0.30)], box=(px - 0.015, 0.0, px + 0.015, 0.62))
    _, _, box = spec
    # move the box with the tracked points
    dx = np.mean([p[0] for p in pts]) - np.mean([p[0] for p in spec[1]])
    dy = np.mean([p[1] for p in pts]) - np.mean([p[1] for p in spec[1]])
    bx = (max(0, box[0] + dx), max(0, box[1] + dy), min(1, box[2] + dx), min(1, box[3] + dy))
    pts = [(min(max(x, bx[0] + 0.002), bx[2] - 0.002), min(max(y, bx[1] + 0.002), bx[3] - 0.002))
           for x, y in pts]
    return masks.point_mask(rgb, pts, box=bx)


class Encoder:
    def __init__(self, path):
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{look.W}x{look.H}",
             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "10",
             "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)

    def write(self, x):
        self.p.stdin.write((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def text_plan(s):
    """Per-shot text cues sorted by in_frame, with hero placement resolved later."""
    return sorted(s["text"], key=lambda t: t["in_frame"])


def render_shot(shot):
    s = SHOTS[shot]
    out_dir = WORK / "shots"
    out_dir.mkdir(parents=True, exist_ok=True)
    if shot == 28:
        return render_endcard()
    frames = stabilised(shot)
    n_src = len(frames)
    e0, e1 = s["edit_in_frame"], s["edit_out_frame"]
    dur = e1 - e0
    speed = s["speed_pct"] / 100
    src_idx = [min(n_src - 1, round(k * speed)) for k in range(dur)]
    cfg = CFG.get(shot)
    cues = text_plan(s)
    heroes = [t for t in cues if t["layer"] in "BC"]
    grays = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]

    # tracked prompt points for every point-based occluder
    land_k = (heroes[0]["lands_frame"] - e0) if heroes else 0
    land_i = src_idx[min(land_k, dur - 1)]
    tracks = []
    if cfg and "occ" in cfg:
        for spec in cfg["occ"]:
            tracks.append(masks.track_points(grays, land_i, spec[1]) if spec[0] == "pts" else None)

    def vis_for(i, z):
        """Visibility (1 = text may show) for source frame i, mapped to output space."""
        if not cfg:
            return None
        rgb = frames[i]
        if cfg.get("vis") == "sky":
            m = 1 - masks.sky_occluder(rgb)
        else:
            occ = np.zeros(rgb.shape[:2], np.float32)
            for spec, tr in zip(cfg["occ"], tracks):
                occ = np.maximum(occ, occluder(spec, rgb, tr[i] if tr else None))
            m = 1 - occ
        m = look.push_in(masks.resize_mask(m, (look.W, look.H)), z, cv2.INTER_LINEAR)
        return m

    def zoom(k):
        return 1 + 0.06 * k / dur

    # resolve hero placement on the landing frame
    place = None
    if heroes:
        h = heroes[0]
        vis = vis_for(land_i, zoom(land_k))
        width = HERO_W
        cx, top, fr = typo.auto_place(
            h["lines"], 1 - vis, width, range(440, 551, 5), cfg["tops"], cfg["prefer"],
            fit=cfg.get("fit", "width"), align=cfg.get("align", "center"),
            max_hidden=cfg.get("max_hidden", 0.30), min_total=cfg.get("min_total", 0.03))
        place = dict(cx=cx, top=top, width=width, fit=cfg.get("fit", "width"), align=cfg.get("align", "center"),
                     kind="brand" if h["layer"] == "C" else "gold")
        print(f"shot {shot}: {h['text']} cx={cx} top={top} hidden={fr.round(2).tolist()}", flush=True)

    enc_t = Encoder(out_dir / f"s{shot:02d}_text.mp4")
    enc_c = Encoder(out_dir / f"s{shot:02d}_clean.mp4")
    hero_cache, small_cache, sub_cache = {}, {}, {}
    vis_prev = None
    flash_sil = {}
    if shot == 1:
        for k in (0, 1):
            raw = frames[src_idx[k]]
            sil = masks.point_mask(raw, *FLASH_PTS)
            flash_sil[k] = look.push_in(masks.resize_mask(sil, (look.W, look.H)), zoom(k), cv2.INTER_LINEAR)

    for k in range(dur):
        f_abs = e0 + k
        i = src_idx[k]
        z = zoom(k)
        bg = look.grade(look.push_in(look.upscale(frames[i]), z), interior=shot in INTERIOR)
        if k in flash_sil:  # frames 1-2: white silhouette, hard off on frame 3
            m = flash_sil[k][..., None]
            bg = bg * (1 - m) + m
        clean = bg
        x = bg
        active = [t for t in cues if t["in_frame"] <= f_abs < t["out_frame"]]
        hero_box = None
        if heroes:
            # hero geometry is needed for small-word positions even before it lands
            hero_box = hero_layer(heroes[0], place, 1.0, hero_cache)[1]
        if any(t["layer"] in "BC" for t in active):
            v = vis_for(i, z)
            # light temporal smoothing kills edge chatter without visible lag
            v = v if vis_prev is None else 0.65 * v + 0.35 * vis_prev
            vis_prev = v
            h = heroes[0]
            p = min(1.0, (f_abs - h["in_frame"] + 1) / h["entrance_frames"])
            L, _ = hero_layer(h, place, p, hero_cache)
            x = typo.composite(x, L, v)
        smalls = [t for t in active if t["layer"] == "A"]
        for t in smalls:
            idx = [u for u in cues if u["layer"] == "A"].index(t)
            n_small = len([u for u in cues if u["layer"] == "A"])
            px, py = small_pos(t["text"], idx, n_small, hero_box)
            p = min(1.0, (f_abs - t["in_frame"] + 1) / 3)
            key = (t["text"], round(p, 3))
            if key not in small_cache:
                small_cache[key] = typo.small(t["text"], px, py, p)
            x = typo.composite(x, small_cache[key])
        for t in active:
            if t["layer"] == "D":
                words = t["text"].split()
                start = SUB_START.get(t["text"], t["in_frame"])
                span = t["out_frame"] - start
                step = min(WORD_STEP, max(4, span // (len(words) + 1)))
                lit = min(len(words), (f_abs - start) // step + 1)
                if (t["text"], lit) not in sub_cache:
                    sub_cache[(t["text"], lit)] = typo.subtitle(words, lit)
                x = typo.composite(x, sub_cache[(t["text"], lit)])
        if shot == 27 and k >= dur - 8:  # dissolve into the end card over the last 8 frames
            a = (k - (dur - 8) + 1) / 9
            card = endcard.frame(0, 1, with_logo=False)
            x = x * (1 - a) + card * a
            clean = clean * (1 - a) + card * a
        enc_t.write(look.finish(x, f_abs))
        enc_c.write(look.finish(clean, f_abs))
    enc_t.close()
    enc_c.close()
    return shot


# phrases that carry across a cut keep their word timing from the first shot
SUB_START = {"Through the quiet lanes,": SHOTS[14]["edit_in_frame"] + 2}


def hero_layer(h, place, p, cache):
    key = round(p, 3)
    if key not in cache:
        cache[key] = typo.hero(h["lines"], place["cx"], place["top"], place["width"], kind=place["kind"],
                               progress=p, fit=place["fit"], align=place["align"])
    return cache[key]


def small_pos(text, idx, n, box):
    """Loose diagonal constellation around the hero block."""
    x0, y0, x1, y1 = box
    w = typo.small_width(text)
    if n == 1:
        return x0 + 6, y0 - 98
    if n == 2:
        return ((x0 + 6, y0 - 98), (min(x1 - w, look.W - 140 - w), y1 + 30))[idx]
    # "So" low-left, "your" higher and to its right, "future" below-right of the hero
    w0 = typo.small_width("So")
    return ((x0 + 6, y0 - 98), (x0 + w0 + 60, y0 - 140), (min(x1 - w, look.W - 140 - w), y1 + 30))[idx]


def render_endcard():
    s = SHOTS[28]
    n = s["duration_frames"]
    enc_t = Encoder(WORK / "shots" / "s28_text.mp4")
    enc_c = Encoder(WORK / "shots" / "s28_clean.mp4")
    for k in range(n):
        f_abs = s["edit_in_frame"] + k
        enc_t.write(look.finish(endcard.frame(k, n), f_abs))
        enc_c.write(look.finish(endcard.frame(k, n, with_logo=False), f_abs))
    enc_t.close()
    enc_c.close()
    return 28


if __name__ == "__main__":
    shots = [int(a) for a in sys.argv[3:]] or sorted(SHOTS)
    # longest/heaviest first so the pool drains evenly
    shots.sort(key=lambda n: -(SHOTS[n]["duration_frames"] * (2 if n in CFG else 1)))
    with Pool(int(os.environ.get("JOBS", "4"))) as pool:
        for done in pool.imap_unordered(render_shot, shots):
            print("done", done, flush=True)
