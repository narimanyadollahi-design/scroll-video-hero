# scroll-video-hero

**English** · [فارسی](README.fa.md)

**Scroll motion for any business.** The camera moves as the visitor scrolls: one continuous move, no cuts, wrapped in a
landing page (nav, headline, a statement that lights up word by word, a closing card).

It is a Claude Code skill plus the tools it drives:

1. **Understands what you have**: a reference you like ("make it like this video"), only an idea, nothing yet, or finished clips.
2. **Designs the scenario and writes the prompts** (stills + chained video prompts) for Veo/Flow, Kling, Runway, Sora, Higgsfield...
3. **Repairs and assembles your clips** into one seamless master: measures every seam, tells you which fix applies, fixes jumps,
   stalls and damaged frames, lets you review by frame number.
4. **Builds the page** (Next.js + GSAP + Tailwind template) and an **offline USB package**.

> AI video models do not honour end frames, so separately generated clips almost never meet. The tools measure each seam and
> tell you whether to cut, bridge, generate a gap clip, or regenerate from the last frame, instead of guessing.

## Install as a Claude Code skill

```bash
git clone https://github.com/narimanyadollahi-design/scroll-video-hero ~/.claude/skills/scroll-video-hero
pip install -r ~/.claude/skills/scroll-video-hero/requirements.txt      # opencv-python, numpy, Pillow
```
Also needed: FFmpeg + FFprobe on PATH, Node.js 18+ (for the page).

Then just talk to Claude:
* "I want scroll motion for my bakery, I don't know where to start." -> it asks a few questions and proposes a concept.
* "I want the scroll effect of this video" + a screen recording -> it reads the motion language and adapts it to your business.
* "Here are my clips, they jump between cuts" -> it measures, repairs and assembles them.

## What is inside

```
SKILL.md                 the workflow Claude follows (intake -> scenario -> clips -> page -> package)
tools/
  scenario_pack.py       business brief -> SCENARIO.md, PROMPTS.md, content.json, recipe.json   (15 industry playbooks)
  analyze_reference.py   a reference video/recording -> numbers + numbered contact sheet
  analyze_clips.py       your clips -> speed, ease tails, end-snap, seam gaps + verdicts + seam frame pairs
  assemble.py            recipe -> one master (clips, flow bridges, retimed gap clips, speed equalizing)
  review_frames.py       numbered frames + contact sheets + segment map, for "frames 277-281 are damaged"
  encode_hero.py         desktop 1080p + mobile 720x1280 + poster (short-GOP)
  check_site.py          pre-flight: GOP, size, jumps, stalls, placeholders
  package_static.py      static export + tiny Range-capable server + launchers (USB)
  last_frame.py  bridge.py  equalize_speed.py  make_placeholder.py
templates/site/          Next.js page with the layered hero (presets: layers | captions; timings in content.json)
templates/usb/           offline launcher
references/              intake.md, playbooks.json, reference-analysis.md, models.md,
                         prompts-video-models.md, layered-hero.md, lessons.md
examples/recipe.example.json
```

## Quick start without Claude

```bash
python tools/scenario_pack.py --list
echo '{"business":"Atelier Noor","product":"Leather bag","industry":"auto","tool":"veo-flow"}' > brief.json
python tools/scenario_pack.py brief.json --out pack            # read pack/SCENARIO.md, generate with pack/PROMPTS.md

python tools/analyze_clips.py clips/01.mp4 clips/02.mp4 ...    # follow the verdict per seam
python tools/assemble.py pack/recipe.json                      # after editing the recipe
python tools/review_frames.py work/master_eq.mp4 --map work/master.map.json --out frames_review
python tools/encode_hero.py work/master_eq.mp4 --out templates/site/public --content templates/site/content.json
python tools/check_site.py templates/site
python tools/package_static.py templates/site --out dist-usb --name "My Brand" --bundle-node
```

## How seams are classified
Camera distance is measured in **eq-frames** (frames of ordinary camera motion between two frames):

| Gap | Fix |
|---|---|
| < 2.5 | hard cut |
| 2.5 - 8 | short smooth-flow bridge or a generated gap clip |
| 8 - 14 | gap clip from your video model (start = A, end = B) |
| > 14 | regenerate the next clip from the last frame of the previous one |

Measured results and the reasoning: `references/lessons.md`.

## Honest limits
* Optical flow cannot invent geometry: above ~15 eq-frames it damages the picture; the tools say so instead of hiding it.
* The skill writes prompts and repairs footage; the generation itself happens in your video model (or an MCP/API you own).
* The hero is a video scrubbed by `currentTime`. Test on a real iPhone (Safari) and an Android phone.
* Brand text, logos and UI are added in HTML, never generated inside the footage.

## License
MIT. See `LICENSE`.
