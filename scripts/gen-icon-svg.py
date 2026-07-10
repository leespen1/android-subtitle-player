#!/usr/bin/env python3
"""Generate a vector adaptive-icon foreground (SVG) for Subtitle Player.

Everything is emitted as plain <path> elements so it converts cleanly to an
Android VectorDrawable (which stays crisp at any launcher size, unlike the
raster mipmaps). The "Subtitle Player" text is converted to outline paths with
fontTools, so no font is needed at render time.

Pipeline (see scripts/build-vector-icon.sh):
  gen-icon-svg.py -> assets/icon-foreground.svg
  svg2vectordrawable -> res/drawable/ic_launcher_foreground.xml
"""
import math

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

AMBER = "#F0CF94"
PANEL = "#12100D"
WHITE = "#F0EEEE"
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

V = 108.0            # VectorDrawable viewport (dp)
CF = 0.70            # art fills 70% of the canvas, centred (safe-zone aware)
CS = CF * V
OFF = (V - CS) / 2.0


def fx(f):
    return OFF + f * CS


def rrect_path(x0, y0, x1, y1, r):
    """Path data for a rounded rectangle."""
    return (
        f"M{x0 + r:.3f},{y0:.3f} "
        f"H{x1 - r:.3f} A{r:.3f},{r:.3f} 0 0 1 {x1:.3f},{y0 + r:.3f} "
        f"V{y1 - r:.3f} A{r:.3f},{r:.3f} 0 0 1 {x1 - r:.3f},{y1:.3f} "
        f"H{x0 + r:.3f} A{r:.3f},{r:.3f} 0 0 1 {x0:.3f},{y1 - r:.3f} "
        f"V{y0 + r:.3f} A{r:.3f},{r:.3f} 0 0 1 {x0 + r:.3f},{y0:.3f} Z"
    )


def squiggle_path(x0, x1, y, amp, wavelength):
    pts = []
    n = 64
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        pts.append((x, y + amp * math.sin(2 * math.pi * (x - x0) / wavelength)))
    d = "M" + " L".join(f"{px:.3f},{py:.3f}" for px, py in pts)
    return d


class Text:
    def __init__(self, path):
        self.font = TTFont(path)
        self.upm = self.font["head"].unitsPerEm
        self.asc = self.font["hhea"].ascent
        self.desc = self.font["hhea"].descent  # negative
        self.cmap = self.font.getBestCmap()
        self.gs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]

    def advance(self, s):
        return sum(self.hmtx[self.cmap[ord(c)]][0] for c in s)

    def line_height(self):
        return self.asc - self.desc

    def path(self, s, scale, start_x, baseline):
        """Outline path for a string, transformed into viewport coords.

        scale is viewport units per em; glyph outlines are in font units, so
        the per-unit factor is scale / units-per-em.
        """
        factor = scale / self.upm
        pen = SVGPathPen(self.gs)
        penx = 0.0
        for c in s:
            gname = self.cmap[ord(c)]
            # map glyph space (font units, y-up) to viewport (y-down)
            m = (factor, 0, 0, -factor, start_x + penx * factor, baseline)
            self.gs[gname].draw(TransformPen(pen, m))
            penx += self.hmtx[gname][0]
        return pen.getCommands()


def build():
    txt = Text(FONT)
    paths = []  # (d, fill, stroke, stroke_width, round_caps)

    # TV outline
    tv = (fx(0.075), fx(0.09), fx(0.925), fx(0.62))
    paths.append((rrect_path(*tv, CS * 0.03), "none", WHITE, CS * 0.020, False))

    # App name, two lines, sized to fill the TV
    lines = ["Subtitle", "Player"]
    tv_w, tv_h = tv[2] - tv[0], tv[3] - tv[1]
    inner_w, inner_h = tv_w * 0.90, tv_h * 0.88
    upm = txt.upm
    widest = max(txt.advance(s) for s in lines) / upm
    lh = txt.line_height() / upm
    scale = min(inner_w / widest, inner_h / (2 * lh))
    line_px = txt.line_height() / upm * scale
    asc_px = txt.asc / upm * scale
    cx = (tv[0] + tv[2]) / 2
    top = (tv[1] + tv[3]) / 2 - line_px  # centre the two-line block
    for i, s in enumerate(lines):
        w = txt.advance(s) / upm * scale
        baseline = top + i * line_px + asc_px
        paths.append((txt.path(s, scale, cx - w / 2, baseline), WHITE, "none", 0, False))

    # Phone with subtitle squiggles
    ph = (fx(0.31), fx(0.69), fx(0.69), fx(0.93))
    paths.append((rrect_path(*ph, CS * 0.035), PANEL, WHITE, CS * 0.016, False))
    pw, phh = ph[2] - ph[0], ph[3] - ph[1]
    pad = pw * 0.16
    left, right = ph[0] + pad, ph[2] - pad
    for i, frac in enumerate((1.0, 0.72, 0.52)):
        y = ph[1] + phh * (0.28 + i * 0.22)
        d = squiggle_path(left, left + (right - left) * frac, y, phh * 0.045, pw * 0.30)
        paths.append((d, "none", AMBER, CS * 0.014, True))

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{V:.0f}" height="{V:.0f}" '
        f'viewBox="0 0 {V:.0f} {V:.0f}">'
    ]
    for d, fill, stroke, sw, round_caps in paths:
        attrs = [f'd="{d}"', f'fill="{fill}"']
        if stroke != "none":
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw:.3f}"')
            if round_caps:
                attrs.append('stroke-linecap="round" stroke-linejoin="round"')
        out.append(f"  <path {' '.join(attrs)}/>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with open("assets/icon-foreground.svg", "w") as f:
        f.write(build())
    print("wrote assets/icon-foreground.svg")
