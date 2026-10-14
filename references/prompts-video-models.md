# Prompts for video models (Veo / Flow, Kling, Runway ...)

These are model-agnostic. Replace the nouns; keep the structure. Always: **1080p from the generator, no audio, constant speed.**

## 1. Chain (preferred)
Clip 1: start frame = your key still, **no end frame**.
Clip N: start frame = `python tools/last_frame.py clipN-1.mp4 start.png`, **no end frame**.

```
Slow steady forward dolly toward <subject> at constant speed, eye-level camera, <what grows/clears>,
nothing else changes, no ease-in, no ease-out.
```
Continuation:
```
Continue the same forward movement at the same constant speed, <next beat>, no turning,
the room and the <object> stay exactly the same, no ease-in, no ease-out.
```
If the camera orbits or shows another part of the space, append:
```
The camera keeps looking in the same direction. Do not turn, orbit or show a different part of the space.
```
If the model rotates the OBJECT instead of moving the camera:
```
Do NOT rotate the <object>. The <object> is a fixed object. Move the virtual camera only.
```

## 2. Gap clip (small gap, start = A and end = B)
Describe the motion you see between the two frames in one sentence (direction, height change, what turns):
```
A very slow, steady camera move inside the same <space>: the camera glides slightly forward and a little to the right
while lowering a few centimeters, so the <object> turns from a three-quarter view to a more frontal view.
The camera keeps looking in the same direction, no turning, no tilting up. Constant speed, no ease-in, no ease-out.
The <space>, <object>, textures, lighting and the view through the glass stay exactly the same; nothing else moves.
```
Take 2-3 outputs, then score them: first frame vs A (< 2 eq-frames), last frame vs B, no end snap. Short moves are
often stretched over 4 s with near-zero speed at the start; `assemble.py` `retime` fixes that.

## 3. Midpoint image (image model, use only when the gap is <= ~10 eq-frames)
Attach A then B:
```
Image 1 and image 2 are two frames of one continuous forward camera move through the same room. Generate the frame
exactly halfway along the camera path between them: the camera position and framing are the midpoint of the two, the
room, furniture, fabric patterns and lighting are identical to both images. Do not change anything except the camera
position. Photoreal, 16:9, no text, no logos.
```
Verify the result: `dist(A, mid)` and `dist(mid, B)` should both be about half of `dist(A, B)`. If it sits next to one end, discard it.

## 4. Reference handedness
3D screenshots can be mirrored relative to the scene (e.g. a chaise on the left vs the right). Add a line:
"Handedness lock: seen from its front, the object always has the <part> on the RIGHT; copy only the viewing angle
of the attached reference, never its left/right layout."

## 5. Notes on Flow / Veo
* Frames-to-Video accepts start and end frames, but the end is only a hint (see snap). Extend continues a Veo clip natively but can still show a seam in the extension; test on one leg first.
* Veo 3.1 durations are short (4-8 s); several sources report 1080p forces 8 s. Fewer, longer clips mean fewer seams.
* Do not describe the room again in continuation prompts: long prompts make the model invent a new view.
