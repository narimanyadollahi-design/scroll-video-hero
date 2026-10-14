"""Shared helpers for the scroll-video-hero toolkit (ffmpeg + OpenCV + numpy; no other dependencies)."""
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np

# Calibration: mean squared gray difference (160x90) between two frames 12 apart in a typical
# forward dolly = 705.3. dist() reports camera distance in "normal-motion frames" (eq-frames):
# dist(a, b) ~ how many frames of ordinary camera motion separate a and b.
M12 = 705.3


def need_ffmpeg():
    for exe in ("ffmpeg", "ffprobe"):
        if not shutil.which(exe):
            sys.exit(f"{exe} was not found on PATH. Install FFmpeg (https://ffmpeg.org) and try again.")


def run(*args, quiet=True):
    subprocess.run([str(a) for a in args], check=True, **({"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL} if quiet else {}))


def load_gray(path, w=160, h=90):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg could not read {path}: {r.stderr.decode(errors='ignore')[:200]}")
    return np.frombuffer(r.stdout, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)


def small_gray(img_bgr, w=160, h=90):
    return cv2.cvtColor(cv2.resize(img_bgr, (w, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)


def dist(a, b):
    """Camera distance between two gray frames in eq-frames."""
    return 12.0 * (float(np.mean((a - b) ** 2)) / M12) ** 0.5


def speed_profile(V, half=4):
    """Noise-robust camera speed (eq-frames per frame) using +-half frames. Do NOT use plain frame
    differences for this: film grain and flicker dominate them and hide real stalls."""
    n = len(V)
    out = []
    for i in range(n):
        a, b = max(0, i - half), min(n - 1, i + half)
        out.append(dist(V[a], V[b]) / max(1, b - a))
    return np.array(out)


def frame_count(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def extract_frame(video, idx, out_png):
    run("ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"select=eq(n\,{int(idx)})", "-frames:v", "1", out_png)
    return out_png


def resolve_key(key, tmp_dir):
    """'path/to/clip.mp4#95' -> PNG of frame 95; anything else is treated as an image path."""
    if "#" in key and key.split("#")[0].lower().endswith((".mp4", ".mov", ".webm", ".mkv")):
        path, idx = key.rsplit("#", 1)
        os.makedirs(tmp_dir, exist_ok=True)
        out = os.path.join(tmp_dir, f"{os.path.basename(path)}_{idx}.png")
        extract_frame(path, int(idx), out)
        return out
    return key
