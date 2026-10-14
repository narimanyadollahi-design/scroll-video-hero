#!/usr/bin/env python3
"""Pre-flight checks for a scroll-video-hero site.

Usage:  python tools/check_site.py path/to/site

Checks: hero files exist, short GOP and no B-frames (scrub-friendly), size budgets, duration matches content.json,
no frame-to-frame jumps in hero.mp4, placeholder strings still present in content.json.
It cannot replace a test on a real phone (iOS Safari especially).
"""
import json
import os
import subprocess
import sys

import numpy as np

import svh

OK, WARN, ERR = [], [], []


def probe_types(path, seconds=3):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pict_type", "-of", "csv=p=0",
                        "-read_intervals", f"%+{seconds}", path], capture_output=True, text=True)
    return [t.strip().strip(",") for t in r.stdout.split() if t.strip().strip(",")]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    svh.need_ffmpeg()
    site = sys.argv[1]
    pub = os.path.join(site, "public")
    hero, mob, poster = (os.path.join(pub, f) for f in ("hero.mp4", "hero-mobile.mp4", "hero-poster.jpg"))
    content = {}
    cp = os.path.join(site, "content.json")
    if os.path.exists(cp):
        content = json.load(open(cp, encoding="utf-8"))

    for f in (hero, mob, poster):
        (OK if os.path.exists(f) else ERR).append(f"{os.path.basename(f)} {'found' if os.path.exists(f) else 'is MISSING'}")
    if os.path.exists(hero):
        types = probe_types(hero)
        gaps, last = [], None
        for i, t in enumerate(types):
            if t == "I":
                if last is not None:
                    gaps.append(i - last)
                last = i
        if "B" in types:
            ERR.append("hero.mp4 has B-frames: scrubbing will stutter (re-encode with tools/encode_hero.py)")
        elif set(types) != {"I"} and (not gaps or max(gaps) > 8):
            ERR.append("hero.mp4 keyframe gap > 8 frames: scrubbing will stutter")
        else:
            OK.append("hero.mp4 is scrub-friendly (short GOP, no B-frames)")
        mb = os.path.getsize(hero) / 1048576
        (OK if mb <= 40 else WARN).append(f"hero.mp4 is {mb:.1f} MB (budget 40)")
        n = svh.frame_count(hero)
        d = content.get("hero", {}).get("video", {}).get("frames")
        if d is not None:
            (OK if d == n else ERR).append(f"content.json frame count {d} vs video {n}" + ("" if d == n else " (re-run encode_hero.py --content)"))
        V = svh.load_gray(hero)
        step = np.array([np.mean((V[i] - V[i - 1]) ** 2) for i in range(1, len(V))]) ** 0.5
        med = float(np.median(step))
        spikes = [i + 2 for i, s in enumerate(step) if s > 4 * med and (i == 0 or step[i - 1] <= 4 * med)]
        if spikes:
            WARN.append(f"possible jumps at frames {spikes[:8]} (frame step >4x median); check with review_frames.py")
        else:
            OK.append("no frame-to-frame jumps found")
        sp = svh.speed_profile(V)
        slow = int((sp < 0.4 * float(np.median(sp))).sum())
        (OK if slow < 0.06 * len(V) else WARN).append(f"{slow} frames move <40% of median camera speed (stalls feel like pauses while scrolling)")
    if os.path.exists(mob):
        mb = os.path.getsize(mob) / 1048576
        (OK if mb <= 12 else WARN).append(f"hero-mobile.mp4 is {mb:.1f} MB (budget 12)")
    blob = json.dumps(content)
    for token in ("TODO", "example.com", "YOUR BRAND", "Your Brand"):
        if token in blob:
            WARN.append(f"content.json still contains placeholder text: {token}")

    for m in OK:
        print("  OK   ", m)
    for m in WARN:
        print("  WARN ", m)
    for m in ERR:
        print("  ERROR", m)
    print(f"\n{len(OK)} ok, {len(WARN)} warnings, {len(ERR)} errors\nReminder: test the scroll on a real iPhone (Safari) and an Android phone.")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
