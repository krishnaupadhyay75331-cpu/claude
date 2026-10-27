# Edit Prompt: Hinglish Advice Reel with Cinematic B-roll and Kinetic Text

## 1. What to make
A 9:16 vertical reel (1080×1920, 30 fps, about 60 seconds) for Instagram Reels or YouTube Shorts. It's an emotional problem → solution ad for a consultant (relationship, astrology or family-advice niche), spoken in Hinglish.
Structure: **talking-head A-roll** cut together with **cinematic, photoreal B-roll** that acts out the problem. The **kinetic word-stack captions** carry the whole edit. The pacing is fast: a cut, transition or text change about every 1–2 seconds, and never a static frame longer than 3 s.

**A-roll source:** my raw talking-head clip (the presenter sits facing the camera on a fluffy cream surface, with a striped curtain behind).
**B-roll:** generate it (prompts are in section 7) or use stock that matches the descriptions.

---

## 2. Global look
- **A-roll grade:** moody and cinematic. Lift the shadows slightly, then crush the blacks. Pull the saturation down about 15% and cool the background (teal/navy). Keep skin tones warm and natural.
- **Bottom gradient:** a black linear gradient covers the bottom 35% of every A-roll shot, going from 0% opacity at 65% of frame height to about 85% at the bottom. Captions sit on top of it.
- **Vignette** on every shot, about 25%.
- **B-roll grade:** warm amber/tungsten interiors (orange lamps, soft window light) with deep teal clothing as the contrast colour. It should look like a film still: shallow depth of field and fine grain.
- Add **fine film grain** over the whole edit (about 8%).
- **Ken Burns on every still:** a slow push-in from 100% to 108% across the shot's length, with an easeInOut curve. Some shots drift sideways a little.
- **A-roll framing:** alternate a **wide/medium shot** (presenter centred, head in the top third) with **punch-in close-ups**. A close-up is a 1.5–1.7× crop, sometimes reframed to a side-profile angle. Cut between them on sentence breaks, as jump cuts.

---

## 3. Typography system (the signature look)
**Main caption style: the "word stack"**
- One **HERO keyword** per phrase. Use a white, rounded geometric sans with a single-storey "a" (Quicksand Bold, Comfortaa Bold or Lexend Medium), at about 120–140 px, with tight tracking.
- **Small companion words** are lowercase in the same font at about 26–32 px, in white at 90%. They go **above-right** (the lead-in words) and **below-left** (the trailing words) of the hero word, tucked tight against it.
- **Position:** centred horizontally, with the baseline at about 72% of frame height (the lower third, over the gradient).
- **Shadow:** a soft black drop shadow at 40%, with blur 12 and distance 0.
- **In animation, synced word by word to the speech:**
  - Each small word **blur-fades in**: Gaussian blur goes from 25 to 0, opacity from 0 to 100, and it rises 8 px. It takes about 6 frames on an easeOut curve.
  - The hero word does the same, plus a scale from 112% to 100% over about 8 frames.
  - The words build up one at a time in the order they're spoken. The finished stack holds until the phrase ends.
- **Out animation:** the whole stack blurs out (blur 0 → 20, opacity 100 → 0) over about 4 frames, then the next stack builds.
- Example layouts from the reference: small "partner" above **Aapka**. **Door** with "kyu ho rha" above and "dheere dheere apse" below. **Reason** with "na hi apko asli" above and "samaj aa rha hai" below. **Solution** with "naa hi koe clear" above.

**Special type treatments:**
1. **Depth "behind subject" title.** A big, thin, tall sans word (about 300 px) with a **steel-blue → white vertical gradient** at 85% opacity. It sits in the top half, partly **masked behind the subject's head and shoulders** (rotoscope the subject). It wipes in from the left and adds its small white words around it. In the reference this is "Kya", with "relationship" and "bachega ja nhi".
2. **Stat title.** An ultra-condensed thin font (Bebas Neue Thin or Antonio Thin) in white, about 330 px tall, at the **top of the frame**. It reveals with a left → right mask wipe over 10 frames. A small **script word** in Great Vibes or Allura sits above it, centred. In the reference this is "10 SAAL", with the script word "Pishle".
3. **Pill label.** White sans text on a **solid emerald/teal rounded rectangle** (#18A38A, corner radius 8). It reveals with a left → right mask wipe in about 8 frames, at the lower third. A white **script italic** word fades in just above it ("couples" over "More than 3000"). There is also a small version of the pill under the CTA ("first whatsapp chat is free").
4. **Glowing callout tags.** White text on a **bright neon-cyan bar** (#2EF2E0). The bar fades to transparent on its right end and has a soft outer glow. Each tag **slides in from the left with motion blur** (8 frames, easeOut) and connects to a point in the scene with a thin white **leader line** (for example, the consultant's hand). Two tags stack, the second 6 frames after the first. In the reference they read "Remedies" and "Guidance".
5. **CTA text:** **"Click the link Below"**, inside curly quotes, in the same rounded sans at about 80 px, at the lower third. It builds word by word with the blur-fade.

---

## 4. Motion-graphic elements
- **Neon question mark:** an outline-only "?" drawn as a **blue neon tube** (core #BFE9FF, glow #2D9BFF, outer glow radius about 40). It **pops in above the subject's head** (scale 0 → 120 → 100%, overshoot, 10 frames) with a 2-flicker neon turn-on. Then it **floats/bobs** ±10 px on a 1.5 s sine and stays up for about 7 s, **staying on screen across the cut** from B-roll to A-roll.
- **Side cut-outs:** **black-and-white cut-outs** of an arguing couple: a woman with arms crossed on the left and a man pointing on the right. They sit at the frame edges behind the presenter at about 70% height and **slide in from off-screen** left and right (12 frames, easeOut) with a soft shadow.
- **Watercolour memory bubble:** above the sad character's head, **ink/watercolour blobs pop in one after another** (5–6 irregular teal-grey splotches, 3 frames apart). Together they form a cloud-shaped mask that reveals a **happy couple selfie** inside. It holds about 2 s, then the blobs **bleed and dissolve** outward.
- **Halo glow:** a **pale-cyan glowing disc** (#CFF6FF, with a soft outer ring and bloom) **grows from 0 to full size behind the character's head** over 15 frames (rotoscope the character so the disc sits behind her). Then it holds and pulses very slightly.
- **Wall light leak:** on the wall behind the character, an **orange-red, fire-like light leak** fades in and flickers organically (screen blend mode, 60%).

---

## 5. Transitions (use these exactly; they repeat)
1. **White flash with paper texture** (the main one): a cut to pure white with a few grey dust specks for 3–6 frames, then a fade into the next shot. It often fades out through a **teal fog/smoke dissolve** (6–8 frames of teal-green haze clearing).
2. **Bokeh transition:** a teal-white **bokeh circles** overlay floods in over 4 frames, flashes white, then reveals the next shot.
3. **Cream flash:** 1–2 frames of solid #F6DFB4 between B-roll and A-roll.
4. **Purple tint pop:** a 2–3 frame magenta/purple colour overlay (#8E3FA8, 60%) on the first frames of a new A-roll shot or on a beat.
5. **Film burn / light leak:** an orange-yellow or **pink-magenta** light leak sweeps across and burns to near-white, then reveals the next shot.
6. **Zoom-blur whip:** an extreme radial zoom blur into a skin or fabric texture, 4 frames, then the next shot starts tight and **zooms out quickly** (180% → 100% in about 20 frames, easeOut).
7. **Light-burst flare:** a white bloom flare grows from the bottom-right, over-exposes to white, then cuts.

---

## 6. Shot-by-shot timeline (match this rhythm)
| Time | Shot | Graphics / text | Transition out |
|---|---|---|---|
| 0:00–0:03.3 | **B-roll:** worried Indian family (father, mother in a saree, sister, brother) leaning over a young woman crying on a navy sofa. The camera drifts right and down, from the parents to the girl | 0:00.8: **neon "?"** pops in above the girl's head and floats | Cream flash |
| 0:03.3–0:07.4 | **A-roll wide** (purple tint pop on the first frames) | The neon "?" stays above the presenter's head. **B&W arguing-couple cut-outs** slide in left and right. Word stacks: *Aapka* (partner) → *Badal* (kyu gya??) → *Door* (kyu ho rha / dheere dheere apse) | White flash → teal fog |
| 0:07.4–0:12.0 | **B-roll:** a girl sitting on a bed with her chin on her hand, looking out a window, with warm lamp light, an open diary and tea | **Watercolour memory bubble** with a happy couple selfie (0:08–0:10.3). Then the **depth title** *Kya* in the blue gradient, partly behind her head (relationship / bachega ja nhi) | White flash |
| 0:12.0–0:18.7 | **A-roll extreme close-up, side profile** (punch-in), entering through a teal blur | No text: let it breathe | Hard cut |
| 0:18.7–0:20.1 | **A-roll wide** | *sbh kush theek* (small) → hero *kab hoga* | Bokeh → white |
| 0:20.1–0:22.6 | **B-roll:** a girl sitting on the floor against a wall, hugging her knees and looking up hopefully, with books and tea on the rug | An **orange light leak** flickers on the wall. Push-in | Pink light leak → pink flash |
| 0:22.6–0:30.6 | **A-roll medium** | Fast stacks, about 1.3 s each: *Relationship* (mein distance) → *Jagde* (baat baat pe) → *insaan* (or ab tesra) → *Reason* (na hi apko asli / samaj aa rha hai) → *Solution* (naa hi koe clear) | Zoom-blur whip |
| 0:30.6–0:34.2 | **B-roll:** a girl sitting on a bed hugging her knees, looking down, with books around her. Quick **zoom out** from a tight shot | 0:32: the **cyan halo** grows behind her head | White flash → teal fog |
| 0:34.2–0:37.0 | **A-roll wide** | *Problem* (Dekhiye / tabb hoti) → *Reason* (Jab koe / clear) | Cut |
| 0:37.0–0:41.0 | **A-roll close-up, side profile** | *Pehle* (Isliyee sabse / mein) → *problem* (apki / properly smjta hu) | Cut |
| 0:41.0–0:42.0 | **B-roll insert:** close-up of a hand writing on a chart / consultation notes on a wooden desk | — | Cut |
| 0:42.0–0:48.5 | **B-roll:** the consultant (a man in a black shirt) and a woman client in teal at a wooden desk, with a brass lamp, a globe and a dark navy bookshelf. Slow push-in | The hero *Problem* builds at the **top of the frame** (kis wajah se / se aa rhi hai), then blurs out. 0:46.5: **cyan callout tags** "Remedies", then "Guidance", slide in with leader lines | Light-burst flare → white |
| 0:48.5–0:53.6 | **A-roll medium** | The **stat title** *10 SAAL* wipes in at the top with the script word "Pishle". The **pill** "More than 3000" wipes in at the lower third, then the script word "couples" appears above it. A purple tint pop at 0:53.4 | Orange film burn |
| 0:53.6–0:56.4 | **B-roll live-action video:** a happy couple dancing at night under warm street lamps in a garden (he twirls her) | — | Bokeh → white |
| 0:56.4–0:58.6 | **A-roll punch-in, medium close-up** | *Baat* (abb deri kis / ki hee...) | Cut on the word |
| 0:58.6–1:03 | **A-roll** (same framing) | **"Click the link Below"** builds word by word. At 1:01 the small teal **pill** "first whatsapp chat is free" wipes in below it. Hold to the end | End |

**Using my footage:** keep the timeline above, but **replace the caption words with the keywords from my speech**. For each sentence, pick the most emotional or important word as the HERO and put the words around it as small companions. If my clip is shorter or longer, scale the sections proportionally. Keep the order hook → problem montage → "why it happens" → authority/stat → happy-ending B-roll → CTA.

---

## 7. B-roll generation prompts (photoreal, 9:16, cinematic, warm tungsten light, shallow DOF, 35mm film look)
1. "An Indian family in a cosy apartment living room: the father in a checked shirt, the mother in a beige saree, a sister and brother leaning over the back of a navy sofa, all looking with concern at a young woman in a teal kurta who sits crying with her hands clasped. Family photos on the wall, warm window light, cinematic, photoreal."
2. "A young Indian woman in a teal kurta sits cross-legged on a bed with her chin resting on her hand, looking sadly out of a window with curtains. Warm bedside lamp, an open diary and a cup of tea on the bed, a cork board with photos, golden-hour light, photoreal."
3. "A young Indian woman in a teal top and black pants sits on the floor against a beige wall, hugging her knees and looking up hopefully. Window-blind light patterns on the wall, books and a tea cup on the rug, warm cinematic light."
4. "A young Indian woman sits on a bed hugging her knees, head bowed. Open books and a framed photo around her, symmetrical composition, warm moody light."
5. "Close-up of a man's hand writing with a pen on a chart and consultation notes on a wooden desk, warm lamp light."
6. "A bearded Indian consultant with glasses, in a black striped shirt, sits at a dark wooden desk across from a woman in a teal kurta, explaining. Brass desk lamp, antique globe, palmistry hand model, dark navy bookshelf with brass ornaments, moody cinematic light."
7. "Night: a happy young Indian couple dancing in a garden path under warm glowing street lamps. He twirls her and her teal lehenga swirls. Bokeh, warm golden light, handheld" (video, 3 s)
8. "A cute happy young Indian couple taking a selfie, smiling, bright." (for the memory bubble)
9. "Black-and-white cut-outs, transparent background: a young woman with arms crossed looking annoyed, and a young man in a white t-shirt pointing angrily." (side cut-outs)

---

## 8. Sound design
- **Music:** a soft emotional piano/ambient bed under the voice at about −22 dB. It swells slightly at the stat/authority section and resolves warmly at the dancing B-roll.
- **SFX:** a **whoosh** on every transition, a **camera-flash/shutter "hit"** on every white flash, a **sparkle/ding** when the neon "?" pops, soft **pops/clicks** for the pill and cyan tags, a **riser** before 0:48 (the stat reveal) and a soft **boom** when "10 SAAL" lands.
- Keep the voice clean and compressed. Duck the music under speech.

## 9. Export
H.264 MP4, 1080×1920, 30 fps, 12–16 Mbps, AAC 320 kbps. Keep all text inside the safe zone (150 px from the top, 300 px from the bottom, 60 px from the sides) so the platform UI doesn't cover it.
