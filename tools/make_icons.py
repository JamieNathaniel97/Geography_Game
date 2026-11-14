"""Draws the app icons (a globe with a green "found it" pin) into icons/. Run: python tools/make_icons.py"""
import math, pathlib
from PIL import Image, ImageDraw

OUT = pathlib.Path(__file__).resolve().parent.parent / "icons"
BG, SEA, LINE, PIN = (23, 38, 43), (207, 227, 234), (31, 111, 139), (47, 158, 85)

def icon(size):
    s = 4  # draw big, then shrink for smooth edges
    W = size * s
    im = Image.new("RGB", (W, W), BG)
    d = ImageDraw.Draw(im)
    c, r = W / 2, W * 0.32  # keeps the globe inside the maskable safe zone
    d.ellipse([c - r, c - r, c + r, c + r], fill=SEA)
    lw = max(2, int(W * 0.012))
    for k in (-0.6, 0, 0.6):  # parallels
        y = c + r * k
        half = math.sqrt(max(0, r * r - (y - c) ** 2))
        d.line([c - half, y, c + half, y], fill=LINE, width=lw)
    for k in (0.45, 1.0):  # meridians
        rx = r * k
        d.ellipse([c - rx, c - r, c + rx, c + r], outline=LINE, width=lw)
    d.ellipse([c - r, c - r, c + r, c + r], outline=LINE, width=lw)
    pr = W * 0.075  # pin
    px, py = c + r * 0.38, c - r * 0.3
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=PIN, outline=BG, width=int(W * 0.015))
    return im.resize((size, size), Image.LANCZOS)

OUT.mkdir(exist_ok=True)
icon(192).save(OUT / "icon-192.png")
icon(512).save(OUT / "icon-512.png")
icon(180).save(OUT / "apple-touch-icon.png")
print("icons written")
