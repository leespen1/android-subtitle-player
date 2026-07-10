#!/usr/bin/env python3
"""Generate Google Play listing graphics into play/.

  play/icon-512.png            512x512 high-res app icon
  play/feature-graphic.png     1024x500 feature graphic

Reuses the icon artwork from gen-native-icons.py so everything stays on-brand.
"""
import importlib.util
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("gni", os.path.join(HERE, "gen-native-icons.py"))
gni = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gni)

BG = gni.BG
AMBER = gni.AMBER
DIM = (154, 135, 95)
FONT = gni.FONT_PATHS[0]


def font(px):
    return ImageFont.truetype(FONT, px)


def store_icon():
    # Full-bleed square; Google Play applies its own corner rounding.
    return gni.render(512, 0.80, "solid")


def feature_graphic():
    W, H = 1024, 500
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    # App icon badge on the left (rounded, like the launcher icon).
    badge = gni.render(400, 0.86, "rounded")
    img.alpha_composite(badge, (70, (H - 400) // 2))

    # Title + tagline on the right.
    tx = 70 + 400 + 56
    title = font(72)
    tagline = font(28)
    d.text((tx, 170), "Subtitle", font=title, fill=AMBER)
    d.text((tx, 170 + 82), "Player", font=title, fill=AMBER)

    # Wrap the tagline within the remaining width.
    max_w = W - tx - 40
    words = "Read movie subtitles on your phone while the film plays on the TV.".split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=tagline) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    ty = 170 + 82 * 2 + 22
    for ln in lines:
        d.text((tx, ty), ln, font=tagline, fill=DIM)
        ty += 36
    return img.convert("RGB")


def main():
    os.makedirs("play", exist_ok=True)
    # Play wants a 32-bit PNG with no transparency; flatten to opaque RGB.
    store_icon().convert("RGB").save("play/icon-512.png")
    feature_graphic().save("play/feature-graphic.png")
    print("wrote play/icon-512.png play/feature-graphic.png")


if __name__ == "__main__":
    main()
