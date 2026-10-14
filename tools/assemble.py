#!/usr/bin/env python3
"""Assemble one seamless master video from clips, hand-made gap clips and optical-flow bridges.

Usage:  python tools/assemble.py recipe.json

Recipe (see examples/recipe.example.json):
  {
    "out_dir": "work", "size": [1920, 1080], "fps": 24, "crf": 10,
    "segments": [
      {"type": "clip",   "src": "clips/01.mp4", "start": 0, "end": 95, "label": "clip 1"},
      {"type": "bridge", "keys": ["clips/01.mp4#95", "mid.png", "clips/02.mp4#0"], "scale": 1.0, "label": "bridge 1"},
      {"type": "clip",   "src": "gap.mp4", "retime": [4.0, 1.7], "label": "gap clip"}
    ],
    "equalize": {"target": 1.5, "maxskip": 4}
  }

 * start/end are 0-based and inclusive. Keys are 'video.mp4#frame' or an image path.
 * retime=[f0,f1]: skip factor at the start/end of the clip (1 = unchanged, 4 = 4x faster). Frames are only skipped.
 * bridge: smooth-flow interpolation tuned for repetitive textures (stripes). 'scale' multiplies the frame count.
 * equalize: drops frames wherever the camera is slower than the target speed, so there are no stalls at seams.
Writes <out_dir>/master.mp4 (or master_eq.mp4) and <out_dir>/master.map.json (label ranges, final frame numbers, 1-based).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np

import svh

HERE = os.path.dirname(os.path.abspath(__file__))


def vf_norm(w, h, fps):
    return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps}"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    svh.need_ffmpeg()
    rp = os.path.abspath(sys.argv[1])
    cfg = json.load(open(rp, encoding="utf-8"))
    base = os.path.dirname(rp)

    def P(p):
        return p if os.path.isabs(p) else os.path.join(base, p)

    out = P(cfg.get("out_dir", "work"))
    w, h = cfg.get("size", [1920, 1080])
    fps, crf = cfg.get("fps", 24), cfg.get("crf", 10)
    for d in ("pieces", "keys", "bridges"):
        os.makedirs(f"{out}/{d}", exist_ok=True)
    x264 = ["-an", "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p"]

    pieces, labels = [], []
    for n, seg in enumerate(cfg["segments"], 1):
        label = seg.get("label", f"{seg['type']} {n}")
        piece = f"{out}/pieces/{n:02d}.mp4"
        t = seg["type"]
        if t == "clip":
            src = P(seg["src"])
            a = seg.get("start", 0)
            b = seg.get("end", svh.frame_count(src) - 1)
            if seg.get("retime"):
                f0, f1 = seg["retime"]
                cap = cv2.VideoCapture(src)
                frames = []
                while True:
                    ok, f = cap.read()
                    if not ok:
                        break
                    frames.append(f)
                frames = frames[a:b + 1]
                nfr = len(frames)
                total = max(2, int(round((nfr - 1) / ((f0 + f1) / 2))))
                picks, pos = [0], 0.0
                for k in range(1, total + 1):
                    pos = min(nfr - 1, pos + f0 + (f1 - f0) * k / total)
                    picks.append(int(round(pos)))
                picks[-1] = nfr - 1
                tmp = f"{out}/pieces/{n:02d}_png"
                shutil.rmtree(tmp, ignore_errors=True)
                os.makedirs(tmp)
                for i, pk in enumerate(picks, 1):
                    cv2.imwrite(f"{tmp}/{i:04d}.png", frames[pk])
                svh.run("ffmpeg", "-v", "error", "-y", "-framerate", fps, "-i", tmp + "/%04d.png", "-vf", vf_norm(w, h, fps), *x264, piece)
                shutil.rmtree(tmp, ignore_errors=True)
            else:
                vf = f"trim=start_frame={a}:end_frame={b + 1},setpts=PTS-STARTPTS," + vf_norm(w, h, fps)
                svh.run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, *x264, piece)
        elif t == "bridge":
            keys = []
            for k in seg["keys"]:
                if "#" in k:
                    path, idx = k.rsplit("#", 1)
                    k = P(path) + "#" + idx
                else:
                    k = P(k)
                keys.append(svh.resolve_key(k, out + "/keys"))
            params = {k: seg.get(k) for k in ("scale", "va", "vb", "smooth", "finest", "patch", "var")}
            sig = hashlib.sha1((json.dumps(params, sort_keys=True) + "|".join(
                f"{k}:{os.path.getsize(k)}:{int(os.path.getmtime(k))}" for k in keys) + f"{w}x{h}").encode()).hexdigest()[:12]
            od = f"{out}/bridges/{sig}"
            if not (os.path.isdir(od) and os.listdir(od)):
                env = dict(os.environ, BRIDGE_W=str(w), BRIDGE_H=str(h), BRIDGE_SCALE=str(seg.get("scale", 1.0)),
                           BRIDGE_VA=str(seg.get("va", 1.0)), BRIDGE_VB=str(seg.get("vb", 1.0)),
                           BRIDGE_SMOOTH=str(seg.get("smooth", 20)), BRIDGE_FINEST=str(seg.get("finest", 2)),
                           BRIDGE_PATCH=str(seg.get("patch", 24)), BRIDGE_VAR=str(seg.get("var", 5)))
                r = subprocess.run([sys.executable, os.path.join(HERE, "bridge.py"), od] + keys, env=env, capture_output=True, text=True)
                if r.returncode:
                    sys.exit(f"bridge failed: {r.stderr[-400:]}")
                print(f"  {label}: {r.stdout.strip()}")
            svh.run("ffmpeg", "-v", "error", "-y", "-framerate", fps, "-i", od + "/%04d.png", "-vf", vf_norm(w, h, fps), *x264, piece)
        else:
            sys.exit(f"unknown segment type: {t}")
        pieces.append(piece)
        labels.append(label)
        print(f"  [{n}/{len(cfg['segments'])}] {label}")

    counts = [svh.frame_count(p) for p in pieces]
    lst = out + "/list.txt"
    with open(lst, "w") as fh:
        for p in pieces:
            fh.write("file '" + os.path.abspath(p).replace("\\", "/") + "'\n")
    master = out + "/master.mp4"
    svh.run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", crf, "-pix_fmt", "yuv420p", master)

    seg_of_frame = []
    for lab, c in zip(labels, counts):
        seg_of_frame += [lab] * c
    final = master
    if cfg.get("equalize"):
        eq = cfg["equalize"]
        final = out + "/master_eq.mp4"
        env = dict(os.environ, MAXSKIP=str(eq.get("maxskip", 4)))
        r = subprocess.run([sys.executable, os.path.join(HERE, "equalize_speed.py"), master, final, str(eq.get("target", 1.5))],
                           env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stderr[-400:])
        print("  " + r.stdout.splitlines()[0])
        picks = np.load(os.path.splitext(final)[0] + "_picks.npy")
        seg_of_frame = [seg_of_frame[int(i)] for i in picks]

    ranges, st = [], 0
    for i in range(1, len(seg_of_frame) + 1):
        if i == len(seg_of_frame) or seg_of_frame[i] != seg_of_frame[st]:
            ranges.append({"label": seg_of_frame[st], "start": st + 1, "end": i})
            st = i
    with open(out + "/master.map.json", "w", encoding="utf-8") as fh:
        json.dump({"video": os.path.basename(final), "fps": fps, "frames": len(seg_of_frame), "segments": ranges}, fh, indent=2, ensure_ascii=False)
    print(f"\nMaster: {final}  ({len(seg_of_frame)} frames, {len(seg_of_frame) / fps:.1f}s)\nMap:    {out}/master.map.json")


if __name__ == "__main__":
    main()
