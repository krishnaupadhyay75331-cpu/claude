# Custom Edit Prompt for Claude: Presenter in a Purple Saree, Edited in the Reference Style

> **Paste everything below into Claude, together with the raw clip** (`copy_08F0E26B-…-compressed.mov`, 756×1344, 30 fps, 58.87 s, stereo 44.1 kHz).

---

## 0. Your role and the order of work

You are a senior short-form video editor and motion designer. Edit the attached raw talking-head clip into a finished **9:16 Hinglish reel**. Copy the motion graphics, text animation, transitions, overlays and sound design of the reference style described below. Change the **colours** to suit this footage, which is royal purple, rani pink, sindoor red and gold.

Work in this order and don't skip a step:

1. **Transcribe** the clip word by word, with timestamps, in **Roman-script Hinglish**, spelled the way she pronounces it ("kyu", "apko", "hee", "rha"; not formal Hindi).
2. **Work out the niche and the message:** what problem she names, what she offers, any years of experience or client numbers she says, her name if she says it, and the call to action.
3. **Fill in the caption plan.** Use the timeline in section 7: put her real words into every row and choose the HERO word for each stack. Output the plan as a table before you render.
4. **Build the edit** to that plan, using the specs in sections 2–6.
5. **Check it** against the QC list in section 10, then export to section 11.

**Hard rules:**
- **Never invent claims.** Numbers, years, client counts, offers ("first chat free"), her name and her title must come from her speech or from me. If something isn't said, use the fallback given in that row, or put a `[PLACEHOLDER]` in the plan for me to fill. Don't put a made-up figure on screen.
- **Stay in sync.** Every caption word appears on the frame its spoken syllable starts, within ±2 frames.
- **Pacing:** a visual change (cut, transition, text build or overlay) at least every 2 s, and no static frame longer than 3 s.
- Keep her **face clear of graphics.** Only the neon "?", the halo and the depth title may sit near her head, and they go above or behind it, never over the face.

---

## 1. About the footage

- **Shot:** a single locked-off, phone-recorded medium shot, eye-level and slightly high. A woman sits facing the camera with her forearms resting on a **cream faux-fur surface**. She is speaking Hindi/Hinglish to camera.
- **Wardrobe:** a **shiny lilac-purple Banarasi silk saree** with a **deep purple border**, the pallu over her head, a **red blouse with small white dots**, **sindoor** and a red bindi, red lipstick, a gold necklace and earrings, a large gold kundan ring, red and brown bangles, and a pink smartwatch.
- **Background:** a **black-and-white vertically striped curtain** (bright and busy). On the left there's a window with a grey grille and a switchboard. Small yellow marigold pieces sit at the right edge.
- **Gestures to use as edit beats:**
  - She makes **namaste** at about **0:05.5–0:06.3** (a greeting, so treat it as her intro).
  - She makes **namaste again** at about **0:57.9–0:58.8** (her sign-off).
  - She makes **open-palm explaining gestures** throughout, for example around 0:14–0:15, 0:17, 0:20–0:21, 0:33, 0:38 and 0:50.
- **There is a reframe in the source at 0:51.6:** the camera moves, giving a tighter, lower framing for the rest of the clip. **Hide it under a transition** (see the timeline).
- **Speech blocks** (measured from the pauses in the audio; use them to time cuts and caption stacks):

| # | Speech | Pause after |
|---|---|---|
| S1 | 0:00.36–0:03.27 | 0.40 s |
| S2 | 0:03.67–0:04.65 | 0.73 s |
| S3 | 0:05.39–0:06.29 (namaste) | 0.50 s |
| S4 | 0:06.79–0:07.32 | 0.39 s |
| S5 | 0:07.70–0:15.92 (long) | 0.51 s |
| S6 | 0:16.43–0:17.50 | 0.40 s |
| S7 | 0:17.90–0:22.03 | 0.58 s |
| S8 | 0:22.61–0:23.38 | 0.76 s |
| S9 | 0:24.14–0:31.48 (long) | 0.45 s |
| S10 | 0:31.94–0:33.24 | 0.42 s |
| S11 | 0:33.66–0:39.27 | 0.67 s |
| S12 | 0:39.94–0:47.16 (long) | 0.36 s |
| S13 | 0:47.52–0:51.52 | 0.41 s (camera reframe at 51.6) |
| S14 | 0:51.93–0:57.33 | 0.46 s |
| S15 | 0:57.79–0:58.87 (namaste sign-off) | end |

- **Tighten the pauses:** cut each pause down to about **0.15–0.20 s** with jump cuts. The A-roll will then run about **54–55 s**. Shift every timestamp in section 7 earlier to match. The section 7 times are in **source time**, so keep the structure and re-time it.

---

## 2. Colour scheme (taken from her footage)

Every accent in the reference was teal or cyan. In this edit, **replace them** with this palette:

| Token | Hex | Used for |
|---|---|---|
| Plum-black | `#14061A` | bottom gradient, shadows, vignette tint |
| Deep purple | `#5B1A6E` | pill fill, border echo |
| Orchid | `#A645B8` | depth-title gradient start, haze |
| Lilac sheen | `#D9B8E8` | depth-title gradient middle, soft haze |
| Rani pink | `#E8318A` | callout-tag bar, tint pops, pink light leaks |
| Neon magenta glow | `#FF4FD8` (core `#FFE1F7`) | neon question mark |
| Gold | `#E2B65A` (light `#F7DFA0`) | halo, pill stroke, bokeh, film burn, sparkles |
| Sindoor red | `#C8102E` | emphasis only (at most 2 words in the whole video) |
| Cream | `#F3E9DA` | cream flash (matches the fur surface) |
| Caption white | `#FFFFFF` / 90% white | all captions |

**A-roll grade** (do this first, after AI-upscaling the 756×1344 source to 1080×1920 with a detail-preserving upscaler):
- **Separate her from the background** with AI person segmentation, feathered 6 px.
  - **Background (the curtain):** exposure −0.8 EV, saturation −40%, plum tint in the shadows (lift the shadows towards `#2A0F33`), and a 6–8 px Gaussian blur for fake shallow depth of field. The busy stripes should fall into a dark, soft, moody backdrop. This is the equivalent of the reference's dark navy studio.
  - **Subject:** highlights −25 to recover the silk sheen (the saree is close to clipping), whites −10, purple saturation −5, a skin vibrance boost, white balance +3 warm, slight local contrast.
  - Keep **lips, sindoor and blouse red** natural, not oversaturated.
- Add a **vignette** of 25–30%, tinted plum-black.
- **Bottom gradient:** plum-black `#14061A`, 0% opacity at 62% of frame height, 88% at the bottom. It sits over her hands and the fur, and all lower-third captions sit on it.
- **Film grain:** 8%, fine, over everything.

**B-roll grade:** warm amber/tungsten interiors with soft window light, and **characters in plum, maroon or rani-pink kurtas** (instead of the reference's teal) so the B-roll ties to her saree. Shallow depth of field, fine grain, the look of a 35 mm film still.

---

## 3. Framing and camera movement for a single static shot

- **Wide** = the full upscaled frame, scaled to 102% to remove edge softness, with a very slow push-in from 102% to 106% across each A-roll segment.
- **Medium punch-in** = a 1.20× crop centred on her face. Her eyes sit at 30–33% of frame height.
- **Close punch-in** = a 1.35× crop, never more (the source resolution can't take it). This stands in for the reference's "side-profile close-up", which this footage can't give you because there's only one angle. **Offset the crop so her face is on the left third**, add a **1.5° rotation**, and let her open hands show bottom-right when she gestures.
- **Cutting:** jump between wide, medium and close **on sentence breaks or pauses** (the gaps in section 1), never in the middle of a word.
- **Micro-shake on the hit words:** a 6-frame scale bump (100 → 103 → 100%) on the HERO words of the fast montage (S9).
- **Ken Burns on every B-roll still:** a slow push-in from 100% to 108% across the shot, easeInOut. Every other still also drifts 20–40 px sideways.

---

## 4. Typography system (keep this exactly as in the reference; it is the signature look)

### 4.1 Main captions: the "word stack" (most of the edit)
- **Font:** a white, rounded geometric sans with a **single-storey "a"**: **Quicksand Bold** first choice, **Comfortaa Bold** or **Lexend Medium** as alternatives. Tight tracking (−10).
- **HERO word:** 120–140 px (scale it down so the stack fits inside 960 px wide). The first letter is capitalised unless the word looks better all lowercase ("insaan"-style).
- **Small companion words:** the same font, lowercase, 26–32 px, 90% white.
  - **Lead-in words** (spoken before the hero) sit **above-right**, with their baseline touching the top of the hero's x-height.
  - **Trailing words** (spoken after the hero) sit **below-left**, tucked under the hero's left half.
  - At most about 4 small words on each side; split longer phrases into two stacks.
- **Position:** centred horizontally, hero baseline at **72% of frame height**.
- **Shadow:** plum-black `#14061A` drop shadow at 45%, blur 12, distance 0.
- **In animation** (each word on its own spoken timestamp):
  - **Small words:** Gaussian blur 25 → 0, opacity 0 → 100%, rise 8 px, **6 frames**, easeOut.
  - **HERO word:** the same, plus scale 112% → 100%, **8 frames**.
- The words **build up one at a time** in spoken order. The finished stack **holds** until the phrase ends.
- **Out animation:** the whole stack does blur 0 → 20 and opacity 100 → 0 over **4 frames**, then the next stack starts.
- **Choosing the HERO word:** take the most emotional, problem-naming or benefit word in the phrase. In a Hinglish advice niche that's things like Rishta, Pati, Saas, Ghar, Shaadi, Jhagde, Takleef, Dukh, Pareshani, Samadhan, Upay, Shanti, Khushi, Pyaar, Vishwas, Bharosa. Use the word she actually says. The rest of the phrase becomes companion words; leave out filler ("toh", "na", "ki") only if the stack would otherwise be too crowded.
- **Emphasis colour:** in the whole video, at most **2 HERO words** may be filled **sindoor red `#C8102E`** instead of white: the single biggest pain word and the biggest promise word.

### 4.2 Special type treatments (restyled to the new palette)
1. **Depth "behind subject" title** (used once, on B-roll #2; see the timeline).
   - A big, **thin, tall sans** (Josefin Sans Thin or Poppins ExtraLight, about 300 px) with a **vertical gradient orchid `#A645B8` → lilac `#D9B8E8` → white**, at 85% opacity.
   - It sits in the top half, **partly masked behind the B-roll character's head and shoulders** (rotoscope or segment the character).
   - It **wipes in left → right** over 10 frames, then its small white companion words blur-fade in around it.
   - Choose a short question word or the key word from that sentence ("Kya", "Kab", "Kaise", "Kyun", or a noun she uses).
2. **Stat / authority title** (S13).
   - An **ultra-condensed thin** font (**Bebas Neue Thin** or **Antonio Thin**), white, about 330 px tall, at the **top of the frame**, above her head (headroom: shrink the A-roll a little or use the wide framing so the title doesn't touch her pallu).
   - It reveals with a **left → right mask wipe**, 10 frames.
   - A **small script word** in **Great Vibes** or **Allura**, gold `#F7DFA0`, sits above it, centred (for example "Pichhle", "Over", "Sirf").
   - **Content:** her experience or number, **only if she says it** (for example "15 SAAL", "5000+"). If she doesn't, use the strongest single claim word she *does* say, set the same way (for example "ANUBHAV", "SAMADHAN"), and add `[PLACEHOLDER: number?]` to the plan.
3. **Pill label.**
   - White Quicksand Bold, about 52 px, on a solid **deep-purple `#5B1A6E` rounded rectangle**: corner radius 10, **1.5 px gold `#E2B65A` stroke**, 18 px horizontal padding.
   - It reveals with a **left → right mask wipe**, 8 frames, at the lower third.
   - A white **script italic** word (Great Vibes) fades in just above it.
   - It's used in three places:
     - **(a)** the intro (S3/S4): script "Namaste" above a pill with her name/title (if she says it), otherwise `[PLACEHOLDER: name/title]`
     - **(b)** the authority section (S13): the supporting line, for example "clients" over "More than [N]"
     - **(c)** the CTA: a small pill (about 34 px text) under the CTA line, for example "first WhatsApp chat free", **only if offered**
4. **Glowing callout tags** (S12, on the consultation B-roll).
   - White Quicksand Bold, about 44 px, on a **rani-pink `#E8318A` bar**. The bar fades to transparent along its right 40% and has a soft outer glow (`#FF4FD8`, 25 px, 50%).
   - Each tag **slides in from the left with motion blur** (8 frames, easeOut) and is joined to a point in the scene (the consultant's hand or notebook) by a thin white **leader line**, which draws on over 6 frames.
   - **Two tags stack**, the second 6 frames after the first.
   - Use the two services or remedies she names ("Upay" / "Margdarshan", "Remedies" / "Guidance", "Kundli" / "Vastu", whatever she actually says).
5. **CTA line:** **"Click the link Below"** (or her own Hinglish CTA if she says one, for example "Neeche link pe click karein"), inside curly quotes, Quicksand Bold, about 80 px, lower third. It **builds word by word** with the blur-fade.

### 4.3 Caption spelling style
Roman Hinglish, casual and phonetic: lowercase small words, no full stops, "??" allowed for questions, "..." allowed for trailing thoughts. Write it the way she pronounces it.

---

## 5. Motion-graphic elements and overlays (PNG/MOV assets)

Build each one as a separate layer, or source it as a PNG/MOV overlay with alpha.

| Element | Spec (restyled) | Where |
|---|---|---|
| **Neon question mark** | Outline-only "?" in the style of a neon tube: core `#FFE1F7`, glow `#FF4FD8`, outer glow radius 40, inner glow 8. **Pops in** with scale 0 → 120 → 100% (overshoot, 10 frames) and a **2-flicker turn-on** (opacity 100/20/100/40/100 over 5 frames). It then **bobs** ±10 px on a 1.5 s sine wave. It **stays on screen across the cut** from B-roll #1 into her A-roll, sitting above her head (clear of the pallu). About 7 s total, then it flickers off | S1 → S2 |
| **Side cut-outs** | **Black-and-white** cut-outs of an Indian couple arguing: a woman (arms crossed, annoyed) on the left and a man (pointing) on the right, 70% of frame height, behind her (layer them between the darkened background and her segmented body). They **slide in** from off-screen left and right, 12 frames, easeOut, with a soft shadow. They leave with a blur-fade at the end of S2/S4. *If her topic isn't couple conflict, choose cut-outs that act out her problem* (for example a saas–bahu argument, or a stressed parent and child) | S2–S4 |
| **Watercolour memory bubble** | Above the B-roll character's head, **5–6 irregular ink/watercolour blobs** (lilac `#D9B8E8` and grey-purple) pop in one after another, 3 frames apart. Together they form a **cloud-shaped mask** that reveals a **happy memory photo** inside (a smiling couple or family). It holds about 2 s, then the blobs **bleed and dissolve** outward over 12 frames | S5 (B-roll #2) |
| **Halo glow** | A **warm gold glowing disc** (`#FFE7B0` centre, `#E2B65A` outer ring, bloom 60 px) **grows from 0 to full size** behind the character's head over 15 frames (character segmented so the halo sits behind her). It then holds with a very slight ±3% pulse every 2 s | S10 (B-roll #4) |
| **Wall light leak** | On the wall behind the character, a **gold-to-rani-pink fire-like light leak** fades in and **flickers organically** (screen blend mode, 60%) | S7 (B-roll #3) |
| **Namaste sparkle** | A tiny gold sparkle burst (6–8 four-point stars, `#F7DFA0`, 12 frames) at her joined hands when she does namaste. This is new, but it uses the reference's "sparkle/ding" moment | S3 and S15 |
| **Paper-texture white flash** | A pure white frame with faint grey dust specks and a paper-fibre texture | Transitions |
| **Bokeh overlay** | Gold and pink bokeh circles (`#F7DFA0` and `#FF8FC8`) | Transitions |
| **Film burn / light leaks** | Gold-orange and magenta-pink light leaks | Transitions |
| **Haze/smoke** | **Lilac-rose haze** (`#E7C6EE`), replacing the reference's teal fog | Transitions |

---

## 6. Transition set (same mechanics as the reference, recoloured)

1. **White flash with paper texture** (the main transition): cut to white with specks for **3–6 frames**, then fade into the next shot through a **lilac-rose haze dissolve** (6–8 frames of `#E7C6EE` smoke clearing).
2. **Bokeh transition:** gold/pink bokeh floods in over 4 frames, **flashes white**, then reveals the next shot.
3. **Cream flash:** **1–2 frames** of solid `#F3E9DA` between B-roll and A-roll.
4. **Tint pop:** a **2–3 frame** overlay on the first frames of a new A-roll shot or on a beat. Alternate **purple `#8E3FA8` at 60%** and **rani pink `#E8318A` at 55%**.
5. **Film burn / light leak:** a **gold-orange** or **magenta-pink** leak sweeps across, burns to near-white, then reveals the next shot.
6. **Zoom-blur whip:** an extreme radial zoom blur into silk-saree texture or skin, 4 frames, then the next shot starts tight and **zooms out quickly** (180% → 100% in about 20 frames, easeOut).
7. **Light-burst flare:** a **warm-white/gold bloom flare** grows from the bottom-right, over-exposes to white, then cuts.

---

## 7. Shot-by-shot timeline for this clip (source timestamps; re-time after tightening the pauses)

`[S#]` refers to the speech blocks in section 1. Her voice runs **continuously under everything**, including the B-roll (B-roll is cutaway with her voice over it).

| Source time | Speech | Picture | Graphics / text | Transition out |
|---|---|---|---|---|
| 0:00.00–0:03.27 | S1 (hook) | **B-roll #1**, a problem scene (an emotional family moment; see section 8). The camera drifts right and down towards the troubled character | 0:00.8: the **neon "?"** pops in above the character's head and bobs. One word stack built from S1's key words; place the hero at **72% height**, or at **25% height** if it would cover the character | **Cream flash** (in the 0:03.27 pause) |
| 0:03.27–0:05.39 | S2 | **A-roll wide**, with a **purple tint pop** on the first 3 frames | The **neon "?"** carries over above her head. The **B&W cut-outs** slide in left and right. A word stack from S2 | Hard cut in the pause |
| 0:05.39–0:07.70 | S3 + S4 (namaste / intro) | **A-roll medium punch-in** (1.20×) | A **gold sparkle** at the namaste hands. The **intro pill**: script "Namaste" above a pill with her name/title, from what she says, else `[PLACEHOLDER]`. The cut-outs and "?" blur out | **White flash → lilac haze** (in the 0:07.32–0:07.70 pause) |
| 0:07.70–≈0:11.5 | S5, first half | **B-roll #2** (a character alone, lost in thought, chin on hand by a window) | **Watercolour memory bubble** (0:08.0–0:10.0), then the **depth title** behind the character's head, with S5's key word and companion words around it | **White flash** at the word gap nearest 0:11.5 |
| ≈0:11.5–0:15.92 | S5, second half | **A-roll close punch-in** (1.35×, face on the left third, 1.5° tilt), entering through a short lilac blur | Either 1–2 word stacks, or **no text for the first 2 s ("let it breathe")** if the line is emotional. Use your judgement; keep the rhythm | Jump cut in the pause |
| 0:15.92–0:17.90 | S6 | **A-roll wide** | 1 word stack | Hard cut |
| 0:17.90–≈0:20.0 | S7, first half | **A-roll medium** | Small words first, then the hero, as in the reference's "sbh kush theek → kab hoga" (a small-text line resolving into a big word) | **Bokeh → white** at the word gap nearest 0:20.0 |
| ≈0:20.0–0:22.03 | S7, second half | **B-roll #3** (a character on the floor against a wall, hugging her knees, looking up hopefully) | The **gold/pink wall light leak** flickers. Push-in. No captions | **Pink light leak → pink flash** |
| 0:22.03–0:24.14 | S8 | **A-roll close punch-in**, with a **rani-pink tint pop** | A single big HERO word (one of the 2 allowed red-emphasis words, if it's the pain word) | Jump cut |
| 0:24.14–0:31.48 | S9 (fast montage) | **A-roll medium**, with a jump cut to **wide** at the sentence break nearest 0:28 | **Fast stacks, about 1.2–1.4 s each (about 5 stacks)**, each hero with a micro-shake bump. This is the reference's "Relationship → Jagde → insaan → Reason → Solution" run, using her words | **Zoom-blur whip** into the saree texture |
| 0:31.48–0:33.66 | S10 | **B-roll #4** (a character on a bed hugging her knees, head bowed, symmetrical). It starts tight and quickly **zooms out** | 0:32.2: the **gold halo** grows behind the character's head | **White flash → lilac haze** |
| 0:33.66–≈0:36.5 | S11, first half ("why it happens") | **A-roll wide** | 2 word stacks | Cut at the word gap |
| ≈0:36.5–0:39.94 | S11, second half | **A-roll close punch-in** (face on the left third) | 2 word stacks. This is where she says why she understands the problem, like the reference's "Pehle… / apki problem properly smjta hu" | Cut |
| 0:39.94–≈0:41.0 | S12, start | **B-roll insert #5**: close-up of a woman's hands with gold rings and red bangles writing in a consultation notebook or chart | — | Cut |
| ≈0:41.0–0:47.16 | S12, rest | **B-roll #6**: an over-the-shoulder consultation. **A woman consultant in a purple silk saree, seen from behind or over her shoulder (face not shown)**, sits across a wooden desk from a worried client. Slow push-in | A hero stack built at the **top of the frame** (25% height) from her "problem / cause" words, which then blurs out. At about 0:45.0, the **two rani-pink callout tags** with her services/remedies slide in, with leader lines to the consultant's hand | **Light-burst flare → white** |
| 0:47.52–0:51.52 | S13 (authority) | **A-roll wide** (headroom for the title) | The **stat title** wipes in at the top with a gold script word above it. The **pill** wipes in at the lower third with a script word above it. A **purple tint pop** at 0:51.2. *Only real numbers; otherwise use the fallback in section 4.2* | **Gold-orange film burn**, timed to **cover the camera reframe at 0:51.6** |
| 0:51.52–≈0:54.0 | S14, first half | **B-roll #7, live-action video:** the happy ending (see section 8), warm golden lights | No captions; let the music lift | **Bokeh → white** at the word gap nearest 0:54.0 |
| ≈0:54.0–0:57.33 | S14, second half | **A-roll** in the **new tighter source framing** (from 0:51.6), with a slight 1.05 → 1.08 push | A word stack, the reference's "Baat / abb deri kis / ki hee..." moment (an urgency line) | Cut on the word |
| 0:57.33–end | S15 (namaste sign-off) + CTA | **A-roll**, same framing. When the speech ends, **freeze-frame her namaste** and hold for **2.0 s** with a slow push-in from 100% to 104% so the CTA can be read (final runtime about 57–58 s after tightening) | A **gold sparkle** at the hands. **"Click the link Below"** builds word by word. Then, 0.6 s later, the **small purple/gold pill** with the offer, only if she offers one | Fade out over 6 frames |

If the transcript shows the content is structured differently (for example the hook is in S1–S2 and the problem montage starts earlier), keep this **order of beats**: hook with B-roll → intro (namaste) → problem montage → "why it happens" → her method/services → authority → happy-ending B-roll → CTA. Move the treatments with their beats.

---

## 8. B-roll generation prompts

Common style for all of them: photoreal, 9:16, cinematic, warm tungsten and window light, shallow depth of field, 35 mm film grain, Indian home interiors, **plum/maroon/rani-pink wardrobe accents**.

Adapt the scenes to her niche once you have the transcript. The defaults below assume a **family / marriage / relationship advice** niche.

1. **B-roll #1 (hook):** "An Indian family in a cosy apartment living room. Mother-in-law in a beige saree, husband and other relatives standing around and leaning towards a young married woman in a maroon kurta with sindoor, who sits on a sofa crying with her hands clasped. Family photos on the wall, warm window light, cinematic, photoreal."
2. **B-roll #2 (lost in thought):** "A young Indian married woman in a plum kurta sits cross-legged on a bed with her chin on her hand, staring sadly out of a curtained window. Warm bedside lamp, an open diary and a cup of chai beside her, a photo frame of a couple on the side table, golden-hour light."
3. **B-roll #2 memory photo** (inside the watercolour bubble): "A happy young Indian couple taking a selfie, smiling, bright daylight, warm."
4. **B-roll #3 (hopeful):** "A young Indian woman in a rani-pink kurta and dark pants sits on the floor against a beige wall, hugging her knees and looking up hopefully. Light patterns from window blinds on the wall, books and a chai cup on the rug, warm cinematic light."
5. **B-roll #4 (low point):** "A young Indian woman in a maroon kurta sits on a bed hugging her knees with her head bowed. Open books and a framed family photo around her, symmetrical composition, warm moody light."
6. **B-roll insert #5:** "Close-up of an Indian woman's hands, with gold kundan rings and red and brown bangles, writing with a pen in a consultation notebook beside a chart on a wooden desk, under warm lamp light."
7. **B-roll #6 (consultation):** "Over-the-shoulder shot from behind a woman consultant in a shiny lilac-purple silk saree with the pallu over her head (face not visible), sitting at a wooden desk across from a worried young Indian woman who is listening. Brass diya and lamp on the desk, notebook, marigolds, a dark plum-toned wall with a bookshelf, moody warm light."
8. **B-roll #7 (happy ending, video 2–3 s):** "Night: a happy young Indian couple laughing and dancing on a garden path under warm glowing string lights and lamps. He twirls her and her rani-pink lehenga swirls. Bokeh, golden light, handheld." (Alternative for a family niche: "a joyful Indian family celebrating together at a festive evening gathering, diyas and fairy lights".)
9. **Side cut-outs (PNG, transparent background, black and white):** "A young Indian woman with arms crossed looking annoyed" and "A young Indian man in a white shirt pointing angrily", both full body down to the knees, isolated.

**Don't generate a likeness of the presenter herself.** In the consultation B-roll, show her only from behind or as hands.

---

## 9. Sound design

- **Music bed:** soft, emotional **Indian-flavoured piano and ambient** (light santoor or flute textures are welcome) at about **−22 dB under her voice**, with sidechain ducking (−8 dB when she speaks).
  - **Hook to montage (0:00–0:31):** sparse and melancholic.
  - **From the authority section (0:47):** a slight swell.
  - **Happy-ending B-roll:** resolves warmly.
  - **CTA:** soft and confident.
- **SFX** (every one is subtle, peaking at −14 to −18 dB):
  - a **whoosh** on every transition
  - a **camera-flash/shutter "hit"** on every white flash
  - a **soft shimmer/ding** when the neon "?" pops, plus a quiet electric **neon buzz/flicker** on its turn-on
  - a **gentle temple-bell / sparkle chime** on both namaste sparkles (a new touch that fits her)
  - soft **pops/clicks** when each pill and callout tag lands
  - a **paper/ink "bloop"** for each watercolour blob
  - a **warm swell** under the halo
  - a short **riser** into the stat reveal (just before 0:47.5)
  - a **soft sub-boom** when the stat title lands
  - a **tape-stop or whoosh-in** on the zoom-blur whip
- **Voice:** apply a high-pass at 80 Hz, a gentle de-esser, 3:1 compression, and a light room-tone reduction (she's in a reverberant room). Normalise the finished mix to **−14 LUFS integrated, −1 dBTP**. The source is hot (about −11 LUFS), so bring it down and don't let it clip.

---

## 10. QC checklist before export

- [ ] Every caption is in sync with the speech (±2 frames) and spelled phonetically in Hinglish.
- [ ] No on-screen number, name or offer appears that she didn't say (placeholders flagged to me).
- [ ] Her face is never covered. The neon "?" and the stat title sit clear of her pallu.
- [ ] The camera reframe at 0:51.6 is completely hidden by the film burn.
- [ ] No punch-in goes beyond 1.35× and nothing looks soft or blocky.
- [ ] The curtain background is darkened and blurred, and no busy bright stripes pull focus.
- [ ] Every accent colour comes from the section 2 palette, and no teal or cyan is left over from the reference.
- [ ] A visual change at least every 2 s, and no static frame longer than 3 s.
- [ ] All text sits inside the safe zone: 150 px from the top, 320 px from the bottom, 60 px from the sides.
- [ ] Audio is at −14 LUFS with no clipping, and the music ducks under every word.

## 11. Export and deliverables

- **Video:** H.264 MP4, 1080×1920, 30 fps, 14–16 Mbps VBR, AAC 320 kbps stereo, Rec.709.
- **Also deliver:**
  1. the filled-in caption plan table (time · speech · hero word · companion words · treatment)
  2. a list of every placeholder I need to confirm
  3. the project/source files, if you built the edit in code or a timeline.
