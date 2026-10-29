# Maa Chamunda Jyotish reel: edit notes

Deliverables are in `deliverables/`:

| File | What it is |
|---|---|
| `reel_final.mp4` | 1080×1920, 30 fps, H.264 High 18 Mbps, AAC 320k/48 kHz, +faststart, 36.07 s |
| `cover_frame.png` | Credibility-card frame ("21 SAAL" behind her head) |
| `captions.csv` / `captions.srt` | Caption table with hero and helper columns |
| `edl.csv` | Layer-by-layer EDL (timecode, layer, asset, motion, effect) |
| `ai_prompts.md` | Image and video prompts, plus generation status |
| `word_timings.md` | Every word: source time, output frame and output time |

## ⚠ Read first

1. **The script is not the one the prompt assumed.** It is a **Jyotish consultation promo**, not a relationship-consultant pitch. Its CTA is **"DM mein 'consultation' likhkar bhejiye"**. There is **no link and no WhatsApp offer**, so neither was invented. The edit grammar is the same and the story world was rewritten around "shaadi / career / future questions".
2. **Names to verify.** Whisper-small mis-hears proper nouns.
   - **"Pushpa Upadhyay ji"** is inferred from "pushpa aap aadai jise". The captions show only **"Pushpa ji"**, to be safe.
   - **"Maa Chamunda Jyotish"** is inferred from "maa chaamuna Jyotish". It appears in the captions twice, so please confirm the spelling.
3. **The B-roll is labelled placeholders.**
   - Higgsfield had 0 credits.
   - Canva's quota allowed 3 images, and its full-resolution files can't be downloaded into the render container.
   - Hugging Face Space invocation is disabled.
   - Stock-photo hosts are blocked from the container.

   Every insert still carries its final motion, overlay, transition and timing. Drop real files into `assets/` and re-render (see `README.md`); nothing else changes.
4. **The music and SFX are synthesised** in `render/audio.py`, so they're royalty-free by construction. Any stock library track can replace the music bed.

## 1. Analysis

- **Source:** HEVC 720×1280, 30 fps, 38.033 s, AAC 44.1 kHz. Integrated loudness −24.5 LUFS, LRA 5.4 LU.
- **Jump cut:** confirmed at **34.033 s (source frame 1021)**, inside a 1.02 s pause (33.065–34.081).
- **Pauses removed** (silencedetect −38 dB / 0.25 s): 0–0.40 head, 5.60–5.77, 14.93–15.03, 17.85–18.08, 33.30–33.57, and the 37.24–38.03 tail. Each pause is cut back to about 0.25 s.
  - The jump-cut pause keeps 0.75 s of breath under the happy-ending B-roll, where the music swells.
  - Every tightening cut lands on a shot change or under B-roll, so none of them read as jump cuts.
- **Result:** 1082 frames = **36.07 s**.

## 2. Transcript (Hinglish, Roman script)

**Full transcript** (source time; word-level detail is in `deliverables/word_timings.md`):

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

**Tightened transcript:** the words are identical. Only the pauses listed above were shortened. There were no "umm"s to remove.

## 3. Beat map (output time)

| Beat | Out (s) | Frames | Lines |
|---|---|---|---|
| B1 Hook | 0.00–3.40 | 0–102 | Kya aapke mind mein bhi shaadi, career, ya future ko lekar koi aisa sawaal hai |
| B2 Problem deepening | 3.40–5.30 | 102–159 | jiska jawab aap kaafi time se dhoondh rahe ho |
| B3 Emotional low | 5.30–9.40 | 159–282 | Kabhi kabhi zaroorat hoti hai… ek naye perspective se samajhne ki |
| B4 Authority | 9.40–11.77 | 282–353 | jiske liye aap mil sakte hain Pushpa ji se |
| B6 Credibility | 11.77–14.37 | 353–431 | jinhe Jyotish ki field mein **21 saal** ka experience hai (her own figure) |
| B5 Method / solution | 14.37–24.20 | 431–726 | kundli vishleshan, face reading, prashna kundli, vastu… consultation ke baare mein jaan sakte hain |
| B8a CTA | 24.20–28.43 | 726–853 | agar aap bhi consultation lena chahte hain… DM mein consultation likhkar bhejiye |
| (bridge) | 28.43–30.00 | 853–900 | Hamari team aapko appointment aur |
| B7 Happy ending | 30.00–32.87 | 900–986 | consultation process ki poori details share kar degi + breath + music swell |
| B8b CTA close | 32.87–36.07 | 986–1082 | Maa Chamunda Jyotish, aapke sawaal ko samajhne ki ek nayi shuruaat. Persistent DM pill, gold chevron, hard cut |

B6 comes before B5 because that's the order she speaks them in.

## 4. Caption plan

See `deliverables/captions.csv` for the full table (phrase, start/end in seconds and frames, hero, helper above-right, helper below-left, special, shot). Each word pops on its own onset frame: opacity 0→100, blur 12→0 px, scale 105→100% over 6 frames.

| Special | Where |
|---|---|
| **Gradient hero** | "Kya", 130 px Poppins Light, rose → walnut, at 0.03 s |
| **Letter-by-letter** | "Consultation", 2 f/letter, at 21.97 s |
| **Var-1 caption over the bokeh** | "Dhoondh / rahe ho" at the S2→S4 flash |
| **Pills** (rose / sage alternating, slide + typewriter) | Kundli Vishleshan · Face Reading · Prashna Kundli · Vastu |
| **Card C** | Script "Jyotish ki field mein", then **21 SAAL** behind her head, then script "ka experience" |
| **CTA** | "DM mein likhkar bhejiye" in quotes + pill `consultation`; after the jump cut, a persistent pill `DM "consultation"` and a gold ↓ chevron in the last 0.6 s |
| **Silent close-ups** | 6.37–7.40 s ("humein apni situation ko") and 14.37–14.97 s ("chahe aapko") |

## 5. Shot list and B-roll plan

| # | Out in–out (s) | Shot | Framing / motion | Overlay |
|---|---|---|---|---|
| 1 | 0.00–1.90 | **S1** living room, family | push 100→112% + truck right | neon rose-gold "?" (flicker 0/100/30/100, 1.5 s pulse) |
| 2 | 1.90–3.40 | WIDE | 100→104% | **Card A**: B&W couple behind her (matte), neon "?" above her, rose tint flash |
| 3 | 3.40–5.30 | **S2** bedroom, diary + chai | push 100→108% | **thought bubble** pop (0→110→100%), **glass cube** drift |
| 4 | 5.30–6.37 | **S4** hugging knees | very slow push | **halo orb** 1.8 s pulse (behind her once a real still is supplied) |
| 5 | 6.37–7.40 | CLOSE | 132→136%, fake DOF | silent |
| 6 | 7.40–9.40 | **S3** floor, blind shadows | tilt-down | **gold light-leak**, then golden white-out (var 2) |
| 7 | 9.40–11.77 | MEDIUM | 122→126%, **snap +8%** on "Pushpa" | |
| 8 | 11.77–14.37 | WIDE | 100→104%, **snap +8%** on "21" | **Card C**, gold sparkle |
| 9 | 14.37–14.97 | CLOSE | | silent |
| 10 | 14.97–17.17 | **S5a** kundli close-up | push 100→110% | pills 1–2 |
| 11 | 17.17–19.83 | **S5b** consultation | pan L→R | pills 3–4, cream flare out (var 3) |
| 12 | 19.83–21.87 | MEDIUM | | |
| 13 | 21.87–24.20 | WIDE | | letter-reveal "Consultation" |
| 14 | 24.20–26.17 | CLOSE | | |
| 15 | 26.17–28.43 | MEDIUM | **snap +8%** on "DM" | CTA quote + pill |
| 16 | 28.43–30.00 | WIDE | | riser into B7 |
| 17 | 30.00–32.87 | **S6** night garden (i2v) | drift; opens on gold flare | rose/sage/gold bokeh, music swell |
| 18 | 32.87–33.90 | MEDIUM | punch-in **hides the 34.03 s jump cut** | persistent DM pill |
| 19 | 33.90–36.07 | CLOSE | | chevron ↓; **hard cut** on "shuruaat" |

**Transitions:** 10 world-switch transitions. Seven are the standard rose/sage/gold bokeh with a cream `#FFF6EC` flash (12 frames), plus var 1 (caption on top), var 2 (golden film burn) and var 3 (cream flare). Expert↔expert changes are hard cuts.

## 6. Audio

- **Voice:** afftdn (light), HPF 80 Hz, +2 dB @ 3.5 kHz, de-esser, compressor 3.5:1 @ −18 dB, then a peak catcher.
- **Music:** 72 BPM piano and pad on Am–F–C–G.
  - Minimal for B1–B4.
  - An arpeggio lift starts at the pills.
  - Fadd9 → G swell under the happy ending.
  - C-major resolve on the CTA, stopping on the hard cut.
  - It sits 12 dB under speech RMS, with a further 4 dB sidechain duck while she talks.
- **SFX (24 events):** whoosh + shimmer per transition, neon buzz ×2, bubble pop, 3 whoosh-hits, gold shimmer, riser, and typewriter ticks.
- **Master:** two-pass loudnorm.

## 7. QC report

| Check | Result | Detail |
|---|---|---|
| Duration 36–40 s; no dead pauses; jump cut hidden | **PASS** | 36.067 s. The jump cut sits under S6 and is followed by a punch-in. One intentional 0.75 s breath under the B7 music swell. |
| Caption words within ±1 f of speech; one hero at a time; Roman Hinglish | **PASS\*** | Each word is keyed to its onset frame, refined from Whisper-small and snapped to audio-energy onsets. \*True accuracy is about ±2–3 frames, limited by the small ASR model. **Please spot-check by ear.** Hero words never stack. |
| Safe zone x 90–990, y 220–1620 | **PASS** | Captions span x 142–938, y 1328–1528. Card C spans y ≈ 300–760, the chevron y ≈ 1585, and the top 220 px stays empty. |
| No teal / cyan / navy | **PASS** | Every graphic colour comes from the rose / sage / gold / cream / walnut tokens. |
| Every signature device present | **PASS (placeholder art)** | Neon "?" ×2, B&W couple composite, thought bubble + glass cube, gold film burn, halo orb, gradient hero, letter reveal, pills, text-behind-subject number, CTA pill and bokeh flashes are all in. The couple and bubble *photos* are placeholders. |
| Text-behind-subject matte clean | **PASS** | MediaPipe multiclass matte, refined with a guided filter. Checked at full resolution on frames 405 and 420: no halo around the hair. |
| B-roll client consistent and different from the presenter | **PENDING** | Depends on the assets you generate. The prompts enforce a dusty-rose kurta and messy bun, and the astrologer's face is hidden. |
| Credibility numbers only from her words | **PASS** | "21 saal" is spoken at 13.62 s. No other figures were used. |
| Upscale not over-sharpened; punch-ins ≤ 145% | **PASS** | Lanczos-4 plus a light unsharp mask (0.35, σ 1). Maximum zoom 136% including snaps. |
| Loudness −14 ±1 LUFS, TP ≤ −1 dBTP, no clipping, music under speech | **PASS** | −14.0 LUFS, TP −2.7 dBTP, LRA 2.3 LU. The music level is set by measurement, not checked by ear. |
| Hard cut at the end, no outro card | **PASS** | Ends on "shuruaat" with the chevron visible. |
| Wall level | **PASS (edge)** | Cream wall at about 84 IRE after the grade: creamy and not crushed. |

## Deviations from the brief (and why)

- **Card C bottom.** The script word "ka experience" is shown *without* a pill. Her only other claim is her name, already shown as a hero word, and inventing a second claim would break the no-fabrication rule.
- **CTA.** The CTA uses her real words (DM / "consultation"). There's no "Click the link Below" and no WhatsApp line.
- **Hard cut into the CTA.** The cut into the CTA shot is a hard cut with a snap zoom instead of a flash, which keeps the flash count at 10 instead of 11.
- **Gradient hero colour.** The gradient on "Kya" stops at 65% of the way to walnut so the word stays legible on dark ground.
