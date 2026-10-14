#!/usr/bin/env python3
"""Save the true last frame (or any frame) of a clip as a lossless PNG.
Use it as the START frame of the next clip when chaining: the model then continues from exactly where the last one stopped.

Usage:  python tools/last_frame.py clip.mp4 out.png [frame_index]
"""
import sys

import svh

svh.need_ffmpeg()
if len(sys.argv) < 3:
    sys.exit(__doc__)
clip, out = sys.argv[1], sys.argv[2]
idx = int(sys.argv[3]) if len(sys.argv) > 3 else svh.frame_count(clip) - 1
svh.extract_frame(clip, idx, out)
print(f"wrote {out} (frame {idx})")
