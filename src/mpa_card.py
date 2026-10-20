#!/usr/bin/env python3
"""MPA News sample card (front/back) as SVG. Brand values live in the <style> block at the top of the SVG."""
import sys
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import wrap  # noqa: E402  (same wrapping rules as the pipeline renderer)

LOGO_URL = "https://mpanews.info/wp-content/uploads/2025/07/cropped-logo.png"
SOURCE = "mpanews.info"
CARD_W, CARD_H, GAP, PAD = 360, 500, 36, 28

# --- sample content: one real headline from mpanews.info (article 13786) ---
CARD = {
    "category": "စီးပွားရေး",
    "headline": "ရန်ကုန် အထည်ချုပ်စက်ရုံ ၄ ရုံ ဆက်တိုက် ပိတ်မည်၊ လူတစ်သောင်းနီးပါး အလုပ်လက်မဲ့ ဖြစ်ရန်ရှိ",
    "date": "၁၉ အောက်တိုဘာ ၂၀၂၆",
    "byline": "MPA",
    "summary": "ရန်ကုန်တွင် အထည်ချုပ်စက်ရုံ ၄ ရုံ ဆက်တိုက် ပိတ်သိမ်းမည်ဖြစ်ပြီး အလုပ်သမား တစ်သောင်းနီးပါး အလုပ်လက်မဲ့ ဖြစ်နိုင်ကြောင်း အလုပ်သမားအဖွဲ့အစည်းက ထုတ်ပြန်။",
    "url": "mpanews.info/headline/13786",
}


def lines_svg(lines, x, y, cls, lh):
    return "\n".join(
        f'<text class="{cls}" x="{x}" y="{y + i * lh:.1f}">{escape(l)}</text>' for i, l in enumerate(lines)
    )


def front(x0):
    inner = CARD_W - 2 * PAD
    h_size, h_lh = 26, 26 * 1.55
    h_lines = wrap(CARD["headline"], h_size, inner)
    y_head = 190
    y_meta = CARD_H - 62
    return f"""<g transform="translate({x0},{GAP})">
  <rect class="front" width="{CARD_W}" height="{CARD_H}" rx="22" filter="url(#shadow)"/>
  <rect class="bar" width="{CARD_W}" height="8" rx="4" x="0" y="0" clip-path="url(#top)"/>
  <image href="{LOGO_URL}" x="{PAD}" y="34" width="150" height="44" preserveAspectRatio="xMinYMid meet"/>
  <text class="src" x="{CARD_W - PAD}" y="62" text-anchor="end">{SOURCE}</text>
  <rect class="chip" x="{PAD}" y="124" width="{22 + 11 * len(CARD['category'])}" height="30" rx="15"/>
  <text class="chiptxt" x="{PAD + 12}" y="144">{escape(CARD['category'])}</text>
  {lines_svg(h_lines, PAD, y_head, 'head', h_lh)}
  <line class="rule" x1="{PAD}" y1="{y_meta - 22}" x2="{CARD_W - PAD}" y2="{y_meta - 22}"/>
  <text class="meta" x="{PAD}" y="{y_meta}">{escape(CARD['date'])}</text>
  <text class="meta" x="{CARD_W - PAD}" y="{y_meta}" text-anchor="end">{escape(CARD['byline'])}</text>
</g>"""


def back(x0):
    inner = CARD_W - 2 * PAD
    s_size, s_lh = 19, 19 * 1.85
    s_lines = wrap(CARD["summary"], s_size, inner)
    return f"""<g transform="translate({x0},{GAP})">
  <rect class="back" width="{CARD_W}" height="{CARD_H}" rx="22" filter="url(#shadow)"/>
  <rect class="bar2" x="{PAD}" y="34" width="34" height="5" rx="2.5"/>
  <text class="label" x="{PAD}" y="66">အကျဉ်းချုပ်</text>
  {lines_svg(s_lines, PAD, 130, 'body', s_lh)}
  <rect class="cta" x="{PAD}" y="{CARD_H - 96}" width="{inner}" height="48" rx="24"/>
  <text class="ctatxt" x="{CARD_W / 2}" y="{CARD_H - 66}" text-anchor="middle">{CARD['url']}</text>
</g>"""


def build():
    w = CARD_W * 2 + GAP * 3
    h = CARD_H + GAP * 2
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>MPA News card</title>
<defs>
  <style>
    /* ---- brand settings: edit colors and font here ---- */
    /* font: Noto Sans Myanmar | ink/dark: #14213D | accent: #C8102E | muted: #6B7280 | canvas: #EEF1F5 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Myanmar:wght@400;700');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800');
    text {{ font-family: 'Noto Sans Myanmar','Pyidaungsu','Myanmar Text','Padauk','Inter',Arial,sans-serif; }}
    .canvas {{ fill: #EEF1F5; }}
    .front {{ fill: #FFFFFF; }}
    .back {{ fill: #14213D; }}
    .bar, .bar2, .cta {{ fill: #C8102E; }}
    .chip {{ fill: #C8102E; }}
    .chiptxt {{ fill: #fff; font-size: 15px; font-weight: 700; }}
    .src {{ fill: #6B7280; font-size: 13px; }}
    .head {{ fill: #14213D; font-size: 26px; font-weight: 700; }}
    .meta {{ fill: #6B7280; font-size: 14px; }}
    .rule {{ stroke: #E5E7EB; stroke-width: 1; }}
    .label {{ fill: #AEB8CC; font-size: 14px; font-weight: 700; letter-spacing: 1.5px; }}
    .body {{ fill: #F4F6FA; font-size: 19px; }}
    .ctatxt {{ fill: #fff; font-size: 16px; font-weight: 700; font-family: 'Inter',Arial,sans-serif; }}
  </style>
  <filter id="shadow" x="-10%" y="-10%" width="120%" height="125%">
    <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0F172A" flood-opacity="0.18"/>
  </filter>
  <clipPath id="top"><rect width="{CARD_W}" height="{CARD_H}" rx="22"/></clipPath>
</defs>
<rect class="canvas" width="{w}" height="{h}"/>
{front(GAP)}
{back(GAP * 2 + CARD_W)}
</svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.write_text(build(), encoding="utf-8")
    print("wrote", out)
