#!/usr/bin/env python3
"""Generate source icons for @capacitor/assets from the Subtitle Player design.

Emits three 1024x1024 PNGs into assets/:
  - icon-background.png : solid dark background (adaptive-icon back layer)
  - icon-foreground.png : the TV + phone artwork, transparent, sized to sit
                          inside the adaptive-icon safe zone (front layer)
  - icon-only.png       : the full composited icon for legacy launchers

`npx @capacitor/assets generate --android` then turns these into the res/
mipmaps. Keep the artwork in sync with the web app's make-icons.py.
"""
import math
from PIL import Image, ImageDraw, ImageFont

BG = (8, 7, 6)
PANEL = (18, 16, 13)
AMBER = (240, 207, 148)
WHITE = (240, 240, 238)
SS = 4

FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(px):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, px)
        except OSError:
            continue
    return ImageFont.load_default()


def text_w(font, s):
    b = font.getbbox(s)
    return b[2] - b[0]


def fit_font(lines, max_w, max_h):
    best, size = load_font(8), 8
    while size < max_h:
        f = load_font(size)
        asc, desc = f.getmetrics()
        if max(text_w(f, ln) for ln in lines) > max_w or (asc + desc) * len(lines) > max_h:
            break
        best, size = f, size + 2
    return best


def squiggle(draw, x0, x1, y, amp, wavelength, width, fill):
    pts, x = [], x0
    step = max(1, int((x1 - x0) / 80))
    while x <= x1:
        pts.append((x, y + amp * math.sin(2 * math.pi * (x - x0) / wavelength)))
        x += step
    draw.line(pts, fill=fill, width=width, joint="curve")


def draw_art(d, ox, oy, cs):
    """Draw the TV + phone artwork inside a content box of side cs at (ox, oy)."""
    fx = lambda f: ox + f * cs
    fy = lambda f: oy + f * cs
    stroke = max(2, int(cs * 0.02))

    tv = [fx(0.075), fy(0.09), fx(0.925), fy(0.62)]
    d.rounded_rectangle(tv, radius=cs * 0.03, outline=WHITE, width=stroke)
    lines = ["Subtitle", "Player"]
    font = fit_font(lines, (tv[2] - tv[0]) * 0.90, (tv[3] - tv[1]) * 0.88)
    asc, desc = font.getmetrics()
    line_h = asc + desc
    ty = (tv[1] + tv[3]) / 2 - line_h * len(lines) / 2
    cx = (tv[0] + tv[2]) / 2
    for ln in lines:
        d.text((cx, ty), ln, font=font, fill=WHITE, anchor="ma")
        ty += line_h

    phone = [fx(0.31), fy(0.69), fx(0.69), fy(0.93)]
    d.rounded_rectangle(phone, radius=cs * 0.035, fill=PANEL,
                        outline=WHITE, width=max(2, int(cs * 0.016)))
    pw, ph = phone[2] - phone[0], phone[3] - phone[1]
    pad = pw * 0.16
    left, right = phone[0] + pad, phone[2] - pad
    for i, frac in enumerate((1.0, 0.72, 0.52)):
        y = phone[1] + ph * (0.28 + i * 0.22)
        squiggle(d, left, left + (right - left) * frac, y,
                 ph * 0.045, pw * 0.30, max(2, int(cs * 0.014)), AMBER)


def render(size, content_fraction, background, ss=SS):
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if background == "solid":
        d.rectangle([0, 0, s, s], fill=BG)
    elif background == "rounded":
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=s * 0.22, fill=BG)
    cs = content_fraction * s
    off = (s - cs) / 2
    if content_fraction > 0:
        draw_art(d, off, off, cs)
    return img.resize((size, size), Image.LANCZOS)


def main():
    # Adaptive front layer: artwork only. The design is a wide rectangle, so it
    # is scaled to keep even its corners inside the adaptive safe circle (a
    # circular launcher mask must not clip the TV frame).
    render(1024, 0.52, None).save("assets/icon-foreground.png")
    # Adaptive back layer: solid colour, no artwork.
    render(1024, 0.0, "solid").save("assets/icon-background.png")
    # Legacy icon: full composited badge.
    render(1024, 0.86, "rounded").save("assets/icon-only.png")
    # Splash: dark background with the artwork centered small, so there is no
    # white flash before the WebView loads. Same image for light and dark mode.
    splash = render(2732, 0.30, "solid", ss=2)
    splash.save("assets/splash.png")
    splash.save("assets/splash-dark.png")
    print("wrote icon-foreground/background/only + splash into assets/")


if __name__ == "__main__":
    main()
