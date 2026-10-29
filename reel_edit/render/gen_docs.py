"""Writes caption CSV/SRT, the layer EDL and the timing tables used in EDIT_NOTES.md."""
import csv, json, os, sys
WD, OUT = sys.argv[1], sys.argv[2]
sys.argv = ["render", WD]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

FPS = 30
def tc(f):
    s = f / FPS
    return f"00:00:{int(s):02d}:{int(round(f % FPS)):02d}"
def srt_t(f):
    ms = int(round(f / FPS * 1000)); return f"00:00:{ms // 1000:02d},{ms % 1000:03d}"
def sec(f): return f"{f / FPS:.2f}"

shot_name = {"WIDE": "expert WIDE", "MEDIUM": "expert MEDIUM", "CLOSE": "expert CLOSE"}
def shot_of(f): k = R.shot_at(f)[2]; return shot_name.get(k, f"B-roll {k}")

rows = R.caption_rows()
extra = [dict(n="C", start=R.c8, end=R.c9, hero="21 SAAL (card C)", h1="Jyotish ki field mein (script)", h2="ka experience (script)", special="text-behind-subject credibility card"),
         dict(n="P", start=R.OF[61], end=R.c12, hero="pills", h1="Kundli Vishleshan · Face Reading", h2="Prashna Kundli · Vastu", special="pills, typewriter"),
         dict(n="CTA", start=R.OF[96], end=R.c16, hero="“DM mein likhkar bhejiye”", h1="toh abhi hume", h2="pill: consultation", special="CTA quote + pill"),
         dict(n="CTA2", start=R.c18 + 3, end=R.NTOT, hero="pill: DM “consultation”", h1="", h2="", special="persistent CTA pill + gold chevron (last 0.6 s)")]
allrows = sorted(rows + extra, key=lambda r: r["start"])
with open(os.path.join(OUT, "captions.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["phrase", "start_s", "end_s", "start_frame", "end_frame", "hero", "helper_above_right", "helper_below_left", "special", "shot"])
    for r in allrows:
        w.writerow([r["n"], sec(r["start"]), sec(r["end"]), r["start"], r["end"], r["hero"], r["h1"], r["h2"], r["special"], shot_of(r["start"])])
with open(os.path.join(OUT, "captions.srt"), "w") as fh:
    for i, r in enumerate(allrows, 1):
        text = " ".join(x for x in (r["h1"], r["hero"], r["h2"]) if x)
        fh.write(f"{i}\n{srt_t(r['start'])} --> {srt_t(r['end'])}\n{text}\n\n")

# ---------------- EDL (layer by layer)
edl = []
FRDESC = {"WIDE": "scale 100->104% ease-in-out push, centre (0.50,0.50)", "MEDIUM": "scale 122->126%, centre on face (0.54,0.507), eyes on upper third",
          "CLOSE": "scale 132->136%, face left of centre (0.57,0.515), bg blur sigma 8 via person matte"}
for a, b, k, ex in R.SHOTS:
    if k in R.FR:
        src0 = R.SRC_IDX[a] / FPS; src1 = (R.SRC_IDX[b - 1] + 1) / FPS
        note = FRDESC[k]
        if ex.get("cardA"): note += "; card A: B&W couple cut-out behind subject (85%, blur 2px), neon '?' at (625,465), rose tint flash 2f"
        if ex.get("cardC"): note += "; card C: '21 SAAL' Antonio Thin 400px x0.86, warm white 95%, behind subject matte, rises 40px/10f"
        if ex.get("cta"): note += "; CTA quote 66px + rose pill 'consultation'"
        edl.append([tc(a), tc(b), "V1 A-roll", f"src.mov {src0:.3f}-{src1:.3f}s", k, note + "; grade: rose-and-sage LUT, sat +8%, vignette 15%, walnut gradient bottom 35%"])
    else:
        kb = R.KB[k]
        fx = {"S1": "neon rose-gold '?' flicker 0/100/30/100 then 1.5s pulse", "S2": "cloud thought bubble pop 0->110->100% (10f) + glass cube drift",
              "S3": "antique-gold light leak sweep -> gold/cream white-out", "S4": "halo orb pulse 100<->106%, 70<->95% opacity, 1.8s",
              "S5a": "pills (Kundli Vishleshan, Face Reading)", "S5b": "pills (Prashna Kundli, Vastu)", "S6": "opens on gold flare, rose/sage/gold bokeh, music swell"}[k]
        edl.append([tc(a), tc(b), "V2 B-roll", f"assets/{k}.png" + (" or S6.mp4" if k == "S6" else ""), f"Ken Burns scale {kb[0]:.2f}->{kb[1]:.2f}, dx {kb[2]}->{kb[3]}, dy {kb[4]}->{kb[5]}", fx])
for c, kind in R.TRANS:
    d = {"std": "rose/sage/gold bokeh bloom f1-4 (+1.5 stops), cream #FFF6EC hold f5-9, fade-up f10-12",
         "var1": "standard bokeh flash, caption 'Dhoondh / rahe ho' stays on top",
         "burn": "golden film-burn: gold #F1D58C -> cream white-out", "flare": "single cream bokeh flare sweep L->R"}[kind]
    edl.append([tc(c - 6), tc(c + 6), "V5 transition", kind, "12 frames", d])
for s in R.SNAPS: edl.append([tc(s), tc(s + 4), "V1 snap zoom", "", "+8% over 4f ease-out", "whoosh-hit SFX"])
for r in rows:
    edl.append([tc(r["start"]), tc(r["end"]), "V4 caption", r["hero"], f"h1: {r['h1']} | h2: {r['h2']}", r["special"] or "word pop: opacity 0->100, blur 12->0, scale 105->100 over 6f"])
for f, name in json.load(open(os.path.join(WD, "sfx_events.json"))):
    edl.append([tc(f), "", "A3 SFX", name, "", ""])
edl.append([tc(0), tc(R.NTOT), "A1 voice", "tightened src audio", "afftdn, HPF 80Hz, +2dB@3.5k, de-ess, comp 3.5:1 @-18dB", "master -14 LUFS / TP -1.5 dBTP"])
edl.append([tc(0), tc(R.NTOT), "A2 music", "synth piano + pad 72 BPM", "Am-F-C-G; lift at pills; swell at S6; C resolve at CTA", "-12 dB under voice, -4 dB sidechain duck"])
edl.sort(key=lambda r: (r[0], r[2]))
with open(os.path.join(OUT, "edl.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["tc_in", "tc_out", "layer", "asset", "motion/params", "effect"]); w.writerows(edl)

# ---------------- tables for the notes
words = R.WORDS
with open(os.path.join(WD, "tables.md"), "w") as fh:
    fh.write("| # | word | source in (s) | out frame | out time (s) |\n|---|---|---|---|---|\n")
    for i, w in enumerate(words):
        fh.write(f"| {i} | {w['w']} | {w['s_ref']:.2f} | {w['of']} | {w['of'] / FPS:.2f} |\n")
    fh.write("\n\nSHOTS\n")
    for a, b, k, ex in R.SHOTS: fh.write(f"| {a} | {b} | {sec(a)} | {sec(b)} | {k} | {ex} |\n")
print("ok", len(edl), "edl rows")
