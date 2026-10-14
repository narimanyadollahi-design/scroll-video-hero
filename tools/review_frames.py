#!/usr/bin/env python3
"""Export every frame of a video as a numbered JPG, plus contact sheets and a segment map, so a human can say
'frames 277-281 are damaged' and you can act on exact frame numbers.

Usage:  python tools/review_frames.py master.mp4 [--map master.map.json] [--out frames_review]
Frame numbers start at 1. 'Delete between f0278 and f0303' means the two named frames stay and 279..302 go.
"""
import argparse
import json
import os
import shutil

import cv2
import numpy as np


def label(t, s):
    cv2.putText(t, s, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(t, s, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--map")
    ap.add_argument("--out", default="frames_review")
    ap.add_argument("--per-sheet", type=int, default=24)
    a = ap.parse_args()
    shutil.rmtree(a.out, ignore_errors=True)
    os.makedirs(a.out + "/frames")
    os.makedirs(a.out + "/sheets")
    cap = cv2.VideoCapture(a.video)
    small, n = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        n += 1
        cv2.imwrite(f"{a.out}/frames/f{n:04d}.jpg", cv2.resize(f, (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
        small.append(cv2.resize(f, (320, 180), interpolation=cv2.INTER_AREA))
    per = a.per_sheet
    for s in range(0, n, per):
        tiles = []
        for i in range(s, min(s + per, n)):
            t = small[i].copy()
            label(t, str(i + 1))
            tiles.append(t)
        while len(tiles) % 6:
            tiles.append(np.zeros((180, 320, 3), np.uint8))
        rows = [np.hstack(tiles[r * 6:(r + 1) * 6]) for r in range(len(tiles) // 6)]
        cv2.imwrite(f"{a.out}/sheets/sheet_{s + 1:04d}-{min(s + per, n):04d}.jpg", np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    lines = [f"{n} frames, numbered from 1\n"]
    if a.map:
        m = json.load(open(a.map, encoding="utf-8"))
        fps = m.get("fps", 24)
        for sg in m["segments"]:
            lines.append(f"{sg['label']}: frames {sg['start']}-{sg['end']} | seconds {(sg['start'] - 1) / fps:.2f}-{(sg['end'] - 1) / fps:.2f}")
    with open(a.out + "/MAP.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"{n} frames -> {a.out}/frames, {a.out}/sheets, {a.out}/MAP.txt")


if __name__ == "__main__":
    main()
