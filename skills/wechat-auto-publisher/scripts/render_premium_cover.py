import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


W, H = 2350, 1000
ROOT = Path(__file__).resolve().parent
# 默认用本包自带人像，可用 WECHAT_PORTRAIT 指到你自己的头像
PORTRAIT = Path(os.environ.get("WECHAT_PORTRAIT", str(ROOT.parent / "assets" / "owner_portrait.jpg")))


def font(size, weight="regular"):
    candidates = {
        "heavy": [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ],
        "regular": [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ],
    }[weight]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def cover_resize(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    size = (int(img.width * scale), int(img.height * scale))
    img = img.resize(size, Image.Resampling.LANCZOS)
    return img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width + W) // 2, (img.height + H) // 2))


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def add_vignette(base):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, int(W * 0.62), H), fill=(0, 0, 0, 92))
    d.rectangle((0, 0, W, 90), fill=(0, 0, 0, 50))
    d.rectangle((0, H - 130, W, H), fill=(0, 0, 0, 60))
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def paste_portrait(base):
    portrait = Image.open(PORTRAIT).convert("RGB")
    crop = ImageOps.fit(portrait, (520, 680), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
    crop = ImageEnhanceLike(crop)

    card_w, card_h = 570, 730
    x, y = 1628, 145

    glow = Image.new("RGBA", (card_w + 80, card_h + 80), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((40, 40, card_w + 40, card_h + 40), radius=42, fill=(44, 171, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(glow, (x - 40, y - 40))

    shadow = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((0, 0, card_w, card_h), radius=36, fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(shadow, (x + 16, y + 20))

    card = Image.new("RGBA", (card_w, card_h), (8, 15, 25, 230))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, card_w - 1, card_h - 1), radius=36, outline=(204, 168, 92, 125), width=2)
    cd.rounded_rectangle((18, 18, card_w - 19, card_h - 19), radius=28, outline=(255, 255, 255, 28), width=1)

    photo_mask = rounded_mask((520, 680), 26)
    card.alpha_composite(crop.convert("RGBA"), (25, 25))
    fade = Image.new("RGBA", (520, 180), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(180):
        fd.line((0, i, 520, i), fill=(3, 9, 17, int(185 * i / 180)))
    card.alpha_composite(fade, (25, 525))

    small = ImageDraw.Draw(card)
    small.text((52, 618), "袁六伟", font=font(42, "heavy"), fill=(255, 255, 255, 238))
    small.text((52, 672), "一人 AI 公司", font=font(24, "regular"), fill=(206, 174, 104, 230))
    card_mask = rounded_mask((card_w, card_h), 36)
    base.paste(card, (x, y), card_mask)


def ImageEnhanceLike(img):
    # Lightweight grade without importing extra modules repeatedly.
    from PIL import ImageEnhance
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(0.92)
    img = ImageEnhance.Brightness(img).enhance(0.98)
    return img


def draw_text(base, variant):
    d = ImageDraw.Draw(base)
    white = (246, 247, 241, 255)
    muted = (169, 181, 194, 235)
    gold = (219, 180, 92, 255)
    cyan = (63, 173, 240, 245)

    d.text((122, 104), "AI BUSINESS · COST ERA", font=font(30, "regular"), fill=(160, 176, 190, 220))
    d.line((122, 154, 536, 154), fill=(208, 168, 86, 210), width=2)

    if variant == "a":
        lines = [("AI自动化", white), ("开始算账", gold)]
        subtitle = "Claude Code 成本下降背后，真正的商业分水岭"
    elif variant == "b":
        lines = [("会用AI不够", white), ("还要会算账", gold)]
        subtitle = "自动化进入经营阶段，成本、边界、复利一起上桌"
    else:
        lines = [("AI员工", white), ("不是免费的", gold)]
        subtitle = "当工具开始长期干活，老板必须管理它的油耗"

    y = 230
    title_font = font(130, "heavy")
    for text, color in lines:
        d.text((118, y), text, font=title_font, fill=(0, 0, 0, 130), stroke_width=0)
        d.text((112, y - 5), text, font=title_font, fill=color)
        y += 148

    d.line((122, 592, 932, 592), fill=(214, 176, 94, 170), width=2)
    d.text((122, 626), subtitle, font=font(34, "regular"), fill=(214, 224, 231, 230))

    d.text((122, 764), "CLAUDE CODE", font=font(28, "regular"), fill=(167, 184, 196, 225))
    d.text((340, 764), "AI AUTOMATION", font=font(28, "regular"), fill=(167, 184, 196, 225))
    d.text((628, 764), "COST STRUCTURE", font=font(28, "regular"), fill=(167, 184, 196, 225))

    d.text((122, 886), "YUAN LIUWEI · ONE-PERSON AI COMPANY", font=font(24, "regular"), fill=(125, 141, 155, 210))
    d.line((120, 850, 960, 850), fill=(255, 255, 255, 44), width=1)
    d.line((2250, 92, 2250, 908), fill=cyan, width=5)


def render(bg_path, variant):
    bg = cover_resize(Image.open(bg_path))
    base = add_vignette(bg)
    paste_portrait(base)
    draw_text(base, variant)
    out = ROOT / f"premium_cover_{variant}.png"
    base.convert("RGB").save(out, quality=95)
    return out


for variant, bg in [("a", "bg_a.png"), ("b", "bg_b.png"), ("c", "bg_c.png")]:
    print(render(ROOT / bg, variant))
