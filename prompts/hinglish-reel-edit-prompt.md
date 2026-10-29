# Edit Prompt: Hinglish Talking-Head Reel → "Problem → Expert Solution" Cinematic Edit

> **How to use:** attach your raw video (`.mov`, 38 s) to a new chat with Claude and paste everything below the line. The prompt is self-contained.

---

## ROLE & GOAL

You are a senior short-form video editor and motion designer who specialises in Indian Instagram Reels (Hinglish, emotional "problem → expert solution → happy ending → CTA" format). I am attaching my raw talking-head video. Turn it into a finished, upload-ready 9:16 Reel. Copy the **editing language** of the reference style described below **exactly**:

- the two alternating visual worlds
- keyword kinetic captions with a hero word and tiny helper words
- pill emphasis cards
- bokeh + white-flash transitions
- neon icon overlays
- the thought bubble
- the halo glow
- the text-behind-subject credibility card
- the sound design

**Re-skin all colours to my video's palette (Section 3).** Do not just add subtitles. This must look like a premium, motion-graphics-heavy edit.

Work in this order and show me your output at each checkpoint marked ✅:

1. **Analyse the footage.** Probe the file, extract frames, transcribe the audio with word-level timestamps, and find the jump cut(s).
2. ✅ **Beat map.** Split my script into story beats (Section 5).
3. ✅ **Caption plan.** Write a word-by-word table of the hero word, helper words, and the in/out frame for each (Section 6).
4. ✅ **B-roll / overlay plan.** For each beat, list the insert, its image prompt, its motion, and its overlay (Sections 7–8).
5. **Build and render** with whatever tools you have. Preferred order:
   1. Remotion (React) or HTML/Canvas frames, plus ffmpeg for compositing
   2. Pure ffmpeg filtergraphs
   3. If you cannot render, a frame-accurate EDL plus layer-by-layer CapCut/Premiere instructions so a human can rebuild it 1:1
6. ✅ **QC pass** against the checklist in Section 12, then deliver the final MP4.

If a tool is missing (no image generator, no speech-to-text model), say so, use the best fallback, and keep going. Don't stop to ask unless it's truly blocking.

---

## 1. SOURCE FOOTAGE: WHAT YOU ARE WORKING WITH

| Property | Value |
|---|---|
| File | `.mov`, HEVC, 720×1280, 30 fps, stereo AAC 44.1 kHz |
| Duration | ≈ 38.0 s |
| Shots | **One continuous locked-off take** with a single jump cut at ≈ 34.0 s (verify it) |
| Speaker | A young Indian woman (early-to-mid 20s, the presenter/"expert"), seated on a beige-taupe crushed-velvet sofa. She talks straight to camera with constant expressive hand gestures. She has long straight black hair worn loose over her shoulders and wears a **sage-green cotton kurta with a coral-pink floral block print**, a beige fabric scrunchie on her right wrist, a thin gold bangle on her left wrist, small stud earrings, and a **black DJI-style wireless lav mic clipped at her chest**. |
| Background | Cream / off-white horizontal wood-grain panelling. A **Radha-Krishna painting** (lotus, peacock tones, gold) sits in the top-right corner. On the left edge is a **dark walnut wood panel with a gold paisley/leaf motif**, plus a dark-brown vertical pillar. The sofa back and cushions run along the bottom third. |
| Light | Soft, even, frontal daylight. Neutral-warm white balance, slightly flat and low contrast (phone footage). |
| Audio | Hinglish speech, integrated loudness ≈ **−24.5 LUFS** (too quiet), LRA ≈ 5.4 LU, light room tone, no music |
| Framing | Medium-wide: head at about 35–48% of frame height, knees at the bottom. Lots of headroom with the painting above her. |

**Important differences from the reference** (adapt to these, don't fight them):

- **There is only ONE camera angle.** The reference cuts between a wide shot and a tight 3/4 profile. You must **fake the second angle with digital punch-ins** (Section 9).
- **The source is 720p.** Upscale to 1080×1920 with a high-quality scaler (Lanczos, or an AI upscaler if available). Keep punch-ins at **≤ 1.45×** of the source so softness stays acceptable, and add a mild unsharp mask after scaling.
- **The presenter is female and is the expert.** The "story world" B-roll character is a **different** person (the troubled client). Never make them look like the same woman.
- **The reference runs 63 s and this video runs 38 s.** Compress the structure: about **5–6 B-roll inserts** and about **7–9 flash transitions** in total. Keep the final reel within 36–40 s. Don't pad it.
- **Output frame rate:** conform to **30 fps**, the native rate, to avoid judder on the talking head. Every "frames" duration in this prompt assumes 30 fps.

---

## 2. THE STYLE TO REPLICATE (summary of the reference edit)

The reference is a 9:16 Instagram Reel in a cinematic **"emotional problem → expert solution → happy ending → CTA"** format, with a Hinglish voiceover from a relationship consultant.

**Two visual worlds alternate:**

1. **STORY world.** Photoreal, AI-generated cinematic stills of a sad young Indian woman in warm, golden-hour Indian homes (a living room with family, a bedroom with a diary and chai, the floor with window-blind shadows, a bed with a halo). Each still gets a slow Ken Burns push or pan **plus exactly one animated overlay effect**. The ending is a real-motion clip of a happy couple dancing in a night garden lit by lamp posts.
2. **EXPERT world.** The presenter talking, alternating between a wide shot and a tight close-up. There is a heavy dark gradient over the bottom 35% of the frame for captions.

**Signature devices (all must appear in your edit, re-coloured):**

- **Cut on every sentence** and alternate wide ↔ close.
- **Bokeh + white-flash transition** on every world switch (≈ 0.4 s), with a whoosh and shimmer SFX.
- **Keyword kinetic captions**, not subtitles. Show one large hero word in a clean geometric sans with tiny lowercase helper words tucked above-right and below-left. Each word pops in exactly when it is spoken (blur → sharp, 105% → 100%). The hero word is replaced, never stacked.
- **Gradient hero word** used once, for the key question (the reference uses "Kya" in a blue gradient).
- **Letter-by-letter reveal** on one word, for example "problem".
- **Rounded pill cards** with typewriter reveals for key offers ("Remedies", "Guidance", "More than 3000", "first whatsapp chat is free"). They slide in from the left and stack.
- **Neon outline "?"** above a confused person's head (flicker-on, then a gentle pulse) and above the presenter.
- **Desaturated B&W cut-out PNG** of an arguing couple composited behind the presenter's shoulders.
- **Cloud thought bubble** with a torn-paper/white-stroke edge, holding a happy-memory photo, popping in with a bounce.
- **Floating 3D glass-cube particle** drifting through one story still.
- **Golden light-leak / film-burn sweep** ending in a golden white-out.
- **Glowing circular halo orb** behind a sad character's head, pulsing.
- **Credibility card with text behind the subject:**
  - a small script word above a huge, thin, ultra-condensed number ("10 SAAL") **masked behind the presenter's head**
  - a script word plus a pill ("More than 3000") at the bottom
- **CTA:** a tighter framing, `"Click the link Below"` in quotes, and a pill with `first whatsapp chat is free`. Hard cut at the end with no outro card.
- **Music:** a soft, emotional ambient piano and pad at 70–80 BPM, low under the voice. It lifts on the happy ending and resolves on the CTA.

---

## 3. COLOUR RE-SKIN: MY VIDEO'S PALETTE (use these instead of the reference's teal/cyan/navy)

My frame is built on **sage green + coral-rose (the kurta), cream (the wall), walnut brown (the wood panel and pillar) and antique gold (the paisley motif and painting).** Derive every graphic from these:

| Role | Reference used | **Use instead** | Hex |
|---|---|---|---|
| Primary accent (pills, glows, emphasis) | Teal `#1FA58A` | **Coral-rose**, sampled from the kurta flowers | `#E2566C` (pill fill), `#F27A8C` (glow) |
| Secondary accent (second pill, bokeh mix) | Teal-green bokeh | **Sage green**, sampled from the kurta base | `#A9B596`, deep sage `#6F7D5E` |
| Neon icon colour ("?", outlines) | Electric cyan `#3FB8FF` | **Warm rose-gold neon**: core `#FFE3E8`, glow `#FF6F8E` | — |
| Gradient hero word | Blue `#6FA8DC → #1C3D6E` | **Rose → walnut**: `#F4A3B0 → #8E2F45`, or gold `#E9C77B → #9C6B22` | — |
| Highlight / sparkle / film burn | Golden orange | **Antique gold** from the wall motif | `#C9A24A`, light `#F1D58C` |
| Caption gradient (bottom 35%) | Black 0 → 85% | **Walnut-black** `#1E1412`, 0 → 80% | `#1E1412` |
| Text | White | **Warm white** | `#FFF8F0` |
| Text shadow | Dark drop shadow | Walnut shadow `#1E1412` at 60%, blur 12 px, offset y +3 px | — |
| Transition flash | Pure white | **Warm cream white** | `#FFF6EC` |
| Bokeh circles | Teal-green | Mix of **rose `#F27A8C`, sage `#B9C6A4`, gold `#F1D58C`**, 30–120 px, soft edges, 40–70% opacity | — |

**Grade (replaces teal-and-orange):** "warm rose-and-sage".

- **EXPERT shots:**
  - Lift contrast slightly (S-curve, blacks down about 4%).
  - Keep skin natural-warm.
  - Push the cream wall a touch warmer and creamier (not yellow).
  - Pull a hint of sage into the shadows and keep saturation of the kurta greens and corals at +5–10%.
  - Add a soft vignette (about 15%) so the eye stays on her face.
  - Don't crush the white wall. It should stay creamy at about 85–90 IRE.
- **STORY stills:** a warm golden-hour amber grade. Sage-green and dusty-rose clothing and props echo the palette so the two worlds feel related.
- **Happy ending:** warm gold lamp light with rose and sage bokeh.

---

## 4. TYPOGRAPHY (keep the reference fonts, recolour only)

| Use | Font | Size on 1080×1920 | Notes |
|---|---|---|---|
| Hero word | **Poppins Medium** (fallbacks: Glacial Indifference, Quicksand Medium) | 100–115 px; long words (e.g. "Relationship") auto-fit to ≤ 820 px wide | Warm white with a walnut shadow. Tracking −1%. |
| Helper words | **Poppins Light**, lowercase | 26–30 px | Above-right and/or below-left of the hero word, 8–12 px gap |
| Gradient hero word (once) | Poppins Light | 120–140 px | Rose → walnut gradient fill (see palette) |
| Big credibility number | **Bebas Neue** (thin/light cut) or **Antonio Thin** | Cap height about 320–380 px, horizontally condensed | Warm white at 95%, masked behind her head |
| Script accent words | **Great Vibes** (or Playfair Display Italic) | 60–80 px | Warm white or light gold `#F1D58C` |
| Pill text | Poppins Medium | 40–46 px | Warm white on a coral-rose pill |
| CTA quote | Poppins Medium | 64–72 px | Include the quotation marks |

**Caption safe zone:** the caption block's vertical centre sits at **y ≈ 1380–1480 px** (lower-middle third), centred horizontally. Keep everything inside **x 90–990 px**. Nothing below **y = 1620**, because Instagram's UI covers it. Nothing in the top 220 px, except the credibility number. In my framing this area falls over her lap and hands, which is exactly why the walnut gradient is needed.

---

## 5. STEP 1: TRANSCRIBE & BEAT-MAP (do this before any design)

1. Transcribe the audio with **word-level timestamps** (Whisper / faster-whisper, language hint `hi`). Write the output in **Hinglish Roman script**, the way Indians type on WhatsApp. For example: "aapka partner badal kyu gaya", not Devanagari and not an English translation. Fix obvious mis-hearings by context.
2. Find dead air, breaths, "umm"s and the jump cut. **Tighten the A-roll:** remove pauses longer than 0.25 s and filler words, but keep the natural rhythm. Don't make it robotic. Recompute every timestamp after tightening.
3. Map the tightened script onto these **beats**. Not every beat has to exist. Use whatever the script naturally contains, but keep this order of emotional energy:

| Beat | Purpose | Typical share of 38 s |
|---|---|---|
| **B1 Hook** | A relatable pain question ("aapka partner badal gaya?", "relationship mein distance?") | 0–5 s |
| **B2 Problem deepening** | Symptoms such as fights, distance, a third person, no reason, no solution | 5–15 s |
| **B3 Emotional low** | The viewer feels seen ("kya relationship bachega?", "sab theek kab hoga?") | 15–20 s |
| **B4 Diagnosis / authority** | "Dekhiye, problem tab hoti hai jab…" | 20–25 s |
| **B5 Method / solution** | What she does: understands the problem, finds the reason, gives remedies and guidance | 25–30 s |
| **B6 Credibility** | Years of experience, number of clients or couples helped. **Only use numbers she actually says.** If she says none, skip the numeric card and use a script + pill card with a real claim from the script instead. Never invent statistics. | 30–33 s |
| **B7 Happy ending** | A short emotional payoff (B-roll only, about 2 s), placed right before the CTA | ≈ 33–35 s |
| **B8 CTA** | "Link below / DM / WhatsApp", spoken by her, covering the jump cut | last 3–5 s |

✅ **Show me:** the full Hinglish transcript with timestamps, the tightened transcript, and the beat table with in/out times.

---

## 6. STEP 2: KINETIC CAPTION SYSTEM (the most important layer)

**Rules (copy the reference behaviour precisely):**

1. **Keywords, not subtitles.** For each phrase of 2–6 words, pick **one HERO word**: the emotional or semantic keyword (a noun or verb such as partner, Door, Jagde, Reason, Solution, Problem, Pehle, Baat). Show the remaining important words as **tiny lowercase helpers**. Drop filler words entirely.
2. **Capitalise only the hero word's first letter** ("Badal", "Door", "Jagde"). Helpers stay lowercase. Keep Hinglish spellings casual and authentic, the way people type ("kyu", "rha", "apse", "smjta").
3. **Layout per phrase:**
   - hero word centred
   - helper 1 small, above-right of the hero word, ending flush with its right edge
   - helper 2 small, below-left of the hero word, starting flush with its left edge
   - at most two helpers on screen at once
4. **Timing:** each word appears on the **exact frame its first syllable is spoken** (taken from the word timestamps). Helpers can lead the hero word by up to 2 frames. The phrase holds until the next phrase starts, then is replaced (a 3-frame crossfade). **Never stack two hero words.**
5. **In-animation (every word):** opacity 0 → 100%, Gaussian blur 12 px → 0, scale 105% → 100%, over **6 frames** with ease-out cubic. Out-animation is a 3-frame fade.
6. **Specials (use each one exactly once, at the matching beat):**
   - **Gradient hero:** the key question word in B3 (e.g. "Kya" with `relationship` below-left and `bachega ja nhi` above-right) uses the rose → walnut gradient, in Poppins Light at 130 px.
   - **Letter reveal:** in B4/B5, one instance of "Problem" (or the main diagnosis word) reveals letter by letter, 2 frames per letter, each letter blurring in.
   - **Pills:** in B5, the solution words ("Remedies", "Guidance", or whatever she names) appear as **coral-rose pills**:
     - Rounded rectangle, corner radius = height/2, height ≈ 86 px, padding 36 px.
     - Fill `#E2566C`, outer glow `#F27A8C` at 35% with a 24 px blur.
     - The pill slides in from x −40 px with a fade (8 frames, ease-out back). Then the text types on left to right, 1.5 frames per character, with a light "tick" SFX per character (or one typewriter loop).
     - A second pill stacks 24 px below the first. Make the alternate pill **sage `#6F7D5E`**, or keep both rose.
   - **Credibility card (B6):** see Section 8, card C.
   - **CTA (B8):**
     - `"Click the link Below"` (or her exact CTA words) in quotes at 68 px, warm white.
     - Under it, a coral-rose pill with her offer line (e.g. `first whatsapp chat is free`), typewriter reveal.
     - In the last 0.6 s, add a small **animated arrow or finger-point chevron ↓** in gold `#F1D58C`, bouncing 3 times, pointing to the caption area.
7. **Silent sections:** leave about 1–2 short close-up moments with **no captions** so her face carries the emotion. The reference does this in its first close-up.

✅ **Show me:** a table with phrase #, start/end (s and frame), hero word, helper 1, helper 2, special treatment, and shot (wide/close/B-roll).

---

## 7. STEP 3: STORY-WORLD B-ROLL (AI stills → animated)

Make **5–6 inserts**, each 1.6–3.5 s, placed over the matching beat. The audio continues underneath, because her voice is the narration over the B-roll. Choose from this menu according to what she actually says:

| # | Use on | Visual (keep consistent: the **same client character** in every still) | Motion | Overlay effect (exactly one per still) |
|---|---|---|---|---|
| S1 | **B1 Hook (first 0.0 s!)** | Indian middle-class living room, warm tungsten light. The client (early 20s, **dusty-rose cotton kurta, hair in a messy bun**, teary) sits on a sofa while worried parents and siblings lean in around her. | Push-in plus truck-right from the parents to her face over the full insert (scale 100 → 112%) | **Neon rose-gold "?"** above her head. It flickers on over 4 frames (opacity 0/100/30/100), then pulses at 1.5 s per cycle (glow 70 ↔ 100%), with a neon-buzz SFX. |
| S2 | B2 (distance / partner changed) | Golden-hour bedroom. The client sits cross-legged on the bed, chin on hand, staring blankly, with a diary and chai in front of her. | Slow push-in | **Cloud thought bubble** (white 8 px stroke, torn-paper inner edge) pops in top-left (scale 0 → 110 → 100% over 10 frames, with a "pop" SFX). It holds a **happy couple selfie** of her smiling with her partner. Add a tiny **floating glass cube** particle drifting across. |
| S3 | B2/B3 (fights, a third person, "sab theek kab hoga") | The client sits on the floor against a cream wall, hugging her knees and looking up hopelessly. Hard golden sunlight throws window-blind shadows. | Slow tilt-down | **Antique-gold light-leak / film-burn** sweeps across the top half, ending in a **golden white-out flash** that becomes the transition out. |
| S4 | B3 (emotional low) | A front-facing symmetrical shot. The client sits on the bed hugging her knees, head bowed, with a framed family photo and books beside her. | Very slow push-in, perfectly centred | **Glowing halo orb** behind her head: a radial gradient (core `#FFF1E6`, mid `#F7B7C2`, rim glow `#F1D58C`). It pulses in scale 100 ↔ 106% and opacity 70 ↔ 95% on a 1.8 s cycle. |
| S5 | B5 (method) | A consultation scene: a hand writing on a **Vedic kundli chart** in a notebook on a wooden desk. Then a wide shot of **a young woman consultant (styled like the presenter: long black hair, sage-green kurta)** facing the client across a desk with a brass lamp, a small Radha-Krishna frame and a diya, in a cream-and-walnut room. | Push-in on the close-up, then a slow pan on the wide shot | The **pills** from Section 6 land on this shot. Add a large cream bokeh flare as the transition out. |
| S6 | **B7 Happy ending** | Night garden path with warm gold lamp posts. The client, now smiling in a **rose/sage lehenga**, twirls with her partner (dark kurta). **Real motion** (image-to-video). | Opens on a heavy gold flare that clears to reveal the dance | Rose and gold floating bokeh. Lift the music here. |

**Image generation prompts** (Nano Banana / Flux / Midjourney / Imagen; 9:16, photoreal, 35 mm, cinematic, shallow depth of field). The client always wears dusty rose and sage. Use the same face and seed across all stills for consistency.

1. **S1:** "Cinematic photoreal vertical shot, Indian middle-class living room, warm tungsten and window light, crying young Indian woman early 20s in a dusty-rose cotton kurta, hair in a messy bun, sitting on a beige sofa with hands clasped, worried father in a grey checked shirt and mother in a beige printed saree leaning over her from the left, younger sister and brother leaning over the sofa back from the right, family photo frames on a cream wall, small brass diya on a shelf, emotional, shallow depth of field, 35mm, warm rose-and-sage grade, 9:16"
2. **S2:** "Golden-hour Indian bedroom, young woman in a dusty-rose kurta sitting cross-legged on a bed with a sage-green block-print bedcover, chin on her hand, lost in thought, open diary and a chai cup in front, sheer curtains, photo pin board, warm lamp glow, melancholic, photoreal, 9:16"
3. **S2 bubble insert:** "Happy candid selfie of a young Indian couple, girl with wavy hair in a sage top smiling, boy in a white shirt, bright daylight, cut-out ready, square crop"
4. **S3:** "Young Indian woman in a dusty-rose kurta sitting barefoot on the floor against a cream wall, hugging her knees, looking up hopelessly, harsh golden sunlight with window-blind shadows on the wall, open book and coffee mug on the rug, cinematic, 9:16"
5. **S4:** "Front-facing symmetrical shot, sad young Indian woman in a dusty-rose kurta sitting on a bed hugging her knees, head bowed, framed family photo and stacked books beside her, warm beige room, soft light, photoreal, 9:16"
6. **Arguing-couple PNG (expert overlay, Section 8 card A):** "Full-body Indian couple arguing, woman with her hand on her hip looking annoyed, man in a white shirt pointing at her, plain white background, studio light". Then remove the background and convert to black and white.
7. **S5a:** "Close-up of a woman's hand with a thin gold bangle writing on a hand-drawn Vedic kundli birth chart in an open notebook, warm wooden desk, stacked books, small brass diya, warm lamp light, shallow depth of field, 9:16"
8. **S5b:** "Young Indian woman consultant with long straight black hair in a sage-green floral kurta sitting across a wooden desk from a young woman client in a dusty-rose kurta taking notes, brass desk lamp, small Radha-Krishna frame, cream panelled walls with walnut wood accents, soft warm cinematic light, 9:16"
9. **S6:** "Night garden path lit by warm golden vintage lamp posts, lush trees, a young Indian couple dancing joyfully, girl twirling in a dusty-rose and sage lehenga, boy in a dark kurta, romantic golden bokeh, cinematic, 9:16"

**Image-to-video** (Kling / Veo / Runway), for all stills where possible:
- **General motion prompt:** "very slow cinematic dolly-in, subtle parallax, characters breathe and blink slightly, no scene change, 5 seconds"
- **S6 prompt:** "the girl twirls under his raised hand, gentle camera drift, lamp bokeh"

**Fallback if there's no generator:** use Ken Burns on stills, or royalty-free stock footage that matches the descriptions. If you have neither, render clearly labelled placeholder cards with the prompt text, so I can drop the assets in later. Keep all timings intact.

✅ **Show me:** the B-roll plan with an exact in/out for each insert and the beat it covers.

---

## 8. EXPERT-WORLD OVERLAYS (on my talking-head footage)

**Always on during expert shots:** walnut-black gradient over the bottom 35% (`#1E1412`, 0% at y = 1250 → 80% at y = 1920), plus a 15% vignette.

- **Card A: "Confusion" composite (B1/B2, first expert shot, about 2–3 s).**
  - Place the **B&W arguing-couple cut-out** behind her on the **left half of the wall**, over the walnut panel area. Size it so their heads sit around y ≈ 420–520. Apply 85% opacity and a slight 2 px blur so it reads as "background thought".
  - **Rotoscope her** (person segmentation, e.g. MediaPipe / rembg / RVM) so the couple sits **behind** her hair and shoulders.
  - Add the **neon rose-gold "?"** above her head at about y ≈ 330, right of centre, avoiding the painting.
  - The first 2 frames of this shot get a **rose/magenta tint flash** (`#F27A8C` at 35%, screen blend).
- **Card B: Golden sparkle (optional, 1×).** A small gold sparkle burst (`#F1D58C`) beside her hand on one emphatic gesture, about 12 frames, with a shimmer SFX.
- **Card C: Credibility card (B6), text behind the subject.**
  - **Top:** a small Great Vibes script word (her phrasing, e.g. `Pichhle`/`Pishe`) at 70 px in light gold `#F1D58C`, placed above a **huge thin condensed number line** in Bebas Neue (e.g. `5 SAAL`, `10 SAAL`, or `500+ CLIENTS`, **using only figures she actually says**), in warm white at 95%. Centre it at y ≈ 470 so it sits on the cream wall at head height. **Mask her head and hair over the text** (segmentation matte) so the text is behind her.
  - Because the cream wall is light, give the number a subtle walnut outer shadow (`#1E1412`, 25%, 30 px blur) for legibility, or set it in **walnut `#5C4139`** instead of white if contrast is weak. Test both and keep the more legible one.
  - Animate the number rising 40 px with a fade over 10 frames and the script word writing on over 12 frames.
  - **Bottom:** the script word (e.g. `couples`/`clients`) in warm white, above a **coral-rose pill** containing the second claim (e.g. "More than 3000"), revealed with a typewriter wipe.
- **Card D: CTA (B8).** See Section 6, rule 6. Hide the jump cut at ≈ 34 s by starting the CTA on a **punch-in** (Section 9), so the cut reads as an intentional angle change.

---

## 9. FAKE MULTI-CAM: PUNCH-IN SYSTEM (replaces the reference's second camera)

Define three framings from my single shot. All are keyframed crops of the 1080×1920 upscale.

| Name | Scale | Anchor / framing | Use |
|---|---|---|---|
| **WIDE** | 100–104% | Full frame, slow drift push 100 → 104% over each shot | Default and hero-caption shots |
| **MEDIUM** | 120–125% | Crop centred on her face/chest. Eyes on the upper-third line (y ≈ 640). | Problem-deepening lines and the CTA |
| **CLOSE ("profile" substitute)** | 135–145% | Face offset **slightly left of centre**, with the Radha-Krishna painting partly in the upper-right as a background accent. Add a fake shallow depth of field: segment her and blur the background 6–10 px. | Emotional lines and silent face moments |

**Rules:**
- **Change framing on every sentence or phrase boundary** (cut on the word gap, never mid-word). Alternate WIDE ↔ MEDIUM/CLOSE. Never cut to the same scale twice in a row.
- Every expert shot has a constant **slow push** of 2–4% over its duration (ease-in-out) so nothing is ever static.
- On 2–3 emphatic words, add a **snap zoom**: +8% over 4 frames, ease-out, with a soft "whoosh-hit" SFX.
- **Reframe hands.** At CLOSE scale, make sure gesturing hands don't get awkwardly cut at the wrist line. If they do, use MEDIUM instead.

---

## 10. TRANSITIONS

- **Signature transition: rose-sage bokeh + cream flash.** Use it on **every** expert ↔ story switch and on the cut into the CTA.
  - It totals **12 frames (0.4 s)** at 30 fps.
  - **Frames 1–4:** 15–25 bokeh circles (rose `#F27A8C`, sage `#B9C6A4`, gold `#F1D58C`, 30–140 px, soft edges) bloom in from the frame edges toward the centre, scaling up. The outgoing shot gets exposure +1.5 stops.
  - **Frames 5–9:** a full-frame **cream white `#FFF6EC`** hold at 100%.
  - **Frames 10–12:** the incoming shot fades up through drifting bokeh, with exposure going from +1.5 back to 0.
  - **SFX:** a soft whoosh starting at frame 1, plus a high shimmer tail.
- **Variation 1 (once):** a caption word stays on top while the bokeh covers the frame. The reference does this with `kab hoga`.
- **Variation 2 (once):** a **golden film-burn white-out** out of S3, where the light-leak ends in a full gold `#F1D58C` → cream flash.
- **Variation 3 (once):** a big single **cream bokeh flare** sweeping across, used out of S5.
- **Expert ↔ expert:** framing changes between expert shots are **hard cuts** (no flash). The flash is reserved for world switches.
- **Ending:** a **hard cut** on the last syllable. No fade, no outro card, no logo.

---

## 11. AUDIO

- **Voice:**
  - Denoise lightly (room tone only, no artefacts).
  - High-pass at 80 Hz.
  - Gentle presence boost (+2 dB at 3–4 kHz).
  - De-ess.
  - Compress firmly (3:1 to 4:1, about −18 dB threshold, fast attack) to get a close, "podcast-y" sound.
  - **Normalise the full mix to −14 LUFS integrated, true peak ≤ −1 dBTP.** The source is −24.5 LUFS, so it needs about +10 dB. Keep the loudness range tight, around 1–3 LU.
- **Music bed:**
  - A royalty-free emotional ambient piano and soft pads at 70–80 BPM, e.g. from the Instagram library, Epidemic or Artlist, or generated. **No copyrighted Bollywood tracks.**
  - Sit it about **12 dB under the voice**, with sidechain ducking −4 dB while she speaks.
  - Arc: sad and minimal for B1–B4, a slight hopeful lift (adding strings or arpeggios) at B5, a **warm swell on B7 (happy ending)**, and a **resolve chord on B8**. The music ends exactly at the hard cut, or with a 0.2 s tail.
- **SFX** (subtle, −20 to −26 LUFS relative):
  - a whoosh and shimmer on every bokeh flash
  - neon buzz and flicker on the "?"
  - a soft pop on the thought bubble
  - a typewriter tick on pill text
  - a whoosh-hit on snap zooms
  - a shimmer on the gold sparkle
  - a low "riser" leading into the happy ending

---

## 12. EXPORT & QC CHECKLIST

**Export:** 1080×1920, **30 fps**, H.264 High profile, about 16–20 Mbps VBR, yuv420p, AAC 320 kbps 48 kHz stereo, `+faststart`, `.mp4`. Also export a **thumbnail/cover frame**: the credibility card frame or the strongest hook frame, with the hero word visible.

Before you deliver, verify each item and report pass or fail:

- [ ] Total duration is 36–40 s, there are no dead pauses, and the jump cut is hidden by a framing change or transition.
- [ ] Every caption word appears within ±1 frame of being spoken. One hero word at a time, never stacked. Hinglish is in Roman script with casual spellings.
- [ ] All captions sit inside the safe zone (x 90–990, y 220–1620). Nothing is covered by the Instagram UI.
- [ ] No teal, cyan or navy remains anywhere. Every graphic uses the rose / sage / gold / cream / walnut palette.
- [ ] Each signature device appears at least once: neon "?", B&W couple composite, thought bubble + glass cube, gold film burn, halo orb, gradient hero word, letter-reveal word, pills, text-behind-subject number, CTA pill, bokeh flashes.
- [ ] The text-behind-subject matte is clean, with no halo or flicker around her hair.
- [ ] The B-roll client character is consistent across stills and clearly a different person from the presenter.
- [ ] Credibility numbers come **only** from her own words. No invented claims.
- [ ] Upscaled footage isn't over-sharpened, and punch-ins never exceed 145%.
- [ ] Loudness is −14 LUFS ±1, true peak ≤ −1 dBTP, there's no clipping, and the music never masks speech.
- [ ] The video ends with a hard cut on the CTA with no outro card.

**Deliverables:**
1. The final MP4.
2. The cover frame PNG.
3. The caption table (CSV/SRT with hero and helper columns).
4. A short layer-by-layer EDL (timecode, layer, asset, effect, parameters) so I can tweak it in CapCut or Premiere.
5. The list of AI image prompts and seeds you used.
