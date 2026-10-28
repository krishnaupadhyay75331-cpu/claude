# EDIT PROMPT: "Shri Krishna Shringar" Instagram Reel (motion-graphics talking-head edit)

> Copy everything below this line and give it to Claude together with the 11 video files (main video + 10 overlay clips). The editor can also use the BGM/SFX library at `D:\Editing assets`.

---

## 0. YOUR ROLE AND THE GOAL

You are a senior short-form video editor and motion designer. Edit my raw footage into a finished **9:16 Instagram Reel** in the same style as a reference edit I like. That reference is a social-media-agency promo built on these moves:

- **text-behind-subject (depth effect)** headlines
- **word-by-word pop captions**
- **floating 3D-tilted UI/photo cards** with spring bounce
- **light-leak / ink-smoke / film-burn transitions**
- **stroke-draw line graphics**
- a **number counter with a spinning gradient ring**
- a **shimmer CTA**
- pop SFX on every graphic and whooshes on every transition

Copy **every one of those techniques, their timings and their easing**. **Do not** copy the reference's colours or words. My video is about a devotional shringar / poshak / puja-samagri shop, so the palette is warm-devotional (defined in §3), and every word on screen must come from what is actually said in **my** video.

Work in whatever pipeline you have: After Effects, Premiere/DaVinci with Fusion, CapCut desktop, or code (Remotion/FFmpeg + a segmentation model for the person matte). If you work in code, deliver the source project too.

---

## 1. SOURCE FILES (read these carefully)

### 1a. Main video (A-roll)
`copy_B33BFD56-28ED-4C32-A059-E549124F613A-compressed.mov`: 1080×1920, 30 fps, HEVC, **31.73 s**, Hinglish voice recorded on a clip-on wireless lav mic.

It has **two physical scenes**:

| Source time | Scene | What's in frame |
|---|---|---|
| **0.00 – 10.80 s** | **Scene N: night street (voice-over)** | Handheld, nobody on camera. Deep indigo/navy night sky fills the top ~40%. A bright lime-green lit tree is at top-right. Warm street lamps and a blurred market crowd sit on the horizon. A white sedan fills the lower half, with another white car bonnet at bottom-left. The speaker talks off-camera. |
| **10.80 – 11.60 s** | **Native whip-pan** | The camera whips right, with heavy motion blur through trees, then a pink/white shopfront. **This is the first transition. Keep it and enhance it** (see §6). |
| **11.60 – 31.73 s** | **Scene S: shop talking-head** | Static, locked-off medium-wide shot. A young Indian woman with long straight black hair, wearing a cream/white kurti top with an all-over grey **elephant print**, ¾ sleeves, blue jeans, a red thread and wooden beads on her right wrist and a black lav mic on her neckline. She stands centre-frame in front of the shop entrance. Behind her: the shop banner **"श्री कृष्ण … श्रृंगार"** (Shri Krishna Shringar) with a Krishna picture. A strip above reads **"लोटस रेस्टोरेंट के सामने, … धर्मशाला के पास"** (opposite Lotus Restaurant, near … Dharamshala). Also visible: hanging red/green decorative pieces, a lime-green neon mannequin sign on the left pillar, sandstone pillar, saffron/yellow deity-dress fabric on the right, coconuts in a steel bowl, a QR code, and yellow/black crates at the bottom. Very colourful, busy, warm. She mostly keeps her hands clasped at her waist, gestures with open palms around 18–22 s, and **smiles at the end (~30.5–31.0 s)**. |

**Measured speech phrases** (from audio pauses; I could not transcribe the words, so **you must transcribe first, see §2**):

| Phrase | Source time | Scene |
|---|---|---|
| P1 | 0.00 – 2.75 | Night street |
| P2 | 3.05 – 5.34 | Night street |
| P3 | 5.65 – 9.69 | Night street |
| P4 | 10.05 – 13.15 | Crosses the whip-pan into the shop |
| P5 | 13.57 – 16.21 | Shop |
| P6 | 16.51 – 17.63 | Shop |
| P7 | 18.05 – 18.98 | Shop |
| P8 | 19.28 – 21.28 | Shop |
| P9 | 21.54 – 21.76 | Shop (one or two words) |
| P10 | 22.08 – 22.38 | Shop (one or two words) |
| P11 | 22.75 – 30.40 | Shop (long closing phrase, likely the CTA / location / "aaj hi aaiye") |
| Tail | 30.40 – 31.73 | Silence, she smiles |

### 1b. Overlay / B-roll clips (all shot inside the shop on iPhone, portrait)
Several are stored as 3840×2160 or 1280×720 with **rotation metadata. Honour the rotation: they are all PORTRAIT.** Conform everything to **30 fps** (some are 29.97).

| File | Length | Content | Best use |
|---|---|---|---|
| `IMG_0462.mov` | 3.2 s | Macro: industrial sewing machine needle stitching gold-lace trim onto **red/pink embroidered fabric**, hands guiding it | "Handmade / custom stitching" moments; tilted photo card |
| `IMG_0463.mov` | 4.2 s | Wider: a woman in a pink dupatta stitching a **red-gold poshak** at the machine, shop shelves behind | Full-screen B-roll; "apne haath se / custom banate hain" |
| `IMG_0680.mov` | 4.6 s | A long row of **bridal bangles (chudiyan)**: maroon, cream, gold, stone-studded. Slow lateral move | Floating card with label "Chudiyan"; full-screen B-roll |
| `IMG_0682.mov` | 4.2 s | Close-up of the same bangles, rotating, sparkling stones | Hero B-roll for bangles; neon-tint→colour card reveal |
| `IMG_0684.mov` | 2.7 s | Handheld: dense bundles of hanging **shringar packets / decorative strings** (silver, gold, colourful) | Fast montage insert ("variety") |
| `IMG_0685.mov` | 8.6 s | Handheld close-ups moving through **packets of mini poshak, laces and shringar items**, Hindi-labelled packs | Montage / card thumbnails (trim the best 1–2 s pieces) |
| `IMG_0696.mov` | 5.2 s | Wide tilt across **floor-to-ceiling shelves of puja samagri**: boxes, jars, bottles, red pouches | "Puja ka saara saamaan / sab kuch ek jagah" |
| `IMG_0697.mov` | 0.6 s | A tall hanging decorative **garland display with a red-gold medallion** at the bottom | 0.4–0.6 s flash cut in the montage |
| `IMG_0698.mov` | 1.7 s | A hand holding a **sky-blue round embroidered aasan / deity poshak with stone work** | Hero product card ("Laddu Gopal ka shringar" if she says so) |
| `IMG_0699.mov` | 3.3 s | Tilt-up over stacks of **colourful deity poshak / chunri**: red, green, gold zari | Full-screen B-roll; card thumbnails |

**Use every overlay at least once.** Choose clip in/out points from the steadiest, sharpest, most colourful moments, and avoid shaky frames and focus hunting. If a moment is unusable, freeze-frame its best frame and treat it as a photo card.

### 1c. Asset library: `D:\Editing assets`
Before you start, **browse this folder and its subfolders** (BGM, SFX, overlays, light leaks, fonts, LUTs, etc.) and pick from it first:
- **BGM:** something upbeat and positive. Ideal: an **Indian-fusion / devotional lo-fi beat with bansuri (flute)**, a nod to the Krishna theme, or a light tabla-pop groove. Second choice: upbeat corporate/lo-fi pop, like the reference. Avoid copyrighted commercial songs.
- **SFX:** pop / bubble pop, soft whoosh, swish/swoosh, riser, impact/hit, **temple bell "ting" or small ghanti**, sparkle/shimmer, camera-shutter click, UI click/tap, number-tick/counter roll, "ding" success. Use light-leak / film-burn / ink-smoke video overlays from the library if it has them.
- If something isn't in the folder, generate it or use royalty-free equivalents, and tell me what you substituted.

---

## 2. STEP 1: TRANSCRIBE AND LOCK THE SCRIPT (do this before designing anything)

1. Transcribe the main video **word by word with word-level timestamps** (Whisper large-v3 or similar, language Hindi/Hinglish). Write the output in **Roman-script Hinglish** (e.g. "Aaj hum aaye hain…"), not Devanagari, because the captions are in Roman Hinglish like the reference.
2. Check the transcript by ear and fix spellings of names, the shop name and the place names. The shop banner reads **श्री कृष्ण … श्रृंगार**; confirm the exact name from the audio and the signboard (likely **"Shri Krishna Shringar"**).
3. Map each word to the phrases P1–P11 above.
4. From the transcript, pick the **keyword list**: the 1–3 most important words per phrase. These become the big headlines; everything else is a small caption. Typical keywords for this kind of video: shop name, city / area name, **poshak, shringar, chudiyan / bangles, puja samagri, handmade / custom, sab kuch ek jagah, price / "₹… se shuru", address / landmark (Lotus Restaurant), "aaj hi visit karo"**.
5. **Never invent facts.** Show a number, price, rating, discount, years, "No.1", "best" or an address on screen **only if she actually says it**, or, for the address, only if it's readable on the signboard. If a slot in the timeline below needs a word she didn't say, use her nearest real phrase instead.
6. Show me the transcript and the keyword list in your first reply before rendering, then continue.

---

## 3. GLOBAL LOOK

### Format
- 1080×1920, 9:16, **30 fps**, final length **≈ 31 s**. You may tighten gaps longer than 0.3 s between phrases with invisible jump-cuts or punch-ins, which brings it to ≈ 29–30 s. Never cut mid-word.
- Export: H.264 High, 16–20 Mbps VBR 2-pass, Rec.709, AAC 320 kbps 48 kHz stereo. Also deliver the project/source file.
- **Instagram safe zones:** keep all important text out of the **top 220 px**, the **bottom 380 px** and the **right-hand 140 px** (the Reels UI buttons).
- **NO** Instagram handle / username watermark, **NO** corner Instagram icon, **NO** handle pop-up, **NO** black Instagram end card. The frame stays clean.

### Colour palette (replaces the reference's blue/green palette)
The shop footage is saffron, red, yellow, maroon and gold. The reference's electric blue contrasts well with that, so blue keeps its job as the main keyword colour, re-themed as **Krishna peacock blue**.

| Role | Reference used | **Use this instead** |
|---|---|---|
| Main keywords (big headlines) | Electric blue gradient #1A8CFF→#00C2FF | **Peacock-blue gradient #0A4DFF → #00B8FF**, top-to-bottom linear, 2 px inner highlight #7FDBFF at the top edge |
| Labels (small product tags) | Neon green #3CE65A | **Marigold gold #FFC23A** (solid), or a gold pill with dark-maroon #4A0E12 text |
| Brand word (shop name) | Orange→pink→magenta gradient | **Saffron → kumkum red → rani pink: #FF9A1F → #E8202A → #D6197F** (keep this one close to the reference's) |
| Secondary gradient (the reference's blue→purple / pink→purple) | Blue→purple | **Peacock blue → mor-pankh teal → violet: #0A4DFF → #00A6A6 → #7B3FE4** |
| Captions | White | **White #FFFFFF**; "muted" captions in warm grey #D9D2C7 |
| Accents / lines / rings | White | White, plus **gold #FFC23A** rings and a peacock-feather motif |

- **Legibility on the busy shop background:** every text layer gets a soft drop shadow (black at 45%, 0 px offset, 18–24 px blur) **and** a very thin 1.5 px dark-maroon #2A0A0C outer stroke at 60%. Wherever headlines sit, add a soft radial darkening (−15% exposure, feathered 400 px) on the background layer only.

### Typography
- Headlines: **Inter / SF Pro Display / Helvetica Now Display, ExtraBold–Black**, tracking −2% to −4%, tight leading (0.9). Big headline size 150–230 px cap height, depending on word length.
- Supporting small words: same family, **Regular/Medium**, white, 54–70 px.
- Captions: same family, **Bold**, 64–76 px, white.
- **Devanagari accent (new, matches the shop banner):** under or above the brand word, a small **"श्री कृष्ण श्रृंगार"** in *Yatra One* or *Tiro Devanagari Hindi*, gold #FFC23A, about 60 px. Use it only for the brand reveal and the final CTA.

### Grade
- **Scene N (night):** keep the rich indigo sky. Lift shadows slightly (+5), denoise chroma, keep the tree's lime green but pull saturation −10 so it doesn't glow. Warm the street lamps slightly. Add a light vignette.
- **Scene S (shop):** warm and natural, slightly desaturated overall (−8 sat), protect skin tones, highlight roll-off on the white shop interior. Use the person matte from §4 to **fake an f/1.8 depth of field**: blur the background behind her by 6–10 px (Gaussian or lens blur) and drop background saturation another −10%. She stays tack sharp. This gives the reference's cinematic shallow-focus look and makes text readable.
- **B-roll:** match warmth to Scene S, gentle +5 vibrance, a slight sharpen. Gold zari and stones should sparkle without clipping.
- Optional: a fine 35 mm grain (strength 5–8%) on everything at the end so the footage and graphics feel unified.

---

## 4. CORE TECHNIQUE: TEXT BEHIND THE SUBJECT (depth effect)

- **Scene S:** rotoscope / segment the woman on every frame (an AI matte such as Rotobrush 3, Magic Mask, SAM2 or RVM, then refine the hair edges). The camera is static, so the matte should be clean. Layer order, bottom to top: **background plate → big headlines + rings + badges → her matte (cut-out) → small captions, labels and cards that should be in front**.
  - Her head sits roughly at **y 630–830 px** and her shoulders at **y 900–1000 px**. Put the big headlines in the **upper third (y ≈ 380–700)** so that her head and hair overlap the bottom 20–40% of the letters, exactly like the reference.
- **Scene N (night street, no person):** create the same depth effect with the scene's own objects. Mask the **lit tree at top-right** and the **roof line of the white sedan**. Headlines sit in the indigo sky **behind the tree leaves**, and icons/cards rise **from behind the car roof**. Track the masks; the footage is handheld.
- **B-roll full-screen moments:** where possible, put the headline behind the main object (e.g. behind the bangle stack in IMG_0682, behind the hand holding the blue aasan in IMG_0698) using a quick object matte.

---

## 5. ANIMATION SYSTEM (same as the reference; use these exact numbers)

| Element | Animation |
|---|---|
| **Word-by-word captions** | Each word appears exactly on its spoken syllable: **scale 80%→100% + opacity 0→100% over 4–6 frames, ease-out (cubic)**. 2–4 words visible at a time, centred at **chest/neck height (y ≈ 1000–1150 in Scene S; y ≈ 1150 over the car in Scene N)**. The currently spoken keyword can flash 1 frame of peacock blue, then settle. Caption group exits: fade + 10 px up over 4 frames. |
| **Headline entrances** | Either a **fast slide / mask reveal from the left** (x −120 px → 0, linear mask wipe) or a **scale-up 70%→100% with directional motion blur**, over **6–8 frames, back-out (overshoot ≈ 1.15)**. Exit: 5-frame scale 100→90% + fade, or slide out to the right with blur. |
| **Floating cards / icons** | **Spring pop: scale 0→110%→100%** over ~10 frames (stiffness ≈ 220, damping ≈ 14). Soft drop shadow (black 35%, y +18 px, blur 40 px). **Slight 3D tilt** (rotateY ±8–12°, rotateZ ±4–6°). While on screen they **float 2–4 px** (sine, 2 s period, each card a different phase). Cards are rounded rectangles (radius 28 px) with a **6 px white frame**, like the reference's IG post cards; video clips play inside the cards. |
| **Labels** | Gold text or a gold pill, popping 2–3 frames after the card it belongs to: scale 80→100%, back-out. |
| **Connector lines** | Thin 4 px white curved line (bezier) drawn with a **stroke-draw over 8–10 frames** from her palm to the card. The line end has a 10 px dot. |
| **Stroke-draw graphics** | Lines and ticks draw on with trim-path 0→100% over ~1 s, ease-in-out. |
| **Counter** | Number rolls with an **ease-out (expo) curve over ~1.2 s**, tabular figures, plus a **gradient progress ring** spinning behind it. |
| **Shimmer** | A diagonal 30° white→transparent gradient band sweeps **left→right across the letters over ~0.7 s**, masked to the text. |
| **Camera punch-ins** (to fake multiple shots from one static take) | Hard cuts between **100% / 112% / 120%** scale at phrase boundaries, re-centred on her face. Add a 1-frame 2% scale "bump" on each cut. Sharpen the 120% shots slightly. |

---

## 6. TRANSITIONS (each 8–10 frames + whoosh SFX)
1. **T1, night → shop (10.80–11.60):** keep the native whip-pan and boost it: add extra directional blur, then a **bright saffron-gold + white light-leak flash** sweeping from the right that peaks at ~11.3 s and burns the frame to near-white for 3 frames, revealing the shop. Big whoosh + soft impact on landing.
2. **T2, into the B-roll burst (~16.3 s):** a **peacock-blue ink / smoke burst** wiping in from top-left, the reference's "blue ink smoke" (8–10 frames, whoosh).
3. **T3, back to the talking-head (~19.2 s):** **white-blue light-leak** from the right (the reference's blue-white glow).
4. **T4, before the final CTA (~27.3 s):** **orange-red film burn** light leak (8–10 frames, whoosh + crackle).
- All other changes inside Scene S are **hard cuts / punch-ins** synced to the beat or the end of a word.

---

## 7. SHOT-BY-SHOT TIMELINE (source timestamps; adjust ±0.2 s to the real word timings from §2)

> Format: **[time] | footage | graphics**. "Keyword" = the real word(s) she says in that phrase (from your transcript). Where I suggest a likely word in quotes, use it **only if she actually says it**; otherwise substitute her real keyword in the same slot and style.

### 0.00 – 2.75 s | P1 | Scene N (night street), 100% → slow 104% push-in
- **Hook headline:** her first keyword (e.g. the city/area or "Shringar") in **huge peacock-blue gradient**, **slides in from the left** in the indigo sky (upper third, y ≈ 350–600), sitting **behind the masked tree leaves** at the right.
- Small white supporting words **just above** it (Medium weight), e.g. the 2–3 words that lead into the keyword.
- A **small tilted photo card spins in at top-right** (rotateZ −25°→−6°, spring): a freeze-frame of **IMG_0699** (colourful poshak stacks), 6 px white frame.
- A **gold label** pops in **under** the headline with her second keyword (e.g. "Poshak" / "Shringar").
- White word-by-word captions at y ≈ 1150 over the car.
- SFX: whoosh on the headline, pop on the card, pop on the label.

### 2.75 – 5.34 s | P2 | Scene N
- The first headline exits (slides out right with blur).
- **3D glossy devotional icons** (the reference used YouTube/FB/IG icons) **rise from behind the car roof** with a bounce, one after another 4 frames apart, then settle **in a row in the upper sky**: a **bangle / chudi**, a **diya (oil lamp)**, a **peacock feather (mor pankh)**, and a **folded poshak / chunri**. Glossy 3D style, soft shadow, slight float, gold and peacock-blue materials. Generate these or take them from `D:\Editing assets`.
- A big peacock-blue headline with P2's main keyword appears **behind the icons / tree**.
- Word captions follow her speech. SFX: 4 quick pops (rising pitch) for the icons.

### 5.34 – 9.69 s | P3 | Scene N
- Icons shrink and fly to the top-left, then disappear.
- **Three "post cards" pop in one after another** above the car (like the reference's three IG post cards), with **video playing inside each** and a white frame:
  1. IMG_0682 (bangles close-up)
  2. IMG_0463 (tailor stitching poshak)
  3. IMG_0698 (blue embroidered aasan)
- Then the cards **shrink and slide to the top-left** as a fanned stack.
- **Caption stack** in the reference's layout:
  - small white lead-in words
  - **big peacock-blue keyword**
  - **warm-grey** line with the rest of the phrase (the reference's grey "Kam nai chalta !!" slot), ending in "!!" only if it's an exclamation.

### 9.69 – 11.60 s | end of P3 → start of P4 | Scene N → **T1 whip + saffron-gold light-leak**
- Clear all graphics 4 frames before the whip. Whoosh + soft impact as the shop is revealed.

### 11.60 – 13.15 s | rest of P4 | Scene S at 100%: BRAND REVEAL (the reference's "Yahi per … Studio" beat)
- Caption: her phrase (e.g. "Yahi pe" / "Yeh hai…") pops in at neck level.
- A **white circle grows from behind her head** (scale 0→100%, back-out) and becomes the **shop badge**: a white circle with a **peacock-feather / flute line icon** in gold and the shop name in small caps. If I give you a logo, use it.
- The **giant brand word** (e.g. **"SHRINGAR"** or the shop's main name word) in the **saffron→kumkum→rani-pink gradient** appears **behind her head**, with **"श्री कृष्ण"** in small gold Devanagari above it.
- SFX: **temple bell "ting"** on the badge, a whoosh on the brand word, and a light sparkle.

### 13.57 – 16.21 s | P5 | Scene S, **punch-in to 112%**: "Right content / Right ads" beat
- **Card 1** (video: **IMG_0463** tailoring, or IMG_0462 macro stitching) pops up **above her right hand**, with a **thin white curved line** drawn from her hand/palm to the card. **Gold label** above it with her keyword (e.g. "Handmade Poshak" / "Custom stitching").
- **Card 2** (video: **IMG_0680** bangles row) pops up **above her left hand**. It first appears with a **peacock-blue tint and glow** (the reference's neon-green tint), which **fades to full colour over ~12 frames**. **Gold label** above it (e.g. "Chudiyan").
- Caption at chest level with the rest of her phrase (the reference's "bhi jaruri hai" slot).
- SFX: pop + click per card, a soft "shimmer" as the tint fades.

### 16.21 – 19.28 s | P6 + P7 | **T2 peacock-blue ink burst** → full-screen B-roll burst
- 16.3–17.6: **IMG_0699** poshak tilt-up, full screen. Big white headline with P6's keyword at the top-left, behind the top of the poshak stack if it can be masked cleanly.
- 18.0–19.0: **IMG_0682** bangles rotating, full screen. Peacock-blue headline with P7's keyword, **behind the bangle stack** (object matte). Add 2–3 tiny sparkle glints on the stones.
- Her voice continues underneath. Captions stay word-by-word, lower-middle.
- Hard cut on a beat between the two clips.

### 19.28 – 21.28 s | P8 | **T3 white-blue light-leak** → Scene S at 100% (she gestures with open palms)
- **Glassmorphism info card** (the reference's frosted Instagram-profile card) pops in at the **top-left** with a bounce: frosted glass, 24 px background blur, a light **gold/cream tint** at 18% opacity, rounded 32 px corners and a 1 px white border at 40%. Inside:
  - the shop badge (small)
  - the **shop name**
  - one line of categories she mentions, e.g. "Poshak • Shringar • Puja Samagri • Chudiyan"
  - a small **location-pin row** with the landmark from the signboard ("Lotus Restaurant ke saamne")
  - **No fake follower counts, ratings or reviews.**
- Captions in the reference's layout: a white lead-in word, a middle word **sliding in from the right**, and the final keyword in the **peacock-blue → teal → violet** secondary gradient.

### 21.28 – 22.75 s | P9 + P10 (short punchy words) | Scene S, punch-ins **120% → 112%**
- Replaces the reference's line-chart beat with the same **stroke-draw technique**: a minimal **white checklist** draws itself behind her on the right side of her head. Each item gets a stroke-drawn tick (✓), and the items are the product categories she names (e.g. ✓ Poshak, ✓ Shringar, ✓ Chudiyan, ✓ Puja samagri). Ticks draw on with a 0.15 s stagger, ~1 s total. Each P9/P10 word lands as a **big single word** with a 120%/112% hard-cut punch-in.
- A **white rounded pill label** with her key phrase (the reference's "Performance marketing" pill) sits at chin level, the text inside in the secondary gradient.
- SFX: tick/click per checkmark, impact on each punch-in.

### 22.75 – 27.30 s | first half of P11 | B-roll montage + "Aur best part" beat
- 22.8–24.6: **fast montage**, about 0.4–0.6 s per clip, cut on beats, alternating full-screen and floating cards over her:
  - **IMG_0696** (puja-samagri shelves)
  - **IMG_0684** (hanging shringar packets)
  - **IMG_0697** (0.5 s flash, garland display)
  - **IMG_0685** (best 1 s of packets)
  - **IMG_0462** (macro stitching)
- Small white words above, **bold white key phrase at chest level**, small white words below (the reference's "humari services / Aur best part / Start hoti hai" stack), all from her actual words.
- 24.6–27.3: back to Scene S at 112%. **Number counter beat:** **only if she says a number** (price "₹… se shuru", years, number of designs, etc.): big white number rolls **0 → that value over ~1.2 s (expo ease-out)**, with a **gold / peacock-blue / white gradient progress ring spinning behind the digits**, a small "₹" or unit after the number, and a caption with the rest of the phrase. **If she says no number**, use the same ring spinning behind a big white keyword instead (e.g. "SAB KUCH EK JAGAH"). Never invent a number.
- SFX: counter tick-roll + "ding" when it lands.

### 27.30 – 30.40 s | rest of P11 | **T4 orange-red film burn** → Scene S at 100%: CTA
- Big white words pop in at the top-left (the reference's "So if you" slot), from her CTA words.
- Small supporting line under it.
- A peacock-blue keyword **slides in** with a **gold circular ring / badge graphic spinning in at its left** (the reference's brown ring, recoloured gold #FFC23A with a peacock-feather glyph).
- Then the final CTA in **bold white caps at chest level**, e.g. **"AAJ HI VISIT KARO"** (use her exact CTA words), with the **shimmer sweep** left→right across the letters. A small line above it, e.g. "to get started" → her lead-in words. Below it, a **location-pin chip** with the landmark (from the signboard / her words).
- Small gold Devanagari **"श्री कृष्ण श्रृंगार"** under the CTA.
- SFX: whoosh, pop, shimmer sparkle, a soft final bell "ting".

### 30.40 – ~31.0 s | Tail
- **End on her smile.** Graphics fade out over 6 frames, then a **quick 8-frame fade to black** (or a hard cut on the music's last hit). Trim the remaining silence.
- **No Instagram end card, no handle.**

---

## 8. SOUND DESIGN
- **Voice first.** Clean the lav audio: high-pass at 80 Hz, gentle noise reduction for the street noise in Scene N (don't make it sound underwater), de-ess, light compression (3:1), make Scene N and Scene S match in loudness and tone, and add a short room-tone crossfade across the whip-pan.
- Final loudness **−14 LUFS integrated, −1 dBTP**. Voice sits around −16 to −14 LUFS short-term. **BGM sits 18–22 dB under the voice**, sidechain-ducked an extra 4–6 dB while she speaks, and rises slightly in the 0.3 s gaps and in the B-roll burst.
- Start the BGM on frame 1 with a quick 4-frame fade-in. Cut it to the beat so that **the whip-pan (11.3 s), the B-roll burst (16.3 s) and the CTA (27.3 s) land on downbeats** (time-stretch ±3% or edit the music to make that happen).
- **SFX on everything that moves:** pop on every caption group, card, icon and label (vary the pitch so it doesn't get monotonous); whoosh on every transition and headline slide; tick on checkmarks and the counter; bell "ting" on the brand reveal and the final CTA; sparkle on the shimmer and on bangle glints. Keep SFX at −22 to −16 dB so they never cover words.

---

## 9. QUALITY CHECKLIST (verify before delivering)
- [ ] Every caption word matches the audio exactly (spelling and timing ±2 frames).
- [ ] Her hair and head overlap the big headlines on every shop-scene headline; no matte chatter or halo on the hair edges.
- [ ] All 10 overlay clips are used, correctly rotated (portrait), no black bars, no shaky or out-of-focus frames.
- [ ] No text in the IG safe-zone margins; nothing covers her face or mouth.
- [ ] No invented numbers, prices, ratings or claims; the shop name and landmark are spelled correctly.
- [ ] Transitions are 8–10 frames, each with a whoosh; cards bounce (0→110→100%) and float 2–4 px.
- [ ] Colours follow §3 (peacock blue / marigold gold / saffron-kumkum-rani brand gradient / white).
- [ ] No Instagram handle, icon, pop-up or end card. Ends on her smile → black.
- [ ] Audio at −14 LUFS, voice always intelligible, no clipping.
- [ ] Export 1080×1920, 30 fps, H.264, ≈ 29–31 s. Deliver the MP4, the project file and a list of the assets used from `D:\Editing assets`.

## 10. WHAT TO SEND BACK
1. The transcript (Roman Hinglish, with timestamps) and the keyword list.
2. A short storyboard (one frame per beat) for my approval, **or** render straight away if you're confident.
3. The final MP4, the project/source file, and a short list of anything you substituted or couldn't do.
