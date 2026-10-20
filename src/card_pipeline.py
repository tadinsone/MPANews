#!/usr/bin/env python3
"""
Card pipeline: two threads, one shared queue.

  Spec thread (producer): defines CardSpecs and puts them on spec_queue.
  Text thread (consumer): takes raw text, applies the latest spec it has
                          received, and emits finished cards.

Usage:
  python card_pipeline.py                 # runs the built-in demo texts
  python card_pipeline.py texts.txt       # one raw text per paragraph (blank-line separated)
  python card_pipeline.py texts.txt -o cards.jsonl
"""
from __future__ import annotations

import argparse
import json
import queue
import re
import sys
import threading
import time
import unicodedata
from dataclasses import dataclass, asdict, field

SENTINEL = None  # tells the consumer the producer is finished


# --------------------------------------------------------------------------
# Card spec
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class CardSpec:
    name: str
    version: int
    layout: str                    # "two-sided" or "single"
    front_title_max: int
    front_body_max: int            # 0 = no front body
    back_title_max: int            # 0 = no back title
    back_body_max: int             # 0 = no back
    ellipsis: str = "…"
    split_markers: tuple = ("::", "Q:/A:")  # how the text may carry its own front/back
    notes: str = ""


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------
SENTENCE_END = re.compile(r"(?<=[.!?။])\s+|(?<=။)")


def truncate(text: str, limit: int, ellipsis: str = "…") -> str:
    """Trim to `limit` characters (ellipsis included).

    Prefers a whitespace boundary. For scripts without spaces (e.g. Burmese)
    it cuts by code point but never leaves a dangling combining mark
    (vowel signs, medials, asat) at the cut, which would break the glyph.
    """
    text = text.strip()
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    budget = max(limit - len(ellipsis), 0)
    cut = text[:budget]
    # prefer last whitespace if it is not too far back
    ws = cut.rfind(" ")
    if ws >= budget * 0.6:
        cut = cut[:ws]
    else:
        # don't strand a combining mark: if the next char continues the
        # cluster, back off until we're on a cluster boundary
        i = len(cut)
        while i > 0 and i < len(text) and unicodedata.category(text[i]).startswith("M"):
            i -= 1
        cut = text[:i]
    return cut.rstrip(" ,;:-") + ellipsis


def split_front_back(raw: str, spec: CardSpec) -> tuple[str, str, str, str]:
    """Return (front_title, front_body, back_title, back_body) before trimming."""
    raw = raw.strip()

    # Explicit Q:/A:
    m = re.search(r"^\s*Q:\s*(.+?)\s*^\s*A:\s*(.+)\Z", raw, re.S | re.M)
    if m:
        return m.group(1).strip(), "", "Answer", m.group(2).strip()

    # Explicit "front :: back"
    if "::" in raw:
        front, back = raw.split("::", 1)
        return front.strip(), "", "", back.strip()

    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if len(lines) > 1:
        title, rest = lines[0], " ".join(lines[1:])
    else:
        sentences = [s for s in SENTENCE_END.split(raw) if s.strip()]
        title = sentences[0]
        rest = " ".join(sentences[1:]) if len(sentences) > 1 else ""

    if spec.layout == "single":
        return title, rest, "", ""
    # two-sided: hook (first sentence of rest) on front, full detail on back
    rest_sentences = [s for s in SENTENCE_END.split(rest) if s.strip()] if rest else []
    hook = rest_sentences[0] if rest_sentences else ""
    return title, hook, "Details", rest or title


# --------------------------------------------------------------------------
# Producer: defines specs and puts them on the queue
# --------------------------------------------------------------------------
def spec_producer(spec_queue: queue.Queue, specs: list[CardSpec], delay: float = 0.2) -> None:
    for spec in specs:
        print(f"[spec-thread]  publish  {spec.name} v{spec.version}  layout={spec.layout}")
        spec_queue.put(spec)
        time.sleep(delay)  # simulates specs evolving over time
    spec_queue.put(SENTINEL)
    print("[spec-thread]  done")


# --------------------------------------------------------------------------
# Consumer: raw text in, finished cards out
# --------------------------------------------------------------------------
def build_card(raw: str, spec: CardSpec, idx: int) -> dict:
    ft, fb, bt, bb = split_front_back(raw, spec)
    card = {
        "id": idx,
        "spec": f"{spec.name}@v{spec.version}",
        "layout": spec.layout,
        "front": {
            "title": truncate(ft, spec.front_title_max, spec.ellipsis),
            "body": truncate(fb, spec.front_body_max, spec.ellipsis),
        },
    }
    if spec.layout == "two-sided" and spec.back_body_max:
        card["back"] = {
            "title": truncate(bt, spec.back_title_max, spec.ellipsis),
            "body": truncate(bb, spec.back_body_max, spec.ellipsis),
        }
    return card


def text_consumer(
    spec_queue: queue.Queue,
    texts: list[str],
    cards_out: list[dict],
    ready: threading.Event,
) -> None:
    # Block until the first spec arrives; nothing can be rendered without one.
    spec = spec_queue.get()
    if spec is SENTINEL:
        print("[text-thread]  no spec received, nothing to do")
        return
    print(f"[text-thread]  using    {spec.name} v{spec.version}")
    ready.set()
    producer_done = False

    for i, raw in enumerate(texts, 1):
        # Pick up newer specs without blocking
        while not producer_done:
            try:
                nxt = spec_queue.get_nowait()
            except queue.Empty:
                break
            if nxt is SENTINEL:
                producer_done = True
            else:
                spec = nxt
                print(f"[text-thread]  switched to {spec.name} v{spec.version}")
        card = build_card(raw, spec, i)
        cards_out.append(card)
        print(f"[text-thread]  card #{i}  ({card['spec']})")
        time.sleep(0.15)  # simulates texts trickling in


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render(card: dict, width: int = 46) -> str:
    def box(label: str, title: str, body: str) -> list[str]:
        out = ["┌" + "─" * (width - 2) + "┐", f"│ {label:<{width-4}} │"]
        for chunk in (title, body):
            for line in _wrap(chunk, width - 4):
                out.append(f"│ {line:<{width-4}} │")
        out.append("└" + "─" * (width - 2) + "┘")
        return out

    lines = [f"Card #{card['id']}  [{card['spec']}]"]
    lines += box("FRONT", card["front"]["title"], card["front"]["body"])
    if "back" in card:
        lines += box("BACK", card["back"]["title"], card["back"]["body"])
    return "\n".join(lines)


def _wrap(text: str, w: int) -> list[str]:
    if not text:
        return []
    out, cur = [], ""
    for word in text.split(" "):
        if len(cur) + len(word) + (1 if cur else 0) <= w:
            cur = f"{cur} {word}".strip()
        else:
            if cur:
                out.append(cur)
            while len(word) > w:  # long unbroken runs (e.g. Burmese)
                out.append(word[:w])
                word = word[w:]
            cur = word
    if cur:
        out.append(cur)
    return out


# --------------------------------------------------------------------------
# Demo data
# --------------------------------------------------------------------------
DEMO_SPECS = [
    CardSpec("flashcard", 1, "two-sided", front_title_max=60, front_body_max=80,
             back_title_max=30, back_body_max=220,
             notes="Study card: short front, fuller back"),
    CardSpec("flashcard", 2, "two-sided", front_title_max=48, front_body_max=60,
             back_title_max=24, back_body_max=160,
             notes="Tightened limits"),
]

DEMO_TEXTS = [
    "Q: What is the Myanmar Fact-Check Network?\nA: A network of 10 media organizations founded in 2025 to verify claims and counter misinformation across Myanmar.",
    "Press freedom index :: A yearly ranking of countries by how freely journalists can work, compiled from surveys and incident data.",
    "Satellite imagery verification\nGeolocating a photo means matching landmarks to map data. Cross-check shadows, terrain and signage. Always record the source and timestamp.",
    "သတင်းအချက်အလက် စစ်ဆေးခြင်း\nသတင်းတစ်ပုဒ်ကို မထုတ်ပြန်မီ အရင်းအမြစ်နှစ်ခုအနည်းဆုံးဖြင့် ကိုက်ညီမှု ရှိမရှိ စစ်ဆေးရမည်။ ဓာတ်ပုံနှင့် ဗီဒီယိုများ၏ မူလရက်စွဲကိုလည်း ဆန်းစစ်ပါ။",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("texts", nargs="?", help="text file; paragraphs separated by blank lines")
    ap.add_argument("-o", "--out", default="cards.jsonl")
    args = ap.parse_args()

    if args.texts:
        with open(args.texts, encoding="utf-8") as f:
            texts = [p.strip() for p in re.split(r"\n\s*\n", f.read()) if p.strip()]
    else:
        texts = DEMO_TEXTS

    spec_queue: queue.Queue = queue.Queue()
    cards: list[dict] = []
    ready = threading.Event()

    t_spec = threading.Thread(target=spec_producer, args=(spec_queue, DEMO_SPECS), name="spec-thread")
    t_text = threading.Thread(target=text_consumer, args=(spec_queue, texts, cards, ready), name="text-thread")

    t_text.start()   # consumer waits on the queue first, to show the hand-off
    t_spec.start()
    t_spec.join()
    t_text.join()

    with open(args.out, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print("\n" + "=" * 50)
    for c in cards:
        print(render(c))
        print()
    print(f"{len(cards)} cards written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
