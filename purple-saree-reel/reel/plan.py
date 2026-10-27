# Edit plan for the purple-saree Karwa Chauth reel. All times are SOURCE seconds; the renderer
# maps them through KEEP (pauses tightened to ~0.18 s). Caption words + times come from words.json.
import json
import os

_W = json.load(open(os.environ.get("REEL_WORDS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.json"))))
_T = {}
for _i, _x in enumerate(_W):
    _T.setdefault(_x["w"].lower().strip("?"), []).append(_x["s"])


def w(word, near):
    """time of the spoken word closest to `near` (source s)."""
    c = _T[word.lower().strip("?")]
    return min(c, key=lambda v: abs(v - near))


# ---- pause tightening: S-block gaps cut to ~0.18 s (cuts land mid-silence) ----
GAPS = [(3.27, 3.67), (4.65, 5.39), (6.29, 6.79), (7.32, 7.70), (15.92, 16.43), (17.50, 17.90),
        (22.03, 22.61), (23.38, 24.14), (31.48, 31.94), (33.24, 33.66), (39.27, 39.94), (47.16, 47.52),
        (51.29, 51.93), (57.33, 57.79)]
KEEP = []
_cur = 0.26
for a, b in GAPS:
    KEEP.append([_cur, a + 0.09])
    _cur = b - 0.09
KEEP.append([_cur, 58.86])
FREEZE = 2.0
REFRAME = 51.6


def mid(a, b):
    return (a + b) / 2


# ---- shots ----
SHOTS = [
    dict(type="broll", n=1, t0=0.0, t1=mid(3.27, 3.67), drift=-30, drift_y=20, out="cream"),
    dict(type="aroll", frame="wide", t0=mid(3.27, 3.67), t1=mid(4.65, 5.39), pop="purple", out="hard"),
    dict(type="aroll", frame="med", t0=mid(4.65, 5.39), t1=mid(7.32, 7.70), out="white"),
    dict(type="broll", n=2, t0=mid(7.32, 7.70), t1=11.57, drift=30, out="white"),
    dict(type="aroll", frame="close", t0=11.57, t1=mid(15.92, 16.43), enter="haze", out="hard"),
    dict(type="aroll", frame="wide", t0=mid(15.92, 16.43), t1=mid(17.50, 17.90), out="hard"),
    dict(type="aroll", frame="med", t0=mid(17.50, 17.90), t1=20.51, out="bokeh"),
    dict(type="broll", n=3, t0=20.51, t1=mid(22.03, 22.61), drift=-25, out="pinkleak"),
    dict(type="aroll", frame="close", t0=mid(22.03, 22.61), t1=mid(23.38, 24.14), pop="rani", out="hard"),
    dict(type="aroll", frame="med", t0=mid(23.38, 24.14), t1=27.56, out="hard"),
    dict(type="aroll", frame="wide", t0=27.56, t1=mid(31.48, 31.94), out="whip"),
    dict(type="broll", n=4, t0=mid(31.48, 31.94), t1=mid(33.24, 33.66), enter="zoomout", out="white"),
    dict(type="aroll", frame="wide", t0=mid(33.24, 33.66), t1=36.40, enter="haze", out="hard"),
    dict(type="aroll", frame="close", t0=36.40, t1=mid(39.27, 39.94), out="hard"),
    dict(type="broll", n=5, t0=mid(39.27, 39.94), t1=41.02, drift=20, out="hard"),
    dict(type="broll", n=6, t0=41.02, t1=mid(47.16, 47.52), drift=-20, out="flare"),
    dict(type="aroll", frame="wide", t0=mid(47.16, 47.52), t1=REFRAME, push=(1.0, 1.03), out="burn"),
    dict(type="broll", n=7, t0=REFRAME, t1=mid(54.27, 54.41), drift=30, out="bokeh"),
    dict(type="aroll", frame="tight", t0=mid(54.27, 54.41), t1="END", push=(1.05, 1.08)),
]

# ---- caption stacks: words = [(text, src_time)], hero = index of hero word ----
def S(words, hero, end=None, **kw):
    d = dict(words=words, hero=hero, **kw)
    if end is not None:
        d["end"] = end
    return d


STACKS = [
    # S1 hook (B-roll #1)
    S([("karwa", w("Karwa", 0.4)), ("chauth", w("Chauth", 0.7)), ("ab", w("ab", 1.19)), ("Vrat", w("vrat", 1.3)),
       ("kam", w("kam", 1.5))], 3, end=1.76),
    S([("aur", w("aur", 1.8)), ("Trend", w("trend", 2.0)), ("zyada", w("zyada", 2.2)), ("ban", w("ban", 2.5)),
       ("rha", w("rha", 2.85)), ("hai", w("hai", 3.06))], 1, end=3.27),
    # S2
    S([("ek", w("ek", 3.73)), ("baar", w("baar", 3.9)), ("Sochiye", w("sochiye", 4.1))], 2, end=4.65),
    # S4 (S3 greeting is the script line)
    S([("Dosto", w("dosto", 6.85))], 0, end=7.32),
    # S5a (B-roll #2)
    S([("karwa", w("Karwa", 7.76)), ("chauth", w("Chauth", 8.0)), ("par", w("par", 8.2)), ("Pati Patni", [w("pati", 8.6), w("patni", 8.94)]),
       ("ke", w("ke", 9.36))], 3, end=9.50),
    # S5b (close)
    S([("lekin", w("lekin", 11.8)), ("aajkal", w("aajkal", 12.2)), ("Social Media", [w("social", 12.5), w("media", 12.9)]),
       ("par", w("par", 13.4)), ("ise", w("ise", 13.6))], 2, end=14.0),
    S([("trend", w("trend", 14.05)), ("ki", w("ki", 14.27)), ("tarah", w("tarah", 14.36)), ("Dekha", w("dekha", 15.2)),
       ("jaata", w("jaata", 15.4)), ("hai", w("hai", 15.76))], 3, end=15.92),
    # S6
    S([("designer", w("designer", 16.5)), ("Lehenge", w("lehenge", 17.0))], 1, end=17.50),
    # S7a: small list resolving into the big word
    S([("reels", w("reels", 18.0)), ("photoshoots", w("photoshoots", 18.6)), ("mehendi", w("mehendi", 19.6)),
       ("ki", w("ki", 19.93)), ("Race", w("race", 20.06))], 4, end=20.37),
    # S8 single big hero
    S([("Galat", w("galat", 22.67)), ("nahi", w("nahi", 22.8)), ("hai", w("hai", 23.17))], 0, end=23.38, hero_size=168),
    # S9 fast montage (micro-shake bumps on each hero)
    S([("hamari", w("hamari", 24.2)), ("Parampara", w("parampara", 24.5)), ("mein", w("mein", 25.05))], 1, end=25.45),
    S([("solah", w("solah", 25.56)), ("Shringaar", w("shringaar", 25.9)), ("vrat", w("vrat", 26.26))], 1, end=26.50),
    S([("ka", w("ka", 26.56)), ("ek", w("ek", 26.68)), ("Hissa", w("hissa", 26.9)), ("hai", w("hai", 27.11))], 2, end=27.39),
    S([("lekin", w("lekin", 27.8)), ("Sawaal", w("sawaal", 28.15)), ("yeh", w("yeh", 28.5)), ("hai", w("hai", 28.91)),
       ("ki", w("ki", 29.13))], 1, end=29.40),
    S([("hum", w("hum", 29.71)), ("Dikhane", w("dikhane", 29.92)), ("ke", w("ke", 30.26)), ("liye", w("liye", 30.4))], 1,
      end=30.78, red=True),
    S([("Vrat", w("vrat", 30.82)), ("kar", w("kar", 31.0)), ("rhe", w("rhe", 31.2)), ("hain??", w("hain", 31.33))], 0, end=31.48),
    # S10 (B-roll #4)
    S([("vrat", w("vrat", 32.0)), ("ka", w("ka", 32.2)), ("asli", w("asli", 32.49)), ("Taakat", w("taakat", 32.88))], 3, end=33.24),
    # S11 wide
    S([("Shraddha", w("shraddha", 33.72)), ("mein", w("mein", 33.94)), ("hai", w("hai", 34.3))], 0, end=34.55, red=True),
    S([("agar", w("agar", 34.76)), ("saath", w("saath", 35.02)), ("mein", w("mein", 35.36)), ("Pati Patni", [w("pati", 35.6), w("patni", 36.06)])], 3, end=36.38),
    # S11 close
    S([("ek", w("ek", 36.43)), ("doosre", w("doosre", 36.58)), ("ke", w("ke", 37.09)), ("liye", w("liye", 37.26)),
       ("Samman", w("samman", 37.57))], 4, end=38.05),
    S([("Samay", w("samay", 38.46)), ("de", w("de", 38.78)), ("sakein", w("sakein", 38.98))], 0, end=39.27),
    # S12 (B-roll #5/#6) built at the top of frame
    S([("ek", w("ek", 40.0)), ("doosre", w("doosre", 40.17)), ("ki", w("ki", 40.51)), ("Izzat", w("izzat", 40.67)),
       ("karein", w("karein", 41.03))], 3, end=41.35, y=0.25),
    S([("aur", w("aur", 41.41)), ("dil", w("dil", 41.62)), ("se", w("se", 41.87)), ("Pyaar", w("pyaar", 42.17)),
       ("jatayein", w("jatayein", 42.3))], 3, end=42.84, y=0.25),
    S([("toh", w("toh", 43.14)), ("wahi", w("wahi", 43.23)), ("sabse", w("sabse", 43.57)), ("Sundar", w("sundar", 43.84)),
       ("karwa", w("Karwa", 44.26)), ("chauth", w("Chauth", 44.52)), ("hai", w("hai", 44.77))], 3, end=44.89, y=0.25),
    S([("aur", w("aur", 45.12)), ("aajkal", w("aajkal", 45.29)), ("toh", w("toh", 45.77)), ("Pati Patni", [w("pati", 45.94), w("patni", 46.25)]),
       ("saath", w("saath", 46.7)), ("mein", w("mein", 47.02))], 3, end=47.16),
    # S13 authority (wide)
    S([("vrat", w("vrat", 47.58)), ("bhi", w("bhi", 47.73)), ("Rakhte", w("rakhte", 47.81)), ("hain", w("hain", 48.12))], 2, end=48.45),
    # S14a on B-roll #7: her question to the audience
    S([("aapki", w("aapki", 51.99)), ("nazar", w("nazar", 52.27)), ("mein", w("mein", 52.7)), ("Karwa Chauth", [w("Karwa", 52.86), w("Chauth", 53.23)])],
      3, end=53.36),
    S([("Vrat", w("vrat", 53.38)), ("hai", w("hai", 53.6)), ("ya", w("ya", 53.82)), ("trend??", w("trend", 54.0))], 0, end=54.27),
    # S14b CTA spoken
    S([("Comment", w("comment", 54.47)), ("mein", w("mein", 54.76)), ("zaroor", w("zaroor", 54.92)), ("likhein", w("likhein", 55.21))],
      0, end=55.58),
    S([("Follow", w("follow", 55.65)), ("karein", w("karein", 55.93))], 0, end=56.33),
]

# ---- overlays / events ----
EVENTS = [
    # neon "?" from 0:00.8, carried across the cut onto her A-roll, flickers off as the greeting starts
    dict(kind="qmark", t=0.8, t_end=5.30, pos_broll=(0.5, 0.20), pos_aroll=(0.70, 0.17), scale=0.8),
    # B&W social-media phone cut-outs (her problem = Karwa Chauth as a social-media trend), behind her
    dict(kind="phones", t=3.70, t_end=6.2, layer="under"),
    # S3 greeting: script line on her own words + gold sparkle at the joined hands + bell
    dict(kind="words", t=5.39, t_end=7.32, style="script", size=104, y=0.64,
         words=[("Jai", w("Jai", 5.45)), ("Maa", w("Maa", 5.52)), ("Chamunda", w("Chamunda", 5.8))]),
    dict(kind="sparkle", t=5.55, pos=(0.50, 0.63), seed=3),
    # B-roll #2: watercolour memory bubble, then depth title + companions
    dict(kind="bubble", t=8.0, t_end=9.95, pos=(0.5, 0.20), seed=4),
    dict(kind="depth", t=w("vishwas", 10.05), t_end=11.40, text="Vishwas", y=0.10),
    dict(kind="depth_words", t=w("pyaar", 9.53), t_end=11.40,
         words=[("pyaar", w("pyaar", 9.53), 0.08, 0.30), ("aur", w("aur", 9.77), 0.215, 0.30),
                ("ka", w("ka", 10.42), 0.56, 0.30), ("dharmik", w("dharmik", 10.62), 0.615, 0.30),
                ("vrat", w("vrat", 10.89), 0.56, 0.335), ("hai", w("hai", 11.10), 0.65, 0.335)]),
    # B-roll #3: gold/pink wall light leak
    dict(kind="wall_leak", t=20.51, t_end=22.32),
    # B-roll #4 halo
    dict(kind="halo", t=32.2, t_end=33.45, pos=(0.5, 0.36)),
    # B-roll #6 callout tags with the values she names
    dict(kind="tags", t=45.10, t_end=47.16, tags=[("Samman · Samay", 0.42, (0.62, 0.60)), ("Izzat · Pyaar", 0.49, (0.66, 0.63))]),
    # S13: stat-style title (no number spoken -> her strongest claim word) + gold script + pill
    dict(kind="stat", t=w("barabari", 49.21), t_end=51.29, text="BARABARI", y=0.085, size=300),
    dict(kind="words", t=w("pyaar", 48.87), t_end=51.29, style="script", size=84, y=0.15, rgb=(247, 223, 160),
         words=[("pyaar", w("pyaar", 48.87)), ("aur", w("aur", 49.03))]),
    dict(kind="pill", t=w("ek", 50.19), t_end=51.29, text="ek acchi misaal", y=0.70, size=52,
         wipe_until=w("misaal", 50.72) + 0.12),
    # her page name (CONFIRM spelling) as a pill, wiping in as she says it
    dict(kind="pill", t=w("Maa", 56.37), t_end=57.33, text="Maa Chamunda Jyotish", y=0.70, size=52,
         wipe_until=w("Jyotish", 57.07) + 0.12),
    # S15 sign-off: greeting + sparkle at the hands, then the CTA line built word by word on the freeze
    dict(kind="words", t=57.79, t_end=58.86, dt_end=2.0, style="script", size=104, y=0.62,
         words=[("Jai", w("Jai", 57.85)), ("Maa", w("Maa", 58.05)), ("Chamunda", w("Chamunda", 58.2))]),
    dict(kind="sparkle", t=57.92, pos=(0.50, 0.58), seed=8),
    dict(kind="cta", t=58.62, dt=0.1, t_end=58.86, dt_end=2.0, words=["“Comment", "mein", "zaroor", "likhein”"], y=0.735, size=80),
]

# micro-shake bumps (S9 heroes) and extra tint pops
BUMPS = [w("parampara", 24.5), w("shringaar", 25.9), w("hissa", 26.9), w("sawaal", 28.15), w("dikhane", 29.92), w("vrat", 30.82)]
POPS = [(51.2, "purple", 0.0)]

MUSIC = dict(swell=47.34, happy=REFRAME, cta=57.33)

# ---- SFX: (source time, name, offset s, peak dBFS) ----
_cuts_white = [mid(7.32, 7.70), 11.57, mid(33.24, 33.66)]
SFX = []
for c in [mid(3.27, 3.67), mid(7.32, 7.70), 11.57, 20.51, mid(22.03, 22.61), mid(33.24, 33.66), mid(47.16, 47.52), REFRAME, mid(54.27, 54.41)]:
    SFX.append((c, "whoosh", -0.25, -17))
for c in _cuts_white + [20.51, mid(54.27, 54.41)]:
    SFX.append((c, "flash", -0.05, -17))
SFX += [(0.8, "shimmer", 0, -17), (0.8, "neon", 0, -20),
        (5.55, "bell", 0, -16), (5.55, "sparkle", 0, -19), (57.92, "bell", 0, -15), (57.92, "sparkle", 0, -19),
        (45.10, "pop", 0, -16), (45.10, "pop", 0.2, -16), (50.19, "pop", 0, -15), (56.37, "pop", 0, -15),
        (32.2, "swell", -0.3, -18), (49.21, "riser", -1.2, -18), (49.21, "boom", 0, -14),
        (mid(31.48, 31.94), "whip", -0.15, -16)]
SFX += [(8.0 + k * 0.1, "bloop", 0, -20) for k in range(6)]

# ---- B-roll briefs (placeholder slates until real stills are dropped into broll/bN.jpg) ----
BROLL = {
    1: dict(label="1 · hook", cx=0.5, cy=0.42, desc=["Young wife in red Karwa Chauth saree, sindoor,", "filming a reel with ring light + puja thali,", "family watching - warm tungsten light"]),
    2: dict(label="2 · alone by window", cx=0.5, cy=0.45, desc=["Married woman in plum kurta, chin on hand,", "holding chalni at a dusk window,", "couple photo on side table"]),
    3: dict(label="3 · mehendi + phone", cx=0.45, cy=0.5, desc=["Woman in rani-pink kurta on the floor,", "mehendi hands, scrolling Karwa Chauth reels,", "blind-light patterns on the wall"]),
    4: dict(label="4 · shraddha", cx=0.5, cy=0.42, desc=["Woman in maroon saree, head bowed in prayer", "before a diya, symmetrical, warm moody light"]),
    5: dict(label="5 · hands insert", cx=0.5, cy=0.55, desc=["Close-up: mehendi hands, red bangles, kundan ring", "holding a Karwa Chauth thali with diya"]),
    6: dict(label="6 · pati patni", cx=0.5, cy=0.45, desc=["Husband offering water to his wife after", "moon sighting, chalni in her hand, OTS shot"]),
    7: dict(label="7 · happy ending (video)", cx=0.5, cy=0.45, desc=["Couple laughing under string lights at night,", "rani-pink lehenga twirl, golden bokeh"]),
}
