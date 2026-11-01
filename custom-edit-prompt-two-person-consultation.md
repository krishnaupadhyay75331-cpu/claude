# Custom Edit Prompt for Claude: Two-Person Consultation Clip, Edited in the "Hinglish Advice Reel" Style

> **How to use:** paste everything below the line into Claude, and attach the raw clip `copy_8843FCC7-12AF-42F7-B5BF-AC68147FD6AA-compressed.mov` with it.
> It's a self-contained brief: it repeats every style spec from the reference prompt (word-stack captions, neon "?", depth titles, pills, callout tags, transitions, sound design). Those specs are adapted to this footage's colours and to a 36-second, two-person conversation.

---

## 0. Your role and the order of work

You are a senior short-form video editor and motion designer. Edit the attached raw clip into a finished **9:16 Hinglish reel**. Copy the motion graphics, text styles, text animation, transitions, overlays, pacing and sound design of the reference style described below. **Change the colour scheme** to this footage's palette (section 2): plum-purple, lilac, rani rose-pink, temple gold, walnut brown and cream. **Do not use the reference's teal/cyan/navy accents.**

Work in this order. Do not skip a step.

1. **Transcribe** the whole clip word by word, with timestamps, in **Roman-script Hinglish**, spelled the casual way people type it in reels ("kyu", "apko", "hai", "rha", "nhi", "smjh"; not formal Hindi, not Devanagari). **Label the speaker on every line**: `A` = the young woman (glasses, pink floral kurta), `B` = the older woman (purple saree).
2. **Work out the story:** what problem A brings, what B explains as the cause, what B offers (remedy, puja, guidance, consultation), any years of experience or client counts said aloud, any names or titles said aloud, and the call to action. Decide the **niche** from the speech (relationship, marriage delay, family conflict, career, health, vastu, astrology, etc.). The deity idols in the background (Shiva, Radha-Krishna) suggest a spiritual/astrology consultant, but **confirm it from the audio**.
3. **Fill in the caption plan.** Use the timeline in section 8. Put the real words into every row, choose the HERO word for each stack, and choose which conditional graphics to use (section 8, "Conditional rules"). **Output the plan as a table and stop for my approval before you render.**
4. **Build the edit** to the approved plan, using the specs in sections 2–7 and 9.
5. **QC** against section 11, then **export** to section 12.

### Asset library: `D:\Editing assets`

All editing assets (fonts, overlays, transitions, SFX, music, LUTs, B-roll) live in **`D:\Editing assets`**. **Always look there first**, before generating or downloading anything.

1. **Scan the folder recursively first**, and list what you find (by sub-folder and file type) in your caption-plan output.
2. **Map each spec in this prompt to the closest asset found.** Expected sub-folders (use these if they exist; otherwise match by file name or type):

| Spec in this prompt | Look for in `D:\Editing assets\…` | Typical files |
|---|---|---|
| Fonts (Quicksand, Josefin/Raleway Thin, Bebas/Antonio Thin, Great Vibes/Allura) | `Fonts\` | .ttf / .otf. Install the missing ones before you build the text. |
| White flash, paper/dust texture, bokeh, film burn, light leaks, light-burst flare | `Overlays\`, `Light Leaks\`, `Transitions\`, `Bokeh\`, `Film Burns\` | .mov/.mp4 (screen or add blend), ProRes 4444 with alpha |
| Neon "?", halo, sparkles, watercolour blobs | `Elements\`, `Graphics\`, `Motion Graphics\`, `PNG\` | .mov with alpha, .png, .mogrt, CapCut templates |
| Teal/fog dissolve (re-tint to plum-lilac) | `Smoke\`, `Fog\`, `Overlays\` | .mov |
| SFX: whoosh, camera flash hit, neon buzz, ding/sparkle, pop/click, riser, boom, temple bell | `SFX\`, `Sound Effects\` | .wav / .mp3 |
| Music bed (piano + sitar/santoor/bansuri, emotional) | `Music\`, `BGM\` | .mp3 / .wav. Pick by mood; check that the licence is cleared for commercial use. |
| LUTs (film print emulation) | `LUTs\`, `LUT\` | .cube |
| B-roll (family, sad girl, kundli, puja, couple dancing) | `B-roll\`, `Stock\`, `Footage\` | .mp4 / .mov / .jpg |
| Templates and presets | `Presets\`, `Templates\`, `MOGRT\` | .prfpset, .mogrt, .drfx, CapCut templates |

3. **Re-colour every overlay** to the palette in section 2 (e.g. a teal fog overlay gets hue-shifted to plum-lilac; a cyan neon element gets re-tinted to rose).
4. **Only generate or download** what is missing, and **list each substitution** (e.g. "No neon '?' found; built in After Effects with a stroke + glow").
5. Save the project, renders and any generated assets to **`D:\Editing assets\Exports\[date]_consultation_reel\`** (create it if missing). **Never overwrite or move the original assets.**

### Hard rules
- **Never invent claims.** Every number, year count, client count, offer ("first chat free", "free consultation"), name, title and phone number on screen must come from the speech or from me. If it isn't said, use the fallback written in that row, or put `[PLACEHOLDER]` in the plan for me to fill. Never put an invented figure on screen.
- **Keep the voice continuous.** The conversation audio is the spine of the edit. B-roll always goes **over** the dialogue as a cutaway (J-cut/L-cut), and you never cut words out to make room for it. The only audio you remove is dead air (section 1.4).
- **Sync:** every caption word appears on the frame its first syllable starts, within ±2 frames.
- **Pacing:** a visual change (cut, punch-in, transition, text build or overlay) at least every **1.5–2 s**, and never a static frame longer than **3 s**.
- **Protect faces:** no graphic ever covers a face or mouth. Only the neon "?", the halo and the depth title go near a head, and they go **above or behind** it (rotoscoped), never on top.
- **Respectful tone:** this is a spiritual/advice consultation. Nothing mocking, no meme SFX, no comic zooms on the older woman. The style is emotional and premium.

---

## 1. About the footage (measured from the file)

### 1.1 File
- HEVC .mov, **1014×1804**, 30 fps, **36.2 s**, stereo AAC 44.1 kHz.
- The audio is **very loud and already compressed**: integrated loudness about **−8 LUFS**, with peaks near clipping. **Normalise it down** (section 10) before you add music.
- Upscale to **1080×1920**. This is a factor of about 1.065, so use a detail-preserving upscaler, or simply scale and sharpen lightly (unsharp mask, radius 0.6, amount 30%).

### 1.2 People and wardrobe
- **Speaker A, the client/questioner:** a young Indian woman, early 20s, with long straight dark hair, **black rectangular glasses** and a **beige-sage kurta with rani-pink floral block print**. She wears a beige satin scrunchie on her right wrist and a clip-on lav mic. She sits in a **dark walnut wooden chair**. Her energy is animated: she talks with her hands a lot.
- **Speaker B, the consultant/expert:** an older Indian woman wearing a **shiny lilac-purple Banarasi saree** with a **deep purple border**, the pallu over her head, a **red blouse with white dots**, sindoor and a red bindi, a **large gold kundan ring**, red and brown bangles and a rose-gold smartwatch. Her hands are clasped on a **cream faux-fur covered table**, with a **clear glass bowl** in front of her. Her energy is calm and authoritative.

### 1.3 Sets (two angles, same room)
- **Angle A** (on Speaker A): a **profile view** facing right, until the last block, where she turns to camera. Behind her are **white wall panels with thin black vertical stripes**, a **walnut-wood panel**, a **wall shelf with a white Shiva idol**, and a **gold-decorated puja shelf with Radha-Krishna idols and marigold garlands**.
- **Angle B** (on Speaker B): a **3/4 view** across the fur table. Behind her are **charcoal-grey and white striped curtains** and a window grille. The gold idols peek in at the left edge.
- The source is **phone footage**: flat, bright, high-key white walls, and nothing like the moody reference. You must regrade it heavily (section 2).

### 1.4 Shot blocks and speech (source time)

The clip is already cut as a back-and-forth. **Dead-air gaps** were found at −22 dB:

| Block | Source time | On camera | Speech | Gap after |
|---|---|---|---|---|
| **K1** | 0:00.00–0:04.40 | A, profile | 0:00.29–0:04.21 | 0.38 s |
| **K2** | 0:04.40–0:07.50 | B, **wider** framing | 0:04.60–0:07.16 | 0.47 s |
| **K3** | 0:07.50–0:09.23 | A, profile | 0:07.63–0:09.07 | 0.25 s |
| **K4** | 0:09.23–0:19.70 | B, 3/4 medium (the **longest block**: 10.5 s) | 0:09.32–0:13.20 · 0:13.43–0:14.92 · 0:15.40–0:19.51 | 0.23 s / 0.48 s / 0.29 s |
| **K5** | 0:19.70–0:23.83 | A, profile | 0:19.81–0:20.28 · 0:20.53–0:23.59 | 0.25 s / 0.23 s |
| **K6** | 0:23.83–0:29.60 | B, 3/4 medium | 0:23.81–0:26.11 · 0:26.52–0:29.20 | 0.41 s / 0.68 s |
| **K7** | 0:29.60–0:36.20 | A, **turned to face the camera**, medium shot, hands moving | 0:29.88–0:35.75 | end |

- **Tighten every gap longer than 0.25 s** down to about **0.12–0.18 s** with an invisible audio cut. Hide the picture jump under a punch-in or a B-roll cutaway. The finished cut will run about **34.5–35 s**. All timeline times in section 8 are in **edit time** for that tightened cut. Re-time them precisely from your transcript.
- **Natural edit beats:**
  - The 0.48 s gap inside K4 (at about 0:14.9) and the 0.41 s gap inside K6 (at about 0:26.1) are the best places for B-roll cutaways or transitions.
  - The 0.68 s gap before K7 is where the "happy ending" B-roll goes.

---

## 2. Colour scheme and grade (taken from this footage)

### 2.1 Palette

These tokens **replace** every teal, cyan and navy accent in the reference:

| Token | Hex | Where it comes from | Used for |
|---|---|---|---|
| Walnut-black | `#1A100C` | chair and wood panel shadows | bottom gradient, vignette tint, drop shadows |
| Deep plum | `#4B1D5E` | saree border | pill fill, CTA pill |
| Orchid | `#A24FC0` | saree | depth-title gradient (top), plum haze in transitions |
| Lilac sheen | `#E6D2F2` | saree highlights | depth-title gradient (bottom), soft haze |
| Rani rose | `#E2477F` | kurta print | callout-tag bar, tint pops, pink light leaks |
| Neon rose (for "?") | core `#FFE4F1`, tube `#FF6FB5`, outer glow `#D6338A` | kurta print, pushed to neon | neon question mark |
| Temple gold | `#E3B04F`, light `#F8DE9C` | idols and garlands | halo disc, pill hairline stroke, bokeh, film burns, sparkles |
| Sindoor red | `#C4122F` | blouse and bindi | emphasis only: **one** word in the whole video, the most dramatic hero word |
| Cream | `#EFE6D6` | fur table | cream flash |
| Caption white | `#FFFFFF`, and 90% white for small words | — | all captions |

### 2.2 A-roll grade (moody "puja-room at dusk")

The reference is dark and moody; this footage is bright and flat. Apply the following in order:

1. **Separate the subject from the background** with AI person segmentation (feather 6 px, refined around the hair and the saree pallu).
2. **Background:**
   - Exposure **−0.9 EV**, highlights −60, whites −40 (this tames the white striped panels).
   - Saturation −35%, **except gold/yellow hues**: keep the idols and marigolds at about −5%, so they glow like small warm points in a dark room.
   - Shadows tinted towards walnut `#2A1812`, midtones slightly warm.
   - Gaussian blur **5–7 px** for fake shallow depth of field. On Angle B the curtain stripes become soft charcoal columns. On Angle A the striped panels and puja shelf become a dark warm wall with glowing gold bokeh.
   - Optional: add 2–3 small, soft gold bokeh orbs (`#E3B04F`, 15% opacity, slow drift) over the puja-shelf area, to echo the reference's lamp-lit studio.
3. **Subject:**
   - Exposure −0.2 EV, contrast +12, warm skin (hue protect 15–35°).
   - Saturation −8% overall, but **protect the purple (saree) and pink (kurta)**: keep them rich, not neon.
   - Keep the gold ring and jewellery highlights.
4. **Global:**
   - **Vignette** 25–30%, tinted walnut-black.
   - **Film grain** 8%, fine.
   - Halation 10% on highlights (a warm bloom on gold and specular highlights).
5. **Bottom gradient** on every A-roll shot: walnut-black `#1A100C` linear, 0% opacity at 62% of frame height → **85% at the bottom**. Captions sit on it.
6. **Match the two angles:** Angle A is warmer and brighter, Angle B is cooler (grey curtains). Balance them so a cut between them doesn't jump. Bring both to the same warm-neutral midtone, with B's curtains pushed slightly plum.

### 2.2a Node-by-node grading pipeline (DaVinci Resolve order; mirror it in Premiere Lumetri or CapCut)

Grade **both speaker angles** through the same node tree. Then balance them shot by shot.

| Node | Name | Settings |
|---|---|---|
| 1 | **Input / CST** | iPhone HEVC footage is usually Rec.709 or HLG. If it's HLG (washed-out, flat highlights), convert with Color Space Transform HLG → Rec.709 Gamma 2.4, tone mapping "Saturation compression". If it's already 709, skip this node. |
| 2 | **Exposure / balance** | Neutralise white balance on the white wall panels (Angle A) and the white curtain stripes (Angle B), then warm both by +250 K. Offset −0.05. Set black point at about 3–4 IRE and highlights at about 90 IRE max (pull the bright walls down). |
| 3 | **Contrast curve** | A gentle S-curve. Lift the toe slightly (a matte black, about 4%), then roll off the highlights softly. Pivot 0.435, contrast 1.12. |
| 4 | **Subject key** | Magic Mask (Person), feathered 6 px. Inside: skin and costume nodes (5–7). Outside: background nodes (8–9). |
| 5 | **Skin tone** | Qualify skin (HSL, hue ~20–35°). Pull hues onto the **skin-tone vectorscope line**, sat −5%, warm midtones +3. Smooth any orange cast from the room lights. |
| 6 | **Costume protect** | Qualify the **purple/lilac saree** (hue ~280–300°): sat +6%, luminance −4% so the silk sheen doesn't clip. Qualify the **rani-pink print** (hue ~340°): sat +4%. Qualify the **red blouse** (hue ~0°): sat −8% to avoid chroma bleed. |
| 7 | **Face light (relight)** | A soft circular window on each face, tracked: +0.15 EV, a warm gain (R +0.02). This is the "key light" the phone shot lacks. Feather 70%. Add a second, very soft window for an **eye-light** lift on the eyes (+0.08 EV, sharpen +10). |
| 8 | **Background crush** | Outside the subject: exposure −0.9 EV, highlights −60, sat −35% except gold hues (see 2.2), walnut shadow tint `#2A1812`, blur 5–7 px. |
| 9 | **Gold glow** | Qualify yellow/gold (idols, marigolds, the ring): sat +10%, add Glow (threshold 0.75, spread 0.4, gain 0.3) for warm sparkle. |
| 10 | **Colour look** | Split-tone: shadows → plum `#2A1430` at 12%, highlights → warm gold `#F2D6A0` at 8%. Midtone "creamy" warmth, with Color Boost +8 for the purple saree. |
| 11 | **Film emulation** | Optional LUT from `D:\Editing assets\LUTs\` (e.g. a Kodak 2383-style print LUT) at **25–35% key output**. If there's no LUT, use node 10 alone. |
| 12 | **Halation + bloom** | Halation (red-orange) 10% on highlights; bloom 8%. |
| 13 | **Sharpen / texture** | Mid-detail +8 on the subject only (none on the skin, see 2.2b); global sharpen radius 0.45. |
| 14 | **Vignette + grain** | Walnut vignette 25–30%; film grain 35 mm fine, 8%. |

**Angle matching:**
- Use the **Angle B medium (K4)** as the hero grade, and match the K1/K3/K5/K7 Angle A shots to it with the scopes. Skin tones should land on the same vectorscope line, and midtone luminance should be within ±3 IRE.
- **K7** (A facing the camera) is lit more brightly from the front. Bring it down 0.15 EV so the CTA section doesn't jump.

**Shot-by-shot variation (for the "feel" of each section):**
- **Hook and problem (K1–K5):** slightly cooler and more desaturated (−5% sat, a hint of plum in the shadows). It feels heavy.
- **Solution (K6):** warmer, with +5% sat on golds and a slightly brighter face window. It feels hopeful.
- **CTA (K7):** the warmest and cleanest grade, with the background blur reduced to 4 px. It feels open and trusting.

### 2.2b Beauty retouch (natural, both speakers)

This is a light, "camera-ready" retouch, not a beauty filter. Faces must still look real and their age. Never slim, reshape or whiten anyone.

- **Skin smoothing:** frequency separation or Resolve "Face Refinement" (or Beauty Studio). Smooth texture by **25–30% for Speaker A** and **20–25% for Speaker B**, and **keep pore detail**. Apply it to skin only, through the skin mask from node 5. Eyes, brows, lips, hair and jewellery stay crisp.
- **Blemishes:** remove temporary blemishes and spots with a tracked patch or AI blemish removal. **Keep the bindi, the sindoor, moles and natural marks.**
- **Under-eyes:** soften dark circles by 30% (luminance lift in a small tracked window, feathered). No full removal.
- **Shine control:** reduce forehead and nose shine (highlight recovery on skin highlights −20%).
- **Eyes:** a brightening lift of +8% on the whites (not pure white) and +10% sharpness on the iris. On **Speaker A's glasses**, reduce lens glare/reflections where possible (highlight recovery inside a tracked lens mask).
- **Teeth:** reduce yellow sat by −15% only if visible and needed.
- **Hair:** remove stray flyaways that cross the face in the punch-ins, only where it's easy (clone/patch, tracked).
- **Jewellery and fabric:** add a slight specular sparkle to the gold ring and the saree zari border (Glow node 9). Remove distracting lint or fluff from the fur table in the K4/K6 punch-ins.
- **Cleanup:**
  - **Remove the lav mic and wire** from Speaker A's kurta in the K7 front-facing shot (AI object removal, or a tracked clone patch) if it's distracting.
  - Remove the **phone** visible in A's lap in K1 (bottom-left), and any distracting **switchboard** on the wall behind (Angle A, top-centre), using object removal or a clean background patch.
- **Stability:** apply a light **warp stabiliser** (smoothness 5%, "Position, Scale, Rotation") to any handheld micro-shake. If the clips are locked off, add a very gentle 1–2 px **handheld drift** to the punch-ins only, for life.
- **Denoise:** temporal NR (frames 2, threshold 6) before the grade, because the phone footage is noisy in the shadows once crushed.

### 2.3 B-roll grade
Warm amber/tungsten interiors (diya and lamp light, golden-hour windows). The contrast colour is **plum and rani-pink clothing**, replacing the reference's teal. The B-roll should look like a film still: shallow depth of field, fine grain, gentle halation. **Ken Burns on every still**: 100% → 108% over the shot, easeInOut, with an occasional slow sideways drift.

### 2.4 Framing and punch-ins
- For every A-roll segment longer than ~2.5 s, **alternate** the original frame (call it "wide") with a **punch-in** (1.35–1.6× crop). Cut on sentence breaks or on removed gaps, as a jump cut.
- On **Angle B**, the punch-in crops to her face and clasped hands. Keep the gold ring in frame when you can: it's a strong detail.
- On **Angle A (profile)**, the punch-in is a tight side-profile close-up (glasses and lips). This is the equivalent of the reference's side-profile close-up angle.
- **Every punch-in drifts.** Add a slow 100% → 104% push so nothing is ever static.
- Keep **head-room** in the top third, because the depth titles and the "?" need space above the head.

---

## 3. Typography system (the signature look)

### 3.1 Main caption: the "word stack"
- **One HERO keyword per phrase:** white, a rounded geometric sans with a **single-storey "a"**. Use **Quicksand Bold**; Comfortaa Bold or Lexend Medium are fallbacks. Size about **120–140 px** at 1080 wide, tracking −10.
- **Small companion words:** lowercase, same font (Quicksand Medium), **26–32 px**, white at 90%. The **lead-in words** sit **above-right** of the hero word and the **trailing words** sit **below-left**, tucked tight so they slightly overlap the hero word's bounding box.
- **Position:** centred horizontally, hero baseline at about **72% of frame height**, on the bottom gradient.
- **Shadow:** soft black drop shadow (40%, blur 12, distance 0).
- **Speaker colour cue** (new, for the two-person format): Speaker A's stacks use pure white. **Speaker B's hero words get a very subtle lilac-to-white vertical gradient** (`#E6D2F2` → `#FFFFFF`). The difference is barely noticeable, but it tells the viewer who's talking.
- **In-animation** (synced word by word):
  - Small words: Gaussian blur 25 → 0, opacity 0 → 100, rise 8 px, 6 frames, easeOut.
  - Hero word: the same, plus scale **112% → 100%** over 8 frames (easeOutBack, overshoot 1.2).
  - Words build up in the order they're spoken, and the finished stack holds until the phrase ends.
- **Out-animation:** the whole stack blurs out (blur 0 → 20, opacity 100 → 0) over 4 frames, then the next stack builds. Stacks never overlap.
- **Choosing the hero word:** for each phrase, pick the most emotional or most concrete word: the problem, the feeling, the cause, the remedy, a number or a deity/ritual name. Avoid fillers (hai, toh, na, ki, ke). Aim for **3–6 words per stack**. If a sentence is long, split it into 2–3 stacks.
- **Spelling:** casual Roman Hinglish, like the reference ("kyu", "apko", "rha", "smjh", "hee..."). Keep a "??" or "..." at the end of a phrase when the speech is a question or trails off.
- **One sindoor-red word:** in the whole video, exactly one hero word (the single most dramatic word of the problem, e.g. the problem's name) is filled with **sindoor red** `#C4122F` and has a soft white outer glow.

### 3.2 Depth "behind subject" title (used 1–2 times)
- A big, thin, tall sans word: **Josefin Sans Thin** or **Raleway Thin**, all lowercase or Title Case, about **300 px** tall.
- Fill: **orchid → lilac** vertical gradient (`#A24FC0` → `#E6D2F2`) at 85% opacity, with a faint gold `#E3B04F` 1 px inner hairline.
- Place it in the **upper half**, partly **masked behind the speaker's head and shoulders** (rotoscope the subject, with the subject layer above the title).
- It **wipes in from the left** (mask wipe, 10 frames). Its small white companion words then blur-fade in around it.
- This is the equivalent of the reference's "Kya" (with "relationship" and "bachega ja nhi").

### 3.3 Stat title (authority beat; only if a number is said)
- An ultra-condensed thin font (**Bebas Neue Thin** or **Antonio Thin**) in white, about **330 px** tall, at the **top of the frame**, behind the subject's head (masked).
- It reveals with a **left → right mask wipe** over 10 frames, letter by letter.
- A small **script word** in **Great Vibes** or **Allura**, in temple gold `#F8DE9C`, sits above it, centred.
- It's the equivalent of "Pishle / 10 SAAL". **Use only a number that is actually said** (years, families, kundlis, clients). If none is said, skip this treatment and use the fallback in section 8.

### 3.4 Pill label
- White sans text (Quicksand SemiBold, 44 px) on a **solid deep plum** rounded rectangle (`#4B1D5E`, corner radius 8, padding 10 × 22 px) with a **1 px temple-gold hairline stroke**.
- It reveals with a **left → right mask wipe** in 8 frames, plus a white 30° light sweep across it.
- A **gold script word** (Great Vibes) fades in just above it.
- A small version (28 px) sits under the CTA.

### 3.5 Glowing callout tags (the remedy/solution beat)
- White text (Quicksand SemiBold, 40 px) on a bright **rani-rose bar** (`#E2477F`). The bar fades to transparent at its right end and has a soft outer glow (`#FF6FB5`, radius 18).
- Each tag slides in from the left with motion blur (8 frames, easeOut), connected by a **thin white leader line** with a small dot to a point in the scene: on Angle B, her clasped hands or her ring.
- **Two or three tags** stack, each 6 frames after the one before.
- Use the real nouns she says, e.g. **"Upay"**, **"Puja"**, **"Guidance"**, **"Remedies"**, **"Kundli analysis"**.

### 3.6 CTA text
- The CTA phrase she actually says (or the fallback **"Click the link Below"**), inside curly quotes “ ”, in the same rounded sans at about **80 px**, at the lower third. It builds word by word with the blur-fade.

### 3.7 Speaker name tag (optional; only if a name or title is said, or I supply one)
- On B's **first** appearance, a small pill (section 3.4 style, 30 px) at the **upper-left safe zone**, holding 2.5 s, with the script-gold title above it, e.g. *"Astrologer"* over the pill "[Name]". If no name is known, **omit it**. Don't write "Expert" or "Guru Maa" unless it was said.

---

## 4. Motion-graphic elements (re-coloured)

- **Neon question mark:**
  - An outline-only "?" drawn as a **rose neon tube** (core `#FFE4F1`, tube `#FF6FB5`, outer glow `#D6338A`, radius ~40).
  - It **pops in above the subject's head**: scale 0 → 120 → 100% with overshoot over 10 frames, plus a **2-flicker neon turn-on** and a buzz SFX.
  - It floats/bobs ±10 px on a 1.5 s sine and stays up for about **6–7 s**, **across the cut** from the opening B-roll into Speaker A's A-roll. On the profile shot it sits above and slightly in front of her face.
- **Side cut-outs (only if the problem is relational: couple, in-laws, family fights):**
  - **Black-and-white** cut-outs of the people in conflict. Couple topic: a woman with arms crossed and a man pointing. In-law/family topic: an older woman scolding and a young woman looking away.
  - They sit at the frame edges behind Speaker A at about 70% height and **slide in** from off-screen left and right (12 frames, easeOut) with a soft shadow.
  - Because A is in profile facing right, put the larger cut-out on the **left** (behind her back) and the smaller one at the far right edge.
- **Watercolour memory bubble:**
  - Above the sad B-roll character's head, **ink/watercolour blobs** pop in one after another: 5–6 irregular **lilac-grey** splotches (`#B9A5C4`), 3 frames apart.
  - Together they form a cloud-shaped mask that reveals a **happy memory** inside: a happy couple or family selfie, matching the topic.
  - It holds about 2 s, then the blobs bleed and dissolve outward.
- **Halo glow:**
  - A **pale temple-gold glowing disc** (`#FCEBC2` centre → `#E3B04F` ring, with bloom) grows from 0 to full size behind the head over 15 frames (rotoscope so it sits behind), then holds and pulses very slightly.
  - Use it **once on B-roll** (the despair shot) and **optionally once behind Speaker B** at her key "solution" line, as a subtle divine-light cue. At 50% opacity it should look like a halo, not a cartoon.
- **Wall light leak:** on the B-roll wall behind the character, an **orange-gold, diya-like flickering light leak** fades in and flickers organically (screen blend, 60%).
- **Gold dust sparkles (new, light touch):** a few tiny gold particles drift upward when the remedy tags appear, and when the stat title lands. Keep it to under 15 particles, 1.2 s.

---

## 5. Transitions (use these; they repeat)

| Name | Spec | Use |
|---|---|---|
| **White flash + paper texture** (main) | Cut to pure white with a few grey dust specks for 3–6 frames, then fade into the next shot. It often fades out through a **plum-lilac fog** dissolve (6–8 frames of `#A24FC0` → `#E6D2F2` haze clearing). | B-roll ↔ A-roll |
| **Bokeh flood** | **Gold-white bokeh** circles flood in over 4 frames, flash white, then reveal the next shot. | Before a key line or the CTA |
| **Cream flash** | 1–2 frames of solid `#EFE6D6` | B-roll → A-roll |
| **Rose tint pop** | 2–3 frames of rani-rose overlay (`#E2477F`, 55%, Overlay blend) on the first frames of a new A-roll shot, or on a beat | Replaces the reference's purple pop |
| **Film burn / light leak** | An orange-gold or pink-magenta light leak sweeps across and burns to near-white, then reveals the next shot | Into the happy ending |
| **Zoom-blur whip** | An extreme radial zoom blur into a texture (the **saree silk** or the **fur table** is perfect), 4 frames. The next shot then starts tight and zooms out fast (180% → 100%, ~20 frames, easeOut). | A → B speaker switches mid-energy |
| **Light-burst flare** | A white-gold bloom flare grows from the bottom-right, over-exposes to white, then cuts | Into the authority/stat section |
| **Hard cut** | — | Most A ↔ B speaker switches, and punch-ins |

Most **A ↔ B conversation cuts stay hard cuts**: back-and-forth dialogue reads best that way. Use a **zoom-blur whip** or a **rose tint pop** on at most 2 of the A ↔ B switches to add energy.

---

## 6. B-roll plan and generation prompts

Generate these as **photoreal 9:16 stills** (then Ken Burns them) or **3 s video clips**. The look is cinematic, warm tungsten light, shallow depth of field and a 35 mm film look. Wardrobe colours are **plum, lilac and rani pink** (not teal) so they match the A-roll. For continuity, the **B-roll "client" character should resemble Speaker A**: a young Indian woman with long straight dark hair, black rectangular glasses, and a pink floral kurta. The **consultant character should resemble Speaker B**: an older Indian woman in a purple Banarasi saree with the pallu over her head, and a red blouse.

Pick the version that matches the topic you transcribed. The "couple" versions are the default for relationships, and the alternatives are given in brackets.

- **BR1 (hook):** "An Indian family in a cosy apartment living room at dusk. A father in a checked shirt, a mother in a beige saree, and a younger brother lean over the back of a dark plum sofa, all looking with concern at a young woman with long straight hair and black glasses, in a pink floral kurta, who sits crying with her hands clasped. Framed family photos and a small brass diya on the shelf, warm lamp light, cinematic, photoreal." Camera: drift right and down, from the parents to the girl.
- **BR2 (memory):** "The same young woman in the pink floral kurta and glasses sits cross-legged on a bed, chin on hand, looking sadly out of a window with sheer curtains. Warm bedside lamp, an open diary and a cup of chai on the bed, golden-hour light, photoreal." Plus a **memory-bubble image**: "A happy young Indian couple taking a selfie, smiling, bright daylight" [family topic: "a happy Indian family laughing together at a dining table"; career topic: "the same young woman smiling in an office holding an offer letter"].
- **BR3 (despair):** "The same young woman sits on her bed hugging her knees, head bowed, open books and a framed photo around her. Symmetrical composition, warm moody light, a soft glow behind her." (The gold halo grows behind her head here.)
- **BR4 (insert):** "Close-up of an older woman's hand with a large gold kundan ring and red bangles, writing with a pen on a hand-drawn Vedic kundli chart on a wooden table. A brass diya and a small Shiva idol nearby, warm lamp light, shallow depth of field."
- **BR5 (consultation):** "An older Indian woman in a lilac-purple Banarasi saree with the pallu over her head and a red blouse sits at a wooden table across from a young woman with glasses in a pink floral kurta, explaining calmly with an open-palm gesture. A cream table cover, a brass diya, marigold garlands and gold Radha-Krishna idols on a shelf behind them, warm moody cinematic light." Slow push-in.
- **BR6 (puja/remedy, optional):** "Close-up of hands lighting a brass diya in front of gold Radha-Krishna idols with marigold garlands, smoke from agarbatti, warm golden glow, shallow depth of field." (3 s video if possible.)
- **BR7 (happy ending, video 3 s):** "Night, a happy young Indian couple dancing on a garden path under warm glowing string lights and street lamps. He twirls her and her rani-pink lehenga swirls. Bokeh, golden light, handheld, slow motion." [Family topic: "a happy Indian family celebrating Diwali with sparklers and diyas, laughing"; career/marriage-delay topic: "a smiling bride in a pink-and-gold lehenga at her haldi/mehendi, petals falling".]
- **Side cut-outs:** "Black-and-white cut-out photos on a transparent background: a young Indian woman with arms crossed looking annoyed, and a young Indian man in a white t-shirt pointing angrily." [Family variant: "an older Indian woman in a saree scolding, pointing" + "a young woman looking away, hurt".]

---

## 7. Graphics density targets (for a ~35 s edit)

| Element | Count |
|---|---|
| Word stacks | 14–18 |
| Neon "?" | 1 (the opening, carried across the cut) |
| Depth title | 1 (2 at most) |
| Stat title | 1 if a number is said; otherwise 0 |
| Pills | 1–2 (stat/offer and CTA) |
| Callout tags | 1 set (2–3 tags) |
| B-roll cutaways | 5–6, each **1.2–2.5 s** (the clip is short, so cutaways are brief) |
| White/bokeh/burn transitions | 5–7 |
| Halo | 1–2 |

---

## 8. Shot-by-shot timeline (edit time, about 35 s; re-time to your tightened cut)

The arc is **hook → problem → why it happens → solution/authority → happy ending → CTA**, mapped onto the conversation blocks K1–K7.

| Edit time | Picture | Audio | Graphics / text | Transition out |
|---|---|---|---|---|
| **0:00–0:01.8** | **BR1**, worried family over the crying girl (drift right and down) | K1 speech starts (A's voice under the B-roll) | 0:00.5: **neon rose "?"** pops in above the crying girl's head, with buzz and flicker. **First word stack starts here**, from A's first words. | **Cream flash** (2 f) |
| **0:01.8–0:04.1** | **K1 A-roll**, A in profile (rose tint pop on the first 3 f). A punch-in to profile close-up at the sentence break. | K1 continues | The neon "?" **carries over** above A's head and keeps bobbing until ~0:06. **Side cut-outs** slide in (if relational). Two word stacks from K1 (e.g. the problem phrase; hero = the problem word). | **Hard cut** |
| **0:04.1–0:06.6** | **K2 A-roll**, B wide → punch-in on her face at mid-sentence | K2 | One or two stacks from B's reply. The "?" fades out (blur 0 → 15, 8 f) as B starts answering. **Name tag** if a name or title is known. | **White flash → plum fog** |
| **0:06.6–0:08.0** | **BR2**, girl by the window | K3 (A's voice) | The **watercolour memory bubble** reveals the happy-memory image. A's K3 words as one stack. | **Hard cut** back to A |
| **0:08.0–0:08.4** | **K3 tail A-roll**, A profile close-up | K3 ends | Stack completes | **Zoom-blur whip** (into the saree silk) |
| **0:08.4–0:12.2** | **K4 part 1**, B 3/4 medium (zoom-out 180 → 100%) | K4 sentence 1 | **Depth title** behind B's head: the key word of her diagnosis (the *cause*, e.g. "dosh", "grah", "karma", "vastu"; use her actual word), with small words around it. Then 1–2 stacks. | **Hard cut** (jump) |
| **0:12.2–0:13.6** | **K4 part 2**, B punch-in (face + ring) | K4 sentence 2 | 1 stack (hero = the strongest word) | **White flash** |
| **0:13.6–0:15.3** | **BR3**, girl hugging her knees, push-in | K4 sentence 3 begins (B's voice) | At 0:14.0 the **gold halo** grows behind her head | **White flash → plum fog** |
| **0:15.3–0:17.6** | **K4 part 3**, B wide, then punch-in at the break | K4 sentence 3 continues | 1–2 stacks. **The sindoor-red hero word goes here** if this is the emotional peak of the problem. | **Hard cut** |
| **0:17.6–0:18.3** | **K5 A-roll**, A profile (a short reaction or question) | K5 phrase 1 | 1 stack | **Hard cut** |
| **0:18.3–0:21.3** | **K5 A-roll**, A profile close-up → **BR4 insert** (ring hand writing a kundli, 1.0 s) at the midpoint | K5 phrase 2 | 1–2 stacks. No text during the BR4 insert. | **Rose tint pop** into B |
| **0:21.3–0:23.4** | **K6 part 1**, B 3/4 medium, with a slow push | K6 sentence 1 (the solution starts) | 1 stack. The **halo behind B** (50%, subtle) as she gives the solution. | **Light-burst flare → white** |
| **0:23.4–0:26.0** | **BR5**, consultation scene, push-in (or **BR6** puja close-up for the first 1 s, then BR5) | K6 sentence 2 (B's voice) | At ~0:24: **callout tags** slide in with leader lines to the consultant's hands (the remedy nouns B says, e.g. "Upay", "Puja", "Guidance"), with gold sparkles | **White flash** |
| **0:26.0–0:28.4** | **K6 end**, B punch-in | K6 ends | **Authority beat:** if B or A says a number, the **stat title** (e.g. "25 SAAL" with the gold script word "Pishle") goes behind her head, plus the **pill** ("[N]+ families/kundlis") with the gold script word above it. **Fallback if no number is said:** a depth title of B's most confident word (e.g. "Bharosa", "Samadhan"). | **Film burn** (orange-gold → pink) |
| **0:28.4–0:30.0** | **BR7**, happy ending (dance / Diwali / bride) | Start of K7 (A's voice, now facing the camera) | None. Let it breathe; the music swells and resolves. | **Bokeh flood → white** |
| **0:30.0–0:32.5** | **K7 A-roll**, A **facing the camera**, medium → punch-in at the break | K7 middle | 1–2 stacks (hero = the result or feeling word, e.g. "Sukoon", "Shaadi", "Khush") | **Hard cut** on a word |
| **0:32.5–0:35.0** | **K7 A-roll**, A punch-in medium close-up | K7 end (the CTA) | The **CTA** builds word by word (her real words, or the fallback “Click the link Below”). Then the **small plum pill** under it, with her actual offer, or `[PLACEHOLDER: offer text]`. Hold the last 0.5 s. | End (a 6-frame fade to walnut-black) |

### Conditional rules
- **Who speaks the hook:** if K1 is a question ("…kyu ho rha hai?"), keep the neon "?" exactly as above. If K1 is a statement, keep the "?" but make the hero word the problem noun.
- **Side cut-outs** only for relationship or family conflict. For other topics (career, health, money), replace them with **two B&W cut-out props** that fit the topic (e.g. a rejected file stamp and a calendar) or skip them.
- **Stat title and pill** only with a spoken number. Never invent one.
- **If K7 isn't a CTA** (e.g. it's a testimonial: "mujhe bahut fayda hua"), make K7's hero words the **result**, and put the CTA only as the small pill “[PLACEHOLDER: CTA]” for me to fill.
- If your tightened cut runs longer or shorter than 35 s, **scale the rows proportionally**, but keep each B-roll cutaway at 1.2–2.5 s, and never cut B-roll mid-word on a stack hero.

---

## 9. Layering order (top → bottom)

1. Transitions and flashes
2. Callout tags, CTA, pills, word stacks
3. The **subject cut-out (roto)**, for depth titles, stat title, halo and the "?" when it sits behind the head
4. Depth title, stat title, halo disc
5. The A-roll/B-roll plate (graded)
6. Side cut-outs (between the plate's background and the subject: use the segmentation so they sit **behind** Speaker A)
7. Global grain, vignette, halation (adjustment layers on top of everything except the text, so text stays crisp)

---

## 10. Sound design

- **Dialogue:**
  - Normalise the source from −8 LUFS down to about **−16 LUFS** integrated, with a true-peak limiter at −1.5 dBTP.
  - Light denoise (room tone), a de-esser, and a gentle compressor (2:1). Even out the two speakers so A and B sit at the same loudness.
  - Add a 10 ms crossfade on every gap-removal cut so nothing clicks.
- **Music:** a soft, emotional **piano + light sitar/santoor or bansuri** ambient bed (devotional-cinematic, not loud bhajan), at about **−24 dB under speech**, ducked by 6 dB while anyone speaks.
  - It **swells** slightly through the remedy and authority section (0:21–0:28).
  - It **resolves warmly** on the happy-ending B-roll (0:28.4–0:30).
  - It thins out under the CTA.
- **SFX:**
  - A soft **whoosh** on every transition.
  - A **camera-flash/shutter "hit"** on every white flash.
  - A **neon buzz + sparkle ding** when the "?" pops.
  - Soft **pops/clicks** for each pill and callout tag.
  - A **temple-bell tink** (very soft) when the halo appears.
  - A **riser** into the light-burst flare (~0:22.8), and a **soft boom** when the stat title lands.
  - A gentle **tick** on each hero word, at −30 dB, barely audible.
  - No comedic or meme sounds.

---

## 11. QC checklist (do this before export)

- [ ] Every caption word is synced within ±2 frames, and every Hinglish spelling is consistent across the video.
- [ ] No graphic covers a face or mouth. The "?", halo and titles sit above or behind heads.
- [ ] No invented numbers, names or offers on screen; any `[PLACEHOLDER]` is flagged to me.
- [ ] The A and B angles match in colour; there are no bright white panels left, and the background reads dark and warm.
- [ ] Skin looks natural: texture is visible and nothing is plastic. The bindi, sindoor and moles are intact. No reshaping or whitening.
- [ ] Skin tones sit on the vectorscope skin line in every shot, and the saree purple isn't clipping.
- [ ] The mic, phone and distracting wall details are removed where specified, with no visible patch artefacts across frames.
- [ ] Every asset used is listed with its path in `D:\Editing assets`, and every substitute or generated asset is flagged.
- [ ] A visual change at least every 2 s, and no static frame longer than 3 s.
- [ ] The dialogue is continuous, with no clipped words at the gap-removal cuts.
- [ ] Exactly one sindoor-red word in the whole video.
- [ ] All text is inside the safe zone: **150 px from the top, 300 px from the bottom, 60 px from the sides**. The CTA and the bottom-most stack sit above the 300 px bottom margin, so the platform UI doesn't cover them.
- [ ] Loudness is −14 to −16 LUFS integrated, true peak ≤ −1 dBTP, and the music never masks speech.

---

## 12. Export

- **H.264 MP4, 1080×1920, 30 fps**, VBR 12–16 Mbps (high profile), **AAC 320 kbps** 48 kHz stereo, Rec.709, faststart enabled.
- Also export a **burned-in thumbnail frame**: the best depth-title frame or the stat frame as a PNG.
- Also deliver the **caption plan table** and the **transcript (SRT, Roman Hinglish)**.
