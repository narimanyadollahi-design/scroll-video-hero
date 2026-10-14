#!/usr/bin/env python3
"""Analyse a REFERENCE the user likes ("make it like this") so you can describe its motion language precisely.

Usage:  python tools/analyze_reference.py reference.(mp4|mov|webm|gif|webp) [--out ref_report] [--sheet-frames 24]

Works on a site screen recording or a plain video. It cannot read text or layouts for you; it gives numbers and a
numbered contact sheet. Then LOOK at the sheet (and 6-9 full-size frames) and fill the template in
references/reference-analysis.md: camera move, layers, timings, type sizes, what to copy and what not to.

Reports: frames, fps, duration, pauses (static ranges = the person stopped scrolling), cuts (hard scene changes),
motion chapters (where the motion character changes) and a numbered contact sheet.
"""
import argparse
import json
import os

import cv2
import numpy as np


def load_frames(path, width=320):
    ext = os.path.splitext(path)[1].lower()
    frames, fps = [], None
    if ext in (".gif", ".webp"):
        from PIL import Image
        im = Image.open(path)
        durs = []
        for i in range(getattr(im, "n_frames", 1)):
            im.seek(i)
            durs.append(im.info.get("duration") or 0)
            fr = np.asarray(im.convert("RGB"))[:, :, ::-1]
            frames.append(fr)
        d = [x for x in durs if x]
        fps = 1000.0 / (sum(d) / len(d)) if d else 15.0
    else:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        while True:
            ok, f = cap.read()
            if not ok:
                break
            frames.append(f)
    if not frames:
        raise SystemExit(f"could not read any frames from {path}")
    h0, w0 = frames[0].shape[:2]
    small = [cv2.resize(f, (width, int(h0 * width / w0)), interpolation=cv2.INTER_AREA) for f in frames]
    return small, fps


def ranges(idx):
    out, s = [], None
    for i in idx:
        if s is None:
            s, p = i, i
        elif i == p + 1:
            p = i
        else:
            out.append((s, p))
            s, p = i, i
    if s is not None:
        out.append((s, p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("--out", default="ref_report")
    ap.add_argument("--sheet-frames", type=int, default=24)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fr, fps = load_frames(a.reference)
    n = len(fr)
    g = [cv2.cvtColor(cv2.resize(f, (160, 90)), cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
    d = np.array([float(np.mean(np.abs(g[i] - g[i - 1]))) for i in range(1, n)])
    med = float(np.median(d)) if len(d) else 0.0
    pauses = ranges([i + 2 for i, x in enumerate(d) if x < 0.35 * max(med, 0.5)])
    pauses = [(s, e) for s, e in pauses if e - s >= 2]
    cuts = [i + 2 for i, x in enumerate(d) if x > max(6 * med, 25)]
    # chapters: split at cuts, otherwise at the largest change of smoothed motion level
    sm = np.convolve(d, np.ones(5) / 5, mode="same") if len(d) >= 5 else d
    chapters, start = [], 1
    for c in cuts + [n + 1]:
        if c - start >= 3:
            seg = d[start - 1:c - 2] if c - 2 > start - 1 else d[start - 1:start]
            chapters.append({"frames": [start, c - 1], "mean_motion": round(float(np.mean(seg)), 2) if len(seg) else 0})
        start = c
    rep = {"file": os.path.basename(a.reference), "frames": n, "fps": round(fps, 2), "duration_s": round(n / fps, 2),
           "size_hint": list(fr[0].shape[1::-1]), "median_motion": round(med, 2),
           "max_motion": round(float(d.max()), 2) if len(d) else 0,
           "pauses": [{"frames": [s, e], "seconds": [round((s - 1) / fps, 2), round((e - 1) / fps, 2)]} for s, e in pauses],
           "hard_cuts_at_frames": cuts, "chapters": chapters,
           "reading": []}
    if not cuts:
        rep["reading"].append("No hard cuts: the reference is ONE continuous move (this is what a scroll hero needs).")
    else:
        rep["reading"].append(f"{len(cuts)} hard cut(s): the reference mixes shots; decide whether to copy the cuts or replace them with one continuous move.")
    if pauses:
        rep["reading"].append("Pauses are where the person stopped scrolling; they are not part of the design.")
    rep["reading"].append("Now open reference_sheet.jpg and fill references/reference-analysis.md.")
    json.dump(rep, open(os.path.join(a.out, "reference_report.json"), "w", encoding="utf-8"), indent=2)

    k = min(a.sheet_frames, n)
    idx = np.linspace(0, n - 1, k).round().astype(int)
    tiles = []
    for i in idx:
        t = cv2.resize(fr[i], (320, int(320 * fr[i].shape[0] / fr[i].shape[1])))
        cv2.putText(t, str(i + 1), (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(t, str(i + 1), (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        tiles.append(t)
    cols = 5
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[r * cols:(r + 1) * cols]) for r in range(len(tiles) // cols)])
    cv2.imwrite(os.path.join(a.out, "reference_sheet.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(json.dumps({k: v for k, v in rep.items() if k != "reading"}, indent=1))
    print("\n".join(rep["reading"]))
    print(f"\nReport: {a.out}/reference_report.json   Sheet: {a.out}/reference_sheet.jpg")


if __name__ == "__main__":
    main()
