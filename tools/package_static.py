#!/usr/bin/env python3
"""Build the site as a fully static export and wrap it in a portable folder you can copy to a USB stick.

Usage:  python tools/package_static.py path/to/site --out dist-usb [--name "Brand"] [--bundle-node]

What you get:  <out>/site (static files), server.js + server.py (tiny servers WITH HTTP Range support, which
the scroll video needs), start-windows.bat, start-mac-linux.command, README.txt, and optionally node/node.exe
(a copy of the Node.js on this machine so the target Windows laptop needs no install).
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "templates", "usb")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--out", default="dist-usb")
    ap.add_argument("--name", default="Site")
    ap.add_argument("--bundle-node", action="store_true")
    a = ap.parse_args()
    site = os.path.abspath(a.site)
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        sys.exit("npm was not found. Install Node.js to build the static export.")
    shutil.rmtree(os.path.join(site, "out"), ignore_errors=True)
    r = subprocess.run([npm, "run", "build"], cwd=site, env=dict(os.environ, EXPORT="1"))
    if r.returncode or not os.path.isdir(os.path.join(site, "out")):
        sys.exit("static export failed (is output:'export' enabled for EXPORT=1 in next.config.mjs?)")
    out = os.path.abspath(a.out)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    shutil.copytree(os.path.join(site, "out"), os.path.join(out, "site"))
    for f in os.listdir(TPL):
        shutil.copy2(os.path.join(TPL, f), os.path.join(out, f))
    readme = os.path.join(out, "README.txt")
    txt = open(readme, encoding="utf-8").read().replace("{{NAME}}", a.name)
    if a.bundle_node:
        node = shutil.which("node")
        if node and os.name == "nt":
            os.makedirs(os.path.join(out, "node"))
            shutil.copy2(node, os.path.join(out, "node", "node.exe"))
        else:
            print("  (--bundle-node only copies node.exe on Windows; skipped)")
    open(readme, "w", encoding="utf-8").write(txt)
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs) / 1048576
    print(f"\nPackage ready: {out} ({size:.0f} MB). Copy the whole folder to the USB stick.")


if __name__ == "__main__":
    main()
