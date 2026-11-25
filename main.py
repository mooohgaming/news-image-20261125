#!/usr/bin/env python3
"""World news of Wednesday 25 November 2026, in one image.

Draws a newspaper front page (1024x1024 PNG) with six verified stories
from 25 November 2026. Pure standard library: own canvas code, own 5x7
bitmap font, own PNG encoder (zlib + struct). No network, no clock,
no randomness -- two runs produce byte-identical output.

Run:  python3 main.py            (writes /output/entry.png)
       MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 233)
INK = (26, 26, 26)
NAVY = (22, 35, 63)
GOLD = (201, 162, 39)
RED = (166, 25, 46)
GREY = (102, 102, 102)
BODY = (51, 51, 51)
CARD_BG = (255, 255, 255)
CARD_LINE = (201, 194, 174)

# 5x7 bitmap font, uppercase + digits + punctuation. '#' = pixel on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_triangle(self, ax, ay, bx, by, cx, cy, color):
        # Scanline fill: walk edges AB/AC then BC.
        pts = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(x0, y0, x1, y1, y)
                xb = interp(x0, y0, x2, y2, y)
            else:
                xa = interp(x1, y1, x2, y2, y)
                xb = interp(x0, y0, x2, y2, y)
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb) - int(xa) + 1, 1, color)

    def circle(self, cx, cy, r, color, fill=False):
        x = 0
        y = r
        d = 3 - 2 * r
        while y >= x:
            if fill:
                self.fill_rect(cx - x, cy - y, 2 * x + 1, 1, color)
                self.fill_rect(cx - x, cy + y, 2 * x + 1, 1, color)
                self.fill_rect(cx - y, cy - x, 2 * y + 1, 1, color)
                self.fill_rect(cx - y, cy + x, 2 * y + 1, 1, color)
            else:
                for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                               (cx + x, cy - y), (cx - x, cy - y),
                               (cx + y, cy + x), (cx - y, cy + x),
                               (cx + y, cy - x), (cx - y, cy - x)):
                    self.fill_rect(px, py, 1, 1, color)
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, y, s, scale, color):
        x = (self.w - self.text_width(s, scale)) // 2
        self.text(x, y, s, scale, color)


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- stories
# Six stories, each verified against a report published on 25 Nov 2026.
STORIES = [
    dict(
        accent=(46, 90, 136), tint=(226, 236, 244),
        head=["BRITAIN TO LICENCE", "ALL KNIFE SALES"],
        body=["HOME OFFICE UNVEILS THE WORLD'S FIRST",
              "LICENSING SCHEME FOR EVERY KNIFE",
              "SALE: SHOPS, ONLINE AND PRIVATE."],
        source="SOURCE: GOV.UK / THE GUARDIAN",
        scene="knife",
    ),
    dict(
        accent=(166, 25, 46), tint=(244, 226, 229),
        head=["MET STILL FAILING ON", "RACE, REVIEW FINDS"],
        body=["A 389-PAGE REVIEW FINDS NO GOOD",
              "PROGRESS ON ANY CASEY REFORM AND",
              "WARNS NEW SCANDALS ARE HIGHLY LIKELY."],
        source="SOURCE: THE GUARDIAN / THE TIMES",
        scene="shield",
    ),
    dict(
        accent=(14, 124, 123), tint=(222, 240, 239),
        head=["AUSTRALIA SIGNS HISTORIC", "PACIFIC TREATY"],
        body=["CANBERRA BECOMES THE SOLOMONS' FIRST",
              "DEFENCE PARTNER OF CHOICE AS THE",
              "ISLANDS LET THEIR CHINA PACT LAPSE."],
        source="SOURCE: REUTERS / AAP",
        scene="treaty",
    ),
    dict(
        accent=(62, 124, 58), tint=(228, 240, 226),
        head=["FRAILTY GAP WIDEST", "IN ENGLAND, STUDY FINDS"],
        body=["THE POOREST 50-YEAR-OLDS IN ENGLAND",
              "ARE FRAILER THAN THE RICHEST BY THE",
              "WIDEST MARGIN OF 31 COUNTRIES."],
        source="SOURCE: THE GUARDIAN / BMC MEDICINE",
        scene="frailty",
    ),
    dict(
        accent=(46, 127, 168), tint=(224, 238, 245),
        head=["COASTS GET 11M POUNDS", "TO FIGHT EROSION"],
        body=["TWELVE COUNCIL PROJECTS GET 11M",
              "POUNDS FOR DRONE SURVEYS, DUNE",
              "RESTORATION AND MOVING ROADS INLAND."],
        source="SOURCE: THE GUARDIAN",
        scene="coast",
    ),
    dict(
        accent=(106, 76, 147), tint=(236, 230, 244),
        head=["AUSTRALIA SAYS SORRY TO", "LGBTQ VETERANS"],
        body=["MARLES APOLOGISES IN PARLIAMENT FOR",
              "DECADES OF WITCH HUNTS THAT FORCED",
              "GAY PERSONNEL OUT OF THE SERVICES."],
        source="SOURCE: REUTERS / DEFENCE.GOV.AU",
        scene="apology",
    ),
]


def draw_scene(c, kind, x, y, w, h, accent, tint):
    c.fill_rect(x, y, w, h, tint)
    c.hline(x, y, w, CARD_LINE)
    c.hline(x, y + h - 1, w, CARD_LINE)
    cx = x + w // 2
    cy = y + h // 2
    if kind == "knife":
        # Shop awning, a knife, and a licence card with a check.
        for i in range(6):
            col = RED if i % 2 == 0 else CARD_BG
            c.fill_rect(x + 18 + i * 26, y + 10, 26, 12, col)
        c.fill_rect(x + 18, y + 22, 156, 4, INK)
        # knife: blade + handle, lying flat
        c.fill_triangle(x + 210, y + 34, x + 300, y + 34, x + 300, y + 52, (120, 120, 120))
        c.line(x + 210, y + 34, x + 300, y + 34, INK, 2)
        c.line(x + 300, y + 34, x + 300, y + 52, INK, 2)
        c.line(x + 210, y + 34, x + 300, y + 52, INK, 2)
        c.fill_rect(x + 300, y + 34, 46, 18, (90, 60, 30))
        c.fill_rect(x + 346, y + 38, 10, 10, GOLD)
        # licence card
        c.fill_rect(x + 372, y + 14, 66, 56, CARD_BG)
        c.vline(x + 372, y + 14, 56, INK)
        c.vline(x + 437, y + 14, 56, INK)
        c.hline(x + 372, y + 14, 66, INK)
        c.hline(x + 372, y + 69, 66, INK)
        c.line(x + 380, y + 42, x + 392, y + 56, (46, 124, 58), 4)
        c.line(x + 392, y + 56, x + 424, y + 26, (46, 124, 58), 4)
        c.text(x + 380, y + 18, "LICENCE", 1, INK)
    elif kind == "shield":
        # Police badge: navy roundel with a gold ring and MET, plus
        # the red review stamp.
        c.circle(cx, y + 40, 30, NAVY, fill=True)
        c.circle(cx, y + 40, 30, GOLD)
        c.circle(cx, y + 40, 24, GOLD)
        c.text(cx - 17, y + 33, "MET", 2, CARD_BG)
        c.fill_rect(x + 330, y + 22, 108, 30, RED)
        c.text(x + 340, y + 30, "REVIEW", 2, CARD_BG)
        c.text(x + 336, y + 56, "389 PAGES", 2, RED)
    elif kind == "treaty":
        # Two flags on poles and a signed document.
        c.vline(x + 30, y + 10, 62, INK, 3)
        c.fill_rect(x + 33, y + 10, 74, 30, (0, 40, 104))
        c.fill_rect(x + 33, y + 10, 74, 6, CARD_BG)
        c.circle(x + 60, y + 28, 3, CARD_BG, fill=True)
        c.vline(x + 330, y + 10, 62, INK, 3)
        c.fill_rect(x + 333, y + 10, 74, 15, (0, 90, 160))
        c.fill_rect(x + 333, y + 25, 74, 15, (0, 140, 70))
        c.circle(x + 352, y + 17, 2, GOLD, fill=True)
        # document with signature
        c.fill_rect(cx - 46, y + 14, 92, 56, CARD_BG)
        c.vline(cx - 46, y + 14, 56, INK)
        c.vline(cx + 45, y + 14, 56, INK)
        c.hline(cx - 46, y + 14, 92, INK)
        c.hline(cx - 46, y + 69, 92, INK)
        c.hline(cx - 36, y + 26, 72, GREY)
        c.hline(cx - 36, y + 36, 72, GREY)
        c.line(cx - 36, y + 58, cx - 10, y + 50, INK, 2)
        c.line(cx - 10, y + 50, cx + 8, y + 60, INK, 2)
        c.line(cx + 8, y + 60, cx + 30, y + 48, INK, 2)
    elif kind == "frailty":
        # Two bars: the poorest (tall, red) vs the richest (short, green),
        # plus a heart with a pulse line.
        c.fill_rect(x + 60, y + 16, 44, 56, RED)
        c.fill_rect(x + 130, y + 46, 44, 26, (62, 124, 58))
        c.text(x + 56, y + 74, "POOREST", 1, RED)
        c.text(x + 128, y + 74, "RICHEST", 1, (62, 124, 58))
        c.text(x + 210, y + 12, "GAP WIDEST", 2, INK)
        c.text(x + 210, y + 30, "AT AGE 50", 2, INK)
        # heart
        hx, hy = x + 330, y + 30
        c.circle(hx, hy, 12, RED, fill=True)
        c.circle(hx + 22, hy, 12, RED, fill=True)
        c.fill_triangle(hx - 10, hy + 6, hx + 32, hy + 6, hx + 11, hy + 34, RED)
        c.line(x + 380, y + 58, x + 396, y + 58, INK, 2)
        c.line(x + 396, y + 58, x + 404, y + 48, INK, 2)
        c.line(x + 404, y + 48, x + 412, y + 66, INK, 2)
        c.line(x + 412, y + 66, x + 420, y + 58, INK, 2)
        c.line(x + 420, y + 58, x + 436, y + 58, INK, 2)
    elif kind == "coast":
        # Cliff, a house on the edge, waves below, a drone above.
        c.fill_rect(x + 20, y + 44, 150, 30, (150, 110, 70))
        c.fill_rect(x + 20, y + 44, 150, 6, (120, 85, 50))
        c.fill_rect(x + 60, y + 18, 34, 26, CARD_BG)
        c.vline(x + 60, y + 18, 26, INK)
        c.vline(x + 93, y + 18, 26, INK)
        c.fill_triangle(x + 56, y + 18, x + 98, y + 18, x + 77, y + 2, RED)
        c.fill_rect(x + 72, y + 30, 10, 14, INK)
        # waves
        for wy in (y + 52, y + 62, y + 72):
            for wx in range(x + 190, x + 430, 24):
                c.line(wx, wy, wx + 12, wy - 5, accent, 2)
                c.line(wx + 12, wy - 5, wx + 24, wy, accent, 2)
        # drone
        c.fill_rect(x + 400, y + 8, 14, 8, INK)
        c.line(x + 392, y + 6, x + 422, y + 6, INK, 2)
        c.circle(x + 392, y + 6, 3, INK, fill=True)
        c.circle(x + 422, y + 6, 3, INK, fill=True)
    elif kind == "apology":
        # Rainbow stripes and a flag on a pole, with a heart.
        bands = [(228, 0, 38), (255, 140, 0), (255, 210, 0),
                 (0, 150, 70), (0, 110, 200), (130, 60, 180)]
        for i, col in enumerate(bands):
            c.fill_rect(x + 20, y + 10 + i * 10, 180, 10, col)
        c.vline(x + 220, y + 8, 68, INK, 3)
        for i, col in enumerate(bands):
            c.fill_rect(x + 223, y + 10 + i * 8, 90, 8, col)
        hx, hy = x + 380, y + 30
        c.circle(hx, hy, 12, RED, fill=True)
        c.circle(hx + 22, hy, 12, RED, fill=True)
        c.fill_triangle(hx - 10, hy + 6, hx + 32, hy + 6, hx + 11, hy + 34, RED)
        c.text(x + 356, y + 68, "SORRY", 2, RED)


def draw_card(c, x, y, w, h, story, number):
    accent = story["accent"]
    c.fill_rect(x, y, w, h, CARD_BG)
    # border
    c.hline(x, y, w, CARD_LINE)
    c.hline(x, y + h - 1, w, CARD_LINE)
    c.vline(x, y, h, CARD_LINE)
    c.vline(x + w - 1, y, h, CARD_LINE)
    # accent stripe
    c.fill_rect(x, y, w, 8, accent)
    # number badge
    c.circle(x + 26, y + 34, 13, accent, fill=True)
    c.text(x + 21, y + 27, str(number), 2, CARD_BG)
    # headline, two lines
    hx = x + 48
    c.text(hx, y + 20, story["head"][0], 3, INK)
    c.text(hx, y + 44, story["head"][1], 3, INK)
    # summary, three lines
    sy = y + 76
    for i, line in enumerate(story["body"]):
        c.text(x + 16, sy + i * 16, line, 2, BODY)
    # illustration strip
    draw_scene(c, story["scene"], x + 16, y + 132, w - 32, 84,
               accent, story["tint"])
    # source line
    c.text(x + 16, y + 228, story["source"], 1, GREY)


def build():
    c = Canvas(W, H, PAPER)
    # Masthead
    c.fill_rect(0, 0, W, 100, NAVY)
    c.text_centered(20, "THE WORLD IN ONE PAGE", 6, CARD_BG)
    c.fill_rect(0, 84, W, 6, GOLD)
    # Date
    c.text_centered(112, "WEDNESDAY 25 NOVEMBER 2026", 5, RED)
    # Subtitle
    c.text_centered(158, "SIX STORIES THAT DEFINED THE DAY", 2, NAVY)
    c.hline(24, 180, W - 48, INK, 2)
    # Six cards: 2 columns x 3 rows
    cw, ch = 488, 258
    gap = 16
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = 24 + col * (cw + gap)
        y = 192 + row * (ch + 12)
        draw_card(c, x, y, cw, ch, story, i + 1)
    # Footer
    c.text_centered(994, "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON 25 NOVEMBER 2026",
                    2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build()
    write_png(os.path.join(out_dir, "entry.png"), canvas)


if __name__ == "__main__":
    main()
