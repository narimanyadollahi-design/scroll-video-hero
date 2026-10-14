#!/usr/bin/env python3
"""Measure a set of AI-generated clips that are meant to play as ONE continuous camera move.

Usage:  python tools/analyze_clips.py clip01.mp4 clip02.mp4 ... [--out report]

Reports, per clip: camera speed profile, slow ease-in/ease-out tails, and a snap at the end (the model
jumping to the requested end frame). Between consecutive clips: the gap between the last frame of one
and the first of the next (in eq-frames), the best cut pair, and a recommendation. Writes the A/B frame
pairs for every seam to  <out>/seams/  so you can ask an image model for a midpoint or a video model for a gap clip.
"""
import argparse
import json
import os

import numpy as np

import svh


def verdict(gap):
    if gap < 2.5:
        return "OK (hard cut is invisible)"
    if gap < 8:
        return "SMALL: short smooth-flow bridge (3-6 frames) or a generated gap clip"
    if gap < 14:
        return "MEDIUM: generate a gap clip (start=A, end=B) in your video model, or a midpoint image"
    return "LARGE: regenerate the next clip starting FROM the last frame of the previous one (chain)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--out", default="svh_report")
    a = ap.parse_args()
    svh.need_ffmpeg()
    os.makedirs(os.path.join(a.out, "seams"), exist_ok=True)
    V = {}
    report = {"clips": [], "seams": []}
    for p in a.clips:
        g = svh.load_gray(p)
        V[p] = g
        sp = svh.speed_profile(g)
        med = float(np.median(sp))
        step = np.array([np.mean((g[i] - g[i - 1]) ** 2) for i in range(1, len(g))]) ** 0.5
        head = int(next((i for i, s in enumerate(sp) if s >= 0.5 * med), 0))
        tail = int(next((i for i, s in enumerate(sp[::-1]) if s >= 0.5 * med), 0))
        snap = [int(i + 1) for i in range(max(0, len(step) - 12), len(step)) if step[i] > 4 * np.median(step)]
        c = {"file": p, "frames": int(len(g)), "median_speed": round(med, 2), "ease_in_frames": head,
             "ease_out_frames": tail, "end_snap_frames": snap}
        report["clips"].append(c)
        print(f"{os.path.basename(p)}: {len(g)} frames | median speed {med:.2f} eq/frame | slow head {head}f, slow tail {tail}f"
              + (f" | END SNAP at frames {snap} (model jumped to the end frame: cut before it)" if snap else ""))
    print()
    for i in range(len(a.clips) - 1):
        p, q = a.clips[i], a.clips[i + 1]
        A, B = V[p], V[q]
        snap = report["clips"][i]["end_snap_frames"]
        # if the model snapped to the end frame, the real last good frame is the one before the snap
        last = (snap[0] - 1) if snap else len(A) - 1
        A = A[: last + 1]
        cuts = sorted((svh.dist(A[x], B[y]), x, y) for x in range(max(0, len(A) - 40), len(A)) for y in range(0, min(60, len(B))))
        gap = svh.dist(A[last], B[0])
        d, x, y = cuts[0]
        s = {"from": p, "to": q, "gap_last_to_first": round(gap, 1), "best_cut": {"dist": round(d, 1), "from_frame": x, "to_frame": y},
             "verdict": verdict(min(gap, d)), "last_good_frame": int(last)}
        report["seams"].append(s)
        print(f"seam {i+1} ({os.path.basename(p)} -> {os.path.basename(q)}): last{'(pre-snap)' if snap else ''}->first {gap:.1f} eq-frames | best cut "
              f"{os.path.basename(p)}#{x} -> {os.path.basename(q)}#{y} = {d:.1f}\n   -> {s['verdict']}")
        svh.extract_frame(p, x, os.path.join(a.out, "seams", f"seam{i+1}_A_{os.path.splitext(os.path.basename(p))[0]}_f{x}.png"))
        svh.extract_frame(q, y, os.path.join(a.out, "seams", f"seam{i+1}_B_{os.path.splitext(os.path.basename(q))[0]}_f{y}.png"))
    json.dump(report, open(os.path.join(a.out, "report.json"), "w", encoding="utf-8"), indent=2)
    print(f"\nReport: {a.out}/report.json   Seam frame pairs: {a.out}/seams/")


if __name__ == "__main__":
    main()
