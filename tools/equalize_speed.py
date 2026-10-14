#!/usr/bin/env python3
"""Equalise camera speed: drop frames wherever the camera moves slower than the target.

Speed is measured as scene distance over +-4 frames (noise-robust, in 'normal-motion frames per frame').
Usage: python tools/equalize_speed.py IN.mp4 OUT.mp4 [TARGET=1.5]
Frames are only ever skipped (never duplicated or synthesised), so no new artifacts are introduced.
"""
import sys, subprocess, os, shutil
import numpy as np, cv2

src, dst = sys.argv[1], sys.argv[2]
target = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
MAXSKIP = float(os.environ.get("MAXSKIP", 4.0))


def load_small(path, w=160, h=90):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)


V = load_small(src)
n = len(V)
d = lambda a, b: 12 * (float(np.mean((V[a] - V[b]) ** 2)) / 705.3) ** 0.5
speed = np.array([d(max(0, i - 4), min(n - 1, i + 4)) / (min(n - 1, i + 4) - max(0, i - 4)) for i in range(n)])
speed = np.maximum(speed, 0.15)

picks, pos = [0], 0.0
while True:
    i = int(round(pos))
    s = np.interp(pos, np.arange(n), speed)
    pos += min(MAXSKIP, max(1.0, target / s))
    j = int(round(pos))
    if j >= n - 1:
        picks.append(n - 1)
        break
    picks.append(j)
picks = sorted(set(picks))
print(f"{n} frames -> {len(picks)} frames (target speed {target})")

tmp = os.path.splitext(dst)[0] + "_png"
shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
cap = cv2.VideoCapture(src)
want = set(picks)
k = 0
idx = 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    if idx in want:
        k += 1
        cv2.imwrite(f"{tmp}/{k:04d}.png", f)
    idx += 1
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", tmp + "/%04d.png", "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", "-an", dst], check=True)
shutil.rmtree(tmp, ignore_errors=True)
np.save(os.path.splitext(dst)[0] + "_picks.npy", np.array(picks))
print("picked source frames (first 30):", picks[:30])
