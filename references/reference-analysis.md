# Reading a reference ("make it like this")

Run `python tools/analyze_reference.py ref --out ref_report`, open `reference_sheet.jpg`, then answer the template below.
Be concrete: frame numbers, fractions of the scroll (0..1), sizes relative to the viewport width.

## Template

**1. Format**: frames / fps / duration (from the report). Is it a screen recording (cursor visible, pauses) or a video?

**2. Camera**: one continuous move or cuts? Direction (forward dolly, orbit, pan, tilt, pull-back)? Speed character
(constant, eased)? What passes the lens (foreground objects that hide transitions)? Where does it end?

**3. Chapters** (frame ranges): what changes in each (scene, colour, subject, text).

**4. Text layers**, one line each: content type, position, size (e.g. "headline ~4.7% of width, 2 lines, bottom-left"),
weight, case, when it enters/leaves (fractions of the scroll), how it moves (parallax speed vs the video), special
effects (word-by-word reveal, fade, mask).

**5. UI chrome**: nav layout, button style, cursor, footer columns, closing card.

**6. Palette and type**: dominant colours; serif/sans/mono roles.

**7. Not transferable** (do not copy): the reference's subject, brand, copy, music, footage.

**8. Translate**: map 4 and 5 to `hero.layers` and `hero.timing` in `content.json`; map 2 and 3 to the storyboard legs
in `scenario_pack.py`'s playbook (the camera move is what you re-create, with the user's subject).

## Worked example (a landing-page screen recording, 75 frames at 15 fps = 5 s)

* **Camera:** one continuous forward push through a single scene (no cuts: the analyzer reports none); the foreground
  (dashboard, headrests, a broken beam) slides out of frame and hides the change of subject; ends tilting up into a ceiling.
* **Chapters:** 1-10 composed hero; 10-35 push past the foreground, colour moves from dark to saturated red/teal;
  35-50 close on the subject while a statement enters; 50-66 footer columns appear; 66-75 closing card rises.
* **Layers:** nav (logo left, dark pill menu in small mono uppercase, white button right); paragraph top-right, small
  (~1% of width), last sentence bold; headline bottom-left ~4.7% of width, two lines, Title Case; CTA bottom-right
  (dark box + arrow box); a large statement (~3.7% of width) that **lights up word by word** as the video moves;
  small columns; a closing card.
* **Motion of text:** the video is pinned and the text moves over it at normal scroll speed or faster (parallax); the
  headline leaves faster than the paragraph.
* **Pauses** at frames 16-18 are the person stopping; not design.
* **Translate:** this is the `layers` preset in the template (`hero.timing` holds the fractions).
