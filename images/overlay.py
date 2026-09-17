from __future__ import annotations

import math
import random
from pathlib import Path

from models import Article, PostImage


def generate_overlay(article: Article, draft_dir: str) -> PostImage | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("    [!] Pillow not installed, skipping overlay generation")
        return None

    width, height = 1200, 627
    img = Image.new("RGB", (width, height), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    random.seed(hash(article.title))

    _draw_grid(draw, width, height)
    _draw_hex_nodes(draw, width, height)
    _draw_circuit_lines(draw, width, height)
    _draw_scanlines(draw, width, height)

    _draw_gradient_overlay(img, height)

    draw = ImageDraw.Draw(img)

    accent = (0, 200, 255)
    accent_dim = (0, 100, 160)
    red_accent = (233, 69, 96)

    draw.rectangle([(0, 0), (6, height)], fill=accent)
    draw.rectangle([(0, 0), (width, 3)], fill=accent_dim)
    draw.rectangle([(0, height - 3), (width, height)], fill=red_accent)

    try:
        font_large = ImageFont.truetype("images/assets/fonts/Inter-Bold.ttf", 38)
        font_medium = ImageFont.truetype("images/assets/fonts/Inter-Bold.ttf", 22)
        font_small = ImageFont.truetype("images/assets/fonts/Inter-Bold.ttf", 16)
    except OSError:
        try:
            font_large = ImageFont.truetype("arial.ttf", 38)
            font_medium = ImageFont.truetype("arial.ttf", 22)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large

    source_names = {
        "unit42": "UNIT 42 | PALO ALTO NETWORKS",
        "cisa_alerts": "CISA ADVISORY",
        "krebs": "KREBS ON SECURITY",
        "bleeping": "BLEEPINGCOMPUTER",
        "hackernews_sec": "THE HACKER NEWS",
        "dark_reading": "DARK READING",
    }
    source_label = source_names.get(article.source_id, article.source_id.upper())

    draw.rectangle([(30, 40), (30 + 4, 40 + 22)], fill=accent)
    draw.text((42, 40), f"THREAT INTELLIGENCE", fill=accent, font=font_small)

    title = article.title.upper()
    lines = _wrap_text(title, font_large, width - 100)
    y = 120
    for line in lines:
        draw.text((40, y), line, fill=(255, 255, 255), font=font_large)
        y += 50

    separator_y = y + 20
    draw.rectangle([(40, separator_y), (300, separator_y + 2)], fill=accent)

    tags = article.tags[:4]
    if tags:
        tag_y = separator_y + 20
        tag_x = 40
        for tag in tags:
            tag_text = tag.upper()
            try:
                bbox = font_small.getbbox(tag_text)
                tw = bbox[2] - bbox[0]
            except AttributeError:
                tw = len(tag_text) * 8
            draw.rectangle([(tag_x - 4, tag_y - 2), (tag_x + tw + 8, tag_y + 20)], fill=(0, 200, 255, 30), outline=accent_dim)
            draw.text((tag_x + 2, tag_y), tag_text, fill=accent, font=font_small)
            tag_x += tw + 24
            if tag_x > width - 100:
                break

    draw.rectangle([(40, height - 60), (40 + 4, height - 60 + 22)], fill=red_accent)
    draw.text((52, height - 60), f"SOURCE: {source_label}", fill=red_accent, font=font_medium)

    _draw_shield_icon(draw, width - 90, 40, accent_dim)

    path = Path(draft_dir) / "image.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), "PNG")

    return PostImage(
        path=str(path),
        source_type="overlay",
        alt_text=f"Cyber threat intel card: {article.title[:80]}",
    )


def _draw_grid(draw, width, height):
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(20, 30, 50), width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(20, 30, 50), width=1)


def _draw_hex_nodes(draw, width, height):
    for _ in range(15):
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        size = random.randint(8, 20)
        color = random.choice([(0, 60, 90), (0, 40, 70), (30, 10, 40)])
        _draw_hexagon(draw, x, y, size, color)
        if random.random() > 0.5:
            x2 = x + random.randint(-120, 120)
            y2 = y + random.randint(-80, 80)
            draw.line([(x, y), (x2, y2)], fill=(0, 50, 80), width=1)


def _draw_hexagon(draw, cx, cy, size, color):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = cx + size * math.cos(angle)
        py = cy + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color)


def _draw_circuit_lines(draw, width, height):
    for _ in range(8):
        x = random.randint(0, width)
        y = random.randint(0, height)
        color = (0, 40, 60)
        for _ in range(random.randint(3, 6)):
            if random.random() > 0.5:
                x2 = x + random.choice([-1, 1]) * random.randint(30, 100)
                draw.line([(x, y), (x2, y)], fill=color, width=1)
                x = x2
            else:
                y2 = y + random.choice([-1, 1]) * random.randint(30, 80)
                draw.line([(x, y), (x, y2)], fill=color, width=1)
                y = y2
            draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=color)


def _draw_scanlines(draw, width, height):
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 15), width=1)


def _draw_gradient_overlay(img, height):
    from PIL import Image as PILImage
    overlay = PILImage.new("RGBA", img.size, (0, 0, 0, 0))
    draw_ov = ImageDraw_from_image(overlay)
    for y in range(height):
        alpha = int(180 * (y / height))
        draw_ov.line([(0, y), (img.width, y)], fill=(5, 5, 15, alpha))
    img.paste(PILImage.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))


def ImageDraw_from_image(img):
    from PIL import ImageDraw
    return ImageDraw.Draw(img)


def _draw_shield_icon(draw, x, y, color):
    points = [
        (x, y), (x + 30, y + 10), (x + 30, y + 35),
        (x + 15, y + 50), (x, y + 50), (x - 15, y + 50),
        (x - 30, y + 35), (x - 30, y + 10),
    ]
    draw.polygon(points, outline=color)
    draw.line([(x, y + 15), (x - 8, y + 30)], fill=color, width=2)
    draw.line([(x - 8, y + 30), (x + 12, y + 20)], fill=color, width=2)


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        try:
            bbox = font.getbbox(test)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w = len(test) * 10

        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines[:4]
