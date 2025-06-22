# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURATION ---
DPI = 300
LOGO_PATH = 'logo.png'
# IMPORTANT: You now need two font files: Regular and Bold.
# Place them in the 'fonts' directory.
PRIMARY_FONT_PATH = 'fonts/NotoSansGeorgian-Regular.ttf'
PRIMARY_FONT_BOLD_PATH = 'fonts/NotoSansGeorgian-Bold.ttf'
FALLBACK_FONT_EN = "arial.ttf"
FALLBACK_FONT_EN_BOLD = "arialbd.ttf"  # Arial Bold


# --- FONT SETUP ---
def get_font(font_path, size, fallback_path=None):
    """Safely load a font from the specified path."""
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Warning: Font at '{font_path}' not found. Trying fallback.")
        if fallback_path:
            try:
                return ImageFont.truetype(fallback_path, size)
            except IOError:
                print(f"FATAL: Fallback font '{fallback_path}' also not found.")
        return ImageFont.load_default()


def cm_to_pixels(cm, dpi=DPI):
    """Converts centimeters to pixels at a given DPI."""
    return int(cm / 2.54 * dpi)


def create_price_tag(item_data, size_config):
    """
    Generates a single price tag image in English.
    """
    width_cm, height_cm = size_config['dims']
    width_px = cm_to_pixels(width_cm)
    height_px = cm_to_pixels(height_cm)

    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)

    # --- Layout Proportions ---
    margin = 0.05 * width_px
    content_width = width_px - (2 * margin)

    # REVISED: Further reduced top section heights to give more room to specs.
    logo_area_height = 0.15 * height_px
    title_area_height = 0.10 * height_px
    footer_area_height = 0.12 * height_px

    logo_area_top = margin
    title_area_top = logo_area_top + logo_area_height
    specs_area_top = title_area_top + title_area_height

    footer_area_bottom = height_px - margin
    footer_area_top = footer_area_bottom - footer_area_height

    specs_area_bottom = footer_area_top - (0.03 * height_px)
    specs_area_height = specs_area_bottom - specs_area_top

    # --- 1. Draw Logo ---
    try:
        with Image.open(LOGO_PATH) as logo:
            logo = logo.convert("RGBA")
            logo.thumbnail((int(content_width * 0.8), int(logo_area_height * 0.9)), Image.Resampling.LANCZOS)
            logo_x = int((width_px - logo.width) / 2)
            logo_y = int(logo_area_top + (logo_area_height - logo.height) / 2)
            img.paste(logo, (logo_x, logo_y), logo)
    except FileNotFoundError:
        font_placeholder = get_font(PRIMARY_FONT_PATH, 40, FALLBACK_FONT_EN)
        draw.text((width_px / 2, logo_area_top + logo_area_height / 2), "Your Logo Here", font=font_placeholder,
                  fill='gray', anchor='mm')

    # --- 2. Draw Item Name ---
    title_font = get_font(PRIMARY_FONT_BOLD_PATH, 50, FALLBACK_FONT_EN_BOLD)
    item_name = item_data.get('Name', 'N/A')
    draw.text((width_px / 2, title_area_top + title_area_height / 2), item_name, font=title_font, fill='black',
              anchor='mm', align='center')

    # --- Separator Line 1 ---
    line_y1 = specs_area_top - (0.01 * height_px)
    draw.line([(margin, line_y1), (width_px - margin, line_y1)], fill='black', width=3)

    # --- 3. Draw Specifications (with mixed bold/regular text) ---
    spec_font_regular = get_font(PRIMARY_FONT_PATH, 32, FALLBACK_FONT_EN)
    spec_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, 32, FALLBACK_FONT_EN_BOLD)
    bullet = "• "

    # REVISED: The increased specs_area_height results in a larger line_height for more spacing.
    line_height = (specs_area_height / size_config['specs']) if size_config['specs'] > 0 else 0

    start_y = specs_area_top
    for spec in item_data.get('specs', []):
        if start_y + line_height >= specs_area_bottom:
            continue

        current_y = start_y + line_height / 2
        start_x = margin + 20

        # Draw bullet first, in regular font
        draw.text((start_x, current_y), bullet, font=spec_font_regular, fill='black', anchor='lm')
        bullet_bbox = draw.textbbox((0, 0), bullet, font=spec_font_regular)
        current_x = start_x + (bullet_bbox[2] - bullet_bbox[0])

        if ':' in spec:
            parts = spec.split(':', 1)
            label = parts[0] + ':'
            value = ' ' + parts[1].strip()

            # Draw bold label
            draw.text((current_x, current_y), label, font=spec_font_bold, fill='black', anchor='lm')
            label_bbox = draw.textbbox((0, 0), label, font=spec_font_bold)
            current_x += (label_bbox[2] - label_bbox[0])

            # Draw regular value
            draw.text((current_x, current_y), value, font=spec_font_regular, fill='black', anchor='lm')
        else:
            # If no colon, draw the whole spec in regular font
            draw.text((current_x, current_y), spec, font=spec_font_regular, fill='black', anchor='lm')

        start_y += line_height

    # --- Separator Line 2 ---
    line_y2 = footer_area_top
    draw.line([(margin, line_y2), (width_px - margin, line_y2)], fill='black', width=3)

    # --- 4. Draw Footer (SKU and Price) ---
    footer_content_y = footer_area_top + (footer_area_height / 2)

    # UPDATED: Using the bold font for the SKU.
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, 38, FALLBACK_FONT_EN_BOLD)
    sku_text = f"SKU: {item_data.get('SKU', 'N/A')}"
    draw.text((margin, footer_content_y), sku_text, font=sku_font, fill='black', anchor='lm')

    # --- Price Logic ---
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, 60, FALLBACK_FONT_EN_BOLD)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, 40, FALLBACK_FONT_EN)

    regular_price_str = item_data.get('Regular price', '').strip()
    sale_price_str = item_data.get('Sale price', '').strip()
    price_x = width_px - margin
    main_price_color = '#D32F2F'

    if sale_price_str and float(sale_price_str.replace(',', '.')) > 0:
        main_price_text = f"₾{sale_price_str}"
        draw.text((price_x, footer_content_y), main_price_text, font=price_font, fill=main_price_color, anchor='rm')

        original_price_text = f"₾{regular_price_str}"
        orig_bbox = draw.textbbox((0, 0), original_price_text, font=strikethrough_font)
        orig_text_width = orig_bbox[2] - orig_bbox[0]

        sale_bbox = draw.textbbox((0, 0), main_price_text, font=price_font)
        sale_text_width = sale_bbox[2] - sale_bbox[0]
        orig_price_x = price_x - sale_text_width - 20

        draw.text((orig_price_x, footer_content_y), original_price_text, font=strikethrough_font, fill='black',
                  anchor='rm')

        draw.line([(orig_price_x - orig_text_width, footer_content_y), (orig_price_x, footer_content_y)], fill='black',
                  width=3)

    elif regular_price_str:
        main_price_text = f"₾{regular_price_str}"
        draw.text((price_x, footer_content_y), main_price_text, font=price_font, fill=main_price_color, anchor='rm')

    # --- Draw border for easier cutting ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=5)

    return img
