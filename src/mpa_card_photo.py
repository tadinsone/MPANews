#!/usr/bin/env python3
"""MPA News photo card (front/back) as SVG. Colors and font are in the <style> block."""
import base64
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import wrap  # noqa: E402

LOGO_URL = "https://mpanews.info/wp-content/uploads/2025/07/cropped-logo.png"
CARD_W, CARD_H, GAP, PAD = 360, 500, 36, 28
IMG_H = 250

CARD = {
    "category": "ခေါင်းကြီးသတင်း",
    "headline": "ဒေါ်အောင်ဆန်းစုကြည်နှင့် နိုင်ကျဉ်းအားလုံး လွတ်မြောက်ရေး ကမ္ဘာလုံးဆိုင်ရာလှုပ်ရှားမှုတွင် ပါဝင်ရန် ဖိတ်ခေါ်",
    "date": "၂၀ အောက်တိုဘာ ၂၀၂၆",
    "label": "တောင်းဆိုချက် ၃ ချက်",
    "demands": [
        "ဒေါ်အောင်ဆန်းစုကြည်အား မိသားစုနှင့် ပုံမှန် ဆက်သွယ်ခွင့်ပေးရန်",
        "ဒေါ်အောင်ဆန်းစုကြည်ကို ချက်ချင်းနှင့် အကန့်အသတ်မရှိ လွှတ်ပေးရန်",
        "နိုင်ငံရေးအကျဉ်းသားအားလုံးကို လွှတ်ပေးရန်",
    ],
    "url": "mpanews.info/headline/13798",
}


def tspans(lines, x, y, cls, lh):
    return "\n  ".join(
        f'<text class="{cls}" x="{x}" y="{y + i * lh:.1f}">{escape(l)}</text>' for i, l in enumerate(lines)
    )


def front(x0, img_b64):
    inner = CARD_W - 2 * PAD
    h_size, h_lh = 21, 33
    h_lines = wrap(CARD["headline"], h_size, inner)
    chip_y = IMG_H + 22
    head_y = chip_y + 60
    foot_y = CARD_H - 24
    chip_w = 22 + 10 * len(CARD["category"])
    return f"""<g transform="translate({x0},{GAP})">
  <rect class="front" width="{CARD_W}" height="{CARD_H}" rx="22" filter="url(#shadow)"/>
  <g clip-path="url(#round)">
    <image href="data:image/jpeg;base64,{img_b64}" x="0" y="0" width="{CARD_W}" height="{IMG_H}" preserveAspectRatio="xMidYMin slice"/>
    <rect class="bar" x="0" y="{IMG_H}" width="{CARD_W}" height="5"/>
  </g>
  <rect class="chip" x="{PAD}" y="{chip_y + 6}" width="{chip_w}" height="28" rx="14"/>
  <text class="chiptxt" x="{PAD + 12}" y="{chip_y + 26}">{escape(CARD['category'])}</text>
  {tspans(h_lines, PAD, head_y, 'head', h_lh)}
  <line class="rule" x1="{PAD}" y1="{foot_y - 36}" x2="{CARD_W - PAD}" y2="{foot_y - 36}"/>
  <image href="{LOGO_URL}" x="{PAD}" y="{foot_y - 28}" width="110" height="32" preserveAspectRatio="xMinYMid meet"/>
  <text class="meta" x="{CARD_W - PAD}" y="{foot_y - 6}" text-anchor="end">{escape(CARD['date'])}</text>
</g>"""


def back(x0):
    inner = CARD_W - 2 * PAD
    size, lh = 18, 18 * 1.8
    y = 140
    parts = []
    for i, d in enumerate(CARD["demands"], 1):
        lines = wrap(d, size, inner - 40)
        parts.append(f'<circle class="num" cx="{PAD + 14}" cy="{y - 6}" r="14"/>')
        parts.append(f'<text class="numtxt" x="{PAD + 14}" y="{y}" text-anchor="middle">{i}</text>')
        parts.append(tspans(lines, PAD + 40, y, "body", lh))
        y += len(lines) * lh + 26
    return f"""<g transform="translate({x0},{GAP})">
  <rect class="back" width="{CARD_W}" height="{CARD_H}" rx="22" filter="url(#shadow)"/>
  <rect class="bar2" x="{PAD}" y="34" width="34" height="5" rx="2.5"/>
  <text class="label" x="{PAD}" y="70">{escape(CARD['label'])}</text>
  {chr(10).join('  ' + p for p in parts).strip()}
  <rect class="cta" x="{PAD}" y="{CARD_H - 96}" width="{inner}" height="48" rx="24"/>
  <text class="ctatxt" x="{CARD_W / 2}" y="{CARD_H - 66}" text-anchor="middle">{CARD['url']}</text>
</g>"""


def build(img_path):
    img_b64 = base64.b64encode(Path(img_path).read_bytes()).decode()
    w, h = CARD_W * 2 + GAP * 3, CARD_H + GAP * 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>MPA News photo card</title>
<defs>
  <style>
    /* brand settings: edit colors and font here */
    /* font: Noto Sans Myanmar | ink/dark: #14213D | accent: #C8102E | muted: #6B7280 | canvas: #EEF1F5 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Myanmar:wght@400;700');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800');
    text {{ font-family: 'Noto Sans Myanmar','Pyidaungsu','Myanmar Text','Padauk','Inter',Arial,sans-serif; }}
    .canvas {{ fill: #EEF1F5; }}
    .front {{ fill: #FFFFFF; }}
    .back {{ fill: #14213D; }}
    .bar, .bar2, .cta, .chip {{ fill: #C8102E; }}
    .chiptxt {{ fill: #fff; font-size: 14px; font-weight: 700; }}
    .head {{ fill: #14213D; font-size: 21px; font-weight: 700; }}
    .meta {{ fill: #6B7280; font-size: 13px; }}
    .rule {{ stroke: #E5E7EB; stroke-width: 1; }}
    .label {{ fill: #AEB8CC; font-size: 14px; font-weight: 700; letter-spacing: 1px; }}
    .body {{ fill: #F4F6FA; font-size: 18px; }}
    .num {{ fill: #C8102E; }}
    .numtxt {{ fill: #fff; font-size: 15px; font-weight: 700; }}
    .ctatxt {{ fill: #fff; font-size: 16px; font-weight: 700; font-family: 'Inter',Arial,sans-serif; }}
  </style>
  <filter id="shadow" x="-10%" y="-10%" width="120%" height="125%">
    <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0F172A" flood-opacity="0.18"/>
  </filter>
  <clipPath id="round"><rect width="{CARD_W}" height="{CARD_H}" rx="22"/></clipPath>
</defs>
<rect class="canvas" width="{w}" height="{h}"/>
{front(GAP, img_b64)}
{back(GAP * 2 + CARD_W)}
</svg>
"""


if __name__ == "__main__":
    Path(sys.argv[2]).write_text(build(sys.argv[1]), encoding="utf-8")
    print("wrote", sys.argv[2])
