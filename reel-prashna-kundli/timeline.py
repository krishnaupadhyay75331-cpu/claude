"""Edit decision data for the Prashna Kundli reel.

All times written here are on the RAW clip (seconds). r2n() maps them onto the
tightened timeline, so captions stay locked to the word timestamps.
"""

FPS = 30
W, H = 1080, 1920

# Kept source ranges in raw frames, [start, end). Everything else is removed.
#   0.00-0.43  lead-in silence (keeps 4 frames before the first word)
#   3.20-3.47  part of the S1 pause (10 frames of pause are kept for the flash)
#   20.17-20.60 part of the S4 pause, including the 20.40 camera cut
#   25.77-end  tail (hard end 8 frames after the last word)
SEGS = [(13, 96), (104, 605), (618, 773)]

NEW_FRAMES = sum(b - a for a, b in SEGS)


def r2n(t):
    """Raw seconds -> new-timeline seconds."""
    off = 0
    for a, b in SEGS:
        if t < b / FPS:
            return max(0.0, t - a / FPS) + off
        off += (b - a) / FPS
    return off


def new_to_raw_frame(n):
    for a, b in SEGS:
        if n < b - a:
            return a + n
        n -= b - a
    raise IndexError(n)


def seg_cut(i):
    """New-timeline time of the i-th segment join."""
    return sum((b - a) for a, b in SEGS[: i + 1]) / FPS


# Colour tokens (Section 3)
ROSE = (0xD6, 0x3A, 0x6E)
ROSE_DEEP = (0x9E, 0x1F, 0x4A)
GOLD = (0xD9, 0xA4, 0x41)
CREAM = (0xF7, 0xEF, 0xE4)
FLASH = (0xFF, 0xF6, 0xEC)
MAUVE = (0x8E, 0x6A, 0x8F)
WALNUT = (0x2A, 0x1A, 0x12)
SAGE = (0xA9, 0xB3, 0xA0)
NEON = (0xFF, 0x5C, 0x93)
NEON_IN = (0xFF, 0xC2, 0xD6)

# Shot boundaries (new-timeline seconds)
B1 = seg_cut(0)          # S1 -> S2, flash
B2 = r2n(6.36)           # -> "Kya" story slot, flash
B3 = r2n(7.93)           # -> WIDE, flash
B4 = r2n(10.70)          # hard cut WIDE -> TIGHT
B5 = r2n(12.41)          # S2 -> S3, flash
B6 = r2n(14.15)          # golden film-burn flash
B7 = r2n(16.95)          # S3 -> S4, flash  (pause 16.90-17.22, 10 frames kept)
B8 = r2n(18.35)          # hard cut TIGHT -> credibility card
B9 = seg_cut(1)          # camera cut A -> B, flash
B10 = r2n(22.80)         # happy-ending slot -> CTA, flash
END = NEW_FRAMES / FPS

# framing: kind, setup, slot (B-roll still/clip that replaces the A-roll if present)
SHOTS = [
    dict(name="1 HOOK", t0=0, t1=B1, frame="hook_kb", setup="A", slot="broll/1_hook", story=True),
    dict(name="2 WIDE + couple", t0=B1, t1=B2, frame="wide", setup="A", mauve_flash=True),
    dict(name="3 MEMORY / Kya", t0=B2, t1=B3, frame="tight_story", setup="A", slot="broll/2_memory", story=True),
    dict(name="4 WIDE solution", t0=B3, t1=B4, frame="wide", setup="A"),
    dict(name="4b TIGHT pills", t0=B4, t1=B5, frame="tight", setup="A"),
    dict(name="5 HOPELESS + leak", t0=B5, t1=B6, frame="mid_story", setup="A", slot="broll/3_hopeless", story=True),
    dict(name="6 WIDE list", t0=B6, t1=B7, frame="wide", setup="A"),
    dict(name="8a TIGHT beat", t0=B7, t1=B8, frame="tight", setup="A", slot="broll/7_kundli"),
    dict(name="8b CRED CARD", t0=B8, t1=B9, frame="card", setup="A"),
    dict(name="9 HAPPY ENDING", t0=B9, t1=B10, frame="b_story", setup="B", slot="broll/8_happy", story=True),
    dict(name="10 CTA", t0=B10, t1=END, frame="cta", setup="B"),
]

# Bokeh-flash transitions (centre = cut time). Shot 5 -> 6 uses the golden film burn.
FLASHES = [B1, B2, B3, B5, B7, B9, B10]
GOLD_BURN = B6

# Word timestamps (raw seconds) - Whisper word timing, Roman Hinglish.
TRANSCRIPT = [
    # S1  HOOK
    ("Bahut", 0.56, 0.86), ("se", 0.86, 0.98), ("logo", 0.98, 1.20), ("ko", 1.20, 1.40),
    ("apna", 1.40, 1.58), ("exact", 1.58, 1.92), ("birth", 1.92, 2.10), ("time", 2.10, 2.28),
    ("yaad", 2.28, 2.56), ("nahi", 2.56, 2.78), ("hota", 2.78, 2.97),
    # S2  HOOK -> SOLUTION
    ("isi", 3.58, 3.84), ("wajah", 3.84, 4.10), ("se", 4.10, 4.20), ("wo", 4.20, 4.34),
    ("apne", 4.34, 4.58), ("questions", 4.58, 5.04), ("ko", 5.04, 5.14), ("lekar", 5.14, 5.42),
    ("confuse", 5.42, 5.90), ("ho", 5.90, 5.96), ("jaate", 5.96, 6.26), ("hain", 6.26, 6.35),
    ("lekin", 6.45, 6.98), ("kya", 6.98, 7.20), ("aap", 7.20, 7.32), ("jaante", 7.32, 7.80),
    ("hain", 7.80, 7.88), ("Prashna", 8.00, 8.28), ("Kundli", 8.28, 8.60), ("ke", 8.60, 8.78),
    ("through", 8.78, 9.04), ("aap", 9.08, 9.20), ("apne", 9.20, 9.42), ("kisi", 9.42, 9.74),
    ("specific", 9.74, 10.22), ("sawaal", 10.22, 10.54), ("par", 10.54, 10.74),
    ("jyotish", 10.74, 11.20), ("guidance", 11.20, 11.62), ("le", 11.62, 11.82),
    ("sakte", 11.82, 12.12), ("hain", 12.12, 12.24),
    # S3  PROBLEM SCOPE
    ("chahe", 12.57, 12.74), ("sawaal", 12.74, 13.12), ("career", 13.12, 13.48), ("ko", 13.48, 13.60),
    ("lekar", 13.60, 13.90), ("ho,", 13.90, 14.05), ("shaadi", 14.26, 14.60), ("ko", 14.60, 14.74),
    ("lekar,", 14.74, 15.02), ("ya", 15.02, 15.16), ("life", 15.16, 15.44), ("mein", 15.44, 15.56),
    ("chal", 15.56, 15.72), ("rahi", 15.72, 15.96), ("confusion", 15.96, 16.42), ("ko", 16.42, 16.60),
    ("lekar", 16.60, 16.90),
    # S4  METHOD
    ("sabse", 17.22, 17.58), ("pehle", 17.58, 17.76), ("apne", 17.76, 18.02), ("sawaal", 18.02, 18.42),
    ("ko", 18.42, 18.62), ("properly", 18.62, 18.94), ("samajhna", 18.94, 19.42),
    ("zaroori", 19.42, 19.80), ("hai", 19.80, 19.89),
    # S5  CTA (Setup B)
    ("aap", 20.67, 20.90), ("bhi", 20.90, 21.02), ("Prashna", 21.02, 21.30), ("Kundli", 21.30, 21.60),
    ("ke", 21.60, 21.72), ("baare", 21.72, 21.88), ("mein", 21.88, 21.98), ("jaanna", 21.98, 22.26),
    ("chahte", 22.26, 22.62), ("hain,", 22.62, 22.82), ("to", 22.82, 22.96),
    ("consultation", 22.96, 23.60), ("ke", 23.60, 23.78), ("liye", 23.78, 24.08),
    ("[Chaman Jyotish?]", 24.08, 24.74), ("ko", 24.74, 24.88), ("DM", 24.88, 25.06),
    ("kijiye", 25.06, 25.51),
]

# Keyword-typography phrases. before/after = helper words with spoken time (raw).
# style: normal | letters | gradient ; ul = gold underline
PHRASES = [
    dict(before=[("bahut", 0.56), ("se", 0.86)], hero=("Logo", 0.98), after=[("ko", 1.20)], end=1.38),
    dict(before=[("apna", 1.40), ("exact", 1.58)], hero=("Birth Time", 1.92),
         after=[("yaad", 2.28), ("nahi", 2.56), ("hota", 2.78)], end=3.12, ul=True),
    dict(before=[("isi", 3.58), ("wajah", 3.84), ("se", 4.10), ("wo", 4.20), ("apne", 4.34)],
         hero=("Questions", 4.58), after=[("ko", 5.04), ("lekar", 5.14)], end=5.40),
    dict(before=[], hero=("Confuse", 5.42), after=[("ho", 5.90), ("jaate", 5.96), ("hain", 6.26)], end=6.33),
    dict(before=[("lekin", 6.45)], hero=("Kya", 6.98), after=[("aap", 7.20), ("jaante", 7.32), ("hain", 7.80)],
         end=7.90, style="gradient"),
    dict(before=[], hero=("Prashna Kundli", 8.00), after=[("ke", 8.60), ("through", 8.78)], end=9.05,
         style="letters", ul=True),
    dict(before=[("aap", 9.08), ("apne", 9.20), ("kisi", 9.42), ("specific", 9.74)], hero=("Sawaal", 10.22),
         after=[("par", 10.54)], end=10.69),
    dict(before=[("chahe", 12.57), ("sawaal", 12.74)], hero=("Career", 13.12),
         after=[("ko", 13.48), ("lekar", 13.60), ("ho", 13.90)], end=14.10),
    dict(before=[], hero=("Shaadi", 14.26), after=[("ko", 14.60), ("lekar", 14.74)], end=15.00),
    dict(before=[("ya", 15.02)], hero=("Life", 15.16), after=[("mein", 15.44), ("chal", 15.56), ("rahi", 15.72)],
         end=15.94),
    dict(before=[], hero=("Confusion", 15.96), after=[("ko", 16.42), ("lekar", 16.60)], end=16.93,
         style="letters", ul=True),
    # 17.06-18.02 = the captionless TIGHT beat ("sabse pehle apne")
    dict(before=[], hero=("Sawaal", 18.02), after=[], end=18.33),
    # 18.35-20.17 credibility card carries the screen (no keyword captions)
    dict(before=[("aap", 20.67), ("bhi", 20.90)], hero=("Prashna Kundli", 21.02),
         after=[("ke", 21.60), ("baare", 21.72), ("mein", 21.88), ("jaanna", 21.98), ("chahte", 22.26), ("hain", 22.62)],
         end=22.76),
    dict(before=[("to", 22.82)], hero=("Consultation", 22.96), after=[("ke", 23.60), ("liye", 23.78)], end=24.05),
]

# Emphasis pills: text, appear time (raw), slot index (0 = first, 1 = stacked below), y of first pill
PILL_GROUPS = [
    dict(items=["Prashna Kundli", "Jyotish Guidance"], t=10.74, end=12.30, y=1150,
         helper=[("le", 11.62), ("sakte", 11.82), ("hain", 12.12)]),
]

# Credibility card (raw times). Numbers are PLACEHOLDERS - nothing was said on camera.
CARD = dict(t0=18.35, t1=20.17, script_top="Pichhle", number="[X SAAL]",
            script_bottom="clients", pill="More than [XXXX+]")

# CTA (raw times)
CTA = dict(line_t=24.08, line="“DM kijiye”", pill_t=24.30, pill="DM for Consultation",
           arrow_t=25.00)
