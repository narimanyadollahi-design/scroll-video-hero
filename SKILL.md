---
name: scroll-video-hero
description: Build scroll-driven motion sites ("scroll motion", Apple-style scroll hero) for ANY business. Starts by understanding what the user has: a reference they like ("make it like this video"), only an idea, nothing yet, or finished clips. Asks a few questions, writes the scenario and the generation prompts (stills + chained video prompts for Veo/Flow, Kling, Runway, Sora, Higgsfield), then turns the clips the user provides into ONE seamless scroll-scrubbed hero video (measures seams, fixes jumps, stalls and damaged frames, reviews frames by number), and ships it in a layered landing page (nav, headline, word-by-word statement, closing card), plus an offline USB package. Use when someone wants scroll animation / scroll motion / a cinematic scrolling website, has video clips that jump or have seams, wants a hero like a reference video, or has no idea yet and needs a concept for their business.
---

# scroll-video-hero

You are a specialist in **scroll motion**: one continuous camera move that the visitor drives with the scroll wheel, forward and
backward, wrapped in a landing page. Your job covers the whole chain: **understand -> design the scenario -> write the prompts ->
repair and assemble the clips -> build the page -> package it**.

Never skip the measuring, and never promise what only the user's footage can deliver.

## Step 0: Intake (always first; see `references/intake.md`)

Work out which situation you are in, ask only what is missing (max 5 questions, each with a default), then act.

| The user gives | Situation | Do |
|---|---|---|
| a video / link / recording + "like this" | **Reference** | `tools/analyze_reference.py`, fill `references/reference-analysis.md`, say the motion language back in 5 lines, then scenario for THEIR business |
| a business or an idea, no video | **Idea** | pick a playbook, `tools/scenario_pack.py`, improve it with specifics, give the prompts |
| "I have nothing, I need scroll motion" | **Nothing** | interview (5 questions), propose one concept (or three if unsure), then as Idea |
| their clips | **Clips ready** | go to Step 2 |

Do not copy anyone's footage, text or brand: copy the *motion language* (camera behaviour, pacing, layers) only. Never download a
link silently; ask for the file or confirm a browser view.

## Step 1: Scenario and prompts

```
python tools/scenario_pack.py brief.json --out pack      # --list shows the industry playbooks
```
Produces `SCENARIO.md` (storyboard of legs: camera move, what the visitor sees, copy beat; page copy; risks; plan),
`PROMPTS.md` (shared style, stills S1..Sn, chained video prompts, gap-clip template), `content.json` (page draft) and
`recipe.json` (assemble skeleton). The playbook is the skeleton; **you add the specifics** of the user's real object, room and material.

Hand the user: the storyboard in 6 lines, the order to generate things, and what to send back
(`clips/01.mp4`, `02.mp4`, ...). If the user wants you to generate through an MCP/API they own (e.g. Higgsfield): check balance,
state count and cost, wait for a clear yes, generate leg 1 only, verify it, then continue. See `references/models.md`.

## Step 2: Measure the clips

```
python tools/analyze_clips.py clips/01.mp4 clips/02.mp4 ... --out report
```
Per seam the gap is in **eq-frames** (frames of ordinary camera motion between two frames):

| Gap | Action |
|---|---|
| < 2.5 | hard cut is invisible |
| 2.5 - 8 | short smooth-flow bridge or a generated gap clip |
| 8 - 14 | gap clip from the video model (start = A, end = B), or a midpoint image **after verifying it is halfway** |
| > 14 | do not bridge: regenerate the next clip **from the last frame of the previous one** (`tools/last_frame.py`) |

Also: cut before an **END SNAP** (model jumps to the end frame in the last ~6 frames); trim or equalize **ease tails**.

Why: video models do not honour end frames; image models' "midpoint" collapses toward one end when the gap is large;
optical flow is fine up to ~8 eq-frames (use the smoothed flow for stripes/fences/bricks), damaging above ~15; plain frame
differences hide stalls because of grain, so speed is measured as distance over +-4 frames. Details: `references/lessons.md`.

## Step 3: Assemble, review, encode

```
python tools/assemble.py recipe.json                                   # clips + bridges + gap clips (+ retime, equalize)
python tools/review_frames.py work/master_eq.mp4 --map work/master.map.json --out ../frames_review
python tools/encode_hero.py work/master_eq.mp4 --out site/public --content site/content.json
python tools/check_site.py site
```
* The user judges by eye and answers with **frame numbers** from the contact sheets. Numbering starts at 1.
  "Delete between f0278 and f0303" keeps those two frames and removes 279-302. "Do not build anything" means a plain cut:
  say the remaining jump in eq-frames, then do it. Regenerate frames and map after every edit (numbers shift). Keep each master.
* Short GOP (keyint 6, no B-frames), CRF 18, 1080p (+ mobile 720x1280). Generate at 1080p in the model; upscaling softens patterns.
* Keep heavy work folders outside the site folder (`next dev` hangs on them). Judge smoothness on `npm run build && npm start`.

## Step 4: The page (see `references/layered-hero.md`)

Copy `templates/site`, edit `content.json` (`hero.layers`, optional `hero.timing`, `hero.preset: "layers" | "captions"`, `brand.logo`)
and `theme.json`. The video is pinned; text layers scroll over it: headline and paragraph leave at different speeds, a statement
rises and lights up word by word, small columns follow, a closing card rises at the end. Match a reference by editing `hero.timing`.
Check mobile by measuring bounding boxes at 375x812 (statement bottom above columns top), not by eye.

## Step 5: Offline / USB

```
python tools/package_static.py site --out dist-usb --name "Brand" --bundle-node
```
A scroll video cannot be scrubbed from `file://`; the package ships a tiny server with HTTP Range support.

## Rules
* Brand text, logos, UI and labels go in HTML, never in generated footage. Avoid faces and hands in close-ups.
* One camera move per clip, constant speed, no ease-in/out, 1080p, no audio, no end frames.
* Say honestly what cannot be fixed (gaps above ~15, damaged geometry) and what the fix costs (re-generating one clip).
* Never publish, push or send anything for the user; prepare it and give the commands.
* Windows: use the Python tools (not long shell heredocs), pass `encoding="utf-8"`, hard-reload after re-encoding (video cache).
* Test on a real iPhone (Safari) and an Android phone before showing a client.
