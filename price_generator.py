# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os
import random
from translations import Translator

# --- CONFIGURATION ---
DPI = 300
PRIMARY_FONT_PATH = 'fonts/NotoSansGeorgian-Regular.ttf'
PRIMARY_FONT_BOLD_PATH = 'fonts/NotoSansGeorgian-Bold.ttf'
FALLBACK_FONT_EN = "arial.ttf"
FALLBACK_FONT_EN_BOLD = "arialbd.ttf"


# --- FONT SETUP ---
def get_font(font_path, size, fallback_path=None):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        if fallback_path:
            try:
                return ImageFont.truetype(fallback_path, size)
            except IOError:
                return ImageFont.load_default()
    return ImageFont.load_default()


def cm_to_pixels(cm, dpi=DPI):
    return int(cm / 2.54 * dpi)


def create_price_tag(item_data, size_config, theme, language='en'):
    width_cm, height_cm = size_config['dims']
    width_px, height_px = cm_to_pixels(width_cm), cm_to_pixels(height_cm)

    img = Image.new('RGB', (width_px, height_px), 'white')

    translator = Translator()

    # --- Theme Setup ---
    text_color = theme.get("text_color", "black")
    price_color = theme.get('price_color', '#D32F2F')
    strikethrough_color = theme.get("strikethrough_color", "black")
    if language == 'ka':
        logo_to_use = theme.get("logo_path_ka", "assets/logo-geo.png")
    else:
        logo_to_use = theme.get("logo_path", "assets/logo.png")
    logo_scale = theme.get("logo_scale_factor", 0.9)
    bullet_image_path = theme.get("bullet_image_path")

    # --- Draw Background Effects ---
    if theme.get("background_snow"):
        snow_draw = ImageDraw.Draw(img)
        for _ in range(70):
            x, y = random.randint(0, width_px), random.randint(0, height_px)
            radius = random.randint(10, 30)
            snow_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(235, 245, 255, 50))

    draw = ImageDraw.Draw(img)

    # --- Layout Proportions ---
    margin = 0.05 * width_px
    top_margin, bottom_margin = 0.03 * height_px, 0.02 * height_px
    logo_area_height, title_area_height, footer_area_height = 0.10 * height_px, 0.11 * height_px, 0.14 * height_px

    logo_area_top = top_margin
    title_area_top = logo_area_top + logo_area_height
    specs_area_top = title_area_top + title_area_height

    footer_area_bottom = height_px - bottom_margin

    # UPDATED: Separated the calculation onto two lines to fix the UnboundLocalError
    footer_area_top = footer_area_bottom - footer_area_height
    specs_area_bottom = footer_area_top - (0.02 * height_px)

    specs_area_height = specs_area_bottom - specs_area_top

    # --- Draw Logo, Title, Separators ---
    try:
        with Image.open(logo_to_use) as logo:
            logo.thumbnail((int((width_px - 2 * margin) * 0.7), int(logo_area_height * logo_scale)),
                           Image.Resampling.LANCZOS)
            img.paste(logo,
                      (int((width_px - logo.width) / 2), int(logo_area_top + (logo_area_height - logo.height) / 2)),
                      logo)
    except FileNotFoundError:
        print(f"Warning: Logo file not found at '{logo_to_use}'")

    title_font = get_font(PRIMARY_FONT_BOLD_PATH, 60, FALLBACK_FONT_EN_BOLD)
    draw.text((width_px / 2, title_area_top + title_area_height / 2), item_data.get('Name', 'N/A'), font=title_font,
              fill=text_color, anchor='mm', align='center')
    draw.line([(margin, specs_area_top - (0.01 * height_px)), (width_px - margin, specs_area_top - (0.01 * height_px))],
              fill=text_color, width=3)

    # --- Draw Specifications ---
    spec_font_regular = get_font(PRIMARY_FONT_PATH, 42, FALLBACK_FONT_EN)
    spec_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, 42, FALLBACK_FONT_EN_BOLD)

    bullet_img = None
    if bullet_image_path and os.path.exists(bullet_image_path):
        try:
            bullet_img = Image.open(bullet_image_path).convert("RGBA")
        except:
            pass

    specs, num_specs = item_data.get('specs', []), len(item_data.get('specs', []))
    if num_specs > 0:
        line_height = specs_area_height / num_specs
        for i, spec in enumerate(specs):
            current_y, current_x = int(specs_area_top + (i * line_height) + (line_height / 2)), int(margin + 20)
            if bullet_img:
                bullet_size = int(line_height * 0.6)
                bullet_resized = bullet_img.resize((bullet_size, bullet_size), Image.Resampling.LANCZOS)
                img.paste(bullet_resized, (current_x, current_y - bullet_size // 2), bullet_resized);
                current_x += bullet_size + 15
            else:
                draw.text((current_x, current_y), "• ", font=spec_font_regular, fill=text_color, anchor='lm');
                current_x += int(spec_font_regular.getbbox("• ")[2])
            if ':' in spec:
                label, value = spec.split(':', 1)
                translated_label = translator.get_spec_label(label.strip(), language);
                label = translated_label + ':'
                draw.text((current_x, current_y), label, font=spec_font_bold, fill=text_color, anchor='lm');
                current_x += int(spec_font_bold.getbbox(label)[2])
                draw.text((current_x, current_y), ' ' + value.strip(), font=spec_font_regular, fill=text_color,
                          anchor='lm')
            else:
                draw.text((current_x, current_y), spec, font=spec_font_regular, fill=text_color, anchor='lm')

    # --- Draw Footer ---
    draw.line([(margin, footer_area_top), (width_px - margin, footer_area_top)], fill=text_color, width=3)
    footer_content_y = footer_area_top + (footer_area_height / 2)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, 60, FALLBACK_FONT_EN_BOLD)
    sku_label_text = translator.get_spec_label("SKU", language)
    draw.text((margin, footer_content_y), f"{sku_label_text}: {item_data.get('SKU', 'N/A')}", font=sku_font,
              fill=text_color, anchor='lm')
    price_font, strikethrough_font = get_font(PRIMARY_FONT_BOLD_PATH, 75, FALLBACK_FONT_EN_BOLD), get_font(
        PRIMARY_FONT_PATH, 60, FALLBACK_FONT_EN)
    sale_price, regular_price = item_data.get('Sale price', '').strip(), item_data.get('Regular price', '').strip()
    price_x = width_px - margin
    if sale_price and float(sale_price.replace(',', '.')) > 0:
        draw.text((price_x, footer_content_y), f"₾{sale_price}", font=price_font, fill=price_color, anchor='rm')
        orig_text, sale_text = f"₾{regular_price}", f"₾{sale_price}"
        orig_bbox, sale_bbox = strikethrough_font.getbbox(orig_text), price_font.getbbox(sale_text)
        orig_x = price_x - (sale_bbox[2] - sale_bbox[0]) - 20
        draw.text((orig_x, footer_content_y), orig_text, font=strikethrough_font, fill=strikethrough_color, anchor='rm')
        draw.line([(orig_x - (orig_bbox[2] - orig_bbox[0]), footer_content_y), (orig_x, footer_content_y)],
                  fill=strikethrough_color, width=3)
    elif regular_price:
        draw.text((price_x, footer_content_y), f"₾{regular_price}", font=price_font, fill=price_color, anchor='rm')
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=5)
    return img
