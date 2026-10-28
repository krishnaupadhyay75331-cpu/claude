# Prashna Kundli Reel: edit notes

Output: `out/reel_prashna_kundli_v1.mp4`. 1080×1920, 30 fps, H.264 High at ~18 Mbps, AAC 320 kbps 48 kHz, **24.63 s**.

## 1. Transcript (Whisper, Roman Hinglish)

**Transcription caveat:** Hugging Face is blocked in this environment, so large-v3 could not be downloaded. I used **Whisper small** (CTranslate2 int8, the only Whisper weights reachable through npm). I ran Hindi and English passes on each block and reconciled them by hand. Word times are accurate to about ±0.1 s.

| Block | Role (adapted) | Line |
|---|---|---|
| S1 0.56–2.97 | HOOK / pain | Bahut se logo ko apna exact birth time yaad nahi hota. |
| S2 3.58–6.35 | HOOK, continued | Isi wajah se wo apne questions ko lekar confuse ho jaate hain. |
| S2 6.45–12.24 | **SOLUTION reveal** | Lekin kya aap jaante hain, Prashna Kundli ke through aap apne kisi specific sawaal par jyotish guidance le sakte hain. |
| S3 12.57–16.90 | PROBLEM scope / agitation | Chahe sawaal career ko lekar ho, shaadi ko lekar, ya life mein chal rahi confusion ko lekar. |
| S4 17.22–19.89 | METHOD / credibility | Sabse pehle apne sawaal ko properly samajhna zaroori hai. |
| S5 20.67–25.51 | CTA (Setup B) | Aap bhi Prashna Kundli ke baare mein jaanna chahte hain, to consultation ke liye **[Chaman Jyotish?]** ko DM kijiye. |

**Mapping change:** you name the solution (Prashna Kundli) at 7.3 s, earlier than the reference's structure expects. S3 is a list of life areas rather than pain. So:
- The "Kya" gradient question lands on *"Lekin kya aap jaante hain"*.
- The solution pills land at the end of S2.
- The film-burn "hopeless" beat covers *career / shaadi*.
- The visual grammar is unchanged.

The full word-level table is in `build/transcript_table.md`, which is generated from `timeline.py`.

## 2. Hero / helper split

| new t | helpers before (above-right) | **HERO** | helpers after (below-left) | treatment |
|---|---|---|---|---|
| 0.55 | bahut se | **Logo** | ko | blur-in, neon "?" flickers on |
| 1.49 | apna exact | **Birth Time** | yaad nahi hota | gold underline |
| 3.88 | isi wajah se wo apne | **Questions** | ko lekar | |
| 4.72 | | **Confuse** | ho jaate hain | |
| 6.28 | lekin | **Kya** | aap jaante hain | MAUVE→ROSE_DEEP gradient, gold sparkles |
| 7.30 | | **Prashna Kundli** | ke through | letter reveal, gold underline |
| 9.52 | aap apne kisi specific | **Sawaal** | par | |
| 10.04 | | pills: `Prashna Kundli` / `Jyotish Guidance` | le sakte hain | typewriter + ticks |
| 12.42 | chahe sawaal | **Career** | ko lekar ho | |
| 13.56 | | **Shaadi** | ko lekar | |
| 14.46 | ya | **Life** | mein chal rahi | |
| 15.26 | | **Confusion** | ko lekar | letter reveal, gold underline |
| 16.25–17.32 | (no captions: the silent TIGHT beat over "sabse pehle apne") | **Sawaal** | | |
| 17.65–19.47 | credibility card instead of captions | | | |
| 19.89 | aap bhi | **Prashna Kundli** | ke baare mein jaanna chahte hain | |
| 21.83 | to | **Consultation** | ke liye | |
| 22.95 | | "DM kijiye" + pill `DM for Consultation` + gold ↓ ×3 | | |

## 3. Final timeline

| new start | new end | shot | visual (as rendered) | overlay | caption words | SFX |
|---|---|---|---|---|---|---|
| 0.00 | 2.77 | 1 HOOK | **[B-roll slot 1 empty]** → her, story grade, Ken Burns 110→126% + truck right | rose neon "?" above head, flicker + pulse | Logo, Birth Time | neon buzz; music starts frame 1 |
| 2.77 | 5.66 | 2 WIDE | Setup A 100→104%, mauve tint flash | small neon "?"; **[couple PNG slot empty]** | Questions, Confuse | whoosh + shimmer at 2.77 |
| 5.66 | 7.23 | 3 MEMORY | **[B-roll slot 2 empty]** → TIGHT, story grade, 138→146% | gold sparkles; **[thought bubble needs still #5]** | Kya (gradient) | whoosh + shimmer at 5.66 |
| 7.23 | 10.00 | 4 WIDE | Setup A 100→104% | | Prashna Kundli (letters), Sawaal | whoosh + shimmer at 7.23 |
| 10.00 | 11.71 | 4b TIGHT | 138→142%, unsharp | two stacked rose pills | le sakte hain | typewriter ticks; music lifts |
| 11.71 | 13.45 | 5 HOPELESS | **[B-roll slot 3 empty]** → 115→122%, story grade | gold/orange film-burn sweep → gold → cream flash | Career | whoosh at 11.71, riser 12.85, whoosh + shimmer at 13.45 |
| 13.45 | 16.25 | 6 WIDE | Setup A 100→104% | | Shaadi, Life, Confusion (letters) | |
| 16.25 | 17.65 | 8a TIGHT | 138→142% (**[kundli still #7 slot empty]**) | | silent beat → Sawaal | whoosh + shimmer at 16.25 |
| 17.65 | 19.47 | 8b CARD | 122→125% | "Pichhle" + **[X SAAL]** behind your head (ISNet mask); "clients" + pill **More than [XXXX+]** | | ticks |
| 19.47 | 21.67 | 9 HAPPY END | **[B-roll clip slot 8 empty]** → Setup B, story grade | golden flare clears | Prashna Kundli | whoosh at 19.47 (covers the camera cut); music swell |
| 21.67 | 24.63 | 10 CTA | Setup B 118→125% push | "DM kijiye", pill, gold arrow ×3 | Consultation | whoosh at 21.67, ticks; music resolves on "kijiye" (23.93) |

Hard end at 24.63, 8 frames after the last word.

**Shot 7 (halo):** skipped. There was no spare time, since S3 runs straight into S4.

## 4. Placeholders and claims to confirm

1. **Years of experience: `[X SAAL]`.** Not said on camera, so it's a placeholder.
2. **Client count: `More than [XXXX+]`.** Not said on camera, so it's a placeholder.
3. **The name in the CTA (24.08–24.74 s).** Whisper hears "Chaman Jyotish / Chamanajyothi". It is **not** shown on screen. Tell me the exact handle if you want it in the CTA.
4. **The CTA offer.** You say *DM for consultation*, so the CTA pill reads `DM for Consultation` and the quote line reads "DM kijiye". There is no "Click the link below" or "FREE" offer, because you don't say either.
5. **S4 word "properly".** It is a low-confidence word; it isn't shown on screen.

## 5. What I could not do (and why)

| Step | Status |
|---|---|
| AI stills #1–#7 and the image-to-video clip #8 | **Not generated.** Higgsfield has 0 credits, Canva `generate-image` returned HTTP 409, and the Hugging Face Space invoke is disabled (`gradio=none`). Each slot falls back to your own footage with the B-roll grade and motion. |
| Arguing-couple PNG behind you, thought bubble | Code is ready but there are no assets, so they are not shown. |
| Whisper large-v3 | Blocked download. I used small instead (see §1). |
| Licensed piano track (Epidemic / Artlist) | No access. The bed is an **original piano + pad composed in code** (`audio.py`), so it is royalty-free by construction, at ~75 BPM, Am–F → C–G–Am–F lift → F–G swell → C resolve. |
| SFX library | All SFX (whoosh, shimmer, neon buzz, ticks, riser) are synthesized in code. |

## 6. Dropping in the B-roll later (one command)

Save your generated files with these names into `broll/`, then re-run `./build.sh`:

| file | used in |
|---|---|
| `broll/1_hook.jpg` | Shot 1 (Ken Burns 100→115% + truck) |
| `broll/2_memory.jpg` | Shot 3 |
| `broll/3_hopeless.jpg` | Shot 5 |
| `broll/7_kundli.jpg` | Shot 8a |
| `broll/8_happy.mp4` (or `.jpg`) | Shot 9 |
| `broll/5_happy_couple.jpg` | thought bubble in Shot 3 (pops in with a pop SFX) |
| `broll/6_couple.png` | B&W arguing couple **behind you** in Shot 2 (transparent PNG; it is masked, 85% opacity, with a cream glow) |

Stills get the golden-hour / mauve-shadow grade automatically. When a still fills Shot 3, consider moving the "Kya" word up to ~52% height in `render.py`.

### Doing it in CapCut instead
1. Import the MP4, then add each still as an overlay at the times in §3.
2. Set the overlay to full-frame 1080×1920 and add keyframes: scale 100% at the in-point, 110–115% at the out-point.
3. Put the overlay **under** the existing flashes. They are baked into the MP4, so trim each overlay to start and end on the flash's cream frames, at the times listed in the SFX column.

## 7. Rebuild

```
./build.sh /path/to/source.mov
```
Requirements: python3, numpy, opencv-python-headless, pillow, onnxruntime, ffmpeg, and the ISNet model at `build/isnet_medium.onnx` (from the npm package `@imgly/background-removal-node`).
