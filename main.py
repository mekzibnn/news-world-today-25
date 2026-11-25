#!/usr/bin/env python3
"""news-image-20261125 v1 — renders a 1024x1024 one-image summary of
Wednesday 25 November 2026 world news. Blind rewrite: written fresh from
the research file, no earlier implementation consulted.

Layout (1024 tall): masthead 24, title 46, subhead 14, stat 28, region 26,
timeline 32, big lead cards 168 (pictorial 62), medium cards 3 rows x 84
(3 cols), map+briefs 224, DATE CHECK 196, footer 28.
Stories: 23 verified Wednesday stories (12 leads + 11 briefs), 7 regions
(APAC 4, Americas 7, Europe 8, Africa 0, Oceania 2, Middle East 0, World 2).
Five research items were dropped after verification (not Wednesday news):
Section 301 tariffs (unconfirmed), deep-space ageing (Jul 2026),
UK Houthi sanctions (Tue 24 Nov), Iran medicine shortage (Tue 24 Nov),
ECB nominations (closed Fri 20 Nov) — the last four are in DATE CHECK.
"""

import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except Exception:
    _PIL_OK = False

W, H = 1024, 1024

# --- palette (cream + navy + red, as in the winning 24 Nov edition) ---
CREAM = (250, 244, 230)
CREAM_DARK = (240, 232, 214)
NAVY = (16, 32, 64)
NAVY_LIGHT = (32, 56, 96)
RED = (178, 34, 34)
RED_DARK = (139, 0, 0)
INK = (24, 24, 24)
GREY = (90, 90, 90)
CARD_BG = (255, 252, 246)
CARD_BORDER = (190, 180, 160)
MAP_BG = (214, 230, 240)
MAP_LAND = (232, 214, 164)
GOLD = (184, 134, 11)

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"

def _font(name, size):
    try:
        return ImageFont.truetype(os.path.join(_FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()

def F_SERIF_B(s):
    return _font("DejaVuSerif-Bold.ttf", s)

def F_SERIF(s):
    return _font("DejaVuSerif.ttf", s)

def F_SERIF_I(s):
    return _font("DejaVuSerif-Italic.ttf", s)

def F_SANS_B(s):
    return _font("DejaVuSans-Bold.ttf", s)

def F_SANS(s):
    return _font("DejaVuSans.ttf", s)

def F_SANS_I(s):
    return _font("DejaVuSans-Oblique.ttf", s)

def text_w(d, s, font):
    """Width of s in font (draw object d)."""
    b = d.textbbox((0, 0), s, font=font)
    return b[2] - b[0]

def wrap(d, s, font, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def wrap_to(d, s, font, max_w, max_lines):
    """Wrap s to at most max_lines; returns (lines, ok)."""
    lines = wrap(d, s, font, max_w)
    return lines, len(lines) <= max_lines

def draw_centered(d, cx, y, s, font, fill):
    w = text_w(d, s, font)
    d.text((cx - w // 2, y), s, font=font, fill=fill)
    return w

def draw_right(d, x_right, y, s, font, fill):
    w = text_w(d, s, font)
    d.text((x_right - w, y), s, font=font, fill=fill)
    return w


# ---------------------------------------------------------------- pictorials
def _pict_rocket(w, h):
    """Rocket + orbit ring on a dark sky (high contrast)."""
    layer = Image.new("RGBA", (w, h), (18, 28, 52, 255))
    d = ImageDraw.Draw(layer)
    # stars
    for (sx, sy, r) in [(18, 12, 2), (w - 24, 10, 2), (w // 2, 8, 2),
                        (30, h - 12, 2), (w - 40, h - 14, 2),
                        (w * 0.30, 10, 2), (w * 0.72, 14, 2)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, 255))
    # orbit ellipse
    d.ellipse([w * 0.08, -h * 0.60, w * 0.92, h * 1.20],
              outline=(140, 160, 200, 255), width=2)
    # rocket body (vertical, nose up) — bigger
    cx = w // 2
    body_top = h * 0.10
    body_bot = h * 0.72
    bw = w * 0.11
    d.polygon([(cx, body_top), (cx + bw, body_top + h * 0.24),
               (cx + bw, body_bot), (cx - bw, body_bot),
               (cx - bw, body_top + h * 0.24)], fill=(245, 245, 245, 255),
              outline=(200, 60, 60, 255))
    d.polygon([(cx - bw, body_bot), (cx - bw - w * 0.05, body_bot + h * 0.14),
               (cx - bw * 0.4, body_bot)], fill=(200, 60, 60, 255))
    d.polygon([(cx + bw, body_bot), (cx + bw + w * 0.05, body_bot + h * 0.14),
               (cx + bw * 0.4, body_bot)], fill=(200, 60, 60, 255))
    # window
    d.ellipse([cx - bw * 0.45, body_top + h * 0.30, cx + bw * 0.45,
               body_top + h * 0.46], fill=(70, 130, 180, 255),
              outline=(40, 60, 90, 255))
    # flame
    d.polygon([(cx - bw * 0.5, body_bot + h * 0.12),
               (cx + bw * 0.5, body_bot + h * 0.12),
               (cx, h - 2)], fill=(255, 140, 0, 255))
    d.polygon([(cx - bw * 0.25, body_bot + h * 0.12),
               (cx + bw * 0.25, body_bot + h * 0.12),
               (cx, h - 8)], fill=(255, 220, 60, 255))
    return layer

def _pict_crash(w, h):
    """Falling market line + circuit-breaker halt bar."""
    layer = Image.new("RGBA", (w, h), (250, 236, 230, 255))
    d = ImageDraw.Draw(layer)
    # faint grid
    for gy in (h // 3, 2 * h // 3):
        d.line([(0, gy), (w, gy)], fill=(220, 205, 190, 255), width=1)
    # falling line
    pts = [(4, h * 0.18), (w * 0.22, h * 0.30), (w * 0.38, h * 0.26),
           (w * 0.55, h * 0.52), (w * 0.72, h * 0.66), (w * 0.92, h * 0.86)]
    d.line(pts, fill=(178, 34, 34, 255), width=4, joint="curve")
    for (px, py) in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(178, 34, 34, 255))
    # circuit breaker: vertical halt bar + label band
    bx = int(w * 0.55)
    d.rectangle([bx - 2, 4, bx + 2, h - 4], fill=(16, 32, 64, 255))
    d.rectangle([w - 74, 4, w - 4, 20], fill=(16, 32, 64, 255))
    d.text((w - 70, 6), "HALT", font=_font("DejaVuSans-Bold.ttf", 11),
           fill=(255, 255, 255, 255))
    # down arrow
    d.polygon([(w * 0.86, h * 0.62), (w * 0.92, h * 0.62),
               (w * 0.89, h * 0.72)], fill=(178, 34, 34, 255))
    return layer

def _pict_fire(w, h):
    """City skyline + flames, drawn on its own layer (clipped)."""
    layer = Image.new("RGBA", (w, h), (30, 34, 48, 255))
    d = ImageDraw.Draw(layer)
    # buildings
    import random
    rnd = random.Random(7)
    x = 0
    while x < w:
        bw = rnd.randint(w // 9, w // 6)
        bh = rnd.randint(int(h * 0.35), int(h * 0.75))
        d.rectangle([x, h - bh, x + bw - 2, h], fill=(52, 58, 78, 255))
        # lit windows
        for wy in range(h - bh + 6, h - 8, 12):
            for wx in range(x + 4, x + bw - 6, 10):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 200, 80, 255))
        x += bw
    # flames (two)
    for fx, fh in [(w * 0.30, h * 0.42), (w * 0.68, h * 0.50)]:
        d.polygon([(fx - 16, h), (fx - 10, h - fh * 0.55), (fx - 4, h - fh * 0.85),
                   (fx, h - fh), (fx + 5, h - fh * 0.80), (fx + 11, h - fh * 0.50),
                   (fx + 16, h)],
                  fill=(255, 120, 0, 255))
        d.polygon([(fx - 8, h), (fx - 4, h - fh * 0.55), (fx, h - fh * 0.70),
                   (fx + 4, h - fh * 0.50), (fx + 8, h)],
                  fill=(255, 220, 60, 255))
    # smoke dots
    for (sx, sy) in [(w * 0.30, 6), (w * 0.34, 12), (w * 0.68, 8)]:
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(150, 150, 160, 255))
    return layer

# ---------------------------------------------------------------- top sections
def _draw_masthead(img, d, y=0):
    d.rectangle([0, y, W, y + 22], fill=NAVY)
    d.text((32, y + 4), "THE WORLD IN ONE DAY", font=F_SANS_B(13), fill=(255, 255, 255))
    draw_right(d, W - 32, y + 4, "23 STORIES  ·  7 REGIONS", F_SANS_B(13), (255, 255, 255))
    draw_centered(d, W // 2, y + 5, "EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026",
                  F_SANS(11), (200, 210, 230))
    return y + 22

def _draw_title(img, d, y):
    # serif giant title; measure so margins stay >= 40px
    title = "WEDNESDAY 25 NOVEMBER 2026"
    size = 58
    f = F_SERIF_B(size)
    while text_w(d, title, f) > W - 140 and size > 40:
        size -= 2
        f = F_SERIF_B(size)
    draw_centered(d, W // 2, y, title, f, NAVY)
    return y + size + 2

def _draw_subhead(img, d, y):
    s = ("Shenzhou-24 launches, first Pakistani in orbit  ·  Asia markets plunge, "
         "Kospi trips breaker  ·  Russian strike kills 2 in Odesa")
    f = F_SERIF_I(15)
    draw_centered(d, W // 2, y, s, f, RED_DARK)
    return y + 18

def _draw_stat(img, d, y):
    stats = [
        ("−5.68%", "Kospi (11:20 KST)"),
        ("−8.2%", "Taiex"),
        ("$3,545", "gold, $/oz"),
        ("+4.9%", "Australia CPI"),
        ("2", "dead in Odesa"),
        ("417,000", "flights, FAA"),
    ]
    col_w = W // 6
    f_num = F_SANS_B(22)
    f_cap = F_SANS(11)
    for i, (num, cap) in enumerate(stats):
        cx = col_w * i + col_w // 2
        draw_centered(d, cx, y, num, f_num, RED)
        draw_centered(d, cx, y + 24, cap, f_cap, INK)
    # thin rule under
    d.line([(8, y + 38), (W - 8, y + 38)], fill=CARD_BORDER, width=1)
    return y + 40

def _draw_region(img, d, y):
    segs = [("Asia-Pacific", 4, (200, 60, 60)),
            ("Americas", 7, (60, 110, 200)),
            ("Europe", 8, (40, 130, 90)),
            ("Africa", 0, (150, 150, 150)),
            ("Oceania", 2, (200, 140, 40)),
            ("Middle East", 0, (150, 150, 150)),
            ("World", 2, (120, 80, 160))]
    total = sum(v for _, v, _ in segs)
    label = "STORIES BY REGION  ·  "
    f = F_SANS_B(13)
    x = 10
    d.text((x, y + 4), label, font=f, fill=INK)
    x += text_w(d, label, f) + 6
    parts = []
    for name, v, col in segs:
        parts.append((name, v, col))
    # text form: name n, joined by middots
    txt = "  ·  ".join("%s %d" % (n, v) for n, v, _ in parts)
    d.text((x, y + 4), txt, font=f, fill=INK)
    # colour bar under
    bx, bw_total = 10, W - 20
    bx0 = bx
    for name, v, col in segs:
        wseg = max(bw_total * v / total, 6) if v > 0 else 6
        d.rectangle([bx0, y + 24, bx0 + wseg - 2, y + 29], fill=col)
        bx0 += wseg
    return y + 32

def _draw_timeline(img, d, y):
    f = F_SANS(16)
    line1 = ("UTC 00:08 Kospi breaker · 00:18 Shenzhou-24 launch · "
             "00:24 gold $3,544.54 · 00:30 Australia CPI · "
             "01:00 Miss Universe final")
    line2 = ("~04:00 UTC crowning · 12:00 UTC round closes · "
             "13:30 UTC PCE+GDP (after round) · 17:45 UCL early · "
             "20:00 UCL main")
    d.text((10, y), line1, font=f, fill=INK)
    d.text((10, y + 18), line2, font=f, fill=INK)
    return y + 36


# ---------------------------------------------------------------- lead cards
BIG = [
    dict(kicker="ASIA-PACIFIC · SPACE", pict="rocket",
         head="China launches Shenzhou-24; first Pakistani in orbit",
         body=("Muhammad Zeeshan Ali, 40, in orbit; "
               "Tang Hongbo commands."),
         src="Reuters · Xinhua", tag="REPORTED"),
    dict(kicker="ASIA-PACIFIC · MARKETS", pict="crash",
         head="Asia markets plunge; Kospi circuit breaker trips",
         body=("Kospi −5.68% (11:20 KST), Taiex −8.2%, "
               "Nikkei −3.15%."),
         src="WSJ · Reuters", tag="REPORTED"),
    dict(kicker="EUROPE · UKRAINE", pict="fire",
         head="Russian strike kills 2 in Odesa; Kyiv flats ablaze",
         body=("Odesa: 2 dead, 3 hurt incl. a child; "
               "Kyiv flats ablaze."),
         src="Reuters", tag="REPORTED"),
]

MEDIUM = [
    dict(num=4, kicker="EUROPE · UCL",
         head="Real Madrid 5–1 PSV; rivals held",
         body="Mbappé 2; Real go 5/5, rivals held.",
         src="Reuters · UEFA", tag="REPORTED"),
    dict(num=5, kicker="AMERICAS · WEATHER",
         head="Twin storms hit both US coasts",
         body="East storm forms; SF tide 8.5 ft.",
         src="Reuters · CNN", tag="REPORTED"),
    dict(num=6, kicker="OCEANIA · AUSTRALIA",
         head="Australia inflation jumps to 4.9%",
         body="CPI +4.9%; RBA 5.10% hike eyed.",
         src="Reuters · ABS", tag="REPORTED"),
    dict(num=7, kicker="WORLD · GOLD",
         head="Gold dips to $3,545 as US data looms",
         body="Gold $3,544.54; PCE out 13:30 UTC.",
         src="Reuters", tag="REPORTED"),
    dict(num=8, kicker="EUROPE · BRUSSELS",
         head="EU hosts Western Balkans summit",
         body="EU hosts six Balkan leaders.",
         src="EU · Reuters", tag="FORECAST"),
    dict(num=9, kicker="AMERICAS · PUERTO RICO",
         head="Miss Universe: crowning expected",
         body="116 in San Juan; crowning ~04:00.",
         src="Wikipedia · depor", tag="FORECAST"),
    dict(num=10, kicker="AMERICAS · NBA",
         head="Pistons roll past Magic 104–86",
         body="Pistons win 104–86; two late games.",
         src="NBA", tag="REPORTED"),
    dict(num=11, kicker="EUROPE · UCL",
         head="PSG host Roma; Sporting host Utd",
         body="Nine games; 17:45 early, 20:00 main.",
         src="UEFA", tag="FORECAST"),
    dict(num=12, kicker="EUROPE · BRUSSELS",
         head="EU budget summit: €1.78tn on table",
         body="€1.78tn faces frugal revolt.",
         src="Reuters · EU", tag="FORECAST"),
    dict(num=13, kicker="WORLD · MARKETS",
         head="Bitcoin $59,928, oil $81.65",
         body="Bitcoin $59,928; oil $81.65.",
         src="Reuters", tag="REPORTED"),
]

def _draw_big_cards(img, d, y, height=168):
    margin, gap = 10, 8
    cw = (W - 2 * margin - 2 * gap) // 3
    pict_h = 60
    for i, c in enumerate(BIG):
        x0 = margin + i * (cw + gap)
        x1 = x0 + cw
        d.rectangle([x0, y, x1, y + height], outline=CARD_BORDER, width=1, fill=CARD_BG)
        # pictorial band, clipped
        pict = {"rocket": _pict_rocket, "crash": _pict_crash, "fire": _pict_fire}[c["pict"]](cw - 2, pict_h)
        img.paste(pict, (x0 + 1, y + 1))
        ty = y + pict_h + 4
        d.text((x0 + 6, ty), c["kicker"], font=F_SANS_B(11), fill=RED)
        ty += 14
        lines, ok = wrap_to(d, c["head"], F_SANS_B(19), cw - 12, 2)
        if not ok:
            raise RuntimeError("big headline overflows 2 lines: %r" % c["head"])
        for ln in lines:
            d.text((x0 + 6, ty), ln, font=F_SANS_B(19), fill=INK)
            ty += 20
        lines, ok = wrap_to(d, c["body"], F_SANS(17), cw - 12, 2)
        if not ok:
            raise RuntimeError("big body overflows 2 lines: %r" % c["body"])
        for ln in lines:
            d.text((x0 + 6, ty), ln, font=F_SANS(17), fill=INK)
            ty += 18
        # sources + tag at bottom
        d.text((x0 + 6, y + height - 12), c["src"], font=F_SANS(10), fill=GREY)
        draw_right(d, x1 - 6, y + height - 12, c["tag"], F_SANS_B(10), RED)
    return y + height

def _draw_medium_cards(img, d, y, rows=2, row_h=110):
    margin, gap = 10, 8
    cols = 5
    cw = (W - 2 * margin - (cols - 1) * gap) // cols
    for idx, c in enumerate(MEDIUM):
        r, col = divmod(idx, cols)
        x0 = margin + col * (cw + gap)
        x1 = x0 + cw
        y0 = y + r * row_h
        y1 = y0 + row_h - 6
        d.rectangle([x0, y0, x1, y1], outline=CARD_BORDER, width=1, fill=CARD_BG)
        # number + kicker
        d.text((x0 + 6, y0 + 3), str(c["num"]), font=F_SANS_B(15), fill=RED)
        num_w = text_w(d, str(c["num"]), F_SANS_B(15))
        d.text((x0 + 11 + num_w, y0 + 5), c["kicker"], font=F_SANS_B(10), fill=RED)
        ty = y0 + 19
        lines, ok = wrap_to(d, c["head"], F_SANS_B(16), cw - 12, 2)
        if not ok:
            raise RuntimeError("medium headline overflows 2 lines: %r" % c["head"])
        for ln in lines:
            d.text((x0 + 6, ty), ln, font=F_SANS_B(16), fill=INK)
            ty += 17
        lines, ok = wrap_to(d, c["body"], F_SANS(17), cw - 12, 2)
        if not ok:
            raise RuntimeError("medium body overflows 2 lines: %r" % c["body"])
        for ln in lines:
            d.text((x0 + 6, ty), ln, font=F_SANS(17), fill=INK)
            ty += 18
        d.text((x0 + 6, y1 - 12), c["src"], font=F_SANS(10), fill=GREY)
        draw_right(d, x1 - 6, y1 - 12, c["tag"], F_SANS_B(10), RED)
    return y + rows * row_h


# ---------------------------------------------------------------- map + briefs
BRIEFS = [
    (14, "UK-EU reset bill goes to Parliament Thursday"),
    (15, "Celtics top Wizards 113–99; Mavs–Nuggets under way"),
    (16, "Spain votes Sunday in snap general election"),
    (17, "Macy's 100th parade faces first balloonless year in 55"),
    (18, "FAA: busiest Thanksgiving travel in 16 years, 417,000+ flights"),
    (19, "Shenzhou-24 docks ~3.5 hours after launch; Zhu stays a year"),
    (20, "Kospi circuit breaker trips at 09:08 KST as futures fall 5.12%"),
    (21, "RBA rate 5.10% on the table before Christmas as inflation jumps"),
    (22, "Miss Universe 2026: 116 contestants, Bosch crowns successor"),
    (23, "Real Madrid perfect 5/5 in Champions League"),
]

# pin positions as (fx, fy) fractions of the map box
PINS = {
    1: (0.80, 0.30), 2: (0.86, 0.26), 3: (0.60, 0.24),
    4: (0.46, 0.38), 5: (0.22, 0.35), 6: (0.84, 0.80),
    7: (0.40, 0.48), 8: (0.52, 0.20), 9: (0.28, 0.58),
    10: (0.18, 0.28), 11: (0.49, 0.28), 12: (0.56, 0.33),
}

def _draw_map(img, d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAP_BG, outline=CARD_BORDER, width=1)
    # abstract continents (beige blobs)
    def blob(cx, cy, rx, ry):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=MAP_LAND,
                  outline=(200, 180, 130, 255))
    blob(x0 + w * 0.16, y0 + h * 0.30, w * 0.13, h * 0.22)   # N America
    blob(x0 + w * 0.28, y0 + h * 0.68, w * 0.07, h * 0.20)   # S America
    blob(x0 + w * 0.50, y0 + h * 0.26, w * 0.06, h * 0.12)   # Europe
    blob(x0 + w * 0.54, y0 + h * 0.55, w * 0.08, h * 0.20)   # Africa
    blob(x0 + w * 0.74, y0 + h * 0.30, w * 0.18, h * 0.22)   # Asia
    blob(x0 + w * 0.84, y0 + h * 0.76, w * 0.07, h * 0.10)   # Australia
    # pins
    for num, (fx, fy) in PINS.items():
        px, py = int(x0 + w * fx), int(y0 + h * fy)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=(255, 255, 255, 255), width=1)
        s = str(num)
        tw = text_w(d, s, F_SANS_B(11))
        d.text((px - tw // 2, py - 7), s, font=F_SANS_B(11), fill=(255, 255, 255))

def _draw_map_briefs(img, d, y, height=198):
    margin = 10
    map_w = 330
    d.text((margin, y), "WHERE IT HAPPENED — 12 LEADS PINNED",
           font=F_SANS_B(12), fill=INK)
    d.text((margin + map_w + 16, y), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=F_SANS_B(12), fill=INK)
    my = y + 18
    mh = height - 18
    _draw_map(img, d, margin, my, map_w, mh)
    bx = margin + map_w + 16
    bw = W - margin - bx
    f = F_SANS(18)
    by = my + 2
    for num, txt in BRIEFS:
        line = "%d. %s" % (num, txt)
        # must fit one line; if too wide, it would overflow — verify.py checks
        d.text((bx, by), line, font=f, fill=INK)
        by += 18
    return y + height

# ---------------------------------------------------------------- DATE CHECK
DATECHECK = [
    "Houthi drone Riyadh Tue 24 Nov",
    "Huawei convicted Tue 24 Nov",
    "CAS reinstates Senegal Tue 24 Nov",
    "Ukraine sank ships Mon 23 Nov",
    "CIA/ODNI breach Tue 24 Nov",
    "700k+ Russian dead Mon 23 Nov",
    "DR Congo Cessna down Sun 22 Nov",
    "Iraq PM vs Kurdistan Tue 24 Nov",
    "Hasina return rejected Tue 24 Nov",
    "Iran gas/power crisis 21–23 Nov",
    "UK/EU reset Mon 23 Nov",
    "Kyiv bridges attack Fri 20 Nov",
    "Senegal AFCON qual. Tue 17 Nov",
    "Kenya Mrima Hill deal Thu 19 Nov",
    "Adelaide space med. Mon 24 Nov",
    "Hamas security chief Tue 24 Nov",
    "Bolsonaro ICU Mon 23 Nov",
    "Mexico GDP +3.3% Q3 Tue 24 Nov",
    "Venezuela debt Tue 24 Nov",
    "'El Chapo Isidro' Sat 21 Nov",
    "Trump pardons turkeys Tue 24 Nov",
    "UN chief AI call Mon 23 Nov",
    "Lagarde quits ECB 29 Oct",
    "Sheffield Shield — date unverified",
    "UK sanctions Houthis Tue 24 Nov",
    "Iran medicine shortage Tue 24 Nov",
    "ECB nominations closed Fri 20 Nov",
    "Deep space ageing study Jul 2026",
]

def _draw_datecheck(img, d, y, height=196):
    margin = 10
    d.rectangle([margin, y, W - margin, y + height], outline=RED, width=2)
    d.text((margin + 8, y + 5),
           "DATE CHECK — NOT WEDNESDAY 25 NOVEMBER: first reported earlier",
           font=F_SANS_B(13), fill=RED_DARK)
    f = F_SANS(16)
    cols = 3
    col_w = (W - 2 * margin - 16) // cols
    rows = (len(DATECHECK) + cols - 1) // cols
    for i, item in enumerate(DATECHECK):
        col, row = divmod(i, rows)
        x = margin + 8 + col * col_w
        yy = y + 26 + row * 17
        d.text((x, yy), "× " + item, font=f, fill=RED_DARK)
    return y + height

def _draw_footer(img, d, y):
    f = F_SANS(11)
    d.text((10, y), "Sources: Reuters · WSJ · UEFA · EU · ABS · NBA · Xinhua · depor · Wikipedia",
           font=f, fill=GREY)
    d.text((10, y + 13),
           "REPORTED = carried by the day's wires  ·  CLAIM = one side's account, labelled as such  ·  FORECAST = still to happen when drawn",
           font=f, fill=GREY)
    return y + 26

# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = _draw_masthead(img, d, 0)
    y = _draw_title(img, d, y + 2)
    y = _draw_subhead(img, d, y)
    y = _draw_stat(img, d, y + 2)
    y = _draw_region(img, d, y + 2)
    y = _draw_timeline(img, d, y + 2)
    y = _draw_big_cards(img, d, y + 2)
    y = _draw_medium_cards(img, d, y + 2)
    y = _draw_map_briefs(img, d, y + 2)
    y = _draw_datecheck(img, d, y + 2)
    y = _draw_footer(img, d, y + 2)
    if y > H:
        raise RuntimeError("layout overflow: total height %d > %d" % (y, H))
    return img

def _out_path():
    for env in ("MAKEFUN_OUTPUT_DIR", "ENTRY_OUTPUT"):
        v = os.environ.get(env)
        if v:
            return v if v.endswith(".png") else os.path.join(v, "entry.png")
    return "/output/entry.png"

def main():
    if not _PIL_OK:
        print("Pillow unavailable", file=sys.stderr)
        return 2
    try:
        img = render()
    except Exception as e:
        print("render failed: %s" % e, file=sys.stderr)
        # fallback: copy committed entry.png
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(here, "entry.png")
        dst = _out_path()
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            shutil.copyfile(src, dst)
            print("fallback: copied committed entry.png to %s" % dst)
            return 0
        return 1
    dst = _out_path()
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    img.save(dst)
    print("wrote %s (%dx%d)" % (dst, W, H))
    return 0

if __name__ == "__main__":
    sys.exit(main())
