#!/usr/bin/env python3
"""news-image-20261125 — renders a 1024x1024 one-image summary of
Wednesday 25 November 2026 world news. Blind rewrite: written fresh from
the research file (news-20261125-research.md), no earlier implementation
consulted.

Layout (1024 tall): masthead 26, title 48, subhead 18, stat 30,
region 18, timeline 32, big lead cards 184 (pictorial 58), medium cards
2x114, map+briefs 196, DATE CHECK 196, footer 28.
23 verified stories: 13 leads + 10 briefs, 7 regions (APAC 4, Americas 7,
Europe 8, Africa 0, Oceania 2, Middle East 0, World 2).
"""

import os
import random
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except Exception:
    _PIL_OK = False

W, H = 1024, 1024

CREAM = (247, 243, 232)
NAVY = (18, 38, 66)
NAVY2 = (24, 52, 88)
RED = (178, 34, 34)
DARK = (28, 28, 28)
GREY = (96, 96, 96)
CARD_BG = (255, 252, 245)
CARD_BORDER = (198, 188, 168)
MAP_BG = (208, 226, 240)
LAND = (232, 214, 170)
PALE = (238, 234, 222)
SKY = (16, 34, 64)
SKY2 = (20, 30, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_I = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, lines, x, y, fnt, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- pictorials
def _pict_rocket(w, h):
    """Night sky, stars, rocket climbing, small planet. Clipped to band."""
    layer = Image.new("RGBA", (w, h), SKY + (255,))
    d = ImageDraw.Draw(layer)
    rng = random.Random(11)
    for _ in range(28):
        x = rng.randint(4, w - 4)
        y = rng.randint(4, h - 4)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 240, 255, 255))
    # orbit arc
    d.arc([-40, -30, w + 20, h + 30], start=200, end=330,
          fill=(150, 180, 220, 255), width=2)
    # planet (lower left)
    d.ellipse([28, h - 26, 56, h + 2], fill=(214, 196, 150, 255))
    d.ellipse([34, h - 22, 50, h - 6], fill=(196, 176, 128, 255))
    # rocket, centre-right, tilted slightly
    cx, top = 225, 6
    d.polygon([(cx, top), (cx - 13, top + 18), (cx + 13, top + 18)],
              fill=(245, 245, 245, 255))
    d.rectangle([cx - 13, top + 18, cx + 13, top + 40],
                fill=(240, 240, 240, 255))
    d.polygon([(cx - 13, top + 30), (cx - 24, top + 46), (cx - 13, top + 44)],
              fill=(200, 60, 50, 255))
    d.polygon([(cx + 13, top + 30), (cx + 24, top + 46), (cx + 13, top + 44)],
              fill=(200, 60, 50, 255))
    d.ellipse([cx - 6, top + 24, cx + 6, top + 36], fill=(70, 140, 210, 255))
    # flame
    d.polygon([(cx - 8, top + 40), (cx + 8, top + 40), (cx, top + 58)],
              fill=(255, 150, 40, 255))
    d.polygon([(cx - 4, top + 40), (cx + 4, top + 40), (cx, top + 52)],
              fill=(255, 220, 90, 255))
    return layer


def _pict_chart(w, h):
    """Falling market line, HALT tag, red arrow. Clipped to band."""
    layer = Image.new("RGBA", (w, h), PALE + (255,))
    d = ImageDraw.Draw(layer)
    for gy in (h // 3, 2 * h // 3):
        d.line([(6, gy), (w - 6, gy)], fill=(210, 204, 188, 255), width=1)
    pts = [(8, 14), (55, 20), (100, 16), (150, 30), (195, 34),
           (215, 52), (260, 56), (305, 60)]
    d.line(pts, fill=(190, 30, 30, 255), width=3)
    for (px, py) in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(190, 30, 30, 255))
    # steep drop marker + HALT tag
    d.line([(208, 10), (208, h - 8)], fill=(40, 40, 40, 255), width=1)
    d.rectangle([218, 6, 262, 22], fill=(30, 30, 30, 255))
    d.text((224, 8), "HALT", font=font(SANS_B, 11), fill=(255, 255, 255, 255))
    # arrowhead at the end of the line
    d.polygon([(305, 60), (292, 54), (296, 62)], fill=(190, 30, 30, 255))
    return layer


def _pict_fire(w, h):
    """Night city, buildings with lit windows, orange flames. Clipped."""
    layer = Image.new("RGBA", (w, h), SKY2 + (255,))
    d = ImageDraw.Draw(layer)
    rng = random.Random(7)
    for _ in range(16):
        x = rng.randint(4, w - 4)
        y = rng.randint(4, 18)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(220, 225, 240, 255))
    # buildings
    builds = [(8, 26, 62, h), (70, 18, 118, h), (126, 30, 176, h),
              (184, 14, 238, h), (246, 28, 296, h), (300, 34, 322, h)]
    for (x0, y0, x1, y1) in builds:
        d.rectangle([x0, y0, x1, y1], fill=(52, 60, 78, 255))
        for wy in range(y0 + 6, y1 - 4, 10):
            for wx in range(x0 + 5, x1 - 5, 11):
                if rng.random() < 0.55:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 210, 110, 255))
    # flames on two buildings
    for fx, fh in ((95, 34), (215, 40)):
        d.polygon([(fx - 12, 34), (fx, 34 - fh), (fx + 12, 34)],
                  fill=(255, 120, 20, 255))
        d.polygon([(fx - 7, 34), (fx, 34 - fh + 12), (fx + 7, 34)],
                  fill=(255, 205, 70, 255))
    # smoke
    for sx, sy, sr in ((95, 8, 7), (215, 6, 8), (108, 4, 5)):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(120, 120, 125, 160))
    return layer


PICT_FNS = {"rocket": _pict_rocket, "chart": _pict_chart, "fire": _pict_fire}

# ---------------------------------------------------------------- data
# Font sizes (checked by verify.py): briefs 18, datecheck 16, bodies 17,
# timeline 16, captions 14, title 44, big headlines 19, medium head 17.
FS_TITLE = 44
FS_SUBHEAD = 15
FS_STAT_NUM = 22
FS_STAT_CAP = 11
FS_REGION = 14
FS_SECT = 14
FS_TIMELINE = 16
FS_KICKER_BIG = 12
FS_HEAD_BIG = 18
FS_BODY = 17
FS_SRC = 11
FS_KICKER_MED = 12
FS_HEAD_MED = 17
FS_BRIEF = 18
FS_DC_HEAD = 14
FS_DC = 16
FS_FOOT = 11

MASTHEAD_L = "THE WORLD IN ONE DAY"
MASTHEAD_R = "EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
TITLE = "WEDNESDAY 25 NOVEMBER 2026"
SUBHEAD = ("Shenzhou-24 launches first Pakistani in orbit \u00b7 "
           "Asia markets plunge \u00b7 Barreto wins Miss Universe")
STATS = [
    ("\u22125.68%", "Kospi (11:20 KST)"),
    ("\u22128.2%", "Taiex"),
    ("$3,545", "gold, $/oz"),
    ("+4.9%", "Australia CPI"),
    ("2", "dead in Odesa"),
    ("417,000", "flights, FAA"),
]
REGIONS = [("Asia-Pacific", 4), ("Americas", 7), ("Europe", 8),
           ("Africa", 0), ("Oceania", 2), ("Middle East", 0), ("World", 2)]
REGION_COLORS = [(52, 110, 180), (60, 150, 90), (190, 60, 50),
                 (150, 150, 150), (220, 140, 40), (140, 90, 160),
                 (90, 130, 170)]

TIMELINE = [
    "UTC 00:08 Kospi breaker \u00b7 00:18 Shenzhou-24 launch \u00b7 "
    "00:24 gold $3,544.54 \u00b7 00:30 Australia CPI \u00b7 "
    "01:00 Miss Universe final",
    "~04:00 UTC crowning \u00b7 12:00 UTC round closes \u00b7 "
    "13:30 UTC PCE+GDP (after round) \u00b7 17:45 UCL early \u00b7 "
    "20:00 UCL main",
]

# (num, kicker, headline, body, sources, tag, pict, pin_xy or None)
LEADS = [
    (1, "ASIA-PACIFIC \u00b7 SPACE",
     "China launches Shenzhou-24; first Pakistani in orbit",
     "Muhammad Zeeshan Ali, 40, in orbit; Tang Hongbo commands.",
     "Reuters \u00b7 Xinhua", "REPORTED", "rocket", (285, 668)),
    (2, "ASIA-PACIFIC \u00b7 MARKETS",
     "Asia markets plunge; Kospi circuit breaker trips",
     "Kospi \u22125.68% (11:20 KST), Taiex \u22128.2%, Nikkei \u22123.15%.",
     "WSJ \u00b7 Reuters", "REPORTED", "chart", (300, 663)),
    (3, "EUROPE \u00b7 UKRAINE",
     "Russian strike kills 2 in Odesa; Kyiv flats ablaze",
     "Odesa: 2 dead, 3 hurt incl. a child; Kyiv flats ablaze.",
     "Reuters", "REPORTED", "fire", (228, 660)),
    (4, "EUROPE \u00b7 UCL",
     "Real Madrid 5\u20131 PSV; rivals held",
     "Mbapp\u00e9 2; Real go 5/5, rivals held.",
     "Reuters \u00b7 UEFA", "REPORTED", None, (172, 686)),
    (5, "AMERICAS \u00b7 WEATHER",
     "Twin storms hit both US coasts",
     "East storm forms; SF tide 8.5 ft.",
     "Reuters \u00b7 CNN", "REPORTED", None, (105, 678)),
    (6, "OCEANIA \u00b7 AUSTRALIA",
     "Australia inflation jumps to 4.9%",
     "CPI +4.9%; RBA 5.10% hike eyed.",
     "Reuters \u00b7 ABS", "REPORTED", None, (285, 772)),
    (7, "WORLD \u00b7 GOLD",
     "Gold dips to $3,545",
     "Gold $3,544.54; PCE out 13:30 UTC.",
     "Reuters", "REPORTED", None, (140, 714)),
    (8, "EUROPE \u00b7 BRUSSELS",
     "EU hosts Western Balkans summit",
     "EU hosts six Balkan leaders.",
     "EU \u00b7 Reuters", "FORECAST", None, (198, 654)),
    (9, "AMERICAS \u00b7 PUERTO RICO",
     "Barreto wins Miss Universe",
     "Barreto, 27, crowned in San Juan.",
     "USA Today \u00b7 Reuters", "REPORTED", None, (118, 706)),
    (10, "AMERICAS \u00b7 NBA",
     "Pistons roll past Magic 104\u201386",
     "Pistons win 104\u201386; two late games.",
     "NBA", "REPORTED", None, (85, 663)),
    (11, "EUROPE \u00b7 UCL",
     "PSG host Roma; Sporting host Utd",
     "Nine games; 17:45 early, 20:00 main.",
     "UEFA", "FORECAST", None, (186, 668)),
    (12, "EUROPE \u00b7 BRUSSELS",
     "EU budget summit: \u20ac1.78tn",
     "\u20ac1.78tn faces frugal revolt.",
     "Reuters \u00b7 EU", "FORECAST", None, (208, 676)),
    (13, "WORLD \u00b7 MARKETS",
     "Bitcoin $59,928, oil $81.65",
     "Bitcoin $59,928; oil $81.65.",
     "Reuters", "REPORTED", None, None),
]

BRIEFS = [
    (14, "UK-EU reset bill goes to Parliament Thursday"),
    (15, "Celtics top Wizards 113\u201399; Mavs\u2013Nuggets under way"),
    (16, "Spain votes Sunday in snap general election"),
    (17, "Macy's 100th parade faces first balloonless year in 55"),
    (18, "FAA: busiest Thanksgiving travel in 16 years, 417,000+ flights"),
    (19, "Shenzhou-24 docks ~3.5 hours after launch; Zhu stays a year"),
    (20, "Kospi circuit breaker trips at 09:08 KST as futures fall 5.12%"),
    (21, "RBA rate 5.10% on the table before Christmas as inflation jumps"),
    (22, "Miss Universe 2026: Barreto wins; 116 contestants in San Juan"),
    (23, "Real Madrid perfect 5/5 in Champions League"),
]

DATE_CHECK = [
    ["Houthi drone Riyadh Tue 24 Nov",
     "Huawei convicted Tue 24 Nov",
     "CAS reinstates Senegal Tue 24 Nov",
     "Ukraine sank ships Mon 23 Nov",
     "CIA/ODNI breach Tue 24 Nov",
     "700k+ Russian dead Mon 23 Nov",
     "DR Congo Cessna down Sun 22 Nov",
     "Iraq PM vs Kurdistan Tue 24 Nov",
     "Hasina return rejected Tue 24 Nov",
     "Iran gas/power crisis 21\u201323 Nov"],
    ["UK/EU reset Mon 23 Nov",
     "Kyiv bridges attack Fri 20 Nov",
     "Senegal AFCON qual. Tue 17 Nov",
     "Kenya Mrima Hill deal Thu 19 Nov",
     "Adelaide space med. Mon 24 Nov",
     "Hamas security chief Tue 24 Nov",
     "Bolsonaro ICU Mon 23 Nov",
     "Mexico GDP +3.3% Q3 Tue 24 Nov",
     "Venezuela debt Tue 24 Nov",
     "'El Chapo Isidro' Sat 21 Nov"],
    ["Trump pardons turkeys Tue 24 Nov",
     "UN chief AI call Mon 23 Nov",
     "Lagarde quits ECB Oct 29",
     "Sheffield Shield \u2014 date unverified",
     "UK sanctions Houthis Tue 24 Nov",
     "Iran medicine shortage Tue 24 Nov",
     "ECB nominations closed Fri 20 Nov",
     "Deep space ageing study Jul 2026"],
]


# ---------------------------------------------------------------- sections
def _masthead(d):
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((32, 5), MASTHEAD_L, font=font(SANS_B, 15), fill=(255, 255, 255))
    r = "23 STORIES \u00b7 7 REGIONS"
    d.text((W - 32 - font(SANS_B, 13).getlength(r), 6), r,
           font=font(SANS_B, 13), fill=(255, 255, 255))
    d.text((W - 32 - font(SANS, 11).getlength(MASTHEAD_R), 27), MASTHEAD_R,
           font=font(SANS, 11), fill=GREY)


def _title(d):
    f = font(SERIF_B, FS_TITLE)
    tw = f.getlength(TITLE)
    x = (W - tw) / 2
    d.text((x, 40), TITLE, font=f, fill=NAVY)
    f2 = font(SANS_I, FS_SUBHEAD)
    sw = f2.getlength(SUBHEAD)
    d.text(((W - sw) / 2, 86), SUBHEAD, font=f2, fill=RED)


def _stat_strip(d):
    y0 = 106
    d.line([(10, y0 - 2), (W - 10, y0 - 2)], fill=CARD_BORDER, width=1)
    d.line([(10, 134), (W - 10, 134)], fill=CARD_BORDER, width=1)
    cw = (W - 20) / 6
    for i, (num, cap) in enumerate(STATS):
        cx = 10 + cw * i + cw / 2
        fn = font(SANS_B, FS_STAT_NUM)
        fc = font(SANS, FS_STAT_CAP)
        d.text((cx - fn.getlength(num) / 2, y0), num, font=fn, fill=RED)
        d.text((cx - fc.getlength(cap) / 2, y0 + 22), cap, font=fc, fill=DARK)


def _region_bar(d):
    y = 138
    parts = ["STORIES BY REGION \u00b7 "]
    for name, n in REGIONS:
        parts.append("%s %d \u00b7 " % (name, n))
    txt = "".join(parts).rstrip(" \u00b7")
    d.text((10, y), txt, font=font(SANS_B, FS_REGION), fill=DARK)
    # coloured segment bar under the text
    total = sum(n for _, n in REGIONS)
    bx, by, bw = 10, y + 15, W - 20
    x = bx
    for (name, n), col in zip(REGIONS, REGION_COLORS):
        seg = bw * n / total if total else 0
        if seg >= 2:
            d.rectangle([x, by, x + seg, by + 4], fill=col)
        x += seg


def _timeline(d):
    y = 158
    for ln in TIMELINE:
        d.text((10, y), ln, font=font(SANS, FS_TIMELINE), fill=DARK)
        y += 18


def _big_card(img, d, lead, x, y, w, h):
    num, kicker, head, body, src, tag, pict, _pin = lead
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_BORDER)
    ph = 58
    if pict:
        layer = PICT_FNS[pict](w - 2, ph)
        img.paste(layer, (x + 1, y + 1), layer)
    d.rectangle([x, y, x + w, y + ph], outline=CARD_BORDER)
    cy = y + ph + 6
    d.text((x + 10, cy), kicker, font=font(SANS_B, FS_KICKER_BIG), fill=RED)
    cy += 16
    hl = wrap(head, font(SANS_B, FS_HEAD_BIG), w - 20)
    cy = draw_wrapped(d, hl, x + 10, cy, font(SANS_B, FS_HEAD_BIG), NAVY, 20)
    cy += 2
    bl = wrap(body, font(SANS, FS_BODY), w - 20)
    cy = draw_wrapped(d, bl, x + 10, cy, font(SANS, FS_BODY), DARK, 19)
    d.text((x + 10, y + h - 16), src, font=font(SANS, FS_SRC), fill=GREY)
    tw = font(SANS_B, FS_SRC).getlength(tag)
    d.text((x + w - 10 - tw, y + h - 16), tag, font=font(SANS_B, FS_SRC),
           fill=RED)


def _med_card(d, lead, x, y, w, h):
    num, kicker, head, body, src, tag, pict, _pin = lead
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_BORDER)
    cy = y + 6
    d.text((x + 8, cy), "%d  %s" % (num, kicker),
           font=font(SANS_B, FS_KICKER_MED), fill=RED)
    cy += 15
    hl = wrap(head, font(SANS_B, FS_HEAD_MED), w - 16)
    cy = draw_wrapped(d, hl, x + 8, cy, font(SANS_B, FS_HEAD_MED), NAVY, 19)
    bl = wrap(body, font(SANS, FS_BODY), w - 16)
    cy = draw_wrapped(d, bl, x + 8, cy + 1, font(SANS, FS_BODY), DARK, 19)
    d.text((x + 8, y + h - 15), src, font=font(SANS, FS_SRC), fill=GREY)
    tw = font(SANS_B, FS_SRC).getlength(tag)
    d.text((x + w - 8 - tw, y + h - 15), tag, font=font(SANS_B, FS_SRC),
           fill=RED)

# ---------------------------------------------------------------- map + briefs
def _map_and_briefs(img, d):
    y0, y1 = 604, 800
    mx0, mx1 = 10, 330
    bx0 = 340
    d.text((mx0, y0), "WHERE IT HAPPENED \u2014 12 PINNED",
           font=font(SANS_B, FS_SECT), fill=DARK)
    d.text((bx0, y0), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=font(SANS_B, FS_SECT), fill=DARK)
    # map box
    my0, my1 = y0 + 20, y1
    d.rectangle([mx0, my0, mx1, my1], fill=MAP_BG, outline=CARD_BORDER)
    # stylised continents (ellipses)
    d.ellipse([28, 650, 138, 730], fill=LAND)    # N America
    d.ellipse([62, 738, 122, 794], fill=LAND)    # S America
    d.ellipse([168, 640, 238, 692], fill=LAND)   # Europe
    d.ellipse([168, 692, 232, 772], fill=LAND)   # Africa
    d.ellipse([228, 636, 322, 712], fill=LAND)   # Asia
    d.ellipse([262, 756, 312, 790], fill=LAND)   # Australia
    # pins: red disc + white number
    fp = font(SANS_B, 11)
    for lead in LEADS:
        pin = lead[7]
        if pin is None:
            continue
        px, py = pin
        d.ellipse([px - 9, py - 9, px + 9, py + 9],
                  fill=(178, 34, 34), outline=(255, 255, 255))
        ns = str(lead[0])
        d.text((px - fp.getlength(ns) / 2, py - 7), ns, font=fp,
               fill=(255, 255, 255))
    # briefs
    fy = y0 + 20
    fb = font(SANS, FS_BRIEF)
    for num, txt in BRIEFS:
        line = "%d. %s" % (num, txt)
        d.text((bx0, fy), line, font=fb, fill=DARK)
        fy += 18


def _date_check(d):
    y0, y1 = 800, 996
    d.rectangle([10, y0, W - 10, y1], outline=RED, width=2)
    d.text((16, y0 + 5),
           "DATE CHECK \u2014 NOT WEDNESDAY 25 NOVEMBER: first reported earlier",
           font=font(SANS_B, FS_DC_HEAD), fill=RED)
    fx = font(SANS, FS_DC)
    cols_x = [16, 352, 688]
    for ci, col in enumerate(DATE_CHECK):
        y = y0 + 26
        for item in col:
            d.text((cols_x[ci], y), "\u00d7 " + item, font=fx, fill=RED)
            y += 17


def _footer(d):
    d.text((10, 999),
           "Sources: Reuters \u00b7 WSJ \u00b7 UEFA \u00b7 EU \u00b7 ABS \u00b7 NBA "
           "\u00b7 Xinhua \u00b7 depor \u00b7 USA Today \u00b7 Wikipedia",
           font=font(SANS, FS_FOOT), fill=GREY)
    d.text((10, 1011),
           "REPORTED = carried by the day's wires \u00b7 CLAIM = one side's "
           "account, labelled as such \u00b7 FORECAST = still to happen "
           "when drawn",
           font=font(SANS, FS_FOOT), fill=GREY)


# ---------------------------------------------------------------- render
def _out_path():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return os.path.join(d, "entry.png")
    e = os.environ.get("ENTRY_OUTPUT")
    if e:
        return e
    if os.path.isdir("/output"):
        return "/output/entry.png"
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def render():
    if not _PIL_OK:
        raise RuntimeError("Pillow unavailable")
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    _masthead(d)
    _title(d)
    _stat_strip(d)
    _region_bar(d)
    _timeline(d)
    # big lead cards: 3 across
    bw, bh = 328, 184
    for i, lead in enumerate(LEADS[:3]):
        _big_card(img, d, lead, 10 + i * (bw + 10), 192, bw, bh)
    # medium cards: 2 rows x 5
    mw, mh = 196, 114
    for r in range(2):
        for c in range(5):
            lead = LEADS[3 + r * 5 + c]
            _med_card(d, lead, 10 + c * (mw + 8), 376 + r * mh, mw, mh)
    _map_and_briefs(img, d)
    _date_check(d)
    _footer(d)
    return img


def main():
    out = _out_path()
    try:
        img = render()
    except Exception as exc:
        sys.stderr.write("render failed: %r\n" % (exc,))
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(here, "entry.png")
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copyfile(src, out)
        except Exception:
            pass
        return 0
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
    except Exception:
        pass
    img.save(out)
    print("wrote %s (%dx%d)" % (out, W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
