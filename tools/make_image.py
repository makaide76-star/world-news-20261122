#!/usr/bin/env python3
"""Draw the entry image: the world news of Sunday 22 November 2026 in one picture.

Pure PIL, deterministic (no randomness, no clock, no network).
Output: assets/entry.png (1024x1024, under 1 MiB).

Stories are the verified 22 November 2026 wire headlines. The Iran claim of
hitting US bases in Bahrain is presented as unconfirmed, never as fact; the
Baltic drone strike is attributed as "likely" Ukraine per Finnish forces,
never as confirmed.

Layout (1024x1024):
  top bar 0-42 | masthead 42-150 | hero 154-418 (Hormuz text + strait visual)
  Baltic + Mexico 442-604 | Indonesia / Nigeria / Florida 626-818
  cyber strip 840-928 | footer 938-1024
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
CREAM = (248, 243, 232)
INK = (22, 30, 42)
RED = (178, 34, 44)
NAVY = (24, 60, 108)
DUSK = (28, 44, 74)
SEA = (18, 52, 86)
GOLD = (196, 140, 30)
FLAME = (232, 110, 30)
GREEN = (32, 108, 74)
GREY = (96, 100, 104)
WHITE = (255, 255, 255)
SOFT = (226, 232, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


canvas = Image.new("RGB", (W, W), CREAM)
pen = ImageDraw.Draw(canvas)


def wrapped(text, fnt, width):
    """Greedy word wrap measured with the real font; never overflows."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if pen.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def paragraph(x, y, text, fnt, fill, width, leading):
    for line in wrapped(text, fnt, width):
        pen.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(x, y, text, colour=RED, size=17):
    pen.text((x, y), text, font=font(SANSB, size), fill=colour)
    return y


def headline(x, y, lines, size=28):
    fnt = font(SERIF, size)
    for line in lines:
        pen.text((x, y), line, font=fnt, fill=INK)
        y += int(size * 1.18)
    return y


def rule(y, x0=28, x1=996, colour=GREY):
    pen.rectangle([x0, y, x1, y + 1], fill=colour)


def flame(cx, base, size):
    """A small stylised flame: layered triangles in orange and gold."""
    pen.polygon([(cx - size, base), (cx, base - size * 1.7),
                 (cx + size, base)],
                fill=FLAME)
    pen.polygon([(cx - size * 0.55, base), (cx, base - size * 1.1),
                 (cx + size * 0.55, base)],
                fill=(255, 200, 60))


# ---------------------------------------------------------------- top bar
pen.rectangle([0, 0, W, 42], fill=INK)
pen.text((28, 10), "SUNDAY  ·  22 NOVEMBER 2026  ·  WORLD NEWS",
         font=font(SANSB, 20), fill=(240, 235, 220))
tag = "ONE DAY · ONE IMAGE"
pen.text((W - 28 - pen.textlength(tag, font=font(SANSB, 20)), 10), tag,
         font=font(SANSB, 20), fill=GOLD)

# ---------------------------------------------------------------- masthead
pen.text((28, 52), "THE WORLD TODAY", font=font(SERIF, 68), fill=INK)
pen.rectangle([28, 136, W - 28, 141], fill=INK)
pen.rectangle([28, 146, W - 28, 148], fill=INK)

# ---------------------------------------------------------------- hero: Hormuz
LX, LW = 28, 580
kicker(LX, 156, "BAHRAIN  ·  STRAIT OF HORMUZ", size=19)
headline(LX, 184, ["IRAN STRIKES BAHRAIN", "TANKERS HIT IN HORMUZ"], size=36)
paragraph(LX, 288,
          "Bahrain says Iran struck a civilian industrial facility on Sitra "
          "Island, setting it ablaze; no casualties were reported. Two "
          "tankers were hit in the Strait of Hormuz. Iran's claim of "
          "hitting US bases in Bahrain is unconfirmed.",
          font(SANS, 19), INK, LW, 23)

# Hero visual: dusk over the strait, two tankers, one burning.
VX0, VY0, VX1, VY1 = 624, 154, 996, 418
pen.rectangle([VX0, VY0, VX1, VY1], fill=DUSK)
# low sun
pen.ellipse([930, 168, 972, 210], fill=(255, 190, 90))
# distant shore
pen.polygon([(VX0, 268), (700, 246), (790, 262), (880, 248), (VX1, 264),
             (VX1, 300), (VX0, 300)], fill=(12, 24, 44))
# sea
pen.rectangle([VX0, 300, VX1, VY1], fill=SEA)
for wy in (318, 336, 356, 378, 398):
    pen.line([(VX0 + 12, wy), (VX1 - 12, wy)], fill=(60, 110, 160), width=2)
# tanker one (left, burning)
pen.rectangle([648, 330, 788, 362], fill=(120, 30, 26))
pen.rectangle([648, 318, 788, 330], fill=(70, 18, 16))
pen.rectangle([700, 296, 730, 318], fill=(200, 200, 200))
for px in range(656, 784, 18):
    pen.rectangle([px, 340, px + 9, 350], fill=(240, 235, 220))
flame(700, 296, 16)
flame(748, 300, 12)
# tanker two (right, smoke)
pen.rectangle([830, 336, 968, 362], fill=(40, 44, 52))
pen.rectangle([830, 326, 968, 336], fill=(24, 28, 34))
pen.rectangle([880, 306, 906, 326], fill=(200, 200, 200))
for px in range(838, 962, 18):
    pen.rectangle([px, 344, px + 9, 352], fill=(240, 235, 220))
for sx, sy, sr in [(892, 292, 12), (880, 274, 15), (898, 256, 11)]:
    pen.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 150, 150))
pen.text((VX0 + 16, VY1 - 30), "SITRA ISLAND · TWO TANKERS HIT",
         font=font(SANSB, 16), fill=GOLD)

rule(430)

# ---------------------------------------------------------------- Baltic + Mexico
# Baltic, left
BX, BW = 28, 532
kicker(BX, 444, "BALTIC SEA  ·  GULF OF FINLAND", size=17)
headline(BX, 468, ["RUSSIAN SHIP ABLAZE", "AFTER DRONE STRIKE"], size=28)
# small ship motif with flame, right of the headline block
pen.rectangle([474, 492, 542, 512], fill=(40, 44, 52))
pen.rectangle([498, 474, 516, 492], fill=(200, 200, 200))
flame(507, 474, 10)
pen.text((472, 516), "16 CREW SAFE", font=font(SANSB, 13), fill=RED)
paragraph(BX, 532,
          "Cargo ship Sparta II, bound for Kaliningrad, caught fire after "
          "a drone strike in the Gulf of Finland and drifted into Finnish "
          "waters. All 16 crew were evacuated; a Russian helicopter then "
          "violated Finnish airspace. Finnish forces say Ukraine was "
          "likely behind it.",
          font(SANS, 16), INK, BW, 20)

# Mexico, right
MX, MW = 584, 412
kicker(MX, 444, "MEXICO  ·  SINALOA", size=17)
headline(MX, 468, ["MEXICO CAPTURES", "\u2018EL CHAPO ISIDRO\u2019"], size=28)
paragraph(MX, 532,
          "Special forces captured Fausto Isidro Meza Flores, wanted by "
          "the FBI, in Guasave, Sinaloa. Eleven died in the raid \u2014 "
          "four soldiers, seven cartel gunmen \u2014 then roadblocks and "
          "burning trucks.",
          font(SANS, 16), INK, MW, 20)

rule(614)

# ---------------------------------------------------------------- three columns
COLS = [
    (28, 312, "INDONESIA  ·  SERANG", RED,
     ["FACTORY FIRE LEAVES", "36 MISSING"],
     "Fire swept a candy factory in Cikande, Serang. Three workers were "
     "killed, four injured and 36 are missing as the search continues."),
    (364, 312, "NIGERIA  ·  BAYELSA", RED,
     ["FUNERAL BOAT", "CAPSIZES; 24 DEAD"],
     "An overcrowded boat carrying mourners capsized in Bayelsa State "
     "after a mechanical failure. At least 24 people died and 24 were "
     "rescued."),
    (700, 296, "FLORIDA  ·  USA", RED,
     ["RIVER BREAKS", "73-YEAR FLOOD RECORD"],
     "The St. Johns River near Cocoa rose to 18.76 ft, passing the 1953 "
     "record of 17.55 ft after days of heavy rain. Nearly 100 high-water "
     "rescues were reported."),
]
for cx, cw, kick, colour, head_lines, body in COLS:
    kicker(cx, 628, kick, colour=colour, size=16)
    headline(cx, 652, head_lines, size=22)
    paragraph(cx, 706, body, font(SANS, 16), INK, cw, 19)

rule(828)

# ---------------------------------------------------------------- cyber strip
kicker(28, 842, "WASHINGTON  ·  CYBERATTACK", size=16)
headline(28, 864, ["HACKERS BREACH FBI AND USDA SYSTEMS"], size=23)
paragraph(28, 896,
          "Hackers breached a US farm-payments system and the FBI\u2019s "
          "National Crime Information Center database \u2014 the second "
          "FBI breach since September. It is unclear whether the two "
          "attacks are linked or who is behind them.",
          font(SANS, 16), INK, 968, 20)

# ---------------------------------------------------------------- footer
pen.rectangle([0, 938, W, W], fill=INK)
pen.text((28, 950),
         "22 NOVEMBER 2026  ·  SOURCES: REUTERS · AP · AFP · AL JAZEERA · "
         "CNN · JAPAN TIMES · DAWN",
         font=font(SANSB, 15), fill=(238, 234, 222))
pen.text((28, 978),
         "Drawn with Python/PIL \u2014 no photographs. Unconfirmed claims "
         "are labelled as such.",
         font=font(SANS, 15), fill=(200, 206, 214))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "entry.png")
canvas.save(OUT, format="PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
