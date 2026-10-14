#!/usr/bin/env python3
"""Create a short placeholder hero video (moving gradient) so a fresh template runs before you have real footage.

Usage:  python tools/make_placeholder.py site/public
"""
import os
import sys

import svh

svh.need_ffmpeg()
out = sys.argv[1] if len(sys.argv) > 1 else "public"
os.makedirs(out, exist_ok=True)
x264 = ["-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-x264-params", "keyint=6:min-keyint=6:scenecut=0:bframes=0", "-pix_fmt", "yuv420p"]
src = ["-f", "lavfi", "-i", "gradients=s=1920x1080:d=6:r=24:speed=0.04:c0=#0b0f14:c1=#2a3b4d:c2=#8a6a3b:nb_colors=3"]
try:
    svh.run("ffmpeg", "-v", "error", "-y", *src, *x264, f"{out}/hero.mp4")
except Exception:
    svh.run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1920x1080:d=6:r=24", *x264, f"{out}/hero.mp4")
svh.run("ffmpeg", "-v", "error", "-y", "-i", f"{out}/hero.mp4", "-vf", "crop=ih*9/16:ih,scale=540:960", *x264, f"{out}/hero-mobile.mp4")
svh.run("ffmpeg", "-v", "error", "-y", "-i", f"{out}/hero.mp4", "-frames:v", "1", "-q:v", "3", f"{out}/hero-poster.jpg")
print(f"placeholder hero written to {out}/ (replace it with: python tools/encode_hero.py master.mp4 --out {out})")
