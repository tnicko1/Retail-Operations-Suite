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


# --- HELPER FUNCTIONS ---
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


def wrap_text(text, font, max_width):
    """
    Wraps text to fit a specified pixel width without breaking words.
    Returns a list of lines.
    """
    lines = []
    # If the text is empty or None, return an empty list
    if not text:
        return []

    words = text.split()
    if not words:
        return []

    current_line = words[0]
    for word in words[1:]:
        # Check the width of the line if the new word is added
        if font.getlength(current_line + " " + word) <= max_width:
            current_line += " " + word
        else:
            # The new word doesn't fit, so finalize the current line
            lines.append(current_line)
            # Start a new line with the current word
            current_line = word

    # Append the last line
    lines.append(current_line)
    return lines


def _create_accessory_tag(item_data, width_px, height_px):
    """
    Creates a special, minimalist price tag for small accessories (6x3.5cm).
    This function contains a completely separate design logic.
    """
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)
    text_color = "black"

    # --- Fonts for the small tag ---
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, 50, FALLBACK_FONT_EN_BOLD)
    name_font = get_font(PRIMARY_FONT_PATH, 55, FALLBACK_FONT_EN)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, 65, FALLBACK_FONT_EN_BOLD)

    # --- Layout proportions ---
    margin = 0.06 * width_px
    top_area_height = 0.22 * height_px
    bottom_area_height = 0.28 * height_px

    # --- Draw Separators ---
    top_sep_y = top_area_height
    draw.line([(margin, top_sep_y), (width_px - margin, top_sep_y)], fill=text_color, width=2)
    bottom_sep_y = height_px - bottom_area_height
    draw.line([(margin, bottom_sep_y), (width_px - margin, bottom_sep_y)], fill=text_color, width=2)

    # --- Draw Content ---
    # 1. SKU (Top area)
    sku_text = item_data.get('SKU', 'N/A')
    draw.text((width_px / 2, top_sep_y / 2), sku_text, font=sku_font, fill=text_color, anchor="mm")

    # 2. Name (Middle area - with text wrapping)
    name_text = item_data.get('Name', 'N/A')
    name_area_width = width_px - (2 * margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    # Calculate line height and starting position for centered block
    _, top, _, bottom = name_font.getbbox("Ag")  # Get ascent/descent for line height
    line_height = bottom - top
    total_text_height = len(wrapped_lines) * line_height
    middle_area_height = bottom_sep_y - top_sep_y
    start_y = top_sep_y + (middle_area_height - total_text_height) / 2

    # Draw each line of the wrapped text
    for i, line in enumerate(wrapped_lines):
        y_pos = start_y + (i * line_height)
        draw.text((width_px / 2, y_pos), line, font=name_font, fill=text_color, anchor="ma", align='center')

    # 3. Price (Bottom area)
    price_y = bottom_sep_y + (height_px - bottom_sep_y) / 2
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()

    display_price = ""
    if sale_price and float(sale_price.replace(',', '.')) > 0:
        display_price = sale_price
    elif regular_price:
        display_price = regular_price

    if display_price:
        price_text = f"₾{display_price}"
        draw.text((width_px / 2, price_y), price_text, font=price_font, fill=text_color, anchor="mm")

    # --- Final Border ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=3)
    return img


def create_price_tag(item_data, size_config, theme, language='en'):
    """
    Main function to create a price tag. It acts as a router, calling the appropriate
    drawing function based on the selected paper size.
    """
    width_cm, height_cm = size_config['dims']
    width_px, height_px = cm_to_pixels(width_cm), cm_to_pixels(height_cm)

    # --- ROUTER: Check for special accessory size ---
    if (width_cm, height_cm) == (6, 3.5):
        return _create_accessory_tag(item_data, width_px, height_px)

    # --- DEFAULT LOGIC: For all other standard sizes ---
    img = Image.new('RGB', (width_px, height_px), 'white')
    translator = Translator()

    # --- Theme Setup ---
    text_color = theme.get("text_color", "black")
    price_color = theme.get('price_color', '#D32F2F')
    strikethrough_color = theme.get("strikethrough_color", "black")
    logo_to_use = theme.get("logo_path_ka", "assets/logo-geo.png") if language == 'ka' else theme.get("logo_path",
                                                                                                      "assets/logo.png")
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

    part_num_font = get_font(PRIMARY_FONT_PATH, 32, FALLBACK_FONT_EN)
    part_number = item_data.get('part_number', '')
    if part_number:
        pn_text = f"P/N: {part_number}"
        pn_y = logo_area_top + (logo_area_height / 2)
        draw.text((width_px - margin, pn_y), pn_text, font=part_num_font, fill=text_color, anchor="rm")

    title_font = get_font(PRIMARY_FONT_BOLD_PATH, 60, FALLBACK_FONT_EN_BOLD)

    # Title with wrapping
    title_text = item_data.get('Name', 'N/A')
    title_area_width = width_px - (2 * margin)
    wrapped_title_lines = wrap_text(title_text, title_font, title_area_width)

    _, top, _, bottom = title_font.getbbox("Ag")
    line_height = bottom - top + 5  # Add 5px spacing between lines
    total_text_height = len(wrapped_title_lines) * line_height
    start_y = title_area_top + (title_area_height - total_text_height) / 2

    for i, line in enumerate(wrapped_title_lines):
        y_pos = start_y + (i * line_height)
        draw.text((width_px / 2, y_pos), line, font=title_font, fill=text_color, anchor='ma', align='center')

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
    footer_center_y = footer_area_top + (footer_area_height / 2)

    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, 60, FALLBACK_FONT_EN_BOLD)
    sku_label_text = translator.get_spec_label("SKU", language)
    sku_full_text = f"{sku_label_text}: {item_data.get('SKU', 'N/A')}"
    draw.text((margin, footer_center_y), sku_full_text, font=sku_font, fill=text_color, anchor="lm")

    price_font, strikethrough_font = get_font(PRIMARY_FONT_BOLD_PATH, 75, FALLBACK_FONT_EN_BOLD), get_font(
        PRIMARY_FONT_PATH, 60, FALLBACK_FONT_EN)
    sale_price, regular_price = item_data.get('Sale price', '').strip(), item_data.get('Regular price', '').strip()
    price_x = width_px - margin
    price_y = footer_center_y

    if sale_price and float(sale_price.replace(',', '.')) > 0:
        draw.text((price_x, price_y), f"₾{sale_price}", font=price_font, fill=price_color, anchor='rm')
        orig_text = f"₾{regular_price}"
        sale_text = f"₾{sale_price}"
        sale_bbox = price_font.getbbox(sale_text)
        orig_x = price_x - (sale_bbox[2] - sale_bbox[0]) - 20
        draw.text((orig_x, price_y), orig_text, font=strikethrough_font, fill=strikethrough_color, anchor='rm')
        drawn_orig_bbox = draw.textbbox((orig_x, price_y), orig_text, font=strikethrough_font, anchor='rm')
        draw.line([(drawn_orig_bbox[0], price_y), (drawn_orig_bbox[2], price_y)], fill=strikethrough_color, width=3)
    elif regular_price:
        draw.text((price_x, price_y), f"₾{regular_price}", font=price_font, fill=price_color, anchor='rm')

    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=5)
    return img
