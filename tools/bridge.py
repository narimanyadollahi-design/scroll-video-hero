#!/usr/bin/env python3
"""Build a seam bridge A -> mid -> B with optical-flow frame interpolation.

Usage: python tools/bridge.py OUT_DIR A.png MID1.png [MID2.png ...] B.png

Frames are allocated per segment in proportion to the measured camera distance, so speed stays constant.
Writes OUT_DIR/0001.png ... (exclusive of A and B themselves); the real key images are inserted as frames.
"""
import sys
import os
import cv2
import numpy as np


def load(path, w, h):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    if im is None:
        raise SystemExit(f"cannot read {path}")
    ih, iw = im.shape[:2]
    # centre-crop to 16:9 then resize
    target = w / h
    if abs(iw / ih - target) > 1e-3:
        nw = int(round(ih * target))
        x0 = (iw - nw) // 2
        im = im[:, x0:x0 + nw]
    return cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA if im.shape[1] > w else cv2.INTER_LANCZOS4)


def flow(a, b, dis):
    ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    fl = dis.calc(ga, gb, None)
    sg = float(os.environ.get("BRIDGE_SMOOTH", 0))
    if sg > 0:
        # camera motion in a static scene is smooth: low-pass the flow so repetitive stripes cannot pull it off
        fl = cv2.GaussianBlur(fl, (0, 0), sg)
    return fl


def warp(img, fl):
    h, w = img.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    mx = (gx + fl[..., 0]).astype(np.float32)
    my = (gy + fl[..., 1]).astype(np.float32)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def interp(p0, p1, t, f01, f10):
    # flows from the target (time t) back to p0 and p1 (Jiang et al. approximation)
    ft0 = -(1 - t) * t * f01 + t * t * f10
    ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
    w0 = warp(p0, ft0)
    w1 = warp(p1, ft1)
    a = w0.astype(np.float32)
    b = w1.astype(np.float32)
    # occlusion-aware blend: where the two warps disagree, trust the temporally nearer frame
    err = cv2.GaussianBlur(np.abs(a - b).mean(axis=2), (0, 0), 3)
    bad = np.clip((err - 12.0) / 24.0, 0, 1)[..., None]
    plain = (1 - t) * a + t * b
    near = a if t < 0.5 else b
    return (1 - bad) * plain + bad * near


def segment(p0, p1, steps, dis):
    """Return `steps-1` frames strictly between p0 and p1."""
    f01 = flow(p0, p1, dis)
    f10 = flow(p1, p0, dis)
    out = []
    for j in range(1, steps):
        t = j / steps
        out.append(np.clip(interp(p0, p1, t, f01, f10), 0, 255).astype(np.uint8))
    return out


def distance(a, b):
    """Rough camera distance between two frames, in 'normal-motion frames' (24 fps clip scale)."""
    ga = cv2.cvtColor(cv2.resize(a, (160, 90), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    gb = cv2.cvtColor(cv2.resize(b, (160, 90), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    return 12 * (float(np.mean((ga - gb) ** 2)) / 705.3) ** 0.5


def main():
    # usage: bridge.py OUT_DIR KEY1 KEY2 [KEY3 ...]   (first = real last frame A, last = real first frame B)
    out_dir = sys.argv[1]
    keys = sys.argv[2:]
    w, h = int(os.environ.get("BRIDGE_W", 1280)), int(os.environ.get("BRIDGE_H", 720))
    os.makedirs(out_dir, exist_ok=True)
    imgs = [load(k, w, h) for k in keys]
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    dis.setFinestScale(int(os.environ.get("BRIDGE_FINEST", 0)))
    dis.setPatchSize(int(os.environ.get("BRIDGE_PATCH", 12)))
    dis.setPatchStride(max(2, int(os.environ.get("BRIDGE_PATCH", 12)) // 3))
    dis.setVariationalRefinementIterations(int(os.environ.get("BRIDGE_VAR", 10)))
    dists = [distance(imgs[i], imgs[i + 1]) for i in range(len(imgs) - 1)]
    scale = float(os.environ.get("BRIDGE_SCALE", 1.0))
    total = max(len(dists) * 2, int(round(sum(dists) * scale)))
    va = float(os.environ.get("BRIDGE_VA", 1.0))   # relative speed at the start (matches clip A end)
    vb = float(os.environ.get("BRIDGE_VB", 1.0))   # relative speed at the end (matches clip B start)
    cum = np.cumsum([0.0] + dists)
    flows = {}
    def pos(u):
        # position along path for normalised time u with linearly varying speed va -> vb
        return (va * u + (vb - va) * u * u / 2) / ((va + vb) / 2)
    frames = []
    for k in range(1, total):
        x = pos(k / total) * cum[-1]
        i = min(int(np.searchsorted(cum, x, side="right") - 1), len(dists) - 1)
        t = (x - cum[i]) / max(dists[i], 1e-6)
        t = min(max(t, 0.0), 1.0)
        if i not in flows:
            flows[i] = (flow(imgs[i], imgs[i + 1], dis), flow(imgs[i + 1], imgs[i], dis))
        f01, f10 = flows[i]
        if t <= 0.0:
            fr = imgs[i]
        elif t >= 1.0:
            fr = imgs[i + 1]
        else:
            fr = np.clip(interp(imgs[i], imgs[i + 1], t, f01, f10), 0, 255).astype(np.uint8)
        frames.append(fr)
    for i, f in enumerate(frames, 1):
        cv2.imwrite(os.path.join(out_dir, f"{i:04d}.png"), f)
    print(f"{len(frames)} frames; segment distances {[round(x) for x in dists]}")


if __name__ == "__main__":
    main()
