"""Build the frame-accurate JSON edit decision list for the "Find Us" route reel.

All edit frames are at 30 fps CFR. Source frames are on the 30 fps conformed
source (route_30p), i.e. source_frame = round(source_seconds * 30).
Text cue offsets are a target grid relative to shot start; they get re-snapped
to the recorded VO phonemes and music beats before the final render.
"""
import json
from pathlib import Path

FPS = 30

# (edit_in, edit_out, src_in, src_out, desc, text cues, occluder/notes)
# text cue: (layer, text, offset_seconds_from_shot_start, position)
SHOTS = [
    (0.0, 1.3, 0.8, 2.1, "Busy market street, woman in red sari on white scooter",
     [("A", "Stop", 0.10, "above-left"), ("B", "SEARCHING", 0.40, "sky upper third")],
     "Frames 1-2: woman+scooter mask filled #FFFFFF, hard off on frame 3. Hero behind shop awnings (L) and pole (L edge) via sky key."),
    (1.3, 2.7, 3.0, 4.4, "Market, fruit cart passing",
     [("A", "Your", 0.05, "above-left"), ("A", "path to", 0.30, "below-right"), ("B", "GUIDANCE", 0.60, "sky upper third")],
     "Behind tall shop building on left (sky key)."),
    (2.7, 3.9, 4.9, 6.1, "Truck and rider ahead",
     [("D", "starts right here.", 0.05, "subtitle")],
     "No hero. Slow push-in 100->106%."),
    (3.9, 5.4, 26.8, 28.3, "Wide main road, cars, tree canopy",
     [("A", "Here's the", 0.05, "above-left"), ("B", "EASY|ROUTE", 0.45, "sky upper third")],
     "Tree branches on right overlap the E of ROUTE (sky key)."),
    (5.4, 7.0, 30.0, 31.6, "Main road under bunting, autos",
     [("A", "to", 0.05, "above-left"), ("C", "SHRI MAA|CHAMUNDA JYOTISH", 0.25, "sky upper third")],
     "Bunting strings keyed over sky, in front of top line."),
    (7.0, 8.1, 23.1, 24.2, "Maroon barrier with Jodhpur stencil, sandstone building",
     [("B", "JODHPUR", 0.20, "sky upper third")],
     "Behind roofline / tree branches top-right (sky key)."),
    (8.1, 9.5, 11.8, 13.2, "Roadside shops, wet road, mini-trucks",
     [("D", "From the main market,", 0.05, "subtitle")],
     "No hero."),
    (9.5, 11.0, 7.0, 8.5, "Petrol pump forecourt, white SUV",
     [("A", "ride past the", 0.05, "above-left"), ("B", "PETROL|PUMP", 0.55, "sky upper third")],
     "Canopy front edge covers bottom of PUMP; light pole crosses PETROL."),
    (11.0, 12.6, 16.0, 17.6, "Following rider in blue shirt along divider",
     [("A", "keep", 0.10, "above-left"), ("B", "STRAIGHT", 0.35, "upper-mid, bottom tucked behind rider")],
     "Behind rider head + shoulders (point-prompt segmentation, tracked) and street-light pole. Source nudged +0.6s from the brief grid so STRAIGHT lands when the rider is centred under the pole."),
    (12.6, 13.9, 24.2, 25.5, "Bricky Bakers storefront behind divider plants",
     [("D", "past Bricky Bakers.", 0.05, "subtitle")],
     "No hero. Store sign stays readable."),
    (13.9, 15.3, 31.0, 32.4, "Bunting overhead, rider in white shirt, white car",
     [("A", "Follow the", 0.05, "above-left"), ("B", "FLAGS", 0.40, "sky upper third")],
     "Bunting in front of letters; rider helmet overlaps bottom."),
    (15.3, 16.5, 38.0, 39.4, "School gate, ornate iron gate and tree",
     [("A", "past the", 0.05, "above-left"), ("B", "SCHOOL|GATE", 0.35, "upper third")],
     "Leaves in front of top line; gate arch covers bottom of GATE. Source runs 1.4s into 1.2s = 117%."),
    (16.5, 17.8, 48.3, 49.6, "Turning off main road into colony",
     [("D", "then turn into the", 0.05, "subtitle"), ("B", "COLONY", 0.80, "sky upper third")],
     "Subtitle removed on the COLONY landing frame. Behind tree + building on left."),
    (17.8, 19.0, 57.0, 58.2, "Narrow sandstone lane, parked cars",
     [("D", "Through the quiet lanes,", 0.05, "subtitle")],
     "Phrase carries across the cut into shot 15."),
    (19.0, 20.2, 60.6, 61.8, "Lane with dog crossing, sandstone houses",
     [("D", "Through the quiet lanes,", -1.15, "subtitle (continued)")],
     "Gentle slide feel; stabilise well."),
    (20.2, 21.8, 66.0, 67.6, "Yellow signboard on pole, red railing",
     [("A", "look for the", 0.05, "above-left"), ("B", "YELLOW|SIGN", 0.55, "upper third")],
     "Pole + signboard in front of letters (strongest depth moment)."),
    (21.8, 22.8, 68.9, 69.9, "Maroon gate, sandstone house",
     [("D", "Red railings,", 0.05, "subtitle")],
     "Maroon boost."),
    (22.8, 24.2, 73.2, 74.6, "Verandah: railing, plants, WELCOME mat",
     [("A", "a warm", 0.05, "above-left"), ("B", "WELCOME", 0.35, "upper third over roof/wall")],
     "Behind hanging plant pots / roof support."),
    (24.2, 25.5, 75.2, 76.5, "Lattice door opening",
     [("A", "and step", 0.05, "above-left"), ("B", "INSIDE", 0.40, "mid-upper")],
     "Door frame + moving lattice door masked; door-creak SFX."),
    (25.5, 26.4, 77.0, 77.9, "Carved wooden door, entering",
     [],
     "Music beat, no text."),
    (26.4, 27.9, 78.2, 79.7, "Interior reveal: marble wall, curtains, chairs",
     [("A", "A peaceful,", 0.05, "above-left"), ("B", "SACRED|SPACE", 0.55, "upper wall")],
     "Behind wall lamp and plant on left."),
    (27.9, 29.3, 81.6, 83.0, "Desk with gold Ganesh idols, certificates",
     [("A", "for your", 0.05, "above-left"), ("B", "KUNDLI", 0.35, "upper wall / lower third")],
     "Behind certificate frames / idol shelf."),
    (29.3, 30.5, 83.0, 84.2, "Desk wider, posters",
     [("B", "CAREER", 0.05, "upper wall")],
     "Behind wall posters on left edge."),
    (30.5, 31.7, 84.4, 85.6, "Seating with printed cover, brown chairs",
     [("A", "and", 0.05, "above-left"), ("B", "FAMILY", 0.25, "lower third")],
     "Chair back overlaps letters."),
    (31.7, 33.7, 70.0, 71.7, "Exterior hold: house, maroon railings, scooter",
     [("A", "So", 0.05, "scattered"), ("A", "your", 0.30, "scattered"), ("A", "future", 0.55, "scattered"),
      ("B", "DESERVES", 0.95, "sky upper third")],
     "Behind roof parapet / upper storey. 2.0s hold; source 1.7s at 85% speed."),
    (33.7, 35.2, 79.8, 81.3, "Interior wide, curtains, warm light",
     [("B", "CLARITY", 0.10, "upper wall")],
     "Behind doorway curtain edge."),
    (35.2, 37.6, 66.4, 68.4, "Signboard again (CTA), 85% speed",
     [("A", "visit", 0.05, "above-left"), ("C", "SHRI MAA|CHAMUNDA JYOTISH", 0.30, "upper third")],
     "Behind pole. Dissolve to end card over last 8 frames."),
    (37.6, 40.4, None, None, "End card: cream silk, logo",
     [("LOGO", "placeholder 3-circle logo + SHRI MAA CHAMUNDA JYOTISH + tagline", 0.0, "centre")],
     "Logo 8-frame fade 95->100%. Music last beat on settle."),
]


def f(t):
    return None if t is None else round(t * FPS)


def build():
    out = []
    for i, (ei, eo, si, so, desc, cues, notes) in enumerate(SHOTS, 1):
        e_in, e_out = f(ei), f(eo)
        rec = {
            "shot": i,
            "description": desc,
            "edit_in_frame": e_in,
            "edit_out_frame": e_out,          # exclusive
            "duration_frames": e_out - e_in,
            "edit_in_tc": tc(e_in),
            "edit_out_tc": tc(e_out),
        }
        if si is not None:
            s_in, s_out = f(si), f(so)
            rec.update({
                "source_in_frame": s_in,
                "source_out_frame": s_out,
                "source_in_s": si,
                "source_out_s": so,
                "speed_pct": round(100 * (s_out - s_in) / (e_out - e_in)),
            })
        rec["text"] = []
        for layer, text, off, pos in cues:
            if layer == "D" and off < 0:
                # continuation of a subtitle from the previous shot
                start = e_in
            else:
                start = e_in + round(off * FPS)
            item = {"layer": layer, "text": text.replace("|", " / "), "lines": text.split("|"),
                    "in_frame": start, "position": pos}
            if layer in ("B", "C"):
                item["entrance_frames"] = 5
                item["lands_frame"] = start + 5
            elif layer == "A":
                item["entrance_frames"] = 3
            item["out_frame"] = e_out  # text never animates out: it cuts with the shot
            rec["text"].append(item)
        # subtitle is removed the frame a hero lands in the same shot
        heroes = [t for t in rec["text"] if t["layer"] in ("B", "C")]
        for t in rec["text"]:
            if t["layer"] == "D" and heroes:
                t["out_frame"] = heroes[0]["in_frame"]
        rec["notes"] = notes
        out.append(rec)
    return {
        "project": "Find Us route reel - Shri Maa Chamunda Jyotish, Jodhpur",
        "fps": FPS,
        "resolution": [1080, 1920],
        "source": {"file": "route.mov", "probed": "HEVC 550x978, ~28.8 fps VFR, 86.38 s",
                   "conform": "fps=30 (frame duplication, no blending)"},
        "total_frames": out[-1]["edit_out_frame"],
        "total_seconds": out[-1]["edit_out_frame"] / FPS,
        "shots": out,
    }


def tc(fr):
    s, ff = divmod(fr, FPS)
    return f"00:00:{s:02d}:{ff:02d}"


if __name__ == "__main__":
    edl = build()
    Path(__file__).with_name("edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    for s in edl["shots"]:
        print(s["shot"], s["edit_in_frame"], s["edit_out_frame"], s.get("source_in_frame"),
              s.get("source_out_frame"), s.get("speed_pct"))
    print("total", edl["total_frames"], edl["total_seconds"])
