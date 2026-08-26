"""
BannerMania — a tiny retro banner generator.

A single-file Flask app that renders text banners as PNG images (and animated
scrolling GIFs), in the spirit of the classic 1989 BannerMania: pick a font,
colors, a background pattern, a text effect, and a decorative border, then
download the result — or turn on marquee mode for a scrolling animation.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5001
"""

from __future__ import annotations

import argparse
import colorsys
import io
import math
import os

from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFilter, ImageFont

app = Flask(__name__)

# --- Font catalog -----------------------------------------------------------
# Maps a friendly name to candidate file paths. The first one that exists on
# the host wins; if none do, Pillow's built-in bitmap font is used as a fallback.
FONT_CANDIDATES = {
    "Impact": [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    ],
    "Arial Black": [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Black.ttf",
    ],
    "Arial Rounded": [
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    ],
    "Comic Sans": [
        "/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf",
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
    ],
    "Chalkduster": [
        "/System/Library/Fonts/Supplemental/Chalkduster.ttf",
    ],
    "Chalkboard": [
        "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc",
        "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
    ],
    "Marker Felt": [
        "/System/Library/Fonts/Supplemental/MarkerFelt.ttc",
    ],
    "Noteworthy": [
        "/System/Library/Fonts/Noteworthy.ttc",
    ],
    "Papyrus": [
        "/System/Library/Fonts/Supplemental/Papyrus.ttc",
    ],
    "Courier": [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Courier.ttc",
    ],
    "Menlo": [
        "/System/Library/Fonts/Menlo.ttc",
    ],
    "Monaco": [
        "/System/Library/Fonts/Monaco.ttf",
    ],
    "Georgia": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    ],
    "Futura": [
        "/System/Library/Fonts/Supplemental/Futura.ttc",
    ],
    "Avenir": [
        "/System/Library/Fonts/Avenir.ttc",
    ],
    "Helvetica Neue": [
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ],
    "Geneva": [
        "/System/Library/Fonts/Geneva.ttf",
    ],
}

EFFECTS = [
    "plain", "outline", "shadow", "3d", "gradient", "rainbow",
    "neon", "glow", "glitch", "emboss",
]
PATTERNS = ["solid", "stripes", "checker", "dots", "diagonal"]
BORDERS = ["none", "single", "double", "dashed", "dotted", "stars", "zigzag", "corners"]
MOTIONS = ["scroll", "wave", "bounce"]

DEFAULT_FONT = next(
    (name for name, paths in FONT_CANDIDATES.items() if any(os.path.exists(p) for p in paths)),
    None,
)


def available_fonts():
    return [n for n, paths in FONT_CANDIDATES.items() if any(os.path.exists(p) for p in paths)]


def resolve_font_path(name: str) -> str | None:
    for p in FONT_CANDIDATES.get(name, []):
        if os.path.exists(p):
            return p
    return None


def load_font(name: str, size: int):
    path = resolve_font_path(name)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    # Fallback: bundled bitmap font (fixed size, but keeps the app working).
    return ImageFont.load_default()


def hex_to_rgb(value: str, fallback=(0, 0, 0)):
    value = (value or "").strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        return fallback
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


def rainbow_color(t: float):
    r, g, b = colorsys.hsv_to_rgb(t % 1.0, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def shift_hue(rgb, delta: float):
    """Rotate an RGB color's hue by `delta` (in turns, 0..1). Grays are
    unaffected (no hue to rotate) — pick a saturated color to see the cycle."""
    if not delta:
        return rgb
    r, g, b = (c / 255 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb((h + delta) % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def font_size_of(font, default=48):
    return getattr(font, "size", default)


def measure(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


# --- Background patterns ----------------------------------------------------
def paint_background(img: Image.Image, pattern: str, bg, accent) -> None:
    draw = ImageDraw.Draw(img)
    w, h = img.size
    if pattern == "solid":
        return
    if pattern == "stripes":
        step = max(20, h // 12)
        for y in range(0, h, step * 2):
            draw.rectangle([0, y, w, y + step], fill=accent)
    elif pattern == "diagonal":
        step = max(24, h // 10)
        for x in range(-h, w, step * 2):
            draw.polygon(
                [(x, 0), (x + step, 0), (x + step + h, h), (x + h, h)], fill=accent
            )
    elif pattern == "checker":
        step = max(24, h // 8)
        for gy, y in enumerate(range(0, h, step)):
            for gx, x in enumerate(range(0, w, step)):
                if (gx + gy) % 2 == 0:
                    draw.rectangle([x, y, x + step, y + step], fill=accent)
    elif pattern == "dots":
        step = max(28, h // 7)
        r = step // 4
        for y in range(step // 2, h, step):
            for x in range(step // 2, w, step):
                draw.ellipse([x - r, y - r, x + r, y + r], fill=accent)


# --- Decorative borders ("marks") -------------------------------------------
def _star(draw, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -3.14159 / 2 + i * 3.14159 / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * _cos(ang), cy + rr * _sin(ang)))
    draw.polygon(pts, fill=color)


def _cos(a):
    import math
    return math.cos(a)


def _sin(a):
    import math
    return math.sin(a)


def draw_border(img: Image.Image, style: str, color) -> None:
    draw = ImageDraw.Draw(img)
    w, h = img.size
    if style == "none":
        return

    if style == "single":
        draw.rectangle([3, 3, w - 4, h - 4], outline=color, width=4)

    elif style == "double":
        draw.rectangle([3, 3, w - 4, h - 4], outline=color, width=4)
        draw.rectangle([13, 13, w - 14, h - 14], outline=color, width=2)

    elif style == "dashed":
        dash, gap, m, t = 22, 14, 6, 5
        for x in range(m, w - m, dash + gap):
            draw.rectangle([x, m, min(x + dash, w - m), m + t], fill=color)
            draw.rectangle([x, h - m - t, min(x + dash, w - m), h - m], fill=color)
        for y in range(m, h - m, dash + gap):
            draw.rectangle([m, y, m + t, min(y + dash, h - m)], fill=color)
            draw.rectangle([w - m - t, y, w - m, min(y + dash, h - m)], fill=color)

    elif style == "dotted":
        r, step, m = 5, 26, 10
        for x in range(m, w - m + 1, step):
            draw.ellipse([x - r, m - r, x + r, m + r], fill=color)
            draw.ellipse([x - r, h - m - r, x + r, h - m + r], fill=color)
        for y in range(m, h - m + 1, step):
            draw.ellipse([m - r, y - r, m + r, y + r], fill=color)
            draw.ellipse([w - m - r, y - r, w - m + r, y + r], fill=color)

    elif style == "stars":
        step, m, r = 42, 22, 12
        for x in range(m, w - m + 1, step):
            _star(draw, x, m, r, color)
            _star(draw, x, h - m, r, color)
        for y in range(m + step, h - m, step):
            _star(draw, m, y, r, color)
            _star(draw, w - m, y, r, color)

    elif style == "zigzag":
        m, step, amp = 8, 24, 10
        top = [(x, m + (amp if (x // step) % 2 else 0)) for x in range(m, w - m + 1, step)]
        bot = [(x, h - m - (amp if (x // step) % 2 else 0)) for x in range(m, w - m + 1, step)]
        draw.line(top, fill=color, width=4, joint="curve")
        draw.line(bot, fill=color, width=4, joint="curve")

    elif style == "corners":
        m, ln, t = 10, 64, 5  # margin, arm length, thickness
        corners = [
            (m, m, 1, 1),            # top-left
            (w - m, m, -1, 1),       # top-right
            (m, h - m, 1, -1),       # bottom-left
            (w - m, h - m, -1, -1),  # bottom-right
        ]
        for cx, cy, dx, dy in corners:
            # horizontal arm
            hx0, hx1 = sorted((cx, cx + dx * ln))
            hy0, hy1 = sorted((cy, cy + dy * t))
            draw.rectangle([hx0, hy0, hx1, hy1], fill=color)
            # vertical arm
            vx0, vx1 = sorted((cx, cx + dx * t))
            vy0, vy1 = sorted((cy, cy + dy * ln))
            draw.rectangle([vx0, vy0, vx1, vy1], fill=color)


# --- Text effects -----------------------------------------------------------
def draw_text_effect(img, text, font, xy, effect, fill, fill2, outline, hue=0.0) -> None:
    """Draw `text` with `effect` onto `img` (RGB or RGBA) at top-left `xy`.
    `hue` (0..1 turns) rotates the color, used by the color-cycle animation."""
    draw = ImageDraw.Draw(img)
    x, y = xy
    fsize = font_size_of(font)
    if hue:
        fill = shift_hue(fill, hue)
        fill2 = shift_hue(fill2, hue)

    if effect == "shadow":
        off = max(3, fsize // 12)
        draw.text((x + off, y + off), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=fill)

    elif effect == "outline":
        w = max(2, fsize // 20)
        draw.text((x, y), text, font=font, fill=fill, stroke_width=w, stroke_fill=outline)

    elif effect == "3d":
        depth = max(4, fsize // 10)
        shade = (lerp(fill[0], 0, 0.6), lerp(fill[1], 0, 0.6), lerp(fill[2], 0, 0.6))
        for i in range(depth, 0, -1):
            draw.text((x + i, y + i), text, font=font, fill=shade)
        draw.text((x, y), text, font=font, fill=fill)

    elif effect == "emboss":
        draw.text((x - 2, y - 2), text, font=font, fill=(255, 255, 255))
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
        muted = (lerp(fill[0], 128, 0.4), lerp(fill[1], 128, 0.4), lerp(fill[2], 128, 0.4))
        draw.text((x, y), text, font=font, fill=muted)

    elif effect == "glitch":
        off = max(3, fsize // 14)
        draw.text((x - off, y), text, font=font, fill=(255, 0, 84))
        draw.text((x + off, y + off // 2), text, font=font, fill=(0, 240, 255))
        draw.text((x, y), text, font=font, fill=fill)

    elif effect in ("neon", "glow"):
        # Glow = a blurred copy of the text behind a crisp core.
        glow_color = fill
        core = (255, 255, 255) if effect == "neon" else fill
        base = img.convert("RGBA") if img.mode != "RGBA" else None
        canvas = base if base is not None else img
        tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((x, y), text, font=font, fill=glow_color)
        blurred = tmp.filter(ImageFilter.GaussianBlur(radius=max(4, fsize // 8)))
        canvas.alpha_composite(blurred)
        canvas.alpha_composite(blurred)
        ImageDraw.Draw(canvas).text((x, y), text, font=font, fill=core)
        if base is not None:
            img.paste(base.convert(img.mode), (0, 0))

    elif effect in ("gradient", "rainbow"):
        cx = x
        n = max(1, len(text))
        for i, ch in enumerate(text):
            t = i / n
            if effect == "gradient":
                color = (
                    lerp(fill[0], fill2[0], t),
                    lerp(fill[1], fill2[1], t),
                    lerp(fill[2], fill2[2], t),
                )
            else:
                color = rainbow_color(t + hue)
            draw.text((cx, y), ch, font=font, fill=color)
            cx += draw.textlength(ch, font=font)

    else:  # plain
        draw.text((x, y), text, font=font, fill=fill)


def _fit_font(draw, text, font_name, width, height, fit_width=True):
    """Pick the largest font size that fits the box. If fit_width is False the
    text may be wider than the box (used by the scrolling marquee)."""
    margin = int(width * 0.06)
    size = int(height * 0.7)
    font = load_font(font_name, size)
    scalable = resolve_font_path(font_name) is not None
    tw, th = measure(draw, text, font)
    if scalable:
        while ((fit_width and tw > width - margin * 2) or th > height * 0.8) and size > 12:
            size -= 4
            font = load_font(font_name, size)
            tw, th = measure(draw, text, font)
    return font


# --- Static PNG banner ------------------------------------------------------
def render_banner(text, font_name, effect, pattern, border, fg, fg2, bg, accent, width, height):
    text = (text or "BANNER").strip() or "BANNER"
    width = max(200, min(width, 3000))
    height = max(120, min(height, 1200))

    fill = hex_to_rgb(fg, (255, 214, 10))
    fill2 = hex_to_rgb(fg2, (255, 71, 71))
    bg_c = hex_to_rgb(bg, (17, 17, 34))
    accent_c = hex_to_rgb(accent, (40, 40, 70))

    img = Image.new("RGB", (width, height), bg_c)
    paint_background(img, pattern, bg_c, accent_c)

    draw = ImageDraw.Draw(img)
    font = _fit_font(draw, text, font_name, width, height, fit_width=True)

    box = draw.textbbox((0, 0), text, font=font)
    x = (width - (box[2] - box[0])) // 2 - box[0]
    y = (height - (box[3] - box[1])) // 2 - box[1]

    draw_text_effect(img, text, font, (x, y), effect, fill, fill2, (0, 0, 0))
    draw_border(img, border, fill)
    return img


# --- Animated scrolling GIF (marquee) ---------------------------------------
def char_color(effect, i, n, fill, fill2, hue=0.0):
    """Resolve the base color for glyph i, so gradient/rainbow vary across the
    word even when drawn one glyph at a time. `hue` rotates for color-cycle."""
    t = i / max(1, n)
    if effect == "gradient":
        c = (lerp(fill[0], fill2[0], t), lerp(fill[1], fill2[1], t), lerp(fill[2], fill2[2], t))
        return shift_hue(c, hue)
    if effect == "rainbow":
        return rainbow_color(t + hue)
    return shift_hue(fill, hue)


# Effects whose look is purely the glyph color (handled via char_color); the
# rest are "structural" and drawn with strokes/shadows/glow around that color.
_COLOR_ONLY = {"plain", "gradient", "rainbow"}


def draw_glyph_tile(ch, font, effect, color, outline):
    """Render ONE glyph with its structural effect onto a small RGBA tile.
    Returns (tile, pen_x, pen_y): paste the tile so the glyph's pen origin lands
    at (target_x - pen_x, target_y - pen_y)."""
    fsize = font_size_of(font)
    pad = max(6, fsize)  # generous — covers shadow/3d/glitch offset and glow blur
    left, t, r, b = font.getbbox(ch)
    tile = Image.new("RGBA", ((r - left) + 2 * pad, (b - t) + 2 * pad), (0, 0, 0, 0))
    # Draw so the glyph's pen origin sits at (pad, pad) inside the tile.
    ox, oy = pad - left, pad - t
    struct = "plain" if effect in _COLOR_ONLY else effect
    draw_text_effect(tile, ch, font, (ox, oy), struct, color, color, outline)
    return tile, pad, pad


def _y_offset(motion, i, frame, frames_n, amp, cycles=2.0):
    """Vertical offset for glyph i at a given frame. Loops seamlessly because
    the phase completes `cycles` whole turns over the frame count."""
    phase = 2 * math.pi * cycles * (frame / frames_n)
    angle = i * 0.6 - phase
    if motion == "bounce":
        return -amp * abs(math.sin(angle))  # hop upward
    return -amp * math.sin(angle)  # wave: bob up and down


def render_scroll_gif(text, font_name, effect, pattern, border, fg, fg2, bg, accent,
                      width, height, speed_ms, frames_n=48, motion="scroll",
                      cycle=False, cycle_turns=1.0):
    text = (text or "BANNER").strip() or "BANNER"
    width = max(200, min(width, 3000))
    height = max(120, min(height, 1200))
    speed_ms = max(20, min(speed_ms, 400))
    frames_n = max(12, min(frames_n, 120))
    if motion not in MOTIONS:
        motion = "scroll"

    fill = hex_to_rgb(fg, (255, 214, 10))
    fill2 = hex_to_rgb(fg2, (255, 71, 71))
    bg_c = hex_to_rgb(bg, (17, 17, 34))
    accent_c = hex_to_rgb(accent, (40, 40, 70))

    # Static background frame (built once), reused each frame.
    base = Image.new("RGB", (width, height), bg_c)
    paint_background(base, pattern, bg_c, accent_c)

    probe = ImageDraw.Draw(base)
    # Wave/bounce need vertical headroom, so fit a bit smaller in those modes.
    fit_h = height * (0.72 if motion != "scroll" else 1.0)
    font = _fit_font(probe, text, font_name, width, int(fit_h), fit_width=False)
    fsize = font_size_of(font)
    box = probe.textbbox((0, 0), text, font=font)
    tw = box[2] - box[0]
    ly = (height - (box[3] - box[1])) // 2 - box[1]

    def hue_at(f):
        return (cycle_turns * f / frames_n) % 1.0 if cycle else 0.0

    frames = []

    if motion == "scroll":
        # Fast path: pre-render the whole word once and slide the layer. With
        # color-cycle on, the word must be re-rendered per frame (hue changes).
        pad = max(20, fsize // 2)
        total = width + tw + pad * 2
        prebuilt = None
        if not cycle:
            prebuilt = Image.new("RGBA", (tw + pad * 2, height), (0, 0, 0, 0))
            draw_text_effect(prebuilt, text, font, (pad - box[0], ly), effect, fill, fill2, (0, 0, 0))
        for i in range(frames_n):
            if cycle:
                layer = Image.new("RGBA", (tw + pad * 2, height), (0, 0, 0, 0))
                draw_text_effect(layer, text, font, (pad - box[0], ly),
                                 effect, fill, fill2, (0, 0, 0), hue=hue_at(i))
            else:
                layer = prebuilt
            offset = width - int(total * (i / frames_n))
            frame = base.copy()
            frame.paste(layer, (offset, 0), layer)
            draw_border(frame, border, fill)
            frames.append(frame)
    else:
        # Per-letter path: place each glyph individually with a vertical offset.
        n = len(text)
        advances = []
        cx = 0.0
        for ch in text:
            advances.append(cx)
            cx += probe.textlength(ch, font=font)
        text_w = cx
        amp = fsize * 0.30
        total = width + text_w
        # Tiles are color-fixed, so precompute them only when NOT cycling.
        tiles = None
        if not cycle:
            tiles = [
                draw_glyph_tile(ch, font, effect, char_color(effect, i, n, fill, fill2), (0, 0, 0))
                for i, ch in enumerate(text)
            ]
        for f in range(frames_n):
            hue = hue_at(f)
            scroll_x = width - int(total * (f / frames_n))
            frame = base.copy().convert("RGBA")
            for i, ch in enumerate(text):
                if ch == " ":
                    continue
                px = scroll_x + advances[i]
                if px > width + fsize or px < -fsize * 2:
                    continue  # fully off-screen; skip the paste
                yo = _y_offset(motion, i, f, frames_n, amp)
                if cycle:
                    color = char_color(effect, i, n, fill, fill2, hue)
                    tile, pen_x, pen_y = draw_glyph_tile(ch, font, effect, color, (0, 0, 0))
                else:
                    tile, pen_x, pen_y = tiles[i]
                frame.alpha_composite(
                    tile, (int(round(px - pen_x)), int(round(ly + yo - pen_y)))
                )
            frame = frame.convert("RGB")
            draw_border(frame, border, fill)
            frames.append(frame)

    # Shared palette across all frames to avoid color flicker. When cycling,
    # sample several frames into one montage so the palette spans every hue.
    if cycle:
        k = min(len(frames), 12)
        idxs = [int(j * len(frames) / k) for j in range(k)]
        sw = max(1, width // k)
        montage = Image.new("RGB", (sw * k, height))
        for col, j in enumerate(idxs):
            montage.paste(frames[j].resize((sw, height)), (col * sw, 0))
        pal = montage.quantize(colors=256)
    else:
        pal = frames[0].quantize(colors=256)
    frames_p = [f.quantize(palette=pal) for f in frames]

    buf = io.BytesIO()
    frames_p[0].save(
        buf, format="GIF", save_all=True, append_images=frames_p[1:],
        duration=speed_ms, loop=0, disposal=2, optimize=True,
    )
    buf.seek(0)
    return buf


# --- Routes -----------------------------------------------------------------
def _common_args():
    return {
        "text": request.args.get("text", "BANNER MANIA"),
        "font_name": request.args.get("font", DEFAULT_FONT or "Default"),
        "effect": request.args.get("effect", "shadow"),
        "pattern": request.args.get("pattern", "solid"),
        "border": request.args.get("border", "single"),
        "fg": request.args.get("fg", "#ffd60a"),
        "fg2": request.args.get("fg2", "#ff4747"),
        "bg": request.args.get("bg", "#111122"),
        "accent": request.args.get("accent", "#28284a"),
        "width": int(request.args.get("width", 1000) or 1000),
        "height": int(request.args.get("height", 300) or 300),
    }


@app.route("/")
def index():
    fonts = available_fonts() or ["Default"]
    return render_template(
        "index.html",
        fonts=fonts,
        effects=EFFECTS,
        patterns=PATTERNS,
        borders=BORDERS,
        motions=MOTIONS,
        default_font=DEFAULT_FONT or "Default",
    )


@app.route("/generate")
def generate():
    img = render_banner(**_common_args())
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    download = request.args.get("download") == "1"
    return send_file(buf, mimetype="image/png",
                     as_attachment=download, download_name="banner.png")


@app.route("/generate.gif")
def generate_gif():
    args = _common_args()
    buf = render_scroll_gif(
        **args,
        speed_ms=int(request.args.get("speed", 60) or 60),
        frames_n=int(request.args.get("frames", 48) or 48),
        motion=request.args.get("motion", "scroll"),
        cycle=request.args.get("cycle") == "1",
        cycle_turns=float(request.args.get("cycle_turns", 1.0) or 1.0),
    )
    download = request.args.get("download") == "1"
    return send_file(buf, mimetype="image/gif",
                     as_attachment=download, download_name="banner.gif")


@app.route("/health")
def health():
    return jsonify(status="ok", fonts=available_fonts(),
                   effects=EFFECTS, patterns=PATTERNS, borders=BORDERS, motions=MOTIONS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BannerMania banner generator")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
