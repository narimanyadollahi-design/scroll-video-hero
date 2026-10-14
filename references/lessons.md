# Lessons from the real project (numbers included)

Case: 5 AI clips (4 s, 24 fps, 1080p) of a camera moving from outside a glass house, through the glass, to a close-up of a sofa.

| Finding | Evidence | Consequence |
|---|---|---|
| Models ignore end frames | SSIM end-of-clip vs next-start: 0.47 and 0.60; one clip snapped to its end frame in the last 6 frames (frame step 29 vs median 5) | Cut before the snap; never rely on end frames |
| Frame differences hide stalls | YDIF said ~5 everywhere; distance-based speed said 0.5 at seams vs 1.5-2 in the clips | Use `speed_profile` (distance over +-4 frames) |
| Gaps in eq-frames | seams measured 10, 20, 17, 22 | <=8 bridge, 8-14 gap clip, >14 chain |
| Optical flow limits | Gaps 16-22 tore furniture; gap 7.5 on a striped fabric still tore the stripes until the flow was smoothed (sigma 20) | Smoothed flow for repetitive textures; never above ~15 |
| Image-model midpoints collapse | `mid` was 4 from B and 19 from A when A-B was 19 | Verify halfway-ness before using |
| Chaining fixes it | New clip started from the last good frame: first frame 1.5 eq-frames from A, no snap | Chain whenever the gap is large |
| Ease tails | clip heads/tails at 0.5-1.0 vs 1.5-2 in the body | Trim, or equalize speed (4 -> 3.4 s of dead time removed) |
| All-intra vs short GOP | all-intra CRF 26 = 21 MB; keyint 6 CRF 18 = 33 MB with SSIM 0.992 | Short GOP, CRF 18 |
| Review by number | User named frames from contact sheets; numbers shift after each edit | Regenerate frames and map after every edit |

Process rules that paid off:
* Read the actual frames (contact sheets), do not trust one metric.
* After each cut, report the remaining jump in eq-frames and frame-step ratio, then let the user decide.
* Do not generate when the user said "do not build"; plain cut + honest number.
* Keep backups of every master; changes are reversible.
