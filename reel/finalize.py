"""Write the SRT and shot table, then assemble and export the final MP4s.

usage: python3 finalize.py <work_dir> <out_dir>
Needs <work_dir>/shots/sNN_{text,clean}.mp4 (render.py) and <work_dir>/mix.wav (audio.py).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EDL = json.loads((HERE / "edl.json").read_text())
FPS = EDL["fps"]
SHOTS = {s["shot"]: s for s in EDL["shots"]}

# VO lines exactly as spoken / shown, keyed by the shots they cover
LINES = [
    ((1,), "Stop searching."),
    ((2,), "Your path to guidance"),
    ((3,), "starts right here."),
    ((4,), "Here's the easy route"),
    ((5,), "to Maa Chamunda Jyotish,"),
    ((6,), "Jodhpur."),
    ((7,), "From the main market,"),
    ((8,), "ride past the petrol pump,"),
    ((9,), "keep straight,"),
    ((10,), "past Bricky Bakers."),
    ((11,), "Follow the flags,"),
    ((12,), "past the school gate,"),
    ((13,), "then turn into the colony."),
    ((14, 15), "Through the quiet lanes,"),
    ((16,), "look for the yellow sign."),
    ((17,), "Red railings,"),
    ((18,), "a warm welcome,"),
    ((19,), "and step inside."),
    ((21,), "A peaceful, sacred space"),
    ((22,), "for your kundli,"),
    ((23,), "career"),
    ((24,), "and family."),
    ((25,), "So your future deserves"),
    ((26,), "clarity."),
    ((27,), "Visit Maa Chamunda Jyotish."),
]


def ts(frame):
    ms = round(frame * 1000 / FPS)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def words(text):
    return re.sub(r"[^\w' ]", " ", text).lower().split()


def srt():
    out = []
    for i, (shots, line) in enumerate(LINES, 1):
        a = min(t["in_frame"] for t in SHOTS[shots[0]]["text"])
        b = SHOTS[shots[-1]]["edit_out_frame"]
        out.append(f"{i}\n{ts(a)} --> {ts(b)}\n{line}\n")
        # every SRT word must be on screen in those shots
        shown = " ".join(t["text"].replace(" / ", " ") for n in shots for t in SHOTS[n]["text"])
        assert all(w in words(shown) for w in words(line)), (line, shown)
    return "\n".join(out)


def table():
    rows = ["| # | Edit in–out (frames) | Edit TC | Source in–out (s) | Speed | Shot | On-screen text |",
            "|---|---|---|---|---|---|---|"]
    for s in EDL["shots"]:
        src = (f"{s['source_in_frame'] / FPS:.2f}–{s['source_out_frame'] / FPS:.2f}"
               if "source_in_frame" in s else "—")
        txt = "; ".join(f"{t['layer']} {t['text']} @{t['in_frame']}" for t in s["text"]) or "—"
        rows.append(f"| {s['shot']} | {s['edit_in_frame']}–{s['edit_out_frame']} | "
                    f"{s['edit_in_tc']}–{s['edit_out_tc']} | {src} | {s.get('speed_pct', '—')}% | "
                    f"{s['description']} | {txt} |")
    return "\n".join(rows) + "\n"


def run(cmd):
    subprocess.run(cmd, check=True)


def assemble(work, out, kind, audio):
    lst = work / f"concat_{kind}.txt"
    lst.write_text("".join(f"file '{(work / 'shots' / f's{n:02d}_{kind}.mp4').resolve()}'\n" for n in sorted(SHOTS)))
    name = "find_us_reel.mp4" if kind == "text" else "find_us_reel_clean.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(audio),
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-b:v", "18M", "-maxrate", "20M", "-bufsize", "36M", "-r", str(FPS), "-g", "60",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", str(out / name)])
    return out / name


def loudnorm(src, dst):
    """Two-pass EBU R128 to -14 LUFS integrated, -1 dBTP."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(p[p.rindex("{"):p.rindex("}") + 1])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
         f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
         f"linear=true,aresample=48000", "-c:a", "pcm_s24le", str(dst)])


if __name__ == "__main__":
    work, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    (out / "find_us_reel.srt").write_text(srt())
    (out / "shot_table.md").write_text(table())
    loudnorm(work / "mix.wav", work / "mix_norm.wav")
    for kind in ("text", "clean"):
        print(assemble(work, out, kind, work / "mix_norm.wav"))
