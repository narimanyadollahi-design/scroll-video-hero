# Intake: start here, before any tool

The user arrives in one of four situations. Detect which, ask **only what is missing** (never more than 5 questions at once,
always with a recommended default), and move on. Do not interrogate; propose, then let them correct.

## A. Which situation?

| They say / send | Situation | Next |
|---|---|---|
| "I want scroll motion like this" + a video, link or recording | **Reference** | Section B, then C |
| "I have an idea / a business, no video yet" | **Idea** | Section C (scenario), then production |
| "Here are my clips" | **Clips ready** | skip to `SKILL.md` step 1 (analyze) |
| "I want scroll motion for my business" and nothing else | **Nothing** | Section D (interview), then C |

If a **link** is given (website, social post, prompt library), do not download it silently. Ask the user to save the
file locally and give you the path; or, if a browser tool is available and the user agrees, view it there. Never copy
a competitor's footage, text or brand; copy the *motion language* (camera behaviour, pacing, layers) only.

## B. Reference -> motion brief
1. `python tools/analyze_reference.py ref.mp4 --out ref_report`.
2. Look at `reference_sheet.jpg` and 6-9 full-size frames. Fill `references/reference-analysis.md` (camera move, layers,
   timings, type sizes, what is NOT transferable).
3. Say it back to the user in 5 lines: "One continuous forward move, text layers scroll over a pinned video, a
   statement lights up word by word, ends on a closing card. Right?" Then continue with C using their business.

## C. Scenario (the creative part)
1. Pick the industry playbook (`python tools/scenario_pack.py --list`) or `generic`.
2. Write the brief JSON (business, product, industry, object, setting, tone, tool, goal) and run
   `python tools/scenario_pack.py brief.json --out pack`.
3. Read `SCENARIO.md` yourself and **improve it with specifics** from the user's world (the real object, the real room,
   the real material). The playbook gives the skeleton; the quality is in the details.
4. Show the user a 6-line storyboard (leg, camera, what they see, copy beat) and ask for one correction round.
5. Hand over `PROMPTS.md` (stills + chained video prompts) and say exactly what to generate in which order, and what to
   send back ("put the clips in `clips/`, name them 01, 02, ...").

If the user wants you to generate (an MCP such as Higgsfield, or an API they own): check balance, state the number of
generations and the likely cost, wait for a clear yes, generate the first leg only, verify with `analyze_clips.py`, then continue.

## D. The interview (when they have nothing)
Ask these, merged into one message, with defaults in brackets. Skip anything already known.

1. **What is the business and the hero product/space?** (one sentence)
2. **What should the visitor feel?** [calm and premium] / energetic / warm and human / technical
3. **Goal?** [portfolio piece] / real client launch / product launch / just exploring
4. **Where will the footage come from?** [you generate it: Veo/Flow, Kling, Runway, Sora, Higgsfield] / filmed / I already have it
5. **Language and brand details?** [English] + logo file / brand colours / fonts, or "choose for me"

Defaults if they say "you decide": 5 legs x 4 s, 1080p, English, dark base with one warm accent, one serif for all text,
layered hero preset, mobile crop centred, USB package not needed.

## E. Things to tell the user early (set expectations)
* The page is a **video scrubbed by scroll**; the smoothness comes from one continuous camera move with no seams.
  That is why the plan is a chain of legs and the first leg is tested before the rest.
* They will generate stills and clips elsewhere; you prepare the prompts, measure the result and fix what is fixable.
* Brand text, logos and UI are added in the page, never generated inside the video.
* Typical effort: 1 test leg, then the rest; plan for ~1.5x the clips because of re-takes.
* Test on a real phone before showing a client.
