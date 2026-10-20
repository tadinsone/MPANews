#!/usr/bin/env python3
"""Three Facebook cards (1080x1350, 4:5) for the FREE HER story on mpanews.info.
Cards 1 and 3 carry a crop of the campaign poster; card 2 is text only.
Colors and font are in STYLE below."""
import base64
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
from render_svg import wrap  # noqa: E402

W, H, PAD = 1080, 1350, 72
INNER = W - 2 * PAD
LOGO_URL = "https://mpanews.info/wp-content/uploads/2025/07/cropped-logo.png"
ARTICLE_URL = "mpanews.info/headline/13798"
DATE_LINE = "20 Oct 2026 · By MPA"

STYLE = """
    /* brand settings: edit colors and font here */
    /* font: Noto Sans Myanmar | ink/dark: #14213D | accent: #C8102E | muted: #6B7280 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Myanmar:wght@400;700');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800');
    text { font-family: 'Noto Sans Myanmar','Pyidaungsu','Myanmar Text','Padauk','Inter',Arial,sans-serif; }
    .paper { fill: #FFFFFF; }
    .dark { fill: #14213D; }
    .accent { fill: #C8102E; }
    .chiptxt { fill: #fff; font-size: 34px; font-weight: 700; }
    .head { fill: #14213D; font-size: 58px; font-weight: 700; }
    .headw { fill: #FFFFFF; font-size: 56px; font-weight: 700; }
    .kicker { fill: #C8102E; font-size: 30px; font-weight: 700; letter-spacing: 2px; font-family: 'Inter',Arial,sans-serif; }
    .kickerw { fill: #FF8A9B; font-size: 30px; font-weight: 700; letter-spacing: 2px; font-family: 'Inter',Arial,sans-serif; }
    .head1 { fill: #14213D; font-size: 52px; font-weight: 700; }
    .head3 { fill: #14213D; font-size: 50px; font-weight: 700; }
    .big { fill: #C8102E; font-size: 140px; font-weight: 800; font-family: 'Inter',Arial,sans-serif; }
    .bigsub { fill: #FFFFFF; font-size: 28px; font-weight: 700; letter-spacing: 4px; font-family: 'Inter',Arial,sans-serif; }
    .item { fill: #14213D; font-size: 36px; }
    .itemw { fill: #F4F6FA; font-size: 46px; }
    .num { fill: #C8102E; }
    .numtxt { fill: #fff; font-size: 34px; font-weight: 700; font-family: 'Inter',Arial,sans-serif; }
    .meta { fill: #6B7280; font-size: 30px; }
    .metaw { fill: #AEB8CC; font-size: 30px; }
    .rule { stroke: #E5E7EB; stroke-width: 2; }
    .rulew { stroke: #34436A; stroke-width: 2; }
    .page { fill: #6B7280; font-size: 28px; font-family: 'Inter',Arial,sans-serif; }
    .pagew { fill: #AEB8CC; font-size: 28px; font-family: 'Inter',Arial,sans-serif; }
"""


def lines(ls, x, y, cls, lh):
    return "\n".join(f'<text class="{cls}" x="{x}" y="{y + i * lh:.1f}">{escape(l)}</text>' for i, l in enumerate(ls))


def footer(n, dark=False):
    rule, meta, page = ("rulew", "metaw", "pagew") if dark else ("rule", "meta", "page")
    y = H - 118
    return f"""<line class="{rule}" x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}"/>
<image href="{LOGO_URL}" x="{PAD}" y="{y + 22}" width="230" height="64" preserveAspectRatio="xMinYMid meet"/>
<text class="{meta}" x="{W - PAD}" y="{y + 64}" text-anchor="end">mpanews.info</text>
<text class="{page}" x="{W - PAD}" y="{y + 100}" text-anchor="end">{n}/3</text>"""


def svg(body, img_b64=None, title=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>{escape(title)}</title>
<defs><style>{STYLE}</style></defs>
{body}
</svg>
"""


def photo(img_b64, h, align):
    # align: xMidYMin (top of poster) or xMidYMax (bottom of poster)
    return (f'<image href="data:image/jpeg;base64,{img_b64}" x="0" y="0" width="{W}" height="{h}" '
            f'preserveAspectRatio="{align} slice"/>')


def card1(img):
    photo_h = 740
    hl = wrap("ဒေါ်အောင်ဆန်းစုကြည်နှင့် နိုင်ကျဉ်းအားလုံး လွတ်မြောက်ရေး ကမ္ဘာလုံးဆိုင်ရာလှုပ်ရှားမှုတွင် ပါဝင်ရန် ဖိတ်ခေါ်", 52, INNER)
    lh = 82
    chip_y = photo_h + 38
    head_y0 = chip_y + 58 + 66
    last = head_y0 + (len(hl) - 1) * lh
    date_y = last + 80
    assert date_y < H - 130, f"card1 text overflows ({date_y})"
    body = f"""<rect class="paper" width="{W}" height="{H}"/>
{photo(img, photo_h, 'xMidYMin')}
<rect class="accent" x="0" y="{photo_h}" width="{W}" height="12"/>
<rect class="accent" x="{PAD}" y="{chip_y}" width="{44 + 34 * 7.2:.0f}" height="58" rx="29"/>
<text class="chiptxt" x="{PAD + 24}" y="{chip_y + 42}">ခေါင်းကြီးသတင်း</text>
{lines(hl, PAD, head_y0, 'head1', lh)}
<text class="meta" x="{PAD}" y="{date_y}">{DATE_LINE}</text>
{footer(1)}"""
    return svg(body, title="MPA News 1/3")


def card2():
    items = [
        "ဒေါ်အောင်ဆန်းစုကြည်အား မိသားစုနှင့် ချက်ချင်းနှင့် ပုံမှန် တွေ့ဆုံ ဆက်သွယ်ခွင့်ပေးရန်",
        "ဒေါ်အောင်ဆန်းစုကြည်အား ခြွင်းချက်မရှိ ချက်ချင်း လွှတ်ပေးရန်",
        "နိုင်ငံရေးအကျဉ်းသားအားလုံး လွှတ်ပေးရန်",
    ]
    title = wrap("FREE HER လှုပ်ရှားမှု၏ အဓိက တောင်းဆိုချက် ၃ ရပ်", 56, INNER)
    y = 170
    parts = [f'<rect class="dark" width="{W}" height="{H}"/>',
             f'<rect class="accent" x="{PAD}" y="96" width="90" height="10" rx="5"/>',
             f'<text class="kickerw" x="{PAD}" y="{y}">FREE HER CAMPAIGN</text>']
    y += 100
    parts.append(lines(title, PAD, y, "headw", 88))
    y += (len(title) - 1) * 88 + 120
    for i, it in enumerate(items, 1):
        ls = wrap(it, 46, INNER - 110)
        parts.append(f'<circle class="num" cx="{PAD + 36}" cy="{y - 14}" r="36"/>')
        parts.append(f'<text class="numtxt" x="{PAD + 36}" y="{y - 2}" text-anchor="middle">{i}</text>')
        parts.append(lines(ls, PAD + 110, y, "itemw", 76))
        y += (len(ls) - 1) * 76 + 130
    assert y < H - 150, f"card2 text overflows ({y})"
    parts.append(f'<text class="metaw" x="{PAD}" y="{H - 150}">FREE HER Campaign Team ထုတ်ပြန်ချက်</text>')
    parts.append(footer(2, dark=True))
    return svg("\n".join(parts), title="MPA News 2/3")


def card3(img):
    items = [
        "လူမှုကွန်ရက်များနှင့် မိတ်ဆွေအသိုင်းအဝိုင်းထံ မျှဝေပေးပါ",
        "FREE HER ဝဘ်ဆိုက်မှ ပို့စကတ်များကို ဒေါင်းလုဒ်ရယူပြီး သက်ဆိုင်ရာနိုင်ငံရှိ မြန်မာသံရုံးသို့ ပေးပို့ပါ",
        "ဝဘ်ဆိုက်မှ နမူနာစာကို ဒေါင်းလုဒ်ရယူ၍ မိမိတို့၏ သဘောထားများ ဖြည့်စွက်ကာ နေထိုင်ရာနိုင်ငံရှိ လွှတ်တော်ကိုယ်စားလှယ်များထံ ပေးပို့ပါ",
        "မြန်မာသံရုံးများရှေ့တွင် ငြိမ်းချမ်းစွာ စုဝေးပါ",
    ]
    band = 420
    poster_w = round(band * 905 / 1280)
    y = band + 12 + 96
    parts = [f'<rect class="paper" width="{W}" height="{H}"/>',
             f'<rect width="{W}" height="{band}" fill="#0B0B0B"/>',
             # whole poster, uncropped, flush right
             f'<image href="data:image/jpeg;base64,{img}" x="{W - PAD - poster_w}" y="0" width="{poster_w}" height="{band}" preserveAspectRatio="xMidYMid meet"/>',
             f'<text class="big" x="{PAD}" y="190">FREE</text>',
             f'<text class="big" x="{PAD}" y="320">HER</text>',
             f'<text class="bigsub" x="{PAD + 4}" y="378">GLOBAL CAMPAIGN</text>',
             f'<rect class="accent" x="0" y="{band}" width="{W}" height="12"/>',
             f'<text class="kicker" x="{PAD}" y="{y}">HOW TO JOIN</text>']
    y += 76
    parts.append(f'<text class="head3" x="{PAD}" y="{y}">ပါဝင်ဆောင်ရွက်ရန် တိုက်တွန်းချက်</text>')
    y += 92
    for i, it in enumerate(items, 1):
        ls = wrap(it, 36, INNER - 100)
        parts.append(f'<circle class="num" cx="{PAD + 30}" cy="{y - 12}" r="30"/>')
        parts.append(f'<text class="numtxt" x="{PAD + 30}" y="{y}" text-anchor="middle" style="font-size:30px">{i}</text>')
        parts.append(lines(ls, PAD + 100, y, "item", 56))
        y += (len(ls) - 1) * 56 + 70
    assert y < H - 130, f"card3 text overflows ({y})"
    parts.append(footer(3))
    return svg("\n".join(parts), title="MPA News 3/3")


if __name__ == "__main__":
    img = base64.b64encode(Path(sys.argv[1]).read_bytes()).decode()
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for name, s in (("fb_card_1.svg", card1(img)), ("fb_card_2.svg", card2()), ("fb_card_3.svg", card3(img))):
        (out / name).write_text(s, encoding="utf-8")
        print("wrote", out / name)
