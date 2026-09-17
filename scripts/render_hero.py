"""Render a sharp Russian README hero (large type, PNG)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

W, H = 2000, 860
BG = (9, 14, 28)
CARD = (16, 23, 38)
LINE = (48, 64, 92)
TEXT = (240, 244, 252)
MUTED = (156, 170, 190)
BLUE = (59, 148, 255)
CYAN = (56, 214, 190)
RED = (251, 113, 133)
GREEN = (74, 222, 128)
WHITE = (255, 255, 255)
CHIP = (20, 31, 52)

NOTO = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
NOTO_MD = "/usr/share/fonts/noto/NotoSans-Medium.ttf"
NOTO_BD = "/usr/share/fonts/noto/NotoSans-Bold.ttf"
FIRA_BD = "/usr/share/fonts/TTF/FiraSans-Bold.ttf"
MONO = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"
CJK = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"


def fnt(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def rr(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render_hero() -> None:
    img = Image.new("RGB", (W, H), BG)
    glow = Image.new("RGB", (W, H), BG)
    ImageDraw.Draw(glow).ellipse((1080, -40, 2100, 900), fill=(18, 42, 86))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(64)), 0.45)
    draw = ImageDraw.Draw(img)

    draw.text((1380, 250), "Я", font=fnt(NOTO_BD, 300), fill=(15, 26, 48))

    rr(draw, (72, 72, 212, 212), 36, WHITE)
    # Center Я in the icon by bbox
    ya = fnt(NOTO_BD, 92)
    bbox = draw.textbbox((0, 0), "Я", font=ya)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((72 + (140 - tw) / 2 - bbox[0], 72 + (140 - th) / 2 - bbox[1]), "Я", font=ya, fill=BLUE)

    draw.text((240, 84), "cjk_sanitizer_ru", font=fnt(FIRA_BD, 54), fill=TEXT)
    draw.text((240, 154), "Кириллица и код остаются.", font=fnt(NOTO, 28), fill=MUTED)
    draw.text((240, 192), "Чужие письменности вырезаются.", font=fnt(NOTO, 28), fill=MUTED)

    chips = ("Кириллица", "Латиница", "Код цел", "CJK режется")
    x = 72
    face = fnt(NOTO_MD, 22)
    for label in chips:
        tw = int(draw.textlength(label, font=face))
        box = (x, 250, x + tw + 40, 304)
        rr(draw, box, 14, CHIP, outline=LINE)
        draw.text((x + 20, 262), label, font=face, fill=CYAN)
        x = box[2] + 16

    rr(draw, (72, 336, 920, 560), 20, CARD, outline=LINE)
    mono = fnt(MONO, 26)
    draw.text((104, 372), "from sanitize import sanitize", font=mono, fill=(125, 211, 252))
    draw.text((104, 420), "cleaned = sanitize(text)", font=mono, fill=TEXT)
    draw.text((104, 480), "# русский и код не трогаем", font=mono, fill=(110, 125, 148))

    rr(draw, (972, 72, 1928, 300), 20, CARD, outline=(110, 48, 60))
    draw.ellipse((1004, 100, 1032, 128), fill=RED)
    draw.text((1052, 92), "ДО", font=fnt(NOTO_BD, 28), fill=RED)
    draw.text((1004, 156), "Ответ: готово", font=fnt(NOTO, 32), fill=TEXT)
    draw.text((1004, 214), "你好 안녕하세요", font=fnt(CJK, 32), fill=RED)

    draw.polygon([(1428, 324), (1476, 324), (1452, 356)], fill=BLUE)

    rr(draw, (972, 376, 1928, 604), 20, CARD, outline=(32, 96, 64))
    draw.ellipse((1004, 404, 1032, 432), fill=GREEN)
    draw.text((1052, 396), "ПОСЛЕ", font=fnt(NOTO_BD, 28), fill=GREEN)
    draw.text((1004, 476), "Ответ: готово", font=fnt(NOTO, 34), fill=TEXT)

    draw.text((72, 640), "Hermes Agent plugin", font=fnt(NOTO, 24), fill=(80, 94, 114))
    draw.text((972, 640), "github.com/reclaw17/cjk_sanitizer_ru", font=fnt(NOTO, 24), fill=MUTED)

    png = ASSETS / "hero.png"
    jpg = ASSETS / "hero.jpg"
    img.save(png, "PNG", optimize=True)
    img.convert("RGB").save(jpg, "JPEG", quality=95, optimize=True)
    print(png, jpg, img.size)


def render_flag_ru() -> None:
    w, h = 48, 32
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, h // 3, w, 2 * h // 3), fill=(0, 57, 166))
    draw.rectangle((0, 2 * h // 3, w, h), fill=(213, 43, 30))
    img.save(ASSETS / "flag-ru.png", "PNG")


def render_flag_us() -> None:
    """Compact Stars and Stripes, readable at 14px height."""
    w, h = 48, 32
    red = (179, 25, 66)
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    stripe = h / 13
    for i in range(13):
        if i % 2 == 0:
            y0 = round(i * stripe)
            y1 = round((i + 1) * stripe)
            draw.rectangle((0, y0, w, y1), fill=red)
    canton_w, canton_h = 21, round(7 * stripe)
    draw.rectangle((0, 0, canton_w, canton_h), fill=(10, 49, 97))
    for row, count in enumerate((6, 5, 6, 5, 6)):
        y = 2 + row * 2
        x0 = 2 if count == 6 else 4
        for col in range(count):
            x = x0 + col * 3
            draw.point((x, y), fill=(255, 255, 255))
            draw.point((x + 1, y), fill=(255, 255, 255))
    img.save(ASSETS / "flag-us.png", "PNG")


def render_icon() -> None:
    size = 512
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)
    rr(draw, (40, 40, 472, 472), 104, WHITE, width=0)
    ya = fnt(NOTO_BD, 260)
    bbox = draw.textbbox((0, 0), "Я", font=ya)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] - 8), "Я", font=ya, fill=BLUE)
    path = ASSETS / "icon.png"
    img.save(path, "PNG", optimize=True)
    print(path, img.size)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_hero()
    render_icon()
    render_flag_ru()
    render_flag_us()
    print(ASSETS / "flag-ru.png")
    print(ASSETS / "flag-us.png")
