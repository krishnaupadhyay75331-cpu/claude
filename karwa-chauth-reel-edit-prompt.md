# VIDEO EDIT PROMPT: "Karwa Chauth shop reel, agency style (kinetic captions, text behind the speaker, glossy 3D pop-ups)"

You are a senior motion designer and short-form video editor who makes premium Instagram reels for agencies. Edit the raw clip below so it moves exactly like a high-end agency promo reel: fast and punchy, with a new graphic every 1–2 seconds, hero text sitting BEHIND the speaker, glossy 3D pop-ups, light-leak flash transitions, and an animated Instagram end card. Keep every motion behaviour in this brief. The colours have been re-designed to match this footage's festive red, gold and pink palette.

If you can run code, build the edit yourself. Use Remotion (React) or After Effects scripting for the graphics, an AI matting model (Robust Video Matting, SAM 2 or rembg) for the speaker mask, and FFmpeg for the final encode. If you can't, write a frame-accurate, step-by-step build sheet that an editor can follow in After Effects or Premiere Pro, or in CapCut Pro as a fallback. Either way, follow every number in this brief.

---

## 0. SOURCE FOOTAGE: WHAT IS ACTUALLY IN THE CLIP

| Property | Value |
|---|---|
| File | iPhone vertical clip, **864×1536**, 30 fps, **42.47 s**, mono speech |
| Speaker | Middle-aged shopkeeper with glasses, **steel-blue checked shirt**, lavalier mic on his collar, speaking **Hinglish** straight to camera |
| Location | Packed Indian festive/gift shop: shelves of gift boxes, peacock décor, a toy jhoola, framed deity photos with marigold garlands, a lavender-pink wall with jaali panels, an AC unit, a CCTV dome and a small TV in the top corners |
| Hero products | Red-and-gold **gota-patti Karwa Chauth thalis**, mesh **chhalnis** (sieves), steel **karwa/lota sets** with multicolour beaded rims, a **heart-shaped red gota thali**, maroon velvet pouches, and a **boxed karwa gift set** (clear plastic lid) |

**Natural structure of the raw clip (source timecodes):**

| Source time | What happens on camera |
|---|---|
| **00.00–05.00** | Standing, handheld, framed from mid-thigh up. Shelves and the framed deity photo are behind him. He looks to camera and talks, with red fabric in the bottom-left corner. Head at about y = 33–40% of frame height. |
| **05.00–07.00** | He turns toward camera-left and gestures with both hands. The camera starts drifting right. |
| **07.00–10.87** | He has moved to the red thali display and places his hand on the gota thalis, half-turned away. The camera is handheld and a bit shaky. |
| **10.87–11.37** | **Silence + fast whip-pan or motion blur** (the camera repositions). This is the built-in transition point. |
| **11.37–22.00** | **Locked-off wide shot.** He is SEATED behind a table draped in red-and-gold lattice gota cloth, with 4–5 thalis/karwa sets in front of him filling the bottom 40% of the frame. Busy shelves fill the top 45%. His head sits at about **y = 40–47%**, his chest at **y = 52–62%**. He talks and touches the thalis and the chhalni on the left. |
| **22.00–26.00** | He reaches across the table, lifts items and gestures toward camera-right. |
| **26.00–28.70** | He lifts and holds up the **heart-shaped red gota thali** in front of his chest. **This is the hero-product moment.** |
| **28.70–29.04** | Short silence. Use it as a cut point. |
| **29.04–33.00** | He lays the heart thali down and arranges it with the maroon velvet pouch. He keeps talking. |
| **33.00–35.50** | He reaches to camera-right and picks up the **boxed karwa gift set**. |
| **35.50–42.47** | He holds the boxed set at chest height, looks to camera and closes his pitch. The clip ends mid-shot. |

> ⚠️ **STEP 1, before you design anything:** Transcribe the audio with **word-level timestamps** (WhisperX or Whisper large-v3, language = Hindi; write the output in Roman Hinglish, all lowercase, as spoken). Every caption, hero word and pop-up below must be timed to the real spoken syllables. Placeholders in `[SQUARE BRACKETS]` mean "use the shopkeeper's actual words at this moment". If his words don't fit the suggested placeholder, **keep the effect and its timing, and swap in his real words.** Never invent claims (prices, customer counts) that he doesn't say. Use the values I supply in Section 9 instead.

---

## 1. GLOBAL LOOK

- **Output:** 9:16, **1080×1920**, 30 fps. Upscale the 864×1536 source by 125% with an AI upscaler (Topaz Proteus/Iris or Real-ESRGAN) **before** any punch-ins so the zooms stay sharp. Final length is about **38–40 s of talking plus a 4.5 s end card.**
- **Colour grade ("festive warm-premium"):**
  - White balance: warm by about +300 K. Remove the slight magenta-lavender cast on the walls so they read as clean warm ivory-pink.
  - Shadows lifted slightly (+5 to +8), gentle S-curve with medium contrast, highlights rolled off so the TV and wall lights don't clip.
  - **Reds:** rich and deep (hue toward crimson, saturation +10), but **never clipping**. Keep detail in the gota lattice and in the maroon velvet.
  - **Golds/yellows:** +8 saturation, slight push toward amber so the gota borders and brass glow.
  - **Skin:** natural warm and protected (use a skin-tone qualifier so the red boost doesn't make his face red).
  - **Blues:** desaturate the steel-blue shirt by −10 so it doesn't compete with the reds and golds.
  - Soft **subject-focus vignette** (oval, about −18% exposure at the edges, feather 60%).
  - **Fake shallow depth of field:** using the speaker matte, apply a 6–10 px lens blur to the BACKGROUND SHELVES ONLY. Do not blur the table or the thalis in front of him, because they are the products. This calms the busy shop wall behind the hero text.
  - Subtle **bloom/glow** on specular highlights (steel karwas, gota sequins) at 10% opacity. It should feel festive without going dreamy.
  - Light film grain, size 0.6, opacity 8%, to unify the footage with the graphics.
- **Pacing:**
  - Cut out every breath, "umm", restart and pause longer than about 0.15 s (tight jump cuts). The raw clip has only two real pauses (10.87 s and 28.70 s), so cut on sentence and phrase boundaries as well, so that **no shot lasts more than 2.5 s.**
  - **Change the framing on every cut.** Standing section: alternate 100% (thigh-up) and 120% (chest-up). Seated locked-off section: rotate between **WIDE 100%** (whole table visible), **MID 125%** (waist-up, top row of thalis visible) and **CLOSE 140%** (chest-up, centred on his face). Always keep his eyes on the upper-third line, at about y = 38–42% after reframing.
  - Add a slow **2–3% push-in** on every shot (linear, the full length of the shot) so the frame is never static. On CLOSE shots, reverse it to a 2% pull-out for variety.
  - Stabilise the handheld section from 0–10.87 s with warp stabilise at 8–10% smoothness, and keep a tiny bit of natural movement.
- **Rule:** the screen must never go **more than about 1.5 s** without a new graphic, caption animation or framing change.
- **Safe zones:** all text and graphics must stay between **8% and 75%** of the frame height (y = 154 px to 1440 px). Keep the **bottom 20%** (below y = 1536 px) clear because the Instagram UI covers it. Keep 64 px side margins, and leave the right 140 px clear between y = 900 and 1500 because the like/comment/share buttons sit there.

---

## 2. COLOUR SYSTEM (re-themed for this footage)

The original reference used cyan, blue and neon-green gradients. Those would clash with this red-and-gold shop. Here is the 1-to-1 replacement. Every effect that used colour X in the reference now uses its replacement.

| Role | Reference colour | **NEW colour for this video** | Hex gradient (top→bottom or left→right) |
|---|---|---|---|
| **Main hero words** | Cyan→electric blue | **Royal Gold** | `#FFE9A8 → #F7B733 → #D98E04` (3-stop, with a slight metallic band at 45%) |
| **Secondary tags / labels** | Neon green | **Mehendi Lime** | `#D4FF4F → #57D45A` |
| **Brand-name word** | Peach→pink | **Rose Sindoor** | `#FFB199 → #FF4F7B → #D1104A` |
| **Emphasis word in a caption line** | Violet→blue | **Festive Magenta** | `#FF5FA2 → #B5179E` |
| **CTA last word** | Cyan→teal | **Saffron Gold** | `#FFD25A → #FF8A00` |
| Caption body text | White | **Warm White** | `#FFF8EE` |
| Text shadow | 35% black | **35% deep maroon** | `#2A0508` @ 35%, 0 4px 12px |
| Chart line / UI strokes | White | Warm White `#FFF8EE` with a gold glow `#FFC34D` @ 40% |
| Ring gradient (counter) | Green→cyan→purple | **Gold→saffron→magenta** | `#FFE08A → #FF9F1C → #E0217A` |

**Contrast rule:** the background behind the hero words (the shelves) is busy and light. Every gradient hero word therefore also gets a **1.5 px inner stroke in `#7A1020` at 40%** plus the maroon drop shadow, so the gold reads clearly against the lavender wall. Check readability on a phone screen at 50% brightness.

---

## 3. TYPOGRAPHY

- **Hero words (big keywords):** extra-bold geometric sans: **Clash Display Bold** (first choice), then Satoshi Black or Poppins ExtraBold. Tracking −2%, size **140–180 px** (scale down to fit inside the 64 px side margins), gradient fill from Section 2.
- **Caption words (spoken subtitles):** **Inter SemiBold** or SF Pro Display Semibold, Warm White `#FFF8EE`, **48–64 px**, no box, soft maroon shadow. Hinglish written as spoken, **all lowercase** (e.g. "aapke liye humne"). Proper nouns are the exception: Karwa Chauth, the shop name and the city.
- **MIXED-SIZE STACK (the key layout rule):** never centre a plain one-line subtitle. Every caption phrase is built as:
  1. a **small Warm White lead-in** (48–56 px) above-left (e.g. "is baar"),
  2. a **huge gradient hero word** (140–180 px) in the middle (e.g. "Karwa Chauth"),
  3. a **small trailing word** (48–56 px) below-right, offset about 80 px right of the hero's left edge (e.g. "ki shopping").
  Lead-in and trailer use Inter SemiBold. The hero uses Clash Display Bold.
- **CTA font:** **Montserrat ExtraBold** (or Bebas Neue), ALL CAPS, Warm White, 96–120 px, tracking +2%. The **last word** gets the **Saffron Gold** gradient.
- **Optional Devanagari accent (nice touch):** one decorative word such as "शुभ" or "करवा चौथ" in **Tiro Devanagari Hindi** or Kalam, Royal Gold, 70 px, 60% opacity, behind the opening hero word. Use it once only, at 0:00–0:03.

---

## 4. MOTION-GRAPHIC TOOLKIT (copy these behaviours exactly)

### A) TEXT BEHIND SUBJECT (signature effect)
- Matte the speaker on every frame with Robust Video Matting or SAM 2. Refine the edges: 1 px choke, 2 px feather, with motion-blur-aware edges on his hands. **On the seated shots the matte must include his body AND any product he is holding**, so the held thali and the box also sit in front of the text.
- Layer order (bottom to top): background plate → **hero text** → speaker/product matte → captions/front graphics → watermark.
- Placement: hero words at **head height**. Standing shots: y ≈ 30–38%. Seated shots: y ≈ 36–44% (after reframing). His head and shoulders should cover the **middle letters** of the word.
- **Entry:** slide in horizontally from the left edge (about 300 px of travel) over **6–8 frames**, ease-out (cubic-bezier 0.16, 1, 0.3, 1), directional motion blur 180° shutter. Then a tiny **2–3% scale settle** over 4 frames. It stays on screen and drifts 1–2 px per frame (about 40 px total) to the right.
- **Exit:** wiped by the next flash transition, or a fast 4-frame fade with a 20 px drift.

### B) WORD-BY-WORD KINETIC CAPTIONS
- Each word appears **exactly on its spoken syllable** (from the Step 1 transcript).
- **Pop-in:** scale **70% → 105% → 100%**, opacity 0→100, Gaussian blur **8 px → 0**, over **4–5 frames**.
- The **trailing small word types on letter by letter** (1 letter per frame).
- **Exit:** fast fade plus a **10 px upward drift** over 3 frames, or wiped away by a transition.
- Default position: just under his chin. Standing shots: y ≈ 48–55%. Seated shots: on his chest at y ≈ 54–62%, over the blue shirt, where white reads well. Never place captions over the red table area below y ≈ 66%.

### C) 3D GLOSSY ICON POP
- App-icon-style **rounded-square 3D icons** (corner radius 28%, bevel, specular highlight top-left, soft contact shadow), about 150×150 px each, 24 px gap.
- **Festive icon set for this shop** (render in 3D, Blender or a Spline-style glossy look):
  1. 🪔 **Diya** (gold body, orange flame, on a deep maroon tile)
  2. 🎁 **Gift box** (red with a gold ribbon, on a gold tile)
  3. 🌙 **Moon + chhalni** (silver crescent seen through a sieve mesh, on a midnight-magenta tile, the core Karwa Chauth symbol)
  - Alternative business set: **WhatsApp**, **Instagram**, **Google Maps pin** (glossy brand-coloured tiles).
- They **drop in from above the frame one at a time, 2–3 frames apart**, with an overshoot bounce (**y overshoot 15 px, settle in 8 frames**) and a **5–10° tilt that straightens** as they land.
- Placement: in a row just above his head (seated: y ≈ 22–28%), centred on his head.
- On landing, add a 6-frame **gold sparkle burst** (8–12 tiny 4-point stars, `#FFE9A8`) behind each icon.
- Exit: scale to 0 with staggered timing, 2 frames apart, from right to left.

### D) FLOATING CARDS
- **Row of 3 product-post cards:** square photo cards (240×240 px, 8 px Warm White border, radius 16 px, soft shadow) showing **stills pulled from this clip**: (1) the gold-rim thali with the chhalni, (2) the steel karwa with the beaded rim, (3) the heart-shaped gota thali. They pop in **staggered left→right** (4 frames apart, scale 0→108→100%), **hover with a ±4 px sine float** (1.2 s period, each offset by 0.3 s), then **shrink to 0 and fade together** over 6 frames.
- **Tall phone-screen thumbnails:** 9:16 cards (300×533 px, radius 32 px, thin 3 px Warm White border, phone notch optional), showing **looping close-up clips** cropped from the footage (product macro crops). They **enter from the LEFT and RIGHT frame edges** at chest height (y ≈ 50%), rotated **±6°** (left card −6°, right card +6°), sliding in over **8 frames with ease-out**, and hold with a ±3 px float. Each has a **Mehendi Lime bold label** above it (Inter ExtraBold 44 px, e.g. "Karwa Thali" / "Chhalni Set").

### E) LOGO BADGE REVEAL
- A **white circular badge** (220 px, 6 px gold `#F7B733` ring) containing the shop logo. If there's no logo yet, use the shop's initials in Clash Display Bold, Rose Sindoor gradient.
- It starts **small (40%) BEHIND the speaker's head**, then **rises up and out above his head** while scaling **40% → 110% → 100%** over **12 frames** with overshoot. A **glossy highlight sweep** (a white diagonal bar at 45%, 60% opacity, 10 frames) crosses it once it lands.
- At the same moment the **brand word** appears **BEHIND him** (Effect A layer) in the **Rose Sindoor** gradient, **revealed letter by letter from the right** (1 letter per 2 frames, each letter fading in with a 6 px blur).

### F) GLASS UI CARD
- A screenshot of the **shop's Instagram profile** (or Google Maps listing with star rating) on a **frosted-glass card**: 760×520 px, radius **24 px**, background blur 30 px, **warm rose-gold tint** (`#FFD8C2` at 18%), 1 px white border at 35%, light inner glow.
- It starts as a **small square behind his head**, then **pops up to the top of the frame** (y ≈ 12–30%) with a **3D perspective tilt (rotateX ≈ 10°, rotateY ≈ −8°)** over 10 frames with overshoot.
- It floats gently (±4 px, rotation ±1°). On exit it **flattens** (rotation → 0), **fades to 0 and shrinks back down** behind his head over 8 frames.

### G) LINE-CHART DRAW-ON
- Thin **Warm White L-shaped axes** (4 px stroke, rounded caps, gold glow) draw on, **vertical then horizontal, 6 frames**.
- A **Warm White zig-zag growth line** then draws **left→right ending in an upward arrow** over **15 frames, ease-in-out**. Small gold dots pop on each vertex (2 frames each).
- Below it, a **white rounded pill label** (radius 999, padding 16×32 px) pops in (scale 0→110→100%, 6 frames) with **Festive Magenta gradient text** (Inter ExtraBold 46 px).
- Position: above his head, y ≈ 14–32%, about 520 px wide, centred.

### H) NUMBER COUNTER + RING
- A large **Warm White bold number** (Clash Display Bold 170 px) **counts 0 → target over about 1 s** (30 frames, ease-out). The digits get a vertical motion blur while rolling.
- Behind it, a **circular ring arc** (360 px diameter, 14 px stroke, round caps) **draws clockwise** in the **Gold→saffron→magenta** gradient, in sync with the count.
- At the end, a small **"₹"** prefix pops in (Royal Gold, 90 px, scale 0→120→100%, 5 frames), with an optional "/-" or "+" suffix.
- A **Warm White caption** sits under it (Inter SemiBold 52 px), e.g. "sirf" / "starting at".

### I) TRANSITIONS
- **Gold light-leak flash** (replaces the reference's blue flash): a **champagne-gold/white burst** (`#FFE9A8` → `#FFFFFF`, with an amber `#FFB000` edge) sweeps **diagonally from bottom-right to top-left**, **peaks at full white for 2–3 frames**, then reveals the next shot. Total about **0.5 s (15 frames)**. Add anamorphic streaks and 10–15 floating gold dust particles in the burst. Use it on **major section changes**.
- **Warm crimson light-leak flash** (for the final CTA section): the same motion but an **orange / pink / crimson film burn** (`#FF8A00`, `#FF4F7B`, `#C2185B`) into white.
- **SFX:** a **whoosh** on every flash, and a soft **pop/click** on every icon, card and badge entrance.

### J) WATERMARK
- Small Warm White **Instagram glyph** (28 px) plus **"@[YOURHANDLE]"** in tiny caps (Inter SemiBold 24 px, tracking +8%, 85% opacity).
- **Top-right** (x = 1080 − 64 px, y = 120 px) for most of the video. **Moves to bottom-left** (x = 64, y ≈ 1400 px, above the safe zone) during the middle section with a 10-frame eased slide, then moves back.

### K) END CARD (last 4–5 s)
- **Pure black** screen. A **white Instagram glyph** (220 px) in the centre.
- The glyph's fill **cross-fades through the Instagram gradient** (`#FEDA75` → `#FA7E1E` → `#D62976` → `#962FBF` → `#4F5BD5`) **and back to white** on a loop of about 2 s.
- **"@[YOURHANDLE]"** in small Warm White caps (Inter SemiBold 40 px, tracking +10%) **fades up 30 px beneath it** (12 frames, starting 0.4 s after the card begins).
- Optional second line at 60% opacity: "[SHOP NAME] • [AREA, CITY]".
- The **watermark stays top-right**.

### L) BONUS EFFECTS (to match the festive theme without breaking the agency look)
- **Product spotlight glow:** when he holds a product up, freeze-zoom 3% with a **Warm White + gold outer-glow outline** (6 px, `#FFE9A8`, glow radius 24 px) traced around the product for **0.5 s**, plus 6–8 twinkling gold sparkles around it.
- **Moon-rise accent (used once):** a small soft-glow crescent moon (`#FFF4D6`, outer glow) rises behind his head at y ≈ 18% during the "Karwa Chauth" hero moment. It drifts up 40 px over 2 s and then fades.

---

## 5. SHOT-BY-SHOT PLAN

Times are **edited-timeline** times (after jump cuts). Source ranges are in ( ) so you can find each shot. Re-time precisely to the transcript; the effect order and density are what matter.

| Edit time | Source | Framing | What to build |
|---|---|---|---|
| **0:00–0:03** | (0.0–3.0) | Standing, 100%, push-in 3% | **Effect A:** "[SHOP NAME]" in huge **Royal Gold** BEHIND his head, sliding in from the left **on frame 1** (no fade from black; the hook must be instant). Optional faint Devanagari "शुभ" behind it. **Effect B:** small Warm White "[lead-in words, e.g. namaste, main]" above-left. A **Mehendi Lime** "[Area / City]" tag (56 px) sits small at the bottom-right of the hero word. Watermark top-right. |
| **0:03–0:06** | (3.0–6.0) | Punch-in 120% chest-up | **Effect C:** 3 glossy 3D icons (🪔 diya, 🎁 gift box, 🌙 moon-chhalni) drop in above his head. Hero word BEHIND him: **"Karwa Chauth"** (Royal Gold), with the moon-rise accent (L). White caption under his chin: "[spoken phrase]". |
| **0:06–0:06.5** | (≈6.0) | — | **Effect I:** gold light-leak flash → cut to the wider shot as he turns toward the thali display. |
| **0:06.5–0:10** | (6.5–10.87) | 100% → 110% | He gestures at and touches the red thalis. **Effect D (row of 3 cards):** product-post cards pop in a row above his head (stills of the best thalis from the seated shot), hover, then pop out. Caption stack: small "[lead-in]" + big **Royal Gold** "[keyword, e.g. thali / collection]" + small "[trailing words]". |
| **0:10–0:10.5** | (10.87–11.37 whip) | — | **Effect I:** gold flash **layered over the existing whip-pan** (the real motion blur helps sell it) → the seated wide shot behind the table. |
| **0:10.5–0:13.5** | (11.4–14.5) | WIDE 100% | **Effect E:** shop logo badge rises from behind his head. "[SHOP NAME / Store]" in **Rose Sindoor** revealed letter by letter behind him. Caption: "[phrase]". **Watermark slides to bottom-left.** |
| **0:13.5–0:17.5** | (14.5–18.5) | MID 125% | **Effect D (phone cards):** left card **"Karwa Thali"**, right card **"Chhalni Set"** (Mehendi Lime labels), each looping a close-up crop of that product from the table. Cards enter from the frame edges at chest height. Caption: "[phrase]". |
| **0:17.5–0:20.5** | (18.5–22.0) | CLOSE 140% | **Effect F:** glass card with the shop's Instagram/Maps profile pops up at the top of the frame. Caption stack: Warm White "[lead-in]" + **Festive Magenta** "[keyword, e.g. designer / handmade / latest]". |
| **0:20.5–0:21** | (≈22.0) | — | **Effect I:** gold flash. |
| **0:21–0:25** | (22.0–26.0) | WIDE 100% | He reaches for and picks up items. **Effect G:** growth chart draws above his head with a pill label: "[e.g. Bestseller / 100+ designs / his actual claim]". **Watermark returns top-right.** |
| **0:25–0:27.5** | (26.0–28.7) | MID 125% → CLOSE on the lift | He holds up the **heart-shaped gota thali**. **Effect L spotlight:** freeze-zoom 3% + Warm White/gold glow outline around the heart thali for 0.5 s, with sparkles. Caption: big Warm White Clash Display "[aur best part]" (110 px) with a small "[subtitle line]" above-right and a "[line]" below-left (mixed-size stack). |
| *(cut)* | (28.70–29.04 silence) | — | Remove the pause with a hard jump cut and a framing change. |
| **0:27.5–0:31** | (29.04–33.0) | WIDE 100% | **Effect H:** counter "0 → [PRICE]" with a "₹" and the gradient ring above his head. Caption under it: "[sirf / starting at …]". If he doesn't say a price, use the value from Section 9, or replace the counter with a "[number] + designs" count. |
| **0:31–0:31.5** | (≈33.0) | — | **Effect I:** **WARM crimson/orange/pink light-leak flash** to white. This marks the start of the CTA section. |
| **0:31.5–0:35** | (33.0–36.5) | MID 125% | He picks up the **boxed karwa gift set**. Caption stack: big Warm White bold "[so agar aap]" types on, small "[trailing words]" right, then the **Royal Gold** hero "[Karwa Chauth shopping]" BEHIND him, with a **glossy 3D gold coin / gift-box icon** popping to its left (Effect C behaviour, single icon). |
| **0:35–0:38.5** | (36.5–42.4) | CLOSE 140% on him + box | **CTA (Effect B timing, CTA font):** "[VISIT US TODAY / CALL NOW]" appears word by word at chest height (y ≈ 55%), last word in the **Saffron Gold** gradient. Small Warm White "[address / landmark / phone]" pops above-right. Glow outline on the box for 0.5 s as it enters. **Hard cut to black** on the last spoken word (cut before 42.4 s if he trails off). |
| **0:38.5–0:43** | — | Black | **Effect K:** black end card, animated Instagram glyph + "@[YOURHANDLE]". |

**Density check:** go through the timeline and confirm there's a new graphic, word pop or framing change at least every 1.5 s. Fill any gap with a punch-in or a small Mehendi Lime tag word.

---

## 6. MASKING AND COMPOSITING NOTES SPECIFIC TO THIS FOOTAGE
- **Seated section (11.4 s onward):** the table and thalis are in the foreground, in front of where the text sits. The text-behind layer only needs to sit behind his **head, shoulders and raised hands**, and must stay above y ≈ 48% so it never runs into the table.
- **Products in hand** (heart thali 26–28.7 s, boxed set 33–42 s): add these objects to the foreground matte so they cover the text and graphics too, which keeps the 3D illusion.
- **Busy shelves:** with the background blur and the inner stroke on the text, the hero words stay readable. If a word still fights the background, add a soft radial darken behind it (black, 15% opacity, 600 px feathered ellipse).
- **TV/CCTV/AC in the top corners:** reduce their brightness by −20% with a soft mask so they don't distract, or cover them with the icons, chart or glass card.
- **Handheld section (0–10.9 s):** track the hero text and icons to his head position (point track on his face) so they stay locked as the camera drifts.

---

## 7. AUDIO
- **Voice:** AI denoise for the shop ambience and fan hum (Adobe Enhance Speech at 60–70% mix, or iZotope RX Voice De-noise). High-pass at 80 Hz, a gentle +2 dB presence lift at 3–4 kHz, de-ess, light compression (3:1, about 4 dB gain reduction), loudness **−14 LUFS integrated**, true peak −1 dBTP.
- **Music:** an upbeat, modern, royalty-free **Indian-fusion pop / festive corporate** beat (dhol or tabla groove under a clean synth pluck, 110–124 BPM). Keep it at **−24 dB under the voice**, duck an extra 3 dB on dense speech, and bring it up to **−18 dB on the end card**. Land the flashes on downbeats where possible.
- **SFX:** a **whoosh** on every flash transition, a soft **pop** on each icon, card and badge, a quiet **tick-tick-tick** during the number counter, a **swoosh** on the chart draw, a light **sparkle/chime** on the product-spotlight glows, and a soft **ghungroo/bell shimmer** on the moon-rise. Keep SFX at about −20 to −16 dB, under the voice.

---

## 8. DELIVERABLE
- **MP4, H.264 High profile, 1080×1920, 30 fps, 16–20 Mbps VBR 2-pass, AAC 320 kbps 48 kHz.** Instagram Reels ready.
- Also export a **clean version without the end card**, and an **SRT** of the captions.
- Before exporting, check that nothing important sits in the bottom 20% or on the right-side button column, that the text is readable on a phone at 50% brightness, and that every caption is in sync to within ±1 frame.

---

## 9. MY DETAILS (fill these in before sending)
- Shop name: `[SHOP NAME]`
- Area / city: `[AREA, CITY]`
- Instagram handle: `@[YOURHANDLE]`
- Logo file: `[attach PNG or "none, use initials"]`
- Price to show in the counter: `[e.g. ₹499]` (only if true)
- Chart pill claim: `[e.g. "Bestseller" / "100+ designs"]`
- CTA line: `[e.g. "VISIT US TODAY" / "CALL NOW: 98xxxxxxx"]`
- Address/landmark line: `[optional]`
