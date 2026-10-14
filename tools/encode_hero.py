#!/usr/bin/env python3
"""Encode a master video for scroll scrubbing: desktop 1080p, mobile 720x1280 (centre crop), poster.

Usage:  python tools/encode_hero.py master.mp4 --out site/public [--content site/content.json]

Why short-GOP, not all-intra: all-intra is seek-perfect but needs ~3x the bytes for the same quality, which
forces a visibly harsh CRF under a size budget. keyint=6 with no B-frames seeks instantly yet looks far better.
"""
import argparse
import json
import os
import subprocess

import svh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--mobile-crf", type=int, default=19)
    ap.add_argument("--gop", type=int, default=6)
    ap.add_argument("--focus", type=float, default=0.5, help="horizontal centre of the mobile crop, 0..1")
    ap.add_argument("--content", help="content.json to update with the hero duration")
    a = ap.parse_args()
    svh.need_ffmpeg()
    os.makedirs(a.out, exist_ok=True)
    x264 = f"keyint={a.gop}:min-keyint={a.gop}:scenecut=0:bframes=0"
    common = ["-an", "-c:v", "libx264", "-preset", "slow", "-x264-params", x264, "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    svh.run("ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", "scale=1920:1080:flags=lanczos", "-crf", a.crf, *common, f"{a.out}/hero.mp4")
    crop = f"crop=ih*9/16:ih:(iw-ih*9/16)*{a.focus}:0,scale=720:1280:flags=lanczos"
    svh.run("ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", crop, "-crf", a.mobile_crf, *common, f"{a.out}/hero-mobile.mp4")
    svh.run("ffmpeg", "-v", "error", "-y", "-i", f"{a.out}/hero.mp4", "-frames:v", "1", "-q:v", "2", f"{a.out}/hero-poster.jpg")
    n = svh.frame_count(f"{a.out}/hero.mp4")
    for f in ("hero.mp4", "hero-mobile.mp4"):
        print(f"{f}: {os.path.getsize(os.path.join(a.out, f)) / 1048576:.1f} MB")
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0",
                        f"{a.out}/hero.mp4"], capture_output=True, text=True).stdout.strip()
    num, den = (r.split("/") + ["1"])[:2]
    fps = float(num) / float(den or 1)
    print(f"{n} frames, {n / fps:.2f}s @ {fps:g} fps")
    if a.content:
        c = json.load(open(a.content, encoding="utf-8"))
        c.setdefault("hero", {})["video"] = {"frames": n, "fps": fps, "duration_seconds": round(n / fps, 3)}
        with open(a.content, "w", encoding="utf-8") as fh:
            json.dump(c, fh, indent=2, ensure_ascii=False)
        print(f"updated {a.content}")


if __name__ == "__main__":
    main()
