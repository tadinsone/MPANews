#!/usr/bin/env python3
"""Render finished cards (cards.jsonl) as end-user SVG images: front and back side by side."""
import json
import sys
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "'Noto Sans Myanmar','Myanmar Text','Padauk','Inter','Segoe UI',Helvetica,Arial,sans-serif"
CARD_W, CARD_H, GAP, PAD = 340, 460, 36, 28


def char_w(ch: str, size: float) -> float:
    cat = unicodedata.category(ch)
    if cat in ("Mn", "Me"):
        return 0.0                      # non-spacing marks add no width
    if cat == "Mc":
        return size * 0.42              # spacing marks (Burmese ေ ာ ျ ြ း) do take width
    if "က" <= ch <= "႟":
        return size * 0.72              # Burmese base letters (conservative)
    return size * 0.54


def wrap(text: str, size: float, max_w: float) -> list[str]:
    """Greedy wrap; breaks at spaces, or mid-run for Burmese (few spaces)."""
    lines, cur, cur_w = [], "", 0.0
    for word in text.split(" "):
        ww = sum(char_w(c, size) for c in word)
        space = char_w(" ", size) if cur else 0
        if cur and cur_w + space + ww <= max_w:
            cur += " " + word
            cur_w += space + ww
            continue
        if cur:
            lines.append(cur)
            cur, cur_w = "", 0.0
        if ww <= max_w:
            cur, cur_w = word, ww
            continue
        for c in word:                  # long unbroken run: split at cluster boundary
            w = char_w(c, size)
            if cur and cur_w + w > max_w and w > 0:
                lines.append(cur)
                cur, cur_w = "", 0.0
            cur += c
            cur_w += w
    if cur:
        lines.append(cur)
    return lines


def text_block(lines, x, y, size, weight, fill, lh, anchor="start"):
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * lh:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{escape(ln)}</text>'
        )
    return "\n    ".join(out)


def side(x0, label, title, body, theme, card_no, side_no):
    bg, fg, muted, accent = theme
    inner_w = CARD_W - 2 * PAD
    t_size, b_size = 25, 17
    t_lines = wrap(title, t_size, inner_w) if title else []
    b_lines = wrap(body, b_size, inner_w) if body else []
    t_lh, b_lh = t_size * 1.5, b_size * 1.7
    block_h = len(t_lines) * t_lh + (18 if t_lines and b_lines else 0) + len(b_lines) * b_lh
    top = 70
    avail = CARD_H - top - 56
    y = top + max((avail - block_h) / 2, 0) + t_size
    parts = [
        f'<g transform="translate({x0},{GAP})">',
        f'  <rect width="{CARD_W}" height="{CARD_H}" rx="22" fill="{bg}" filter="url(#shadow)"/>',
        f'  <rect x="{PAD}" y="30" width="34" height="5" rx="2.5" fill="{accent}"/>',
        f'  <text x="{PAD}" y="58" font-size="12" font-weight="700" letter-spacing="2.4" fill="{muted}">{label}</text>',
    ]
    if t_lines:
        parts.append("  " + text_block(t_lines, PAD, round(y, 1), t_size, 700, fg, t_lh))
        y += (len(t_lines) - 1) * t_lh + 18 + b_size
    else:
        y += b_size
    if b_lines:
        parts.append("  " + text_block(b_lines, PAD, round(y, 1), b_size, 400, fg, b_lh))
    parts.append(
        f'  <text x="{CARD_W - PAD}" y="{CARD_H - 24}" font-size="12" fill="{muted}" text-anchor="end">'
        f'{card_no} · {side_no}/2</text>'
    )
    parts.append("</g>")
    return "\n".join(parts)


def render_card(card: dict) -> str:
    front, back = card["front"], card.get("back")
    n = 2 if back else 1
    width = CARD_W * n + GAP * (n + 1)
    height = CARD_H + 2 * GAP
    light = ("#FFFFFF", "#1B2430", "#7B8794", "#E8590C")
    dark = ("#1B2430", "#F4F6F8", "#9AA5B1", "#FFA94D")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}">',
        f'<title>Card {card["id"]}: {escape(front["title"])}</title>',
        "<defs>",
        '<filter id="shadow" x="-10%" y="-10%" width="120%" height="125%">'
        '<feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0F172A" flood-opacity="0.18"/></filter>',
        "</defs>",
        f'<rect width="{width}" height="{height}" fill="#EEF1F5"/>',
        side(GAP, "FRONT", front["title"], front["body"], light, card["id"], 1),
    ]
    if back:
        svg.append(side(GAP * 2 + CARD_W, "BACK", back["title"], back["body"], dark, card["id"], 2))
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for line in src.read_text(encoding="utf-8").splitlines():
        card = json.loads(line)
        p = out_dir / f"card_{card['id']}.svg"
        p.write_text(render_card(card), encoding="utf-8")
        print("wrote", p)


if __name__ == "__main__":
    main()
