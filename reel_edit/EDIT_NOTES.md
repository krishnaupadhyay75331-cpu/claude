# Maa Chamunda Jyotish reel: edit notes

**Expert-only cut, no B-roll.** The whole reel is built from the presenter's single take, using WIDE / MEDIUM / CLOSE punch-ins.

Deliverables are in `deliverables/`:

| File | What it is |
|---|---|
| `reel_final.mp4` | 1080×1920, 30 fps, H.264 High 18 Mbps, AAC 48 kHz, +faststart, **35.60 s** |
| `cover_frame.png` | Credibility-card frame ("21 SAAL" behind her head) |
| `captions.csv` / `captions.srt` | Caption table with hero and helper columns |
| `edl.csv` | Layer-by-layer EDL (timecode, layer, asset, motion, effect) |
| `word_timings.md` | Every word: source time, output frame and output time |

## ⚠ Read first

1. **The script is a Jyotish consultation promo,** not the relationship-consultant script the prompt assumed. Its CTA is **"DM mein 'consultation' likhkar bhejiye"**. There is **no link and no WhatsApp offer**, so neither was invented.
2. **Names to verify.** Whisper-small mis-hears proper nouns.
   - **"Pushpa Upadhyay ji"** is inferred. The captions show only **"Pushpa ji"**.
   - **"Maa Chamunda Jyotish"** is inferred, and it appears in the captions twice. Please confirm the spelling.
3. **The music and SFX are synthesised** in `render/audio.py`, so they're royalty-free by construction.

## What changed when the B-roll was removed

- **Removed:**
  - all 6 story inserts
  - the devices that only lived on them: thought bubble + glass cube, halo orb, gold film burn, the S1 neon "?", and the S6 happy ending
  - the B&W couple cut-out behind her (it was an image placeholder)
  - the world-switch transitions
- **Expert↔expert changes are hard cuts.** The bokeh + cream flash remains on just two cuts: into the CTA shot (26.17 s) and over the source jump cut (32.40 s).
- **Every tightening cut and the jump cut land on a framing change,** so none of them read as jump cuts.
- **The 0.75 s pause** that used to sit under the happy-ending B-roll would now be dead air on her face, so it's tightened like the other pauses. That makes the runtime **35.60 s, 0.4 s under the 36 s floor**. The alternative would be leaving a visible dead pause.
- **Kept:**
  - neon "?" above her head (1.90–3.40 s)
  - gradient hero "Kya"
  - letter-by-letter "Consultation"
  - service pills over her
  - the "21 SAAL" text-behind-subject card + gold sparkle
  - 3 snap zooms
  - CTA quote + pill
  - persistent DM pill + gold chevron
  - hard-cut ending

## 1. Analysis

- **Source:** HEVC 720×1280, 30 fps, 38.033 s, AAC 44.1 kHz, −24.5 LUFS.
- **Jump cut:** confirmed at **34.033 s (source frame 1021)**.
- **Pauses removed:**
  - 0–0.40 head
  - 5.60–5.77
  - 14.93–15.03
  - 17.85–18.08
  - 33.30–34.03, which resumes exactly on the post-jump frame
  - the 37.24–38.03 tail
- **Result:** 1068 frames = **35.60 s**.

## 2. Transcript (Hinglish, Roman script; source time)

| Source time | Line |
|---|---|
| 0.45–5.54 | Kya aapke mind mein bhi shaadi, career, ya future ko lekar koi aisa sawaal hai, jiska jawab aap kaafi time se dhoondh rahe ho? |
| 5.90–9.70 | Kabhi kabhi zaroorat hoti hai humein apni situation ko ek naye perspective se samajhne ki, |
| 9.98–14.88 | jiske liye aap mil sakte hain Pushpa Upadhyay(?) ji se, jinhe Jyotish ki field mein 21 saal ka experience hai. |
| 15.17–24.92 | Chahe aapko kundli vishleshan, face reading, prashna kundli, ya vastu se related guidance chahiye, Maa Chamunda(?) Jyotish mein aap apni zaroorat ke according consultation ke baare mein jaan sakte hain. |
| 25.12–29.08 | Agar aap bhi consultation lena chahte hain, toh abhi hume DM mein "consultation" likhkar bhejiye. |
| 29.37–33.20 | Hamari team aapko appointment aur consultation process ki poori details share kar degi. |
| *34.03* | *[jump cut]* |
| 34.07–37.12 | Maa Chamunda Jyotish: aapke sawaal ko samajhne ki ek nayi shuruaat. |

## 3. Beat map (output time)

| Beat | Out (s) | Frames | Lines |
|---|---|---|---|
| B1 Hook | 0.00–3.40 | 0–102 | Kya aapke mind mein bhi shaadi, career, ya future ko lekar koi aisa sawaal hai |
| B2 Problem | 3.40–5.20 | 102–156 | jiska jawab aap kaafi time se dhoondh rahe ho |
| B3 Emotional low | 5.20–9.40 | 156–282 | Kabhi kabhi zaroorat hoti hai… ek naye perspective se samajhne ki |
| B4 Authority | 9.40–11.77 | 282–353 | jiske liye aap mil sakte hain Pushpa ji se |
| B6 Credibility | 11.77–14.37 | 353–431 | jinhe Jyotish ki field mein **21 saal** ka experience hai |
| B5 Method | 14.37–24.20 | 431–726 | kundli vishleshan, face reading, prashna kundli, vastu… consultation ke baare mein jaan sakte hain |
| B8a CTA | 24.20–28.43 | 726–853 | agar aap bhi consultation lena chahte hain… DM mein consultation likhkar bhejiye |
| Process | 28.43–32.40 | 853–972 | Hamari team aapko appointment aur consultation process ki poori details share kar degi (music swells here) |
| B8b CTA close | 32.40–35.60 | 972–1068 | Maa Chamunda Jyotish, aapke sawaal ko samajhne ki ek nayi shuruaat |

## 4. Shot list

| # | Out (s) | Framing | Notes |
|---|---|---|---|
| 1 | 0.00–1.90 | MEDIUM | gradient hero "Kya" |
| 2 | 1.90–3.40 | WIDE | neon rose-gold "?" above her, rose tint flash |
| 3 | 3.40–5.20 | CLOSE | fake DOF |
| 4 | 5.20–6.37 | MEDIUM | starts on a tightening cut |
| 5 | 6.37–7.40 | CLOSE | silent: "humein apni situation ko" |
| 6 | 7.40–9.40 | WIDE | |
| 7 | 9.40–11.77 | MEDIUM | snap +8% on "Pushpa" |
| 8 | 11.77–14.37 | WIDE | **21 SAAL** behind her head, snap on "21", gold sparkle |
| 9 | 14.37–14.97 | CLOSE | silent: "chahe aapko"; starts on a tightening cut |
| 10 | 14.97–17.17 | MEDIUM | pills: Kundli Vishleshan, Face Reading |
| 11 | 17.17–19.83 | WIDE | pills: Prashna Kundli, Vastu; starts on a tightening cut |
| 12 | 19.83–21.87 | MEDIUM | |
| 13 | 21.87–24.20 | WIDE | letter-reveal "Consultation" |
| 14 | 24.20–26.17 | CLOSE | |
| 15 | 26.17–28.43 | MEDIUM | **flash in**, CTA quote + pill, snap on "DM" |
| 16 | 28.43–30.00 | WIDE | |
| 17 | 30.00–32.40 | CLOSE | |
| 18 | 32.40–33.43 | MEDIUM | **flash over the source jump cut**; persistent DM pill |
| 19 | 33.43–35.60 | CLOSE | gold chevron ↓ in the last 0.6 s, **hard cut** |

Captions are in `deliverables/captions.csv`. Each word pops on its own onset frame: opacity 0→100, blur 12→0 px, scale 105→100% over 6 frames.

## 5. Audio

- **Voice:** afftdn (light), HPF 80 Hz, +2 dB @ 3.5 kHz, de-esser, compressor 3.5:1 @ −18 dB.
- **Music:** 72 BPM piano and pad on Am–F–C–G, with a lift at the pills, a swell under "consultation process… details", and a C-major resolve on the CTA close. It stops on the hard cut. It sits 12 dB under speech RMS, with a further 4 dB sidechain duck.
- **SFX (13 events):** whoosh + shimmer on the 2 flashes, neon buzz, 3 whoosh-hits, gold shimmer, and typewriter ticks.
- **Master:** two-pass loudnorm.

## 6. QC report

| Check | Result | Detail |
|---|---|---|
| Duration 36–40 s | **FAIL (by 0.4 s)** | 35.60 s. Everything is content, nothing is padded. To reach 36.0 s, keep 0.4 s more of the pause before "Maa Chamunda" (`plan.py`, jump-cut line). |
| No dead pauses; jump cut hidden | **PASS** | All pauses are ≤ 0.25 s. The jump cut sits under a flash and a punch-in. |
| Captions on the spoken frame; one hero at a time; Roman Hinglish | **PASS\*** | Keyed to onsets refined from Whisper-small. \*Real accuracy is about ±2–3 frames, so please spot-check by ear. |
| Safe zone x 90–990, y 220–1620 | **PASS** | Captions span x 142–938, y 1328–1528. |
| Palette (no teal / cyan / navy) | **PASS** | Rose / sage / gold / cream / walnut only. |
| Text-behind-subject matte clean | **PASS** | MediaPipe matte + guided filter. Checked at full resolution. |
| Credibility numbers only from her words | **PASS** | "21 saal". |
| Upscale; punch-ins ≤ 145% | **PASS** | Lanczos-4 + light unsharp mask. Maximum 136%. |
| Loudness / true peak | **PASS** | −14.0 LUFS, −2.7 dBTP, LRA 2.2 LU. |
| Hard cut at the end, no outro | **PASS** | Ends on "shuruaat". |
| Signature devices | **Reduced by request** | The B-roll-only devices were removed with the B-roll (see above). |
