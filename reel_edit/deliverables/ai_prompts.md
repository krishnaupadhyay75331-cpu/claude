# AI image / video prompts

**Status of generation in this session**
- **Higgsfield:** 0 credits on the free plan, so nothing was generated.
- **Canva `generate-image`:** 3 images generated before the credit quota ran out. Canva does not expose seeds. The full-resolution files can't be downloaded from the render container because canva.com is blocked there, so the render uses labelled placeholders for these too.
  - S1: Canva media id `MAHZY6nuex4`, https://www.canva.com/M/MAHZY6nuex4
  - Arguing couple and S5a: the jobs were accepted, but their results were never retrieved.
- **Hugging Face Spaces (FLUX):** invocation is disabled for this connector.

To finish the reel, generate the stills below with any generator (Nano Banana, Flux, Midjourney or Imagen). Then save them in `reel_edit/assets/` with the exact file names and run the render again (see `README.md`).

**Consistency:** the client is the same young woman in every still, in a dusty-rose kurta with her hair in a messy bun. Generate S1 first, then pass it as a character reference (or use the same seed) for S2, S3, S4, S5b and S6. Keep her visibly different from the presenter: different face shape, hair up rather than long and loose.

> **Adapted to the real script.** The video is a Jyotish consultation promo, not a relationship-consultant script. The client's problem is "unanswered questions about shaadi, career and future". The prompts below are written for that story.

| File | Beat | Covers (spoken) | Prompt |
|---|---|---|---|
| `S1.png` | B1 Hook, 0.00–1.90 s | "Kya aapke mind mein bhi shaadi, career, ya…" | Cinematic photoreal vertical shot, Indian middle-class living room, warm tungsten and window light, worried young Indian woman early 20s in a dusty-rose cotton kurta, hair in a messy bun, teary eyes, sitting on a beige sofa with hands clasped, looking up confused; worried father in a grey checked shirt and mother in a beige printed saree leaning over her from the left, younger sister and brother leaning over the sofa back from the right, family photo frames on a cream wall, small brass diya on a shelf, sage green cushions, emotional, shallow depth of field, 35mm film look, warm rose-and-sage color grade, empty space above her head, 9:16 |
| `S2.png` | B2, 3.40–5.30 s | "jiska jawab aap kaafi time se dhoondh rahe ho" | Golden-hour Indian bedroom, the same young woman in a dusty-rose kurta sitting cross-legged on a bed with a sage-green block-print bedcover, chin on her hand, lost in thought, open diary and a chai cup in front, sheer curtains, photo pin board, warm lamp glow, melancholic, photoreal, 35mm, empty space top-left, 9:16 |
| `bubble.png` | in S2's thought bubble | (her hoped-for future) | Happy candid selfie of a young Indian couple, girl with wavy hair in a sage top smiling, boy in a white shirt, bright daylight, square crop, photoreal |
| `S4.png` | B3, 5.30–6.37 s | "Kabhi kabhi zaroorat hoti hai" | Front-facing symmetrical shot, the same sad young Indian woman in a dusty-rose kurta sitting on a bed hugging her knees, head bowed, framed family photo and stacked books beside her, warm beige room, soft light, photoreal, 9:16 (the renderer segments her and puts the halo orb behind her head) |
| `S3.png` | B3, 7.40–9.40 s | "ek naye perspective se samajhne ki" | The same young woman in a dusty-rose kurta sitting barefoot on the floor against a cream wall, hugging her knees, looking up with a first hint of hope, harsh golden sunlight with window-blind shadows on the wall, open book and coffee mug on the rug, cinematic, 9:16 |
| `couple.png` | expert card A, 1.90–3.40 s | "…future ko lekar koi aisa sawaal hai" | Full-body Indian couple arguing, woman with hand on hip looking annoyed, man in a white shirt pointing at her, plain white background, studio light (a white background is keyed out and the image converted to B&W automatically) |
| `S5a.png` | B5, 14.97–17.17 s | "kundli vishleshan, face reading" | Close-up of a woman's hand with a thin gold bangle writing on a hand-drawn Vedic kundli birth chart (North Indian diamond grid) in an open notebook, warm wooden desk, stacked books, small brass diya, rudraksha mala, warm lamp light, shallow depth of field, 9:16 |
| `S5b.png` | B5, 17.17–19.83 s | "prashna kundli, ya vastu se related guidance" | Over-the-shoulder from behind a mature Indian woman astrologer in a sage-green saree (face not visible), at a wooden desk across from the same young client in a dusty-rose kurta listening hopefully, kundli papers, brass desk lamp, small Radha-Krishna frame, diya, cream panelled walls with walnut accents, warm cinematic light, 9:16 |
| `S6.mp4` or `S6.png` | B7 happy ending, 30.00–32.87 s | "consultation process ki poori details share kar degi" | Night garden path lit by warm golden vintage lamp posts, lush trees, the same young woman now smiling in a dusty-rose and sage lehenga twirling with her partner in a dark kurta, romantic golden bokeh, cinematic, 9:16 |

**Image-to-video** (Kling / Veo / Runway), optional for every still:
- General: "very slow cinematic dolly-in, subtle parallax, characters breathe and blink slightly, no scene change, 5 seconds"
- S6: "the girl twirls under his raised hand, gentle camera drift, lamp bokeh"

S5b deliberately hides the astrologer's face. Pushpa ji is a real person, and showing an AI-generated face would misrepresent her. If you want her in the reel, use a real photo of her instead.
