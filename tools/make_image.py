#!/usr/bin/env python3
"""Render the 22 November 2026 front page as a single 1024x1024 PNG.

The page is assembled from a small table of stories plus a handful of
generic drawing helpers, so adding or rewording a story means editing
one entry in STORIES rather than touching any coordinates by hand.
Everything here is fixed: no clock, no randomness, no network access,
so the same input always produces the same bytes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)      # warm newsprint cream
CARD = (255, 253, 247)       # near-white card face
INK = (22, 22, 26)           # body text
NAVY = (18, 38, 66)          # masthead band + strip
RULE = (120, 110, 92)        # hairline rules
MUTED = (92, 86, 74)         # secondary text
TINT = (238, 231, 216)       # motif panel wash

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 24

# ---------------------------------------------------------------- stories
# Each entry: short label, headline broken into display lines, a compact
# body paragraph, an accent colour and the name of a geometric motif.
STORIES = [
    {
        "kicker": "MIDDLE EAST \u00b7 GULF TENSIONS",
        "headline": ["IRAN STRIKES BAHRAIN", "TANKERS HIT IN HORMUZ"],
        "body": (
            "Bahrain says Iran struck a civilian industrial facility on "
            "Sitra Island, setting it ablaze. No casualties were reported. "
            "Two tankers were also hit in the Strait of Hormuz. Iran's "
            "claim of striking US bases in Bahrain remains UNCONFIRMED."
        ),
        "accent": (150, 28, 22),
        "motif": "flames",
    },
    {
        "kicker": "BALTIC SEA \u00b7 GULF OF FINLAND",
        "headline": ["RUSSIAN SHIP ABLAZE", "AFTER DRONE STRIKE"],
        "body": (
            "Cargo ship Sparta II, bound for Kaliningrad, caught fire "
            "after a drone strike and drifted into Finnish waters. All "
            "16 crew were evacuated. A Russian helicopter violated "
            "Finnish airspace. Finnish forces say Ukraine was likely "
            "behind the strike."
        ),
        "accent": (24, 64, 110),
        "motif": "ship",
    },
    {
        "kicker": "MEXICO \u00b7 SINALOA",
        "headline": ["MEXICO CAPTURES", "\u2018EL CHAPO ISIDRO\u2019"],
        "body": (
            "Fausto Isidro Meza Flores was captured in Guasave, Sinaloa. "
            "Eleven people died in the operation \u2014 four soldiers and "
            "seven cartel gunmen. Roadblocks and burning trucks followed "
            "across the region."
        ),
        "accent": (18, 96, 72),
        "motif": "cuffs",
    },
    {
        "kicker": "INDONESIA \u00b7 SERANG",
        "headline": ["FACTORY FIRE LEAVES", "36 MISSING"],
        "body": (
            "A fire at a candy factory in Cikande, Serang, killed three "
            "people and injured four. Thirty-six workers remain missing "
            "as the search continues."
        ),
        "accent": (168, 84, 16),
        "motif": "factory",
    },
    {
        "kicker": "NIGERIA \u00b7 BAYELSA STATE",
        "headline": ["FUNERAL BOAT", "CAPSIZES; 24 DEAD"],
        "body": (
            "An overcrowded boat carrying mourners capsized in Bayelsa "
            "State after a mechanical failure. Twenty-four people died "
            "and 24 were rescued."
        ),
        "accent": (16, 88, 130),
        "motif": "waves",
    },
    {
        "kicker": "FLORIDA \u00b7 USA",
        "headline": ["RIVER BREAKS", "73-YEAR FLOOD RECORD"],
        "body": (
            "The St. Johns River near Cocoa, Florida, reached 18.76 ft, "
            "passing the 1953 record of 17.55 ft. Nearly 100 high-water "
            "rescues were carried out."
        ),
        "accent": (14, 92, 96),
        "motif": "gauge",
    },
]

BREACH = {
    "kicker": "CYBER",
    "headline": "HACKERS BREACH FBI AND USDA SYSTEMS",
    "body": (
        "USDA farm-payments system and FBI crime database breached "
        "\u2014 the second FBI breach since September. Culprit and link "
        "unclear."
    ),
}

FOOTER_SOURCES = "Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 CNN \u00b7 Japan Times \u00b7 Dawn"
FOOTER_DATE = "SUNDAY \u00b7 22 NOVEMBER 2026"


# ---------------------------------------------------------------- fonts
def _font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF_BIG = None
SERIF = None
SERIF_SM = None
SANS_BOLD = None
SANS = None
SANS_SM = None


def _load_fonts():
    global SERIF_BIG, SERIF, SERIF_SM, SANS_BOLD, SANS, SANS_SM
    SERIF_BIG = _font("DejaVuSerif-Bold.ttf", 62)
    SERIF = _font("DejaVuSerif-Bold.ttf", 27)
    SERIF_SM = _font("DejaVuSerif-Bold.ttf", 24)
    SANS_BOLD = _font("DejaVuSans-Bold.ttf", 14)
    SANS = _font("DejaVuSans.ttf", 15)
    SANS_SM = _font("DejaVuSans.ttf", 13)


# ---------------------------------------------------------------- text tools
def _wrap(draw, text, font, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _para(draw, x, y, text, font, fill, max_w, leading):
    """Draw a wrapped paragraph; return the y just below the last line."""
    for line in _wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _kicker(draw, x, y, text, accent):
    draw.text((x, y), text, font=SANS_BOLD, fill=accent)
    return y + 20


# ---------------------------------------------------------------- motifs
# Each motif painter receives the draw context, a bounding box
# (x0, y0, x1, y1) and the story accent colour, and draws only simple
# flat geometry inside that box.

def _flames(draw, box, accent):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    base = y1 - 8
    draw.polygon(
        [(x0 + 8, base), (cx - 28, y0 + 42), (cx - 8, y0 + 62),
         (cx - 2, y0 + 18), (cx + 22, y0 + 58), (cx + 34, y0 + 34),
         (x1 - 8, base)],
        fill=accent,
    )
    draw.polygon(
        [(cx - 22, base), (cx - 6, y0 + 58), (cx + 4, y0 + 74),
         (cx + 20, base)],
        fill=(232, 148, 32),
    )
    draw.rectangle([x0 + 6, base, x1 - 6, base + 5], fill=(90, 60, 30))


def _ship(draw, box, accent):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    deck = y0 + int(h * 0.45)
    draw.rectangle([x0 + int(w * 0.30), y0 + 2, x0 + int(w * 0.42), deck - 2],
                   fill=accent)
    draw.rectangle([x0 + int(w * 0.44), y0 + int(h * 0.18),
                    x0 + int(w * 0.68), deck - 2], fill=(210, 110, 40))
    draw.rectangle([x0 + int(w * 0.70), y0 + int(h * 0.26),
                    x0 + int(w * 0.88), deck - 2], fill=(60, 120, 90))
    draw.polygon(
        [(x0 + 2, deck), (x1 - 2, deck), (x1 - int(w * 0.16), deck + int(h * 0.24)),
         (x0 + int(w * 0.16), deck + int(h * 0.24))],
        fill=accent,
    )
    wy = deck + int(h * 0.30)
    for wx in range(x0 + 4, x1 - 14, 18):
        draw.arc([wx, wy, wx + 16, wy + 10], 0, 180,
                 fill=(70, 130, 170), width=3)
    draw.ellipse([x0 + int(w * 0.68), y0, x0 + int(w * 0.78), y0 + 8],
                 fill=(240, 120, 40))
    draw.ellipse([x0 + int(w * 0.78), y0 + 4, x0 + int(w * 0.86), y0 + 12],
                 fill=(245, 170, 60))


def _cuffs(draw, box, accent):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cy = (y0 + y1) // 2
    r = min(w, h) // 2 - 6
    for cx in (x0 + r + 4, x1 - r - 4):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=accent, width=5)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=accent)
    draw.rectangle([x0 + r + 4, cy - 4, x1 - r - 4, cy + 4], fill=accent)
    sx = (x0 + x1) // 2
    star = []
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = 11 if i % 2 == 0 else 5
        star.append((sx + rad * math.cos(ang), y0 + 10 + rad * math.sin(ang)))
    draw.polygon(star, fill=(212, 160, 32))


def _factory(draw, box, accent):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    base = y1 - 4
    roof = y0 + int(h * 0.42)
    draw.rectangle([x0 + int(w * 0.24), y0 + int(h * 0.22),
                    x0 + int(w * 0.34), base], fill=accent)
    draw.rectangle([x0 + 4, roof + int(h * 0.14), x1 - 4, base],
                   fill=(120, 70, 40))
    teeth = [(x0 + 4, roof + int(h * 0.14))]
    for i in range(3):
        px = x0 + 4 + (x1 - x0 - 8) * (i + 1) // 3
        teeth.append((px - (x1 - x0 - 8) // 6, roof))
        teeth.append((px, roof + int(h * 0.14)))
    draw.polygon(teeth, fill=accent)
    for wx in range(x0 + 8, x1 - 14, 18):
        draw.rectangle([wx, roof + int(h * 0.26), wx + 10, roof + int(h * 0.40)],
                       fill=(255, 220, 120))
    for fx, fy, fr in [(0.30, 0.10, 4), (0.38, 0.05, 5), (0.47, 0.11, 3)]:
        sx, sy = x0 + int(w * fx), y0 + int(h * fy)
        draw.ellipse([sx - fr, sy - fr, sx + fr, sy + fr], fill=(150, 150, 150))


def _waves(draw, box, accent):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for row in range(3):
        yy = y0 + int(h * (0.30 + row * 0.26))
        colour = accent if row % 2 == 0 else (70, 150, 190)
        for wx in range(x0 + 2, x1 - 16, 20):
            draw.arc([wx, yy, wx + 18, yy + 12], 180, 360, fill=colour, width=3)
    draw.polygon(
        [(x0 + int(w * 0.22), y0 + int(h * 0.28)),
         (x1 - int(w * 0.30), y0 + int(h * 0.28)),
         (x1 - int(w * 0.36), y0 + int(h * 0.44)),
         (x0 + int(w * 0.28), y0 + int(h * 0.44))],
        fill=(90, 60, 30),
    )
    draw.rectangle([x0 + int(w * 0.44), y0 + int(h * 0.08),
                    x0 + int(w * 0.50), y0 + int(h * 0.28)], fill=(90, 60, 30))


def _gauge(draw, box, accent):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, y1 - 14
    r = min(x1 - x0, y1 - y0) // 2 - 4
    draw.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=accent, width=6)
    import math
    for deg in range(180, 361, 30):
        a = math.radians(deg)
        x_a, y_a = cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a)
        x_b, y_b = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.line([x_a, y_a, x_b, y_b], fill=INK, width=2)
    tip_a = math.radians(225)
    draw.line([cx, cy, cx + (r - 10) * math.cos(tip_a),
               cy + (r - 10) * math.sin(tip_a)], fill=(190, 30, 20), width=4)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    draw.text((x0 + 4, y0 + 2), "18.76 ft", font=SANS_BOLD, fill=accent)


def _lockboard(draw, box, accent):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6],
                           radius=6, outline=accent, width=3)
    for row in range(2):
        for col in range(4):
            kx = x0 + 18 + col * 22
            ky = y0 + 16 + row * 20
            draw.rectangle([kx, ky, kx + 14, ky + 12], fill=(200, 200, 200))
    draw.rectangle([x1 - 34, y0 + 14, x1 - 14, y0 + 30], fill=(212, 160, 32))
    draw.arc([x1 - 32, y0 + 4, x1 - 16, y0 + 20], 180, 360,
             fill=(212, 160, 32), width=3)
    draw.rectangle([x0 + 14, y1 - 26, x0 + 52, y1 - 12], fill=accent)


MOTIFS = {
    "flames": _flames,
    "ship": _ship,
    "cuffs": _cuffs,
    "factory": _factory,
    "waves": _waves,
    "gauge": _gauge,
    "lockboard": _lockboard,
}


def _paint_motif(draw, name, box, accent):
    """Dispatch to the motif painter for `name` inside `box`."""
    painter = MOTIFS[name]
    draw.rounded_rectangle(box, radius=8, fill=TINT)
    inner = (box[0] + 8, box[1] + 8, box[2] - 8, box[3] - 8)
    painter(draw, inner, accent)


# ---------------------------------------------------------------- cards
def _hero_card(draw, story):
    x0, y0, x1, y1 = MARGIN, 128, PAGE_W - MARGIN, 398
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD,
                           outline=RULE, width=1)
    draw.rectangle([x0, y0, x0 + 6, y1], fill=story["accent"])
    tx = x0 + 26
    y = _kicker(draw, tx, y0 + 14, story["kicker"], story["accent"])
    for line in story["headline"]:
        draw.text((tx, y), line, font=_font("DejaVuSerif-Bold.ttf", 40),
                  fill=INK)
        y += 48
    y += 6
    _para(draw, tx, y, story["body"], SANS, INK, 584, 20)
    _paint_motif(draw, story["motif"], (664, 150, 976, 376), story["accent"])
    draw.text((664, 380), "Sitra Island \u00b7 Strait of Hormuz",
              font=SANS_SM, fill=MUTED)


def _grid_card(draw, story, x0, y0, x1, y1):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD,
                           outline=RULE, width=1)
    draw.rectangle([x0, y0, x0 + 5, y1], fill=story["accent"])
    tx = x0 + 18
    y = _kicker(draw, tx, y0 + 10, story["kicker"], story["accent"])
    for line in story["headline"]:
        draw.text((tx, y), line, font=SERIF_SM, fill=INK)
        y += 30
    _para(draw, tx, y + 4, story["body"], SANS_SM, INK, (x1 - x0) - 36, 17)
    _paint_motif(draw, story["motif"],
                 (x1 - 108, y0 + 10, x1 - 12, y0 + 62), story["accent"])


def _flood_card(draw, story):
    x0, y0, x1, y1 = MARGIN, 780, PAGE_W - MARGIN, 884
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD,
                           outline=RULE, width=1)
    draw.rectangle([x0, y0, x0 + 6, y1], fill=story["accent"])
    tx = x0 + 26
    y = _kicker(draw, tx, y0 + 10, story["kicker"], story["accent"])
    one_line = " ".join(story["headline"])
    draw.text((tx, y), one_line, font=SERIF, fill=INK)
    _para(draw, tx, y + 34, story["body"], SANS_SM, INK, 720, 17)
    _paint_motif(draw, story["motif"], (800, 792, 976, 872), story["accent"])


def _breach_band(draw):
    x0, y0, x1, y1 = MARGIN, 894, PAGE_W - MARGIN, 962
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=NAVY)
    draw.text((x0 + 18, y0 + 8), BREACH["kicker"],
              font=SANS_BOLD, fill=(212, 160, 32))
    draw.text((x0 + 88, y0 + 8), BREACH["headline"],
              font=_font("DejaVuSans-Bold.ttf", 19), fill=(255, 255, 255))
    draw.text((x0 + 18, y0 + 38), BREACH["body"],
              font=SANS_SM, fill=(220, 224, 230))


# ---------------------------------------------------------------- page
def build_page():
    """Compose the whole front page and return it as a PIL image."""
    _load_fonts()
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    # Top dateline band.
    draw.rectangle([0, 0, PAGE_W, 30], fill=NAVY)
    top = "SUNDAY \u00b7 22 NOVEMBER 2026 \u00b7 WORLD NEWS"
    tw = draw.textlength(top, font=SANS_BOLD)
    draw.text(((PAGE_W - tw) / 2, 7), top, font=SANS_BOLD,
              fill=(255, 255, 255))

    # Masthead.
    title = "THE WORLD TODAY"
    tw = draw.textlength(title, font=SERIF_BIG)
    draw.text(((PAGE_W - tw) / 2, 40), title, font=SERIF_BIG, fill=INK)
    draw.line([MARGIN, 116, PAGE_W - MARGIN, 116], fill=INK, width=2)
    draw.line([MARGIN, 120, PAGE_W - MARGIN, 120], fill=RULE, width=1)

    _hero_card(draw, STORIES[0])

    # Two-by-two grid for stories 2-5.
    cols = [(MARGIN, 500), (524, PAGE_W - MARGIN)]
    rows = [(408, 584), (594, 770)]
    for idx, story in enumerate(STORIES[1:5]):
        cx0, cx1 = cols[idx % 2]
        ry0, ry1 = rows[idx // 2]
        _grid_card(draw, story, cx0, ry0, cx1, ry1)

    _flood_card(draw, STORIES[5])
    _breach_band(draw)

    # Footer: sources, then the date.
    sw = draw.textlength(FOOTER_SOURCES, font=SANS_SM)
    draw.text(((PAGE_W - sw) / 2, 972), FOOTER_SOURCES,
              font=SANS_SM, fill=MUTED)
    dw = draw.textlength(FOOTER_DATE, font=SANS_BOLD)
    draw.text(((PAGE_W - dw) / 2, 994), FOOTER_DATE,
              font=SANS_BOLD, fill=MUTED)
    return page


def render(out_path):
    """Build the page and save it as a PNG at `out_path`."""
    page = build_page()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.save(out, format="PNG")
    return out


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "assets" / "entry.png"
    render(target)
    print(f"wrote {target}")
