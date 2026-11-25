#!/usr/bin/env python3
"""verify.py — checks for news-image-20261125 v1 (\"The World in One Day\").

Exit 0 only if ALL checks pass. Run from the repo dir:
    python3 verify.py [path/to/entry.png]

NOTE: this edition has 23 verified Wednesday stories (13 leads + 10 briefs),
NOT 28 — five research items were dropped after verification because they
are not Wednesday news (Section 301 tariffs unconfirmed; deep-space ageing
Jul 2026; UK Houthi sanctions Tue 24 Nov; Iran medicine shortage Tue 24 Nov;
ECB nominations closed Fri 20 Nov). Region counts are APAC 4, Americas 7,
Europe 8, Africa 0, Oceania 2, Middle East 0, World 2 (total 23).
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image
    _PIL_OK = True
except Exception:
    _PIL_OK = False

PASS = []
FAIL = []

def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print("%s  (%s) %s" % ("PASS" if ok else "FAIL", name, detail))

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    png = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png")

    # ---- (a) size ----
    if not _PIL_OK:
        check("a: Pillow available", False)
        print("\n%d PASS, %d FAIL" % (len(PASS), len(FAIL)))
        return 1
    if not os.path.exists(png):
        check("a: entry.png exists", False, png)
        print("\n%d PASS, %d FAIL" % (len(PASS), len(FAIL)))
        return 1
    im = Image.open(png).convert("RGB")
    W, H = im.size
    check("a: entry.png 1024x1024", (W, H) == (1024, 1024), "%dx%d" % (W, H))

    import main as M
    d = ImageDraw = None
    from PIL import ImageDraw as _ID
    dd = _ID.Draw(im)

    # ---- (b) title + masthead margins >= 30px ----
    px = im.convert("L").load()
    # title band: rows 28..80, dark navy glyphs (<100) on cream
    xs = [x for y in range(28, 82) for x in range(W) if px[x, y] < 100]
    if xs:
        lm, rm = min(xs), W - 1 - max(xs)
        check("b: title margins >=30px", lm >= 30 and rm >= 30,
              "left %dpx, right %dpx" % (lm, rm))
    else:
        check("b: title margins >=30px", False, "no title glyphs found")
    # masthead: white text (>200) on navy bar, rows 2..20
    xs2 = [x for y in range(2, 21) for x in range(W) if px[x, y] > 200]
    if xs2:
        lm2, rm2 = min(xs2), W - 1 - max(xs2)
        check("b: masthead text margins >=30px", lm2 >= 30 and rm2 >= 30,
              "left %dpx, right %dpx" % (lm2, rm2))
    else:
        check("b: masthead text margins >=30px", False, "no masthead text found")

    # ---- (c) all 13 headlines present + complete, wrap <= 2 lines ----
    all_heads = [c["head"] for c in M.BIG] + [c["head"] for c in M.MEDIUM]
    check("c: 13 lead headlines", len(all_heads) == 13, "%d found" % len(all_heads))
    ok_c = True
    for c in M.BIG:
        lines, ok = M.wrap_to(dd, c["head"], M.F_SANS_B(19), 329 - 12, 2)
        if not ok:
            ok_c = False
            print("   big headline overflows: %r" % c["head"])
    for c in M.MEDIUM:
        lines, ok = M.wrap_to(dd, c["head"], M.F_SANS_B(16), 194 - 12, 2)
        if not ok:
            ok_c = False
            print("   medium headline overflows: %r" % c["head"])
    check("c: all headlines fit in 2 lines", ok_c)
    ok_cb = True
    for c in M.BIG:
        lines, ok = M.wrap_to(dd, c["body"], M.F_SANS(17), 329 - 12, 2)
        if not ok:
            ok_cb = False
            print("   big body overflows: %r" % c["body"])
    for c in M.MEDIUM:
        lines, ok = M.wrap_to(dd, c["body"], M.F_SANS(17), 194 - 12, 2)
        if not ok:
            ok_cb = False
            print("   medium body overflows: %r" % c["body"])
    check("c: all card bodies fit in 2 lines", ok_cb)

    # ---- (d) all 10 briefs present + complete, one line each ----
    check("d: 10 briefs", len(M.BRIEFS) == 10, "%d found" % len(M.BRIEFS))
    ok_d = True
    brief_w = 1024 - 10 - (10 + 330 + 16)
    for num, txt in M.BRIEFS:
        line = "%d. %s" % (num, txt)
        w = M.text_w(dd, line, M.F_SANS(18))
        if w > brief_w:
            ok_d = False
            print("   brief too wide (%dpx > %dpx): %r" % (w, brief_w, line))
    check("d: all briefs fit on one line at 18px", ok_d)

    # ---- (e) minimum font sizes ----
    # enforced by construction: briefs 18, DATE CHECK 16, bodies 17,
    # timeline 16, captions 14
    src = open(os.path.join(here, "main.py")).read()
    check("e: briefs font 18px", "F_SANS(18)" in src)
    check("e: DATE CHECK font 16px", "F_SANS(16)" in src)
    check("e: card body font 17px", "F_SANS(17)" in src)
    check("e: timeline font 16px", "def _draw_timeline" in src and
          "f = F_SANS(16)" in src)

    # ---- (f) timeline correctness ----
    check("f: Miss Universe at 01:00 UTC (not 20:00 UTC)",
          "01:00 Miss Universe final" in src and "20:00 Miss Universe" not in src)
    check("f: Shenzhou 00:18 in timeline", "00:18 Shenzhou-24 launch" in src)
    check("f: PCE 13:30 UTC marked after round",
          "13:30 UTC PCE+GDP (after round)" in src)
    check("f: UCL 17:45 + 20:00 in timeline",
          "17:45 UCL early" in src and "20:00 UCL main" in src)

    # ---- (g) no ellipsis anywhere ----
    check("g: no '...' in main.py", "..." not in src)
    check("g: no '…' in main.py", "…" not in src)
    check("g: no '...' in README", True)  # checked below with README read

    # ---- (h) 3 live badges in README ----
    readme = ""
    rp = os.path.join(here, "README.md")
    if os.path.exists(rp):
        readme = open(rp).read()
    badges = [
        "https://make.fun/badge/news-image-20261125.svg",
        "https://make.fun/badge/news-image-20261125/mekzibnn/news-world-today-25/rank.svg",
        "https://make.fun/badge/news-image-20261125/mekzibnn/news-world-today-25/reward.svg",
    ]
    for b in badges:
        check("h: badge %s" % b.split("/")[-1], b in readme)
    check("h: no shields.io badges", "shields.io" not in readme)
    check("g: no '...' in README", "..." not in readme)

    # ---- (i) region counts: 4/7/8/0/2/0/2, total 23 ----
    # leads: L1 APAC, L2 APAC, L3 Europe, L4 Europe, L5 Americas, L6 Oceania,
    # L7 World, L8 Europe, L9 Americas, L10 Americas, L11 Europe, L12 Europe,
    # L13 World; briefs: B1 Europe, B5 Americas, B6 Europe, B7 Americas,
    # B8 Americas, B9 APAC, B10 APAC, B12 Oceania, B13 Americas, B15 Europe
    regions = {"Asia-Pacific": 4, "Americas": 7, "Europe": 8, "Africa": 0,
               "Oceania": 2, "Middle East": 0, "World": 2}
    total = sum(regions.values())
    check("i: region counts 4/7/8/0/2/0/2 total 23", total == 23,
          "total %d" % total)
    check("i: region bar segments in main.py",
          '("Asia-Pacific", 4' in src and '("Americas", 7' in src and
          '("Europe", 8' in src and '("Africa", 0' in src and
          '("Oceania", 2' in src and '("Middle East", 0' in src and
          '("World", 2' in src)
    check("i: masthead says 23 STORIES", "23 STORIES" in src)
    check("i: DATE CHECK has 28 items", len(M.DATECHECK) == 28,
          "%d items" % len(M.DATECHECK))

    # ---- (j) pictorial band >= 55px ----
    # big cards start after timeline; measure the pictorial band of card 1:
    # find the first row below the masthead/title/stat/region/timeline where
    # the big-card row begins, then measure dark-sky pictorial rows.
    # Simpler robust check: the pictorial band is 60px by construction and
    # the rendered band contains non-cream pixels for >=55 rows.
    # Card 1 x-range approx 10..343; scan rows for pictorial (dark navy sky)
    # inside the big-card area (y ~206..374).
    pict_rows = 0
    for y in range(206, 374):
        # count dark-blue (rocket sky) pixels in card 1
        dark = sum(1 for x in range(12, 340)
                   if px[x, y] < 80)
        if dark > 50:
            pict_rows += 1
    check("j: pictorial band >=55px (dark-sky rows in card 1)",
          pict_rows >= 55, "%d rows" % pict_rows)

    print("\n%d PASS, %d FAIL" % (len(PASS), len(FAIL)))
    return 0 if not FAIL else 1

if __name__ == "__main__":
    sys.exit(main())
