"""
Generate decorative illustration assets for the login screen using PIL.
Produces a stylized library banner (book stack + arch + decorative shapes)
suitable for both light and dark themes.
"""

import os
from PIL import Image, ImageDraw, ImageFont


ASSETS_DIR = "assets"


def _try_load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make_library_banner(width=480, height=140, theme="light"):
    """
    Draw a stylized library scene: column of books, decorative arches,
    soft gradient background.
    """
    if theme == "light":
        bg_top = (245, 247, 251)        # LIGHT_BG
        bg_bottom = (231, 236, 245)
        accent = (11, 31, 58)            # NAVY
        gold = (184, 134, 11)            # GOLD
        shelf = (139, 90, 43)
    else:
        bg_top = (16, 28, 50)
        bg_bottom = (8, 18, 36)
        accent = (212, 162, 46)          # GOLD_LIGHT
        gold = (184, 134, 11)
        shelf = (95, 60, 28)

    img = Image.new("RGBA", (width, height), bg_top + (255,))
    draw = ImageDraw.Draw(img)

    # Vertical gradient background
    for y in range(height):
        ratio = y / height
        r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * ratio)
        g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * ratio)
        b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Decorative dots in background
    import random
    random.seed(7)
    for _ in range(35):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.choice([1, 1, 2])
        alpha = random.randint(40, 120)
        col = (gold[0], gold[1], gold[2], alpha)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     fill=col)

    # Bottom shelf line (gold underline)
    draw.line([(20, height - 18), (width - 20, height - 18)],
              fill=gold + (255,), width=2)

    # Bookshelf base with stack of books — left
    book_colors = [
        (176, 50, 50), (60, 110, 180), (60, 160, 100),
        (200, 130, 30), (130, 70, 170), (40, 130, 150),
    ]
    base_y = height - 22
    book_widths = [16, 22, 18, 24, 20, 16, 22, 18]
    x = 40
    random.seed(13)
    for i, w in enumerate(book_widths):
        h_book = random.randint(48, 80)
        col = book_colors[i % len(book_colors)]
        draw.rectangle([x, base_y - h_book, x + w, base_y],
                       fill=col + (255,), outline=accent + (255,), width=1)
        # Decorative line on book
        draw.line([(x + 3, base_y - h_book + 8),
                   (x + w - 3, base_y - h_book + 8)],
                  fill=(255, 255, 255, 90), width=1)
        x += w + 2

    # Right side: open book / arch silhouette
    arch_x = width - 160
    arch_y = 28
    arch_w = 130
    arch_h = height - 50

    # Arch frame (subtle)
    draw.rounded_rectangle([arch_x, arch_y, arch_x + arch_w, arch_y + arch_h],
                           radius=arch_w // 2,
                           outline=accent + (180,), width=2)

    # Open book inside arch
    book_x = arch_x + 18
    book_y = arch_y + 28
    book_w = arch_w - 36
    book_h = 50
    # Two pages
    draw.polygon([
        (book_x, book_y + 8),
        (book_x + book_w // 2 - 2, book_y),
        (book_x + book_w // 2 - 2, book_y + book_h),
        (book_x, book_y + book_h - 4),
    ], fill=(255, 255, 255, 240), outline=accent + (255,))
    draw.polygon([
        (book_x + book_w // 2 + 2, book_y),
        (book_x + book_w, book_y + 8),
        (book_x + book_w, book_y + book_h - 4),
        (book_x + book_w // 2 + 2, book_y + book_h),
    ], fill=(255, 255, 255, 240), outline=accent + (255,))
    # Page lines
    for i, y_off in enumerate([16, 26, 36]):
        draw.line([(book_x + 6, book_y + y_off),
                   (book_x + book_w // 2 - 8, book_y + y_off)],
                  fill=(120, 120, 130, 180), width=1)
        draw.line([(book_x + book_w // 2 + 8, book_y + y_off),
                   (book_x + book_w - 6, book_y + y_off)],
                  fill=(120, 120, 130, 180), width=1)

    # Golden star/sparkles around book
    star_positions = [(arch_x + 8, arch_y + 14),
                      (arch_x + arch_w - 16, arch_y + 22),
                      (arch_x + arch_w - 8, arch_y + arch_h - 30)]
    for sx, sy in star_positions:
        draw.line([(sx - 4, sy), (sx + 4, sy)], fill=gold + (255,), width=2)
        draw.line([(sx, sy - 4), (sx, sy + 4)], fill=gold + (255,), width=2)

    # Center text
    font_big = _try_load_font(20, bold=True)
    font_small = _try_load_font(11, bold=False)
    text_color = accent if theme == "light" else (240, 240, 245)
    sub_color = (110, 120, 135) if theme == "light" else (180, 190, 210)

    title = "Knowledge Begins Here"
    sub = "हर पुस्तक एक नई दुनिया"

    # Approximate text positions (roughly centered)
    try:
        tw = draw.textlength(title, font=font_big)
    except Exception:
        tw = len(title) * 9
    try:
        sw = draw.textlength(sub, font=font_small)
    except Exception:
        sw = len(sub) * 6

    cx = width // 2
    draw.text((cx - tw // 2, 38), title, fill=text_color + (255,),
              font=font_big)
    draw.text((cx - sw // 2, 66), sub, fill=sub_color + (255,),
              font=font_small)

    return img


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    light_path = os.path.join(ASSETS_DIR, "login_banner_light.png")
    dark_path = os.path.join(ASSETS_DIR, "login_banner_dark.png")

    light_img = make_library_banner(theme="light")
    light_img.save(light_path, "PNG")
    print(f"✓ {light_path}  ({os.path.getsize(light_path)/1024:.1f} KB)")

    dark_img = make_library_banner(theme="dark")
    dark_img.save(dark_path, "PNG")
    print(f"✓ {dark_path}  ({os.path.getsize(dark_path)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
