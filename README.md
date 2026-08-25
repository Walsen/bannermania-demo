# BannerMania 🎪

A tiny retro banner generator, inspired by the classic 1989 **BannerMania**.
Type some text, pick a font, colors, a background pattern, a text effect, and a
decorative border — then download a **PNG**, or flip on marquee mode for a
scrolling **animated GIF**.

Built with **Flask** (backend) + **Pillow** (image rendering) and a small
vanilla-JS front end with a live preview.

## Features

- **16 fonts**: Impact, Arial Black, Arial Rounded, Comic Sans, Chalkduster,
  Chalkboard, Noteworthy, Papyrus, Courier, Menlo, Monaco, Georgia, Futura,
  Avenir, Helvetica Neue, Geneva
- **10 text effects**: `plain`, `outline`, `shadow`, `3d`, `gradient`,
  `rainbow`, `neon`, `glow`, `glitch`, `emboss`
- **5 background patterns**: `solid`, `stripes`, `checker`, `dots`, `diagonal`
- **8 decorative borders ("marks")**: `none`, `single`, `double`, `dashed`,
  `dotted`, `stars`, `zigzag`, `corners`
- **🎞️ Animated scrolling marquee** — a looping right-to-left GIF, with an
  adjustable scroll speed (fast / medium / slow) and three **motion modes**:
  - `scroll` — the classic flat marquee (all letters level)
  - `wave` — each letter bobs on a sine curve, and the wave travels along the
    text as it scrolls
  - `bounce` — each letter hops upward in sequence
  Per-letter modes work with every text effect (neon glow, 3D, glitch, …) and
  loop seamlessly.
- **🌈 Color cycle** — an optional marquee toggle that rotates the text hue a
  full turn over the loop. Composes with any effect and any motion mode; loops
  seamlessly. (Grays have no hue to rotate — use a saturated color.)
- 4 fully customizable colors (two text colors + background + accent)
- 4 banner sizes (web, social, wide header, square)
- 🎲 "Surprise me" randomizer (font, effect, pattern, border, colors)
- One-click download (PNG for static, GIF for marquee)
- Auto font-sizing so text always fits — static banners fit to width, the
  marquee fits to height so long text stays large and scrolls

## Setup

```bash
cd "AWS Community Builder/demo"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5001

### Options

```bash
python app.py --host 127.0.0.1 --port 5001 --debug
```

## How it works

- `GET /` serves the UI (`templates/index.html`).
- `GET /generate?...` renders a **static banner PNG** on the fly with Pillow and
  streams it back.
- `GET /generate.gif?...` renders an **animated scrolling GIF**. In `scroll`
  mode the text is drawn once on a wide transparent layer, then a banner-sized
  window slides across it frame by frame over a static background. In `wave` /
  `bounce` mode each glyph is instead rendered onto its own tile and composited
  per frame at its scrolled x plus a vertical offset, so any effect still works
  per letter. Frames share one palette to avoid color flicker, the vertical
  phase completes whole cycles per loop (so it loops seamlessly), and the GIF
  loops forever. With **color cycle** on, the text is re-rendered each frame with
  a rotated hue, and the shared palette is built from a montage of sampled frames
  so the full hue range survives GIF quantization.
- `GET /health` returns JSON listing the available fonts, effects, patterns, and
  borders.

All banner parameters are query-string args, so the live preview `<img>` and the
download link are just two URLs.

### Query parameters

Shared by both `/generate` and `/generate.gif`:

| Param | Meaning | Example |
|---|---|---|
| `text` | Banner text | `HELLO` |
| `font` | Font name | `Impact` |
| `effect` | Text effect | `neon` |
| `pattern` | Background pattern | `stripes` |
| `border` | Decorative border | `stars` |
| `fg` / `fg2` | Text color / second color (gradient) | `#ffd60a` |
| `bg` / `accent` | Background / pattern accent color | `#111122` |
| `width` / `height` | Banner size in px | `1000` / `300` |
| `download` | `1` to force a file download | `1` |

Extra parameters for `/generate.gif` only:

| Param | Meaning | Default |
|---|---|---|
| `motion` | Marquee motion: `scroll`, `wave`, or `bounce` | `scroll` |
| `cycle` | `1` to rotate the text hue over the loop | off |
| `cycle_turns` | Hue turns completed per loop | `1.0` |
| `speed` | Milliseconds per frame (lower = faster) | `60` |
| `frames` | Number of frames in the loop (12–120) | `48` |

**Examples**

```bash
# Static neon banner with a double border
curl "http://127.0.0.1:5001/generate?text=NEON+NIGHTS&effect=neon&border=double&fg=%2300eaff&bg=%230a0018" -o banner.png

# Scrolling rainbow marquee with a star border
curl "http://127.0.0.1:5001/generate.gif?text=AWS+Community+Builder&effect=rainbow&pattern=stripes&border=stars&speed=55" -o banner.gif

# Per-letter wave marquee (each letter bobs as it scrolls)
curl "http://127.0.0.1:5001/generate.gif?text=WAVE+RIDER&effect=rainbow&motion=wave&border=dotted&speed=55" -o wave.gif

# Color-cycling 3D marquee (text hue rotates over the loop)
curl "http://127.0.0.1:5001/generate.gif?text=COLOR+CYCLE&effect=3d&cycle=1&border=double&fg=%23ff3ca0&speed=55" -o cycle.gif
```

## Project layout

```
demo/
├── app.py               # Flask backend + Pillow renderer (/, /generate, /generate.gif, /health)
├── templates/index.html # retro web UI
├── static/style.css     # 80s CRT styling
├── static/app.js        # live preview, animate toggle, speed slider, randomizer, download
├── requirements.txt     # Flask + Pillow
└── README.md
```

## Notes

- Fonts are resolved from macOS system paths, with Linux `msttcorefonts`
  fallbacks. Only the fonts actually present on the host are offered in the UI.
  If none are found, Pillow's built-in bitmap font is used (fixed size), so the
  app still works everywhere — it just won't scale the text.
- GIF rendering is more work than a PNG (dozens of frames), so the front end
  debounces edits a little longer in marquee mode. Sizes and frame counts are
  clamped server-side.
- The server binds to `127.0.0.1` by default (local only). `/generate*` render
  on the fly from unauthenticated query params — fine for local/demo use; if you
  ever expose it publicly, add input caps + rate limiting.
