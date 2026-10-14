# Notes per generator (verify against the vendor's current docs: these tools change monthly)

What matters for scroll hero footage is the same everywhere: **1080p, no audio, one camera move per clip, constant speed,
start frame = previous last frame, no reliance on end frames.**

| Tool | Use it for | Notes |
|---|---|---|
| **Google Flow / Veo 3.1** | video legs | Frames to Video (start, optional end). Extend continues a Veo clip natively but can show a seam; test one leg. Typical clip 4-8 s; reports say 1080p forces 8 s: plan fewer, longer legs. Ingredients/reference images help keep an object consistent. |
| **Gemini image / Nano Banana** | stills, midpoints | Good for keeping a room and object consistent across stills when you attach the previous still. A "midpoint" between far-apart frames tends to collapse to one endpoint: measure with `analyze_clips.py` before using it. |
| **Kling** | video legs | Image-to-video; start+end frame mode exists but the end is a hint. Use the highest quality mode; 5 s clips. |
| **Runway** | video legs | Image-to-video; camera controls are useful for a pure dolly. |
| **Sora** | video legs | Image-to-video; keep prompts short and literal. |
| **Higgsfield (MCP)** | stills + video + upscaling | Check `balance`, quote the cost, generate the first leg only. Upload the last frame with the media upload flow to start the next leg. |
| **Midjourney / GPT-image** | stills | Fine for keyframe stills; they cannot hold an exact object across many frames without a reference. |

Practical rules:
* Generate at the final resolution. Upscaling afterwards softens fine patterns (stripes, weave, text on objects).
* If the model changes lighting between clips, say it in the prompt: "same lighting as the first frame, no change of time of day".
* If a model keeps overshooting or snapping at the end, ask for a shorter move or cut at the snap (the analyzer reports it).
* Keep every raw clip and the prompt that made it; re-takes are normal.
