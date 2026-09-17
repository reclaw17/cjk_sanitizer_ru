"""Render Russian README hero and icon with real fonts."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

W, H = 1600, 680
BG = (8, 13, 28)
CARD = (15, 22, 36)
LINE = (42, 56, 84)
TEXT = (236, 242, 252)
MUTED = (148, 163, 184)
BLUE = (56, 151, 255)
CYAN = (45, 212, 191)
RED = (248, 113, 113)
GREEN = (74, 222, 128)
WHITE = (255, 255, 255)
CHIP = (21, 32, 54)

FIRA = "/usr/share/fonts/TTF/FiraSans-Regular.ttf"
FIRA_BD = "/usr/share/fonts/TTF/FiraSans-Bold.ttf"
NOTO = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
NOTO_BD = "/usr/share/fonts/noto/NotoSans-Bold.ttf"
MONO = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"
CJK = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"


def fnt(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def rr(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def draw_mixed(draw: ImageDraw.ImageDraw, x: int, y: int, parts: list[tuple[str, ImageFont.FreeTypeFont, tuple[int, int, int]]]) -> None:
    for text, face, color in parts:
        draw.text((x, y), text, font=face, fill=color)
        x += int(draw.textlength(text, font=face))


def render_hero() -> None:
    img = Image.new("RGB", (W, H), BG)
    glow = Image.new("RGB", (W, H), BG)
    ImageDraw.Draw(glow).ellipse((1000, -60, 1800, 760), fill=(16, 38, 78))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(52)), 0.5)
    draw = ImageDraw.Draw(img)

    draw.text((1220, 200), "Я", font=fnt(NOTO_BD, 260), fill=(16, 28, 52))

    rr(draw, (64, 64, 176, 176), 28, WHITE)
    draw.text((90, 70), "Я", font=fnt(NOTO_BD, 76), fill=BLUE)

    draw.text((200, 70), "cjk_sanitizer_ru", font=fnt(FIRA_BD, 44), fill=TEXT)
    draw.text(
        (200, 128),
        "Кириллица и код остаются. Чужие письменности вырезаются.",
        font=fnt(NOTO, 22),
        fill=MUTED,
    )

    chips = ("Кириллица", "Латиница", "Код цел", "CJK режется")
    x = 64
    face = fnt(NOTO, 18)
    for label in chips:
        tw = int(draw.textlength(label, font=face))
        box = (x, 208, x + tw + 32, 250)
        rr(draw, box, 12, CHIP, outline=LINE)
        draw.text((x + 16, 216), label, font=face, fill=CYAN)
        x = box[2] + 14

    rr(draw, (64, 278, 760, 448), 16, CARD, outline=LINE)
    mono = fnt(MONO, 20)
    draw.text((88, 304), "from sanitize import sanitize", font=mono, fill=(125, 211, 252))
    draw.text((88, 344), "cleaned = sanitize(text)", font=mono, fill=TEXT)
    draw.text((88, 392), "# русский и код не трогаем", font=mono, fill=(100, 116, 139))

    rr(draw, (820, 64, 1536, 248), 18, CARD, outline=(96, 42, 52))
    draw.ellipse((848, 84, 868, 104), fill=RED)
    draw.text((884, 76), "ДО", font=fnt(FIRA_BD, 22), fill=RED)
    draw_mixed(
        draw,
        848,
        136,
        [
            ("Ответ: ", fnt(NOTO, 26), TEXT),
            ("你好 안녕하세요", fnt(CJK, 26), (252, 165, 165)),
            (" готово", fnt(NOTO, 26), TEXT),
        ],
    )

    draw.polygon([(1168, 268), (1200, 268), (1184, 294)], fill=BLUE)

    rr(draw, (820, 316, 1536, 500), 18, CARD, outline=(30, 86, 58))
    draw.ellipse((848, 336, 868, 356), fill=GREEN)
    draw.text((884, 328), "ПОСЛЕ", font=fnt(FIRA_BD, 22), fill=GREEN)
    draw.text((848, 400), "Ответ: готово", font=fnt(NOTO, 28), fill=TEXT)

    draw.text((64, 548), "Hermes Agent plugin", font=fnt(FIRA, 20), fill=(71, 85, 105))
    draw.text(
        (820, 548),
        "github.com/reclaw17/cjk_sanitizer_ru",
        font=fnt(FIRA, 20),
        fill=MUTED,
    )

    path = ASSETS / "hero.jpg"
    img.save(path, "JPEG", quality=93, optimize=True)
    print(path, img.size)


def render_icon() -> None:
    size = 512
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)
    rr(draw, (48, 48, 464, 464), 96, WHITE)
    draw.text((128, 96), "Я", font=fnt(NOTO_BD, 280), fill=BLUE)
    path = ASSETS / "icon.png"
    img.save(path, "PNG", optimize=True)
    print(path, img.size)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_hero()
    render_icon()
