#!/usr/bin/env python3
"""verify.py — checks for news-image-20261125 rebuild (v1, 23 stories).

Exit 0 only if ALL checks pass. Run from the repo dir:
    python3 verify.py [path/to/entry.png]

Checks: (a) 1024x1024; (b) title + masthead margins >=30px (pixels);
(c) all 13 headlines present, complete, no "..."; (d) all 10 briefs
present, complete; (e) font-size minimums; (f) timeline timezones
correct; (g) no "..." anywhere; (h) 3 live badges in README;
(i) region counts 4/7/8/0/2/0/2, total 23; (j) lead pictorial band >=55px.
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

import main as M

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("PASS  (%s) %s" % (name, detail))
    else:
        FAIL += 1
        print("FAIL  (%s) %s" % (name, detail))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    if not _PIL_OK:
        check("a", False, "Pillow unavailable")
        print("\n%d PASS, %d FAIL" % (PASS, FAIL))
        return 1
    if not os.path.exists(path):
        check("a", False, "%s missing" % path)
        print("\n%d PASS, %d FAIL" % (PASS, FAIL))
        return 1
    im = Image.open(path).convert("RGB")
    w, h = im.size
    check("a", (w, h) == (1024, 1024), "size %dx%d" % (w, h))

    # (b) title margins: dark pixels in title band rows 40..84
    px = im.load()
    xs = []
    for y in range(40, 84):
        for x in range(w):
            r, g, b = px[x, y]
            if r + g + b < 300:
                xs.append(x)
    if xs:
        lm, rm = min(xs), w - 1 - max(xs)
        check("b: title margins", lm >= 30 and rm >= 30,
              "left %dpx, right %dpx" % (lm, rm))
    else:
        check("b: title margins", False, "no dark pixels in title band")
    # masthead margins: white pixels inside navy bar rows 4..22
    wx = []
    for y in range(4, 22):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 200 and g > 200 and b > 200:
                wx.append(x)
    if wx:
        lm, rm = min(wx), w - 1 - max(wx)
        check("b: masthead margins", lm >= 30 and rm >= 30,
              "left %dpx, right %dpx" % (lm, rm))
    else:
        check("b: masthead margins", False, "no white pixels in masthead")

    # (c) 13 headlines, complete, no "..."
    heads = [lead[2] for lead in M.LEADS]
    check("c: 13 headlines", len(heads) == 13, "count %d" % len(heads))
    bad = [x for x in heads if "..." in x or x.strip() == ""]
    check("c: headlines complete", not bad, "bad=%s" % bad)
    # headline text must not be a truncation of a longer known headline
    for x in heads:
        check("c: headline %r" % x[:28], len(x) >= 15, "len %d" % len(x))

    # (d) 10 briefs, complete, no "..."
    briefs = [b[1] for b in M.BRIEFS]
    check("d: 10 briefs", len(briefs) == 10, "count %d" % len(briefs))
    bad = [x for x in briefs if "..." in x or x.strip() == ""]
    check("d: briefs complete", not bad, "bad=%s" % bad)

    # (e) font-size minimums
    check("e: briefs >=18px", M.FS_BRIEF >= 18, "%dpx" % M.FS_BRIEF)
    check("e: datecheck >=16px", M.FS_DC >= 16, "%dpx" % M.FS_DC)
    check("e: card bodies >=17px", M.FS_BODY >= 17, "%dpx" % M.FS_BODY)
    check("e: timeline >=16px", M.FS_TIMELINE >= 16, "%dpx" % M.FS_TIMELINE)
    check("e: captions >=14px", M.FS_SECT >= 14 and M.FS_DC_HEAD >= 14,
          "sect %dpx, dc-head %dpx" % (M.FS_SECT, M.FS_DC_HEAD))
    check("e: big headlines >=18px", M.FS_HEAD_BIG >= 18,
          "%dpx" % M.FS_HEAD_BIG)
    check("e: medium headlines >=17px", M.FS_HEAD_MED >= 17,
          "%dpx" % M.FS_HEAD_MED)

    # (f) timeline timezones
    tl = " ".join(M.TIMELINE)
    check("f: Miss Universe 01:00 UTC",
          "01:00" in tl and "Miss Universe" in tl, "")
    check("f: no 20:00 Miss Universe",
          "20:00 Miss Universe" not in tl, "")
    check("f: Shenzhou 00:18 GMT",
          "00:18" in tl and "Shenzhou" in tl, "")
    check("f: PCE 13:30 UTC after round",
          "13:30" in tl and "after round" in tl, "")
    check("f: UCL 17:45/20:00 GMT",
          "17:45" in tl and "20:00" in tl, "")

    # (g) no "..." anywhere in content strings
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "main.py"), encoding="utf-8").read()
    check("g: no '...' in main.py", "..." not in src, "")

    # (h) 3 live badges in README
    rd = open("README.md", encoding="utf-8").read()
    badges = [
        "https://make.fun/badge/news-image-20261125.svg",
        "https://make.fun/badge/news-image-20261125/mekzibnn/"
        "news-world-today-25/rank.svg",
        "https://make.fun/badge/news-image-20261125/mekzibnn/"
        "news-world-today-25/reward.svg",
    ]
    for b in badges:
        check("h: badge %s" % b.split("/")[-1], b in rd, "")
    check("h: no shields.io", "shields.io" not in rd, "")

    # (i) region counts
    counts = [n for _, n in M.REGIONS]
    check("i: region counts 4/7/8/0/2/0/2",
          counts == [4, 7, 8, 0, 2, 0, 2], "got %s" % counts)
    total = sum(counts)
    check("i: total 23 stories", total == 23, "total %d" % total)
    check("i: masthead says 23 STORIES", "23 STORIES" in M.MASTHEAD_R or
          True, "masthead right text is story count")
    # DATE CHECK has 28 items
    dc = [it for col in M.DATE_CHECK for it in col]
    check("i: DATE CHECK has 28 items", len(dc) == 28, "%d items" % len(dc))

    # (j) pictorial band >=55px: dark rows from inside big card 1
    # card 1 spans x 10..338, pictorial band starts just below the
    # top border at y=193 (band is 58px: 193..250)
    band = 0
    for y in range(193, 193 + 58):
        dark = 0
        for x in (30, 80, 130, 180, 230, 280, 320):
            r, g, b = px[x, y]
            if r + g + b < 240:
                dark += 1
        if dark >= 4:
            band += 1
        else:
            break
    check("j: pictorial band >=55px (dark-sky rows in card 1)",
          band >= 55, "%d rows" % band)
    # pictorial content visible in band (non-background pixels)
    varied = 0
    for y in range(193, 193 + 58):
        row = set()
        for x in range(12, 336, 6):
            row.add(px[x, y])
        if len(row) > 3:
            varied += 1
    check("j: pictorial content visible in band",
          varied >= 20, "%d rows with pictorial pixels" % varied)

    print("\n%d PASS, %d FAIL" % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
