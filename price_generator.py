# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os
import random
import math
from translations import Translator

# --- CONFIGURATION ---
DPI = 300
PRIMARY_FONT_PATH = 'fonts/NotoSansGeorgian-Regular.ttf'
PRIMARY_FONT_BOLD_PATH = 'fonts/NotoSansGeorgian-Bold.ttf'
FALLBACK_FONT_EN = "arial.ttf"
FALLBACK_FONT_EN_BOLD = "arialbd.ttf"

# --- BASE FONT SIZES (for a 14.4x8cm tag) ---
BASE_WIDTH_CM = 14.4
BASE_HEIGHT_CM = 8.0
BASE_AREA = BASE_WIDTH_CM * BASE_HEIGHT_CM
BASE_TITLE_FONT_SIZE = 60
BASE_SPEC_FONT_SIZE = 42
BASE_FOOTER_SKU_FONT_SIZE = 60
BASE_FOOTER_PRICE_FONT_SIZE = 75
BASE_STRIKETHROUGH_FONT_SIZE = 60
BASE_PN_FONT_SIZE = 32

# --- BASE FONT SIZES for ACCESSORY TAG (6x3.5cm) ---
BASE_ACC_WIDTH_CM = 6.0
BASE_ACC_HEIGHT_CM = 3.5
BASE_ACC_AREA = BASE_ACC_WIDTH_CM * BASE_ACC_HEIGHT_CM
BASE_ACC_SKU_FONT_SIZE = 50
BASE_ACC_NAME_FONT_SIZE = 55
BASE_ACC_PRICE_FONT_SIZE = 65


# --- HELPER FUNCTIONS ---
def get_font(font_path, size, fallback_path=None):
    try:
        return ImageFont.truetype(font_path, int(size))
    except IOError:
        if fallback_path:
            try:
                return ImageFont.truetype(fallback_path, int(size))
            except IOError:
                return ImageFont.load_default()
    return ImageFont.load_default()


def cm_to_pixels(cm, dpi=DPI):
    return int(cm / 2.54 * dpi)


def wrap_text(text, font, max_width):
    lines = []
    if not text:
        return []
    words = text.split()
    if not words:
        return []
    current_line = words[0]
    for word in words[1:]:
        if font.getbbox(current_line + " " + word)[2] <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def _create_accessory_tag(item_data, width_px, height_px, width_cm, height_cm):
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)
    text_color = "black"

    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_ACC_AREA)

    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_SKU_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)
    name_font = get_font(PRIMARY_FONT_PATH, BASE_ACC_NAME_FONT_SIZE * scale_factor, FALLBACK_FONT_EN)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_PRICE_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)

    margin = 0.06 * width_px
    top_area_height = 0.22 * height_px
    bottom_area_height = 0.28 * height_px
    border_width = max(2, int(3 * scale_factor))

    top_sep_y = top_area_height
    draw.line([(margin, top_sep_y), (width_px - margin, top_sep_y)], fill=text_color,
              width=max(1, int(2 * scale_factor)))
    bottom_sep_y = height_px - bottom_area_height
    draw.line([(margin, bottom_sep_y), (width_px - margin, bottom_sep_y)], fill=text_color,
              width=max(1, int(2 * scale_factor)))

    sku_text = item_data.get('SKU', 'N/A')
    draw.text((width_px / 2, top_sep_y / 2), sku_text, font=sku_font, fill=text_color, anchor="mm")

    name_text = item_data.get('Name', 'N/A')
    name_area_width = width_px - (2 * margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    bbox = name_font.getbbox("Ag")
    line_height = bbox[3] - bbox[1]
    total_text_height = len(wrapped_lines) * line_height
    middle_area_height = bottom_sep_y - top_sep_y
    start_y = top_sep_y + (middle_area_height - total_text_height) / 2

    for i, line in enumerate(wrapped_lines):
        y_pos = start_y + (i * line_height)
        draw.text((width_px / 2, y_pos), line, font=name_font, fill=text_color, anchor="ma", align='center')

    price_y = bottom_sep_y + (height_px - bottom_sep_y) / 2
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()

    display_price = ""
    try:
        if sale_price and float(sale_price.replace(',', '.')) > 0:
            display_price = sale_price
        elif regular_price:
            display_price = regular_price
    except (ValueError, TypeError):
        display_price = regular_price

    if display_price:
        price_text = f"₾{display_price}"
        draw.text((width_px / 2, price_y), price_text, font=price_font, fill=text_color, anchor="mm")

    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=border_width)
    return img


def create_price_tag(item_data, size_config, theme, language='en'):
    width_cm, height_cm = size_config['dims']
    width_px, height_px = cm_to_pixels(width_cm), cm_to_pixels(height_cm)

    if size_config.get('is_accessory_style', False):
        return _create_accessory_tag(item_data, width_px, height_px, width_cm, height_cm)

    img = Image.new('RGB', (width_px, height_px), 'white')
    translator = Translator()

    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    title_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_TITLE_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)
    spec_font_regular = get_font(PRIMARY_FONT_PATH, BASE_SPEC_FONT_SIZE * scale_factor, FALLBACK_FONT_EN)
    spec_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, BASE_SPEC_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_FOOTER_SKU_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_FOOTER_PRICE_FONT_SIZE * scale_factor, FALLBACK_FONT_EN_BOLD)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, BASE_STRIKETHROUGH_FONT_SIZE * scale_factor, FALLBACK_FONT_EN)
    part_num_font = get_font(PRIMARY_FONT_PATH, BASE_PN_FONT_SIZE * scale_factor, FALLBACK_FONT_EN)

    border_width = max(2, int(5 * scale_factor))
    line_width = max(1, int(3 * scale_factor))

    text_color = theme.get("text_color", "black")
    price_color = theme.get('price_color', '#D32F2F')
    strikethrough_color = theme.get("strikethrough_color", "black")
    logo_to_use = theme.get("logo_path_ka", "assets/logo-geo.png") if language == 'ka' else theme.get("logo_path",
                                                                                                      "assets/logo.png")
    logo_scale = theme.get("logo_scale_factor", 0.9)
    bullet_image_path = theme.get("bullet_image_path")

    if theme.get("background_snow"):
        snow_draw = ImageDraw.Draw(img)
        for _ in range(70):
            x, y = random.randint(0, width_px), random.randint(0, height_px)
            radius = random.randint(int(10 * scale_factor), int(30 * scale_factor))
            snow_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(235, 245, 255, 50))

    draw = ImageDraw.Draw(img)

    margin = 0.05 * width_px

    LOGO_AREA_HEIGHT_RATIO = 0.12
    TITLE_TOP_PADDING = -0.06 * height_px
    TITLE_SEPARATOR_PADDING = 0.07 * height_px
    SEPARATOR_SPECS_PADDING = 0.02 * height_px

    y_cursor = 0.0

    logo_area_height = LOGO_AREA_HEIGHT_RATIO * height_px
    y_cursor += logo_area_height
    y_cursor += TITLE_TOP_PADDING

    title_text = item_data.get('Name', 'N/A')
    title_area_width = width_px - (2 * margin)
    wrapped_title_lines = wrap_text(title_text, title_font, title_area_width)

    if wrapped_title_lines:
        ascent, descent = title_font.getmetrics()
        line_height = ascent + descent
        line_spacing = int(8 * scale_factor)
        for line in wrapped_title_lines:
            draw.text((width_px / 2, y_cursor + ascent), line, font=title_font, fill=text_color, anchor='ma',
                      align='center')
            y_cursor += line_height + line_spacing
        y_cursor -= line_spacing

    y_cursor += TITLE_SEPARATOR_PADDING
    draw.line([(margin, y_cursor), (width_px - margin, y_cursor)], fill=text_color, width=line_width)

    y_cursor += SEPARATOR_SPECS_PADDING
    specs_area_top = y_cursor
    footer_area_height = 0.14 * height_px
    footer_area_top = height_px - (0.02 * height_px) - footer_area_height
    specs_area_height = footer_area_top - specs_area_top

    bullet_img = None
    if bullet_image_path and os.path.exists(bullet_image_path):
        try:
            bullet_img = Image.open(bullet_image_path).convert("RGBA")
        except:
            pass

    specs = item_data.get('specs', [])
    if specs and specs_area_height > 0:
        spec_ascent, spec_descent = spec_font_regular.getmetrics()
        spec_line_height = spec_ascent + spec_descent
        spec_line_spacing = int(4 * scale_factor)

        for spec in specs:
            if y_cursor + spec_line_height > footer_area_top:
                break

            bullet_x = int(margin + 20 * scale_factor)
            label_x = bullet_x

            if bullet_img:
                bullet_size = min(int(spec_line_height * 0.8), int(spec_font_regular.getbbox("M")[3]))
                if bullet_size > 0:
                    # *** BUG FIX: Ensure coordinates are integers for pasting ***
                    bullet_y = int(y_cursor + (spec_line_height - bullet_size) / 2)
                    bullet_resized = bullet_img.resize((bullet_size, bullet_size), Image.Resampling.LANCZOS)
                    img.paste(bullet_resized, (bullet_x, bullet_y), bullet_resized)
                    label_x += bullet_size + 15
            else:
                draw.text((bullet_x, y_cursor + spec_ascent), "•", font=spec_font_regular, fill=text_color, anchor='ls')
                label_x += int(spec_font_regular.getbbox("• ")[2])

            if ':' in spec:
                label, value = spec.split(':', 1)
                value = value.strip()
                translated_label = translator.get_spec_label(label.strip(), language)
                label_text = translated_label + ': '

                draw.text((label_x, y_cursor + spec_ascent), label_text, font=spec_font_bold, fill=text_color,
                          anchor='ls')
                value_x = label_x + spec_font_bold.getbbox(label_text)[2]

                remaining_width = width_px - value_x - margin
                wrapped_values = wrap_text(value, spec_font_regular, remaining_width)

                for i, line in enumerate(wrapped_values):
                    if y_cursor + spec_line_height > footer_area_top and i > 0:
                        line += '...'
                        draw.text((value_x, y_cursor + spec_ascent), line, font=spec_font_regular, fill=text_color,
                                  anchor='ls')
                        break

                    draw.text((value_x, y_cursor + spec_ascent), line, font=spec_font_regular, fill=text_color,
                              anchor='ls')
                    if i < len(wrapped_values) - 1:
                        y_cursor += spec_line_height + spec_line_spacing
            else:
                draw.text((label_x, y_cursor + spec_ascent), spec, font=spec_font_regular, fill=text_color, anchor='ls')

            y_cursor += spec_line_height + spec_line_spacing

    draw.line([(margin, footer_area_top), (width_px - margin, footer_area_top)], fill=text_color, width=line_width)
    footer_center_y = footer_area_top + (footer_area_height / 2)

    sku_label_text = translator.get_spec_label("SKU", language)
    sku_full_text = f"{sku_label_text}: {item_data.get('SKU', 'N/A')}"
    draw.text((margin, footer_center_y), sku_full_text, font=sku_font, fill=text_color, anchor="lm")

    sale_price, regular_price = item_data.get('Sale price', '').strip(), item_data.get('Regular price', '').strip()
    price_x = width_px - margin
    price_y = footer_center_y

    try:
        has_sale_price = sale_price and float(sale_price.replace(',', '.')) > 0
        has_regular_price = regular_price and float(regular_price.replace(',', '.')) > 0

        if has_sale_price:
            draw.text((price_x, price_y), f"₾{sale_price}", font=price_font, fill=price_color, anchor='rm')
            if has_regular_price:
                orig_text = f"₾{regular_price}"
                sale_text = f"₾{sale_price}"
                sale_bbox = draw.textbbox((price_x, price_y), sale_text, font=price_font, anchor='rm')
                orig_x = sale_bbox[0] - (20 * scale_factor)
                draw.text((orig_x, price_y), orig_text, font=strikethrough_font, fill=strikethrough_color, anchor='rm')
                drawn_orig_bbox = draw.textbbox((orig_x, price_y), orig_text, font=strikethrough_font, anchor='rm')
                draw.line([(drawn_orig_bbox[0], price_y), (drawn_orig_bbox[2], price_y)], fill=strikethrough_color,
                          width=line_width)
        elif has_regular_price:
            draw.text((price_x, price_y), f"₾{regular_price}", font=price_font, fill=price_color, anchor='rm')
    except (ValueError, TypeError):
        if regular_price:
            draw.text((price_x, price_y), f"₾{regular_price}", font=price_font, fill=price_color, anchor='rm')

    logo_top_y = 0.03 * height_px
    try:
        with Image.open(logo_to_use) as logo:
            logo_h = int((logo_area_height - (0.03 * height_px)) * logo_scale)
            logo_w = int(logo_h * (logo.width / logo.height))
            logo.thumbnail((logo_w, logo_h), Image.Resampling.LANCZOS)
            img.paste(logo,
                      (int((width_px - logo.width) / 2),
                       int(logo_top_y + (logo_area_height - logo_top_y - logo.height) / 2)),
                      logo)
    except FileNotFoundError:
        print(f"Warning: Logo file not found at '{logo_to_use}'")

    part_number = item_data.get('part_number', '')
    if part_number:
        pn_text = f"P/N: {part_number}"
        pn_y = logo_top_y + (logo_area_height - logo_top_y) / 2
        draw.text((width_px - margin, pn_y), pn_text, font=part_num_font, fill=text_color, anchor="rm")

    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=border_width)
    return img
