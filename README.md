# MPA News cards

Tools for turning news text into social-media cards for [mpanews.info](https://mpanews.info) (Myanmar Pressphoto Agency).

## What's inside

| Path | What it is |
| --- | --- |
| `src/card_pipeline.py` | Two threads sharing a queue. The **spec thread** (producer) publishes card specs (layout, field limits). The **text thread** (consumer) takes raw text, applies the latest spec and builds finished cards. |
| `src/render_svg.py` | Renders pipeline cards (`cards.jsonl`) as front/back SVG images. |
| `src/mpa_fb_cards.py` | Builds the three 1080×1350 Facebook cards for the FREE HER story. |
| `src/mpa_card.py`, `src/mpa_card_photo.py` | Front/back sample cards (text only, and with a photo). |
| `assets/free-her-poster.jpg` | The campaign poster used on the photo cards. |
| `output/` | Generated SVG cards. |
| `index.html` | Preview page that shows the cards in a browser. |

## Run it

Python 3.9+ and the standard library only.

```bash
# spec thread + text thread demo, writes cards.jsonl
python3 src/card_pipeline.py -o output/cards.jsonl

# your own texts: one text per paragraph, blank line between
python3 src/card_pipeline.py my_texts.txt -o cards.jsonl

# render pipeline cards to SVG
python3 src/render_svg.py output/cards.jsonl output/svg

# Facebook cards (needs the poster image)
python3 src/mpa_fb_cards.py assets/free-her-poster.jpg output/facebook
```

## Branding

Fonts and colors are in the `<style>` block of each script (`STYLE` in `mpa_fb_cards.py`).
Current values are placeholders: Noto Sans Myanmar, red `#C8102E`, navy `#14213D`. Replace them with the MPA News brand values.
The logo is loaded from `https://mpanews.info/wp-content/uploads/2025/07/cropped-logo.png`.

## Preview page (GitHub Pages)

In the repository go to **Settings → Pages**, choose **Deploy from a branch**, pick `main` and `/ (root)`, and save.
GitHub then shows the page address on that screen.
