#!/usr/bin/env python3
"""Render entry.png for news-image-20261125 V1 (ATM).

Written from scratch in this session (2026-11-25), for Wednesday 25 Nov 2026.
Layout (new for this day — not the ni24 layout):
  - Kicker + serif masthead + red italic subhead naming the three shocks.
  - DATE CHECK strip naming 16 items left out (first reported before 25 Nov).
  - Region strip: 7 regions with story counts.
  - THREE SHOCKS: three big illustrated panels (tariffs / Ras Tanura / Kospi),
    each with one huge baked number, instead of three small text columns.
  - GRID: 12 stories in 2 columns x 6 rows, headlines ~2x the size of the
    5-6 column grids on the leaderboard, each card with a mini scene and a
    NEW/TODAY tag saying what is new today, plus a C/R/CL evidence tag.
  - THE DAY IN NUMBERS: 8 big numbers strip.
  - SMALL PRINT index: 22 more stories, honestly labelled as small print.
All drawings are procedural vector work in this file; no external assets.
Deterministic: no randomness, no clock, no network. Rendered at 2x then
downscaled with LANCZOS to 1024x1024.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S
MX = 20                    # side margin (in 1024 units; scaled below)
CW = 1024 - 2 * MX         # content width = 984

# ---------- palette (muted, 10 colours; W1-W5 in sistem-visual.txt) ----------
PAPER    = (247, 242, 231)  # cream paper
INK      = (20, 20, 20)     # near-black
GREY     = (110, 108, 100)
FAINT    = (150, 148, 138)
RED      = (178, 34, 34)    # kept for the most urgent (W4)
DARKRED  = (140, 20, 20)
NAVY     = (16, 24, 48)
DUSK     = (46, 52, 84)
SEA      = (28, 52, 76)
WHITE    = (255, 255, 255)
CREAMBOX = (255, 246, 240)  # date-check fill
GREEN    = (46, 125, 50)    # CONFIRMED
AMBER    = (176, 124, 0)    # REPORTED
ORANGE   = (230, 126, 34)
YELLOW   = (240, 196, 60)
TEAL     = (0, 121, 107)
SKY      = (135, 180, 205)
FIRE     = (220, 90, 30)

REGION = {
    "AMERICAS":     (46, 125, 50),
    "EUROPE":       (31, 78, 121),
    "MIDEAST":      (179, 84, 30),
    "ASIA-PACIFIC": (178, 34, 34),
    "AFRICA":       (106, 90, 20),
    "OCEANIA":      (0, 121, 107),
    "WORLD":        (110, 108, 100),
}
REGION_COUNTS = [
    ("AMERICAS", 9), ("EUROPE", 5), ("MIDEAST", 6), ("ASIA-PACIFIC", 7),
    ("AFRICA", 4), ("OCEANIA", 3), ("WORLD", 3),
]

# ---------- fonts ----------
FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


SERIF_B = lambda s: font(FD + "DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: font(FL + "LiberationSerif-BoldItalic.ttf", s)
SANS_B  = lambda s: font(FD + "DejaVuSans-Bold.ttf", s)
SANS    = lambda s: font(FD + "DejaVuSans.ttf", s)
SANS_I  = lambda s: font(FL + "LiberationSans-Italic.ttf", s)


def sc(v):
    """Scale a 1024-unit value to render pixels."""
    return int(v * S)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, max_w):
    """Truncate with ellipsis to fit max_w (single line)."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1]
    return text + "…"


def text_h(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[3] - b[1]


# ---------- data ----------
SHOCKS = [
    {
        "num": "14", "num_size": 76, "bg": SEA, "scene": "ship",
        "tag": "NEW", "ev": "C",
        "head": "U.S. TARIFFS ON 14 ECONOMIES",
        "body": "USTR proposes Section 301 duties: China up to 20%, India 25%, EU 15%.",
    },
    {
        "num": "550,000", "num_size": 44, "bg": DARKRED, "scene": "refinery",
        "tag": "NEW", "ev": "R",
        "head": "RAS TANURA: REFINERY HIT",
        "body": "Houthis claim strike on Saudi's largest refinery; 4 drones downed; Brent +2.4%.",
    },
    {
        "num": "−6.2%", "num_size": 60, "bg": NAVY, "scene": "chart",
        "tag": "NEW", "ev": "C",
        "head": "KOSPI PLUNGES 6.2%",
        "body": "Seoul closes at 4,697.51 as AI doubts return; Samsung −9.9%, SoftBank −14.8%.",
    },
]

GRID = [
    # (region, tag, ev, headline, summary, scene, number)
    ("ASIA-PACIFIC", "TODAY", "C", "SHENZHOU-24 DOCKS AT TIANGONG",
     "Pakistan's Ali is the first foreigner aboard the station", "rocket", "00:18"),
    ("AMERICAS", "NEW", "C", "CARTAGENA: 20 HOSTAGES FREED",
     "17-hour supermarket siege ends; one gunman killed", "rescue", "20"),
    ("EUROPE", "NEW", "C", "POUNDLAND FALLS: 11,000 JOBS",
     "Discount chain enters administration after no buyer found", "shop", "11,000"),
    ("EUROPE", "NEW", "C", "UK ENERGY CAP TO RISE 26%",
     "Typical bill £1,723 to £2,166 from January", "bolt", "+26%"),
    ("AMERICAS", "NEW", "C", "US ECONOMY GROWS 4.3%",
     "Fastest in three years; inflation at 3.8%", "bars", "4.3%"),
    ("MIDEAST", "NEW", "R", "US WEIGHS STRIKING IRAN LEADERS",
     "Reports say Khamenei among targets; Israel cites chemicals", "target", None),
    ("MIDEAST", "NEW", "C", "HODEIDAH PORT STRUCK",
     "Coalition hits port; Houthis threaten Jeddah", "port", "80%"),
    ("EUROPE", "NEW", "R", "MERZ: RUSSIA WANTS MORE",
     "Berlin: Moscow escalating massively beyond Ukraine", "flag", None),
    ("MIDEAST", "NEW", "C", "KNESSET: OCT 7 INQUIRY ADVANCES",
     "State inquiry approved over Netanyahu's objections", "columns", "7"),
    ("OCEANIA", "NEW", "C", "SOLOMONS PICK AUSTRALIA",
     "Security pact bars foreign bases; ends China pact", "handshake", "1st"),
    ("ASIA-PACIFIC", "NEW", "C", "BANGLADESH WAGES UP 36%",
     "Minimum wage to 17,000 taka amid protests", "factory", "+36%"),
    ("AFRICA", "NEW", "C", "RAMAPHOSA WINS COURT FIGHT",
     "Court drops finding that risked impeachment", "scales", "1"),
]

NUMBERS = [
    ("−6.2%", "KOSPI"), ("14", "TARIFFS"),
    ("550,000", "RAS TANURA"), ("$93.60", "BRENT"),
    ("4.3%", "US GDP Q3"), ("+26%", "ENERGY CAP"),
    ("11,000", "JOBS"), ("20", "FREED"),
]

ALSO = [
    "Ábrego García leaves US for Spain",
    "DR Congo aircraft missing; Ebola teams trapped",
    "Venezuela reveals $237.5bn debt",
    "North Korea expels Swiss diplomat",
    "Miners trapped in flooded Indonesia gold mine",
    "Australia inflation hits 4.9%",
    "CIA and intelligence office breached",
    "US–Armenia launch TRIPP transit route",
    "Pentagon criticises Canada's defence spending",
    "Miss Universe: Jennifer Barreto of Puerto Rico",
    "Sudan drone strikes kill 19 in Blue Nile",
    "England heat deaths hit record ~5,200",
    "EU unveils €50bn tech fund",
    "Dangote IPO to be Africa's biggest listing",
    "Argentina enters technical recession",
    "UNAIDS warns HIV gains could unravel",
    "Hanoi gas blast kills 7",
    "Ras Al Khaimah bus crash kills 13",
    "Ex-officer guilty of Sydney double murder",
    "Edmonton to host 2028 Grey Cup",
    "South Pole Telescope's clearest distant map",
    "Japan unveils moon-water rover prototype",
]

DATE_CHECK = ("DATE CHECK — LEFT OUT, NOT 25 NOVEMBER: Huawei verdict · 700,000 Russian "
              "dead leak · Senegal restored · Riyadh tower · Hormuz tankers · Chen Jining · "
              "Cuba life expectancy · Zambia treason · Iraq oilfields · singer flogged · "
              "Gaza strike · Poland no-fly zone · Benghazi ships · Iowa blast · Wolbachia · "
              "Dimorphos")


# ---------- mini scenes (one accent per illustration; one big number each) ----------
def scene_ship(d, x0, y0, w, h):
    """Container ship + tariff bars on a sea band."""
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], fill=SEA)
    d.rectangle([sc(x0), sc(y0 + h * 0.62), sc(x0 + w), sc(y0 + h)], fill=(18, 38, 60))
    # hull
    d.polygon([(sc(x0 + w * 0.08), sc(y0 + h * 0.55)), (sc(x0 + w * 0.92), sc(y0 + h * 0.55)),
               (sc(x0 + w * 0.82), sc(y0 + h * 0.72)), (sc(x0 + w * 0.18), sc(y0 + h * 0.72))],
              fill=(30, 30, 30))
    # containers
    for i, c in enumerate([(178, 34, 34), (240, 196, 60), (46, 125, 50), (31, 78, 121)]):
        d.rectangle([sc(x0 + w * (0.16 + i * 0.17)), sc(y0 + h * 0.34),
                     sc(x0 + w * (0.30 + i * 0.17)), sc(y0 + h * 0.55)], fill=c)
    # tariff bars rising
    for i in range(4):
        bh = h * (0.10 + i * 0.06)
        d.rectangle([sc(x0 + w * (0.70 + i * 0.06)), sc(y0 + h * 0.42 - bh),
                     sc(x0 + w * (0.74 + i * 0.06)), sc(y0 + h * 0.42)], fill=YELLOW)


def scene_refinery(d, x0, y0, w, h):
    """Refinery towers + fire + smoke."""
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], fill=DARKRED)
    d.rectangle([sc(x0), sc(y0 + h * 0.70), sc(x0 + w), sc(y0 + h)], fill=(40, 12, 12))
    for i in range(3):
        tx = x0 + w * (0.14 + i * 0.22)
        d.rectangle([sc(tx), sc(y0 + h * 0.38), sc(tx + w * 0.10), sc(y0 + h * 0.70)], fill=(90, 30, 24))
        d.polygon([(sc(tx), sc(y0 + h * 0.38)), (sc(tx + w * 0.05), sc(y0 + h * 0.22)),
                   (sc(tx + w * 0.10), sc(y0 + h * 0.38))], fill=(60, 18, 14))
    # flames (one bright accent: fire orange)
    for i, fx in enumerate([0.30, 0.52, 0.74]):
        d.polygon([(sc(x0 + w * (fx - 0.05)), sc(y0 + h * 0.70)),
                   (sc(x0 + w * fx), sc(y0 + h * 0.38)),
                   (sc(x0 + w * (fx + 0.05)), sc(y0 + h * 0.70))], fill=FIRE)
    # smoke puffs
    for cx, cy, r in [(0.30, 0.22, 0.09), (0.52, 0.14, 0.11), (0.74, 0.20, 0.08)]:
        d.ellipse([sc(x0 + w * (cx - r)), sc(y0 + h * (cy - r)),
                   sc(x0 + w * (cx + r)), sc(y0 + h * (cy + r))], fill=(120, 110, 100))


def scene_chart(d, x0, y0, w, h):
    """Falling market chart with a red plunge line."""
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], fill=NAVY)
    # gridlines
    for i in range(1, 4):
        yy = y0 + h * i / 4
        d.line([sc(x0 + w * 0.06), sc(yy), sc(x0 + w * 0.94), sc(yy)], fill=DUSK, width=sc(1))
    # bars falling
    vals = [0.85, 0.78, 0.82, 0.62, 0.66, 0.42, 0.30]
    for i, v in enumerate(vals):
        bx = x0 + w * (0.08 + i * 0.125)
        d.rectangle([sc(bx), sc(y0 + h * (0.92 - v * 0.7)),
                     sc(bx + w * 0.08), sc(y0 + h * 0.92)], fill=(96, 122, 168))
    # plunge line (one bright accent: red)
    pts = [(sc(x0 + w * (0.10 + i * 0.13)), sc(y0 + h * (0.24 + i * 0.09 + (0.10 if i > 3 else 0))))
           for i in range(7)]
    d.line(pts, fill=RED, width=sc(3))
    d.ellipse([sc(pts[-1][0] / S - 4), sc(pts[-1][1] / S - 4),
               sc(pts[-1][0] / S + 4), sc(pts[-1][1] / S + 4)], fill=RED)


def mini_scene(d, kind, x0, y0, w, h, num):
    """Small scene block for a grid card; number baked in white bold."""
    bg = {"rocket": NAVY, "rescue": TEAL, "shop": (110, 108, 100), "bolt": AMBER,
          "bars": GREEN, "target": DARKRED, "port": (179, 84, 30), "flag": (31, 78, 121),
          "columns": (90, 60, 110), "handshake": TEAL, "factory": (120, 40, 40),
          "scales": (150, 120, 20)}[kind]
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], fill=bg)
    cx, cy = x0 + w / 2, y0 + h / 2
    if kind == "rocket":
        d.polygon([(sc(cx), sc(y0 + 4)), (sc(cx - 9), sc(cy + 6)), (sc(cx + 9), sc(cy + 6))], fill=WHITE)
        d.rectangle([sc(cx - 9), sc(cy + 6), sc(cx + 9), sc(y0 + h - 12)], fill=WHITE)
        d.polygon([(sc(cx - 9), sc(y0 + h - 12)), (sc(cx), sc(y0 + h - 2)),
                   (sc(cx + 9), sc(y0 + h - 12))], fill=YELLOW)
        for sx, sy in [(x0 + 8, y0 + 8), (x0 + w - 10, y0 + 12), (x0 + 12, y0 + h - 10)]:
            d.ellipse([sc(sx - 1.5), sc(sy - 1.5), sc(sx + 1.5), sc(sy + 1.5)], fill=WHITE)
    elif kind == "rescue":
        d.rectangle([sc(x0 + 8), sc(y0 + 12), sc(x0 + w - 8), sc(y0 + h - 6)], fill=WHITE)
        d.rectangle([sc(cx - 7), sc(y0 + h - 20), sc(cx + 7), sc(y0 + h - 6)], fill=bg)
        d.rectangle([sc(x0 + 12), sc(y0 + 16), sc(x0 + 22), sc(y0 + 26)], fill=bg)
        d.rectangle([sc(x0 + w - 22), sc(y0 + 16), sc(x0 + w - 12), sc(y0 + 26)], fill=bg)
    elif kind == "shop":
        d.rectangle([sc(x0 + 6), sc(y0 + 16), sc(x0 + w - 6), sc(y0 + h - 6)], fill=WHITE)
        d.polygon([(sc(x0 + 4), sc(y0 + 16)), (sc(x0 + w - 4), sc(y0 + 16)),
                   (sc(x0 + w - 10), sc(y0 + 6)), (sc(x0 + 10), sc(y0 + 6))], fill=RED)
        d.rectangle([sc(cx - 8), sc(y0 + h - 18), sc(cx + 8), sc(y0 + h - 6)], fill=bg)
    elif kind == "bolt":
        d.polygon([(sc(cx + 4), sc(y0 + 4)), (sc(cx - 8), sc(cy + 2)), (sc(cx - 1), sc(cy + 2)),
                   (sc(cx - 4), sc(y0 + h - 4)), (sc(cx + 8), sc(cy - 2)),
                   (sc(cx + 1), sc(cy - 2))], fill=YELLOW)
    elif kind == "bars":
        for i, v in enumerate([0.35, 0.55, 0.45, 0.8]):
            bx = x0 + 10 + i * 11
            d.rectangle([sc(bx), sc(y0 + h - 8 - v * (h - 16)),
                         sc(bx + 8), sc(y0 + h - 8)], fill=WHITE)
    elif kind == "target":
        for r, c in [(20, WHITE), (14, RED), (8, WHITE)]:
            d.ellipse([sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r)], fill=c)
    elif kind == "port":
        d.rectangle([sc(x0), sc(y0 + h - 14), sc(x0 + w), sc(y0 + h)], fill=(18, 38, 60))
        d.rectangle([sc(x0 + 10), sc(y0 + 14), sc(x0 + 14), sc(y0 + h - 14)], fill=WHITE)
        d.line([sc(x0 + 10), sc(y0 + 14), sc(x0 + w - 10), sc(y0 + 26)], fill=WHITE, width=sc(2))
        d.rectangle([sc(x0 + w - 26), sc(y0 + h - 24), sc(x0 + w - 8), sc(y0 + h - 14)], fill=YELLOW)
    elif kind == "flag":
        d.rectangle([sc(cx - 1), sc(y0 + 6), sc(cx + 1), sc(y0 + h - 6)], fill=WHITE)
        d.polygon([(sc(cx + 1), sc(y0 + 6)), (sc(cx + 24), sc(y0 + 12)),
                   (sc(cx + 1), sc(y0 + 18))], fill=RED)
    elif kind == "columns":
        for i in range(3):
            bx = x0 + 10 + i * 14
            d.rectangle([sc(bx), sc(y0 + 12), sc(bx + 8), sc(y0 + h - 10)], fill=WHITE)
        d.rectangle([sc(x0 + 6), sc(y0 + 8), sc(x0 + w - 6), sc(y0 + 12)], fill=WHITE)
        d.rectangle([sc(x0 + 6), sc(y0 + h - 10), sc(x0 + w - 6), sc(y0 + h - 6)], fill=WHITE)
    elif kind == "handshake":
        d.ellipse([sc(cx - 16), sc(cy - 8), sc(cx - 2), sc(cy + 8)], fill=WHITE)
        d.ellipse([sc(cx + 2), sc(cy - 8), sc(cx + 16), sc(cy + 8)], fill=YELLOW)
    elif kind == "factory":
        d.rectangle([sc(x0 + 8), sc(y0 + 18), sc(x0 + w - 8), sc(y0 + h - 6)], fill=WHITE)
        d.polygon([(sc(x0 + 8), sc(y0 + 18)), (sc(x0 + 18), sc(y0 + 8)),
                   (sc(x0 + 28), sc(y0 + 18))], fill=WHITE)
        d.rectangle([sc(x0 + w - 16), sc(y0 + 6), sc(x0 + w - 10), sc(y0 + 18)], fill=WHITE)
    elif kind == "scales":
        d.line([sc(cx), sc(y0 + 8), sc(cx), sc(y0 + h - 8)], fill=WHITE, width=sc(2))
        d.line([sc(cx - 16), sc(y0 + 12), sc(cx + 16), sc(y0 + 12)], fill=WHITE, width=sc(2))
        d.polygon([(sc(cx - 20), sc(y0 + 22)), (sc(cx - 12), sc(y0 + 22)),
                   (sc(cx - 16), sc(y0 + 14))], fill=WHITE)
        d.polygon([(sc(cx + 12), sc(y0 + 22)), (sc(cx + 20), sc(y0 + 22)),
                   (sc(cx + 16), sc(y0 + 14))], fill=WHITE)
    if num:
        f = SANS_B(13)
        tw = d.textlength(num, font=f)
        # number sits bottom-left over a dark chip so it stays readable
        d.rectangle([sc(x0 + 2), sc(y0 + h - 16), sc(x0 + 2 + tw / S + 6), sc(y0 + h - 2)],
                    fill=(0, 0, 0))
        d.text((sc(x0 + 5), sc(y0 + h - 16)), num, font=f, fill=WHITE)


# ---------- page ----------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MX, MX + CW
    y = 14

    # kicker
    f_kick = SANS_B(15)
    kick = "THE WORLD IN ONE DAY  •  37 STORIES  •  7 REGIONS  •  EVERY ONE DATED 25 NOV 2026"
    d.text((sc((1024 - d.textlength(kick, font=f_kick) / S) / 2), sc(y)), kick, font=f_kick, fill=INK)
    y += 24

    # masthead
    f_mast = SERIF_B(52)
    mast = "Wednesday 25 November 2026"
    d.text((sc((1024 - d.textlength(mast, font=f_mast) / S) / 2), sc(y)), mast, font=f_mast, fill=INK)
    y += 66

    # subhead
    f_sub = SERIF_I(21)
    sub = "Tariffs on 14 economies  ·  Ras Tanura burning  ·  Kospi −6.2%"
    d.text((sc((1024 - d.textlength(sub, font=f_sub) / S) / 2), sc(y)), sub, font=f_sub, fill=RED)
    y += 32

    # DATE CHECK strip
    dc_h = 48
    d.rectangle([sc(x0), sc(y), sc(x1), sc(y + dc_h)], outline=RED, width=sc(2), fill=CREAMBOX)
    f_dc = SANS(12.5)
    lines = wrap(d, DATE_CHECK, f_dc, sc(CW - 24))
    ly = y + 5
    for ln in lines[:3]:
        d.text((sc(x0 + 12), sc(ly)), ln, font=f_dc, fill=INK)
        ly += 13
    y += dc_h + 8

    # region strip
    f_reg = SANS_B(13)
    chip_w = CW / 7
    for i, (name, n) in enumerate(REGION_COUNTS):
        cx0 = x0 + i * chip_w
        d.rectangle([sc(cx0 + 1), sc(y), sc(cx0 + chip_w - 1), sc(y + 30)], fill=REGION[name])
        label = f"{name} {n}"
        d.text((sc(cx0 + chip_w / 2 - d.textlength(label, font=f_reg) / S / 2), sc(y + 8)),
               label, font=f_reg, fill=WHITE)
    y += 30 + 8

    # THREE SHOCKS — three big panels
    gap = 12
    pw = (CW - 2 * gap) / 3
    ph = 218
    scenes = {"ship": scene_ship, "refinery": scene_refinery, "chart": scene_chart}
    for i, s in enumerate(SHOCKS):
        px = x0 + i * (pw + gap)
        # scene block with huge baked number
        sh = 104
        scenes[s["scene"]](d, px, y, pw, sh)
        f_num = SANS_B(s["num_size"])
        nw = d.textlength(s["num"], font=f_num) / S
        d.rectangle([sc(px + 8), sc(y + 8),
                     sc(px + 8 + nw + 14), sc(y + 8 + s["num_size"] + 8)], fill=(0, 0, 0))
        d.text((sc(px + 15), sc(y + 10)), s["num"], font=f_num, fill=WHITE)
        # tag row
        ty = y + sh + 6
        f_tag = SANS_B(11)
        w0 = d.textlength(s["tag"], font=f_tag) / S
        w1 = d.textlength(s["ev"], font=f_tag) / S
        for (tg, col, bx, tw) in [(s["tag"], RED, px, w0),
                                  (s["ev"], GREEN if s["ev"] == "C" else AMBER, px + w0 + 14, w1)]:
            d.rectangle([sc(bx), sc(ty), sc(bx + tw + 8), sc(ty + 15)], fill=col)
            d.text((sc(bx + 4), sc(ty + 2)), tg, font=f_tag, fill=WHITE)
        # headline (2 lines max)
        f_head = SANS_B(19)
        hl = wrap(d, s["head"], f_head, sc(pw - 8))
        hy = ty + 20
        for ln in hl[:2]:
            d.text((sc(px + 2), sc(hy)), ln, font=f_head, fill=INK)
            hy += 22
        # body (2 lines)
        f_body = SANS(12.5)
        bl = wrap(d, s["body"], f_body, sc(pw - 8))
        by = hy + 2
        for ln in bl[:2]:
            d.text((sc(px + 2), sc(by)), ln, font=f_body, fill=INK)
            by += 15
        # panel border
        d.rectangle([sc(px), sc(y), sc(px + pw), sc(y + ph)], outline=INK, width=sc(1))
    y += ph + 8

    # GRID — 12 stories, 2 columns x 6 rows
    gw = (CW - gap) / 2
    gh = 50
    for r in range(6):
        for c in range(2):
            region, tag, ev, head, summ, scene, num = GRID[r * 2 + c]
            gx = x0 + c * (gw + gap)
            gy = y + r * (gh + 3)
            col = REGION[region]
            # left mini scene
            mini_scene(d, scene, gx, gy, 62, gh, num)
            # tag row
            f_tag = SANS_B(10)
            tx = gx + 70
            d.rectangle([sc(tx), sc(gy + 3), sc(tx + 44), sc(gy + 15)], fill=RED)
            d.text((sc(tx + 4), sc(gy + 4.5)), tag, font=f_tag, fill=WHITE)
            ev_col = GREEN if ev == "C" else AMBER
            d.rectangle([sc(tx + 48), sc(gy + 3), sc(tx + 64), sc(gy + 15)], fill=ev_col)
            d.text((sc(tx + 53), sc(gy + 4.5)), ev, font=f_tag, fill=WHITE)
            # region label right
            f_rl = SANS_B(9)
            rl = region
            d.text((sc(gx + gw - d.textlength(rl, font=f_rl) / S - 4), sc(gy + 5)), rl,
                   font=f_rl, fill=col)
            # headline + summary
            f_h = SANS_B(17)
            d.text((sc(tx), sc(gy + 18)), fit_text(d, head, f_h, sc(gw - 74)), font=f_h, fill=INK)
            f_s = SANS(12.5)
            d.text((sc(tx), sc(gy + 36)), fit_text(d, summ, f_s, sc(gw - 74)), font=f_s, fill=(60, 58, 52))
            # card border (neighbour backgrounds differ via scene colours)
            d.rectangle([sc(gx), sc(gy), sc(gx + gw), sc(gy + gh)], outline=(200, 196, 182), width=sc(1))
    y += 6 * gh + 5 * 3 + 8

    # THE DAY IN NUMBERS strip
    f_nlab = SANS_B(10)
    d.text((sc(x0), sc(y)), "THE DAY IN NUMBERS", font=SANS_B(13), fill=INK)
    y += 20
    nw = CW / 8
    for i, (val, lab) in enumerate(NUMBERS):
        cx0 = x0 + i * nw
        d.rectangle([sc(cx0 + 1), sc(y), sc(cx0 + nw - 1), sc(y + 48)],
                    fill=NAVY if i % 2 == 0 else DUSK)
        f_v = SANS_B(22)
        d.text((sc(cx0 + nw / 2 - d.textlength(val, font=f_v) / S / 2), sc(y + 6)),
               val, font=f_v, fill=WHITE)
        d.text((sc(cx0 + nw / 2 - d.textlength(lab, font=f_nlab) / S / 2), sc(y + 34)),
               lab, font=f_nlab, fill=(200, 200, 190))
    y += 48 + 8

    # SMALL PRINT index — 22 more, honestly labelled
    f_sp = SANS_B(12)
    sp_label = "SMALL PRINT — 22 MORE FROM WEDNESDAY 25 NOVEMBER  (READ AT FULL SIZE)"
    d.text((sc(x0), sc(y)), sp_label, font=f_sp, fill=GREY)
    y += 18
    f_a = SANS(12.5)
    col_w = CW / 3
    for i, item in enumerate(ALSO):
        col = i % 3
        row = i // 3
        ax = x0 + col * col_w
        ay = y + row * 14
        d.text((sc(ax), sc(ay)), fit_text(d, "· " + item, f_a, sc(col_w - 10)),
               font=f_a, fill=(60, 58, 52))
    y += 8 * 14 + 6

    # footer
    f_f = SANS(11)
    foot = ("ALL STORIES FIRST REPORTED OR HAPPENING ON WEDNESDAY 25 NOVEMBER 2026  •  "
            "SOURCES: ONETURN, REUTERS, AP, CNN, XINHUA, USTR  •  DRAWN BY PROGRAM, NO PHOTOS")
    d.text((sc((1024 - d.textlength(foot, font=f_f) / S) / 2), sc(y)), foot, font=f_f, fill=GREY)
    y += 16
    assert y <= 1024, f"overflow: y={y}"
    return img, y


def main():
    img, used = render()
    small = img.resize((1024, 1024), Image.LANCZOS)
    small.save("entry.png", optimize=True)
    print(f"rendered entry.png, used height {used}/1024")


if __name__ == "__main__":
    main()
