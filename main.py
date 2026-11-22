#!/usr/bin/env python3
"""SUNDAY PLANET - one image that sums up the world news of 22 November 2026.

Magazine-cover / infographic style: a drawn globe for the COP31 climate
talks in Antalya, a giant headline, the summit president's own words, the
fight inside the draft, and the day's other big stories as number cards
(IG Metall's strike call in Germany, US deportees arriving in Liberia).

Pure Python 3 standard library. Writes entry.png into the directory named
by MAKEFUN_OUTPUT_DIR (default /output). Fully deterministic: the same
bytes on every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# --------------------------------------------------------------------------
# 5x7 block typeface, drawn by hand for this program.
# Each glyph is 7 rows of 5 pixels; text advances 6 pixels per character.
# --------------------------------------------------------------------------

FONT = {
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "B": ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "G": [".XXXX", "X....", "X....", "X..XX", "X...X", "X...X", ".XXX."],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "J": ["XXXXX", "....X", "....X", "....X", "....X", "X...X", ".XXX."],
    "K": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "N": ["X...X", "XX..X", "XX..X", "X.X.X", "X..XX", "X..XX", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "Q": [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "V": ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    "W": ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "X.X.X", ".X.X."],
    "X": ["X...X", ".X.X.", "..X..", "..X..", "..X..", ".X.X.", "X...X"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "Z": ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    "0": [".XXX.", "X...X", "X..XX", "X.X.X", "XX..X", "X...X", ".XXX."],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "2": [".XXX.", "X...X", "....X", "..XX.", ".X...", "X....", "XXXXX"],
    "3": ["XXXXX", "...X.", "..X..", "...X.", "....X", "X...X", ".XXX."],
    "4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
    "5": ["XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."],
    "6": [".XXX.", "X....", "X....", "XXXX.", "X...X", "X...X", ".XXX."],
    "7": ["XXXXX", "....X", "...X.", "..X..", "..X..", "..X..", "..X.."],
    "8": [".XXX.", "X...X", "X...X", ".XXX.", "X...X", "X...X", ".XXX."],
    "9": [".XXX.", "X...X", "X...X", ".XXXX", "....X", "....X", ".XXX."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".XX..", ".XX.."],
    ",": [".....", ".....", ".....", ".....", ".XX..", ".XX..", ".X..."],
    ":": [".....", ".XX..", ".XX..", ".....", ".XX..", ".XX..", "....."],
    ";": [".....", ".XX..", ".XX..", ".....", ".XX..", ".XX..", ".X..."],
    "'": ["..X..", "..X..", ".X...", ".....", ".....", ".....", "....."],
    '"': [".X.X.", ".X.X.", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "XXXXX", ".....", ".....", "....."],
    "\u2014": [".....", ".....", ".....", "XXXXX", ".....", ".....", "....."],
    "\u00b7": [".....", ".....", ".....", "..X..", ".....", ".....", "....."],
    "$": ["..X..", ".XXXX", "X.X.X", ".XXX.", "..X.X", "X.X.X", ".XXX."],
    "%": ["XX..X", "XX.X.", "....X", "...X.", "..X..", ".X...", "X..XX"],
    "/": ["....X", "....X", "...X.", "..X..", ".X...", "X....", "X...."],
    "(": ["..XX.", ".X...", "X....", "X....", "X....", ".X...", "..XX."],
    ")": [".XX..", "...X.", "....X", "....X", "....X", "...X.", ".XX.."],
    "!": ["..X..", "..X..", "..X..", "..X..", "..X..", ".....", "..X.."],
    "?": [".XXX.", "X...X", "....X", "..XX.", "..X..", ".....", "..X.."],
    "&": [".XX..", "X..X.", "X.X..", ".X...", "X.X.X", "X..X.", ".XX.X"],
    "+": [".....", "..X..", "..X..", ".XXX.", "..X..", "..X..", "....."],
    "\u00dc": [".X.X.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "\u0130": ["..X..", ".....", "XXXXX", "..X..", "..X..", "..X..", "XXXXX"],
}


def text_width(text, scale):
    """Pixel width of a string in the block typeface."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


# --------------------------------------------------------------------------
# Pixel canvas and PNG writer (standard library only).
# --------------------------------------------------------------------------


class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.px = bytearray(color) * (width * height)

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def get(self, x, y):
        i = (y * self.width + x) * 3
        return self.px[i], self.px[i + 1], self.px[i + 2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            if 0 <= yy < self.height:
                base = yy * self.width
                for xx in range(x, x + w):
                    if 0 <= xx < self.width:
                        i = (base + xx) * 3
                        self.px[i] = color[0]
                        self.px[i + 1] = color[1]
                        self.px[i + 2] = color[2]

    def frame(self, x, y, w, h, thick, color):
        self.rect(x, y, w, thick, color)
        self.rect(x, y + h - thick, w, thick, color)
        self.rect(x, y, thick, h, color)
        self.rect(x + w - thick, y, thick, h, color)

    def disc(self, cx, cy, r, color, clip=None):
        """Filled circle; if clip=(ccx, ccy, cr) is given, only pixels
        inside that circle are painted."""
        r2 = r * r
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            span = int((r2 - dy * dy) ** 0.5) if r2 - dy * dy >= 0 else -1
            if span < 0:
                continue
            for xx in range(cx - span, cx + span + 1):
                if clip is not None:
                    ccx, ccy, cr = clip
                    if (xx - ccx) ** 2 + (yy - ccy) ** 2 > cr * cr:
                        continue
                self.set(xx, yy, color)

    def ring(self, cx, cy, r, thick, color):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - thick <= d <= r:
                    self.set(xx, yy, color)


def write_png(canvas, path):
    """Encode the canvas as a PNG with zlib/struct only."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.width,
                                      canvas.height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# --------------------------------------------------------------------------
# Palette and text drawing.
# --------------------------------------------------------------------------

PAPER = (247, 240, 220)
CARD = (255, 253, 246)
INK = (20, 32, 54)
RED = (179, 49, 42)
TEAL = (14, 106, 120)
OCEAN = (43, 141, 168)
OCEAN_LINE = (28, 110, 136)
LAND = (84, 158, 92)
LAND_DARK = (60, 126, 72)
GOLD = (203, 148, 46)
GREY = (96, 96, 88)


def draw_text(cv, x, y, text, scale, color, align="left"):
    """Draw text in the block typeface; align may be left/center/right."""
    w = text_width(text, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == "X":
                    cv.rect(x + col_i * scale, y + row_i * scale,
                            scale, scale, color)
        x += 6 * scale
    return w


def centered(cv, y, text, scale, color):
    draw_text(cv, W // 2, y, text, scale, color, align="center")


# --------------------------------------------------------------------------
# The globe motif for the climate talks.
# --------------------------------------------------------------------------


def draw_globe(cv, cx, cy, r):
    cv.disc(cx, cy, r, OCEAN)
    # Latitude bands: flattened ellipses across the disc.
    for frac in (-0.62, -0.31, 0.0, 0.31, 0.62):
        ly = cy + int(frac * r)
        rx = int(r * (1.0 - frac * frac) ** 0.5)
        ry = max(2, int(rx * 0.16))
        for xx in range(cx - rx, cx + rx + 1):
            t = (xx - cx) / rx if rx else 0
            yy = ly + int(ry * (1 - t * t) ** 0.5)
            cv.set(xx, yy, OCEAN_LINE)
            cv.set(xx, yy + 1, OCEAN_LINE)
    # Longitude arcs: tall thin ellipses.
    for frac in (-0.66, -0.33, 0.0, 0.33, 0.66):
        rx = max(2, int(abs(frac) * r)) if frac else 2
        for yy in range(cy - r, cy + r + 1):
            t = (yy - cy) / r
            off = int(rx * (1 - t * t) ** 0.5)
            for sgn in (1, -1):
                xx = cx + sgn * off if frac else cx
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    cv.set(xx, yy, OCEAN_LINE)
    # Stylised continents: clusters of land discs clipped to the globe.
    clip = (cx, cy, r - 2)
    blobs = [
        (-0.52, -0.20, 0.24), (-0.40, 0.24, 0.17), (-0.30, 0.52, 0.10),
        (0.02, -0.34, 0.15), (0.06, 0.10, 0.22), (0.16, 0.40, 0.13),
        (0.44, -0.28, 0.26), (0.60, 0.04, 0.17), (0.52, 0.38, 0.12),
        (-0.66, -0.34, 0.13), (-0.36, -0.02, 0.12), (-0.20, 0.30, 0.09),
        (0.24, -0.18, 0.13), (0.30, 0.22, 0.10), (0.66, -0.14, 0.10),
    ]
    for fx, fy, fr in blobs:
        cv.disc(cx + int(fx * r), cy + int(fy * r), int(fr * r),
                LAND, clip=clip)
    # A darker green heart over Africa/Europe for depth.
    cv.disc(cx + int(0.06 * r), cy + int(0.12 * r), int(0.13 * r),
            LAND_DARK, clip=clip)
    cv.ring(cx, cy, r + 3, 3, INK)


# --------------------------------------------------------------------------
# The cover itself.
# --------------------------------------------------------------------------


def draw_card(cv, x, y, w, h, kicker, number, label, sub, num_color):
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, 3, INK)
    mid = x + w // 2
    if kicker:
        draw_text(cv, mid, y + 4, kicker, 2, RED, align="center")
    draw_text(cv, mid, y + 4, number, 5, num_color, align="center")
    draw_text(cv, mid, y + 43, label, 2, INK, align="center")
    draw_text(cv, mid, y + 59, sub, 2, GREY, align="center")


def compose():
    cv = Canvas(W, H, PAPER)
    cv.frame(14, 14, W - 28, H - 28, 4, INK)
    cv.frame(24, 24, W - 48, H - 48, 2, INK)

    # Masthead and date.
    centered(cv, 42, "THE SUNDAY PLANET", 9, INK)
    cv.rect(60, 122, W - 120, 4, RED)
    centered(cv, 136, "SUNDAY 22 NOVEMBER 2026", 4, RED)
    cv.rect(60, 176, W - 120, 3, INK)

    # Globe for the climate talks.
    draw_globe(cv, W // 2, 296, 104)

    # Giant headline: the deal is on the table, not yet adopted.
    centered(cv, 420, "DEAL ON", 14, INK)
    centered(cv, 526, "THE TABLE", 14, INK)
    cv.rect(312, 634, W - 624, 8, GOLD)

    # Where the talks stand, in GMT as the summit itself runs.
    centered(cv, 658, "OBJECTION WINDOW CLOSED 03:00 GMT", 3, TEAL)
    centered(cv, 688, "APPROVAL SESSION 06:00 GMT \u00b7 ANTALYA, "
                      "T\u00dcRK\u0130YE", 3, TEAL)

    # The summit president's own words, verbatim.
    centered(cv, 724, '"WE BELIEVE THAT WE HAVE PUT FORWARD A TEXT', 3, INK)
    centered(cv, 754, 'WHICH ALL THE PARTIES CAN AGREE UPON."', 3, INK)
    centered(cv, 788, "\u2014 MURAT KURUM, PRESIDENT OF COP31", 2, GREY)

    # The fight inside the draft.
    centered(cv, 818, "THE FIGHT INSIDE: THE DRAFT ERASED EVERY", 2, INK)
    centered(cv, 838, "FOSSIL-FUEL MENTION \u2014 COAL, OIL, GAS \u2014 AND", 2, INK)
    centered(cv, 858, "THE $120BN/YEAR TARGET. IN ITS PLACE: AT LEAST", 2, INK)
    centered(cv, 878, "TRIPLE ADAPTATION FINANCE BY 2035. EU'S HOEKSTRA:", 2, INK)
    centered(cv, 898, "'A GOOD DEAL OR NO DEAL'", 2, RED)

    # The day in numbers: three story cards along the foot.
    draw_card(cv, 40, 920, 296, 76, "", "200", "DELEGATIONS",
              "AT COP31 \u00b7 ANTALYA", TEAL)
    draw_card(cv, 364, 920, 296, 76, "", "23,000", "WORKERS CALLED OUT",
              "24H STRIKE \u00b7 MONDAY", RED)
    draw_card(cv, 688, 920, 296, 76, "", "25", "DEPORTEES ARRIVE",
              "LIBERIA \u00b7 CAP 1,200", INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(compose(), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
