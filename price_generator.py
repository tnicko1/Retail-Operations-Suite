# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
from utils import resource_path
from PIL import Image, ImageDraw, ImageFont
import os
import random
import math
import re
import xml.etree.ElementTree as ET
from translations import Translator
from data_handler import get_default_layout_settings
import qrcode
import io
import urllib.request
from PyQt6.QtWidgets import QApplication
try:
    import cairosvg
    from io import BytesIO
except ImportError:
    cairosvg = None
    BytesIO = None
    print("Warning: cairosvg library not found. SVG support will be disabled.")

try:
    from assets.school_icons import create_laptop_icon, create_book_icon, create_ruler_icon
except ImportError:
    # This might happen during packaging, handle gracefully.
    create_laptop_icon = create_book_icon = create_ruler_icon = None


def load_image_path(path, color=None):
    """
    Loads an image from a path. If the path is for an SVG, it can optionally
    recolor it before converting it to a Pillow Image object.
    """
    if not path:
        return None

    if path.lower().endswith('.svg'):
        if not (cairosvg and BytesIO):
            return None

        try:
            if not color:
                # No color change, convert directly for performance
                png_bytes = cairosvg.svg2png(url=path)
            else:
                # Read SVG content
                with open(path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()

                # Parse the SVG XML
                root = ET.fromstring(svg_content.encode('utf-8'))

                # Register the SVG namespace to correctly find elements
                ET.register_namespace('', "http://www.w3.org/2000/svg")

                # Find all elements and change the fill color
                for element in root.iter():
                    if 'fill' in element.attrib and element.attrib['fill'] != 'none':
                        element.set('fill', color)

                modified_svg_bytes = ET.tostring(root, encoding='utf-8')
                png_bytes = cairosvg.svg2png(bytestring=modified_svg_bytes)

            return Image.open(BytesIO(png_bytes))
        except Exception as e:
            print(f"Error processing SVG {path}: {e}")
            return None
    else:
        # Handle raster images
        try:
            return Image.open(path)
        except FileNotFoundError:
            return None



# A mapping of keywords to icon filenames.
# The order is important: more specific keywords should come before more general ones.
SPEC_ICON_MAP = {
    'armchair.svg': ['materials', 'armrests'],
    'max-weight.svg': ['maximum weight', 'max weight'],
    'gauge.svg': ['print speed (iso)', 'print speed'],
    'printer-check.svg': ['print technology'],
    'ratio.svg': ['print resolution', 'resolution'],
    'scan-text.svg': ['scan type'],
    'smartphone-nfc.svg': ['mobile printing', 'mobile printing'],
    'recycle.svg': ['monthly duty cycle'],
    'chart-network.svg': ['topology'],
    'audio-waveform.svg': ['waveform type'],
    'zap.svg': ['output voltage', 'input voltage', 'output voltage'],
    'timer-reset.svg': ['output frequency', 'input frequency'],
    'usb.svg': ['output connection count', 'hdmi', 'usb', 'audio jack', 'ports'],
    'cable.svg': ['output connection type', 'input connection type'],
    'plug-zap.svg': ['input voltage range'],
    'battery-plus.svg': ['number of batteries'],
    'shield-user.svg': ['warranty'],
    'cpu.svg': ['cpu', 'processor', 'chipset', 'cores'],
    'circuit-board.svg': ['motherboard', 'socket', 'threads', 'cpu cooler'],
    'hard-drive.svg': ['drive bays', 'ssd', 'hdd', 'storage'],
    'fan.svg': ['cooler support', 'installed coolers', 'fan support'],
    'package-open.svg': ['fans included', 'included accessories', 'portability', 'portable design', 'what\'s in the box'],
    'memory-stick.svg': ['ram', 'memory'],
    'monitor.svg': ['screen', 'display', 'matrix', 'screen size'],
    'ruler-dimension-line.svg': ['dimensions', 'size'],
    'ruler-dimension-line-height.svg': ['height'],
    'monitor-cog.svg': ['panel type', 'aspect ratio', 'vesa mount compatibility', 'os', 'operating system', 'vesa'],
    'monitor-check.svg': ['flicker-free technology'],
    'refresh-ccw.svg': ['refresh rate'],
    'clock-arrow-down.svg': ['response time'],
    'contrast.svg': ['contrast', 'contrast ratio',],
    'shredder.svg': ['tearing prevention', 'gsync', 'freesync', 'vsync'],
    'sunset.svg': ['backlight'],
    'gpu.svg': ['graphics', 'gpu', 'vram'],
    'battery-charging.svg': ['battery', 'power', 'wattage', 'mah'],
    'webcam.svg': ['camera', 'webcam'],
    'keyboard.svg': ['keyboard', 'mouse'],
    'wifi.svg': ['wifi', 'nfc'],
    'origami.svg': ['design'],
    'weight.svg': ['max weight', 'weight'],
    'biceps-flexed.svg': ['armrest', 'armrests'],
    'anvil.svg': ['chair frame', 'frame material', 'material', 'material(s)'],
    'wheel.svg': ['number of wheels'],
    'paint-bucket.svg': ['color'],
    'printer.svg': ['print', 'scan', 'copy'],
    'info.svg': ['brand', 'model', 'barcode', 'part number'],
    'card-sd.svg': ['memory type', 'memory speed', 'max memory', 'memory card support', 'optical drive'],
    'sun.svg': ['brightness'],
    'eye-off.svg': ['viewing angle', "viewing angles"],
    'network.svg': ['interface', 'ethernet', 'network'],
    'pc-case.svg': ['formfactor', 'case', 'build material', 'ip_rating'],
    'archive-restore.svg': ['adf capacity'],
    'square-power.svg': ['power supply', 'efficiency', 'modular', 'capacity', 'psu included'],
    'volume-2.svg': ['audio', 'microphone'],
    'speaker.svg': ['audio output', 'audio input', 'speakers', 'speaker', 'speaker(s)'],
    'lock.svg': ['fingerprint sensor', 'face recognition'],
    'cog.svg': ['supported os', 'sim_support', 'smart features', 'tuner'],
    'file-cog.svg': ['functions', 'papersize', 'connector'],
    'projector.svg': ['optical zoom', 'lamp life', 'power consumption', 'mounting'],
    'shrink.svg': ['ultra-narrow bezels', 'form factor'],
    'gamepad-2.svg': ['game mode'],
    'app-window.svg': ['app support'],
    'bluetooth-connected.svg': ['bluetooth'],
    'settings-2.svg': ['mechanism'],
    'columns-3-cog.svg': ['backrest adjustment', 'adjustable arm rests', 'seat adjustment', 'height adjustment', 'tilt mechanism'],
    'swatch-book.svg': ['color depth', 'color support', 'bit depth', 'color gamut'],
}

# A pre-sorted list of all keywords for efficient matching.
SORTED_SPEC_KEYWORDS = None

def _get_sorted_spec_keywords():
    """
    Prepares and sorts all keywords from SPEC_ICON_MAP by length, descending.
    This ensures that more specific keywords are checked before less specific ones.
    The result is cached in a global variable for performance.
    """
    global SORTED_SPEC_KEYWORDS
    if SORTED_SPEC_KEYWORDS is None:
        all_keywords = []
        for icon, keywords in SPEC_ICON_MAP.items():
            for keyword in keywords:
                all_keywords.append((keyword, icon))
        # Sort by keyword length, descending
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        SORTED_SPEC_KEYWORDS = all_keywords
    return SORTED_SPEC_KEYWORDS

def get_icon_path_for_spec(spec_text):
    """Returns an icon path based on keywords in the specification text."""
    spec_lower = spec_text.lower()
    icon_dir = resource_path("assets/spec_icons")

    sorted_keywords = _get_sorted_spec_keywords()

    for keyword, icon in sorted_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', spec_lower):
            return os.path.join(icon_dir, icon)

    # Default icon if no specific match
    return os.path.join(icon_dir, 'info.svg')


def contains_georgian(text):
    """Checks if a string contains any Georgian characters."""
    # Georgian Unicode range: U+10A0 to U+10FF
    return any('\u10A0' <= char <= '\u10FF' for char in text)


DPI = 300
# --- FONT PATHS (assuming they are in a 'fonts' directory) ---
PRIMARY_FONT_PATH = resource_path("fonts/static/Montserrat-Regular.ttf")
PRIMARY_FONT_BOLD_PATH = resource_path("fonts/static/Montserrat-Bold.ttf")
GEL_FONT_PATH = resource_path("fonts/NotoSansGeorgian-Bold.ttf")
FALLBACK_FONT_GEORGIAN_REGULAR = resource_path("fonts/NotoSansGeorgian-Regular.ttf")
FALLBACK_FONT_GEORGIAN_BOLD = resource_path("fonts/NotoSansGeorgian-Bold.ttf")

# --- BASE DIMENSIONS AND FONT SIZES ---
# Used for scaling elements based on the tag's surface area.
# Base area for a standard tag (e.g., 8.8cm x 5.5cm)
BASE_AREA = 8.8 * 5.5
BASE_TITLE_FONT_SIZE = 48
BASE_SPEC_FONT_SIZE = 22
BASE_FOOTER_SKU_FONT_SIZE = 36
BASE_FOOTER_PRICE_FONT_SIZE = 44
BASE_STRIKETHROUGH_FONT_SIZE = 30
BASE_PN_FONT_SIZE = 16

# --- ACCESSORY TAG SPECIFIC ---
BASE_ACC_AREA = 5.0 * 3.0  # Base area for a smaller accessory tag
BASE_ACC_SKU_FONT_SIZE = 42
BASE_ACC_NAME_FONT_SIZE = 42
BASE_ACC_PRICE_FONT_SIZE = 45


def get_font(primary_path, size, is_bold=False):
    """
    Tries to load the primary font. If it fails, returns the default PIL font.
    """
    size = int(size)
    try:
        return ImageFont.truetype(primary_path, size)
    except (IOError, TypeError):
        # Final fallback to a default font
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


def _create_dynamic_background(width, height):
    """Creates a visually interesting, abstract background for price tags."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Subtle Gradient Background ---
    # Create a very light gray to white vertical gradient. Made it slightly darker.
    top_color = (230, 230, 230)
    bottom_color = (255, 255, 255)
    for y in range(height):
        # Interpolate color
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * (y / height))
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * (y / height))
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # --- Abstract Shapes and Lines ---
    # Use a list of soft, appealing colors with higher transparency
    colors = [
        (227, 76, 94, 45),   # Soft Red
        (76, 175, 80, 45),  # Muted Green
        (33, 150, 243, 45),  # Soft Blue
        (255, 193, 7, 40),   # Amber
        (156, 39, 176, 40)   # Purple
    ]

    # Draw a few more large, semi-transparent circles
    for _ in range(random.randint(3, 5)):
        color = random.choice(colors)
        radius = random.randint(int(width * 0.3), int(width * 0.7))
        x = random.randint(-int(radius * 0.5), int(width - radius * 0.5))
        y = random.randint(-int(radius * 0.5), int(height - radius * 0.5))
        draw.ellipse([x, y, x + radius * 2, y + radius * 2], fill=color)

    # Draw a few more, slightly thicker, sweeping lines
    for _ in range(random.randint(4, 6)):
        color = random.choice(colors)
        start_x = random.randint(0, width)
        start_y = random.randint(0, height)
        end_x = random.randint(0, width)
        end_y = random.randint(0, height)
        line_width = random.randint(2, 5)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=line_width)

    return img


def _draw_qr_code(img, url, position, size):
    """
    Generates and draws a QR code from a given URL.
    """
    if not url:
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").resize((size, size))
    img.paste(qr_img, position)


def _draw_sale_overlay(img, draw, width_px, height_px, scale_factor, theme, language='en', center_x=None, center_y=None, outer_radius=None, is_special=False):
    """
    Draws a 'SALE' starburst overlay with rotated text.
    Accepts optional center_x, center_y, and outer_radius for custom positioning and sizing.
    """
    translator = Translator()
    # If center coordinates are not provided, use the default top-right position.
    if center_x is None:
        center_x = width_px * 0.92
    if center_y is None:
        center_y = height_px * 0.15

    # Use provided radius or default, and calculate inner radius based on it
    if outer_radius is None:
        outer_radius = 80 * scale_factor
    inner_radius = outer_radius * 0.75  # Maintain ratio

    num_points = 12
    points = []
    for i in range(num_points * 2):
        radius = outer_radius if i % 2 == 0 else inner_radius
        angle = i * math.pi / num_points - (math.pi / 2)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))

    overlay_color = 'purple' if is_special else theme.get('price_color', '#D32F2F')
    draw.polygon(points, fill=overlay_color, outline="black", width=int(2 * scale_factor))

    # --- Rotated "SALE" text ---
    # Scale font size based on the star's radius for better fitting
    sale_font_size = outer_radius * 0.48
    
    # Choose font based on language
    if language == 'ka':
        sale_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, sale_font_size, is_bold=True)
    else:
        sale_font = get_font(PRIMARY_FONT_BOLD_PATH, sale_font_size, is_bold=True)
        
    sale_text = translator.get_spec_label("SPECIAL" if is_special else "SALE", language)
    rotation_angle = -25

    # Get text size
    text_bbox = sale_font.getbbox(sale_text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create a transparent image for the text
    text_img = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((-text_bbox[0], -text_bbox[1]), sale_text, font=sale_font, fill="white")

    # Rotate the text image
    rotated_text_img = text_img.rotate(rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)

    # Calculate position to paste the rotated text image so it's centered in the star
    paste_x = int(center_x - rotated_text_img.width / 2)
    paste_y = int(center_y - rotated_text_img.height / 2)

    # Paste onto the main image
    img.paste(rotated_text_img, (paste_x, paste_y), rotated_text_img)



def _create_accessory_tag(item_data, width_px, height_px, width_cm, height_cm, theme, background_cache=None):
    # --- BRANDING & THEME OVERRIDES ---
    bg_color = theme.get('accessory_background_color', 'white')
    accent_color = theme.get('accessory_accent_color', 'black')
    name_color = theme.get('accessory_name_color', 'black')
    price_color = theme.get('accessory_price_color', 'black')
    sku_color = theme.get('accessory_sku_color', 'black')
    logo_path = theme.get('accessory_logo_path')

    # --- BACKGROUND ---
    sku = item_data.get('SKU', 'N/A')
    if background_cache is not None and sku in background_cache:
        img = background_cache[sku].copy()
    else:
        if theme.get('background_grid'):
            img = _create_grid_background(width_px, height_px, color=theme.get('background_color', '#2E7D32'))
        else:
            img = Image.new('RGB', (width_px, height_px), bg_color)

        # --- ACCENTS ---
        if background_cache is not None:
            background_cache[sku] = img.copy()

    draw = ImageDraw.Draw(img, 'RGBA')

    # --- ACCENTS ---
    # Must be drawn after the main background is set

    # --- Special case for default 6x3.5cm tags ---
    is_default_theme = not any(theme.get(key) for key in ['background_grid', 'background_snow', 'draw_school_icons', 'accessory_logo_path'])
    if is_default_theme and width_cm == 6 and height_cm == 3.5:
        price_color = "black"



    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_ACC_AREA)

    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_SKU_FONT_SIZE * scale_factor, is_bold=True)
    name_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_NAME_FONT_SIZE * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_PRICE_FONT_SIZE * scale_factor, is_bold=True)
    gel_font = get_font(GEL_FONT_PATH, BASE_ACC_PRICE_FONT_SIZE * scale_factor, is_bold=True)

    margin = 0.06 * width_px
    top_area_height = 0.22 * height_px
    bottom_area_height = 0.28 * height_px
    border_width = max(2, int(3 * scale_factor))

    top_sep_y = top_area_height
    bottom_sep_y = height_px - bottom_area_height
    
    # --- BRAND LOGO ---
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo_max_h = top_area_height * 0.8
                logo.thumbnail((width_px, logo_max_h), Image.Resampling.LANCZOS)
                logo_x = int(margin)
                logo_y = int((top_area_height - logo.height) / 2)
                img.paste(logo, (logo_x, logo_y), logo)
        except FileNotFoundError:
            print(f"Warning: Brand logo not found at {logo_path}")


    # Conditionally draw separators
    if not theme.get('draw_school_icons'):
        line_width = max(1, int(2 * scale_factor))

        draw.line([(margin, top_sep_y), (width_px - margin, top_sep_y)], fill=accent_color,
                  width=line_width)
        draw.line([(margin, bottom_sep_y), (width_px - margin, bottom_sep_y)], fill=accent_color,
                  width=line_width)

    sku_text = item_data.get('SKU', 'N/A')
    sku_y = top_sep_y / 2

    # --- Sticky Note for SKU ---
    if theme.get('draw_school_icons'):
        note_padding = 15 * scale_factor
        sku_bbox = sku_font.getbbox(sku_text)
        sku_width = sku_bbox[2] - sku_bbox[0]
        sku_height = sku_bbox[3] - sku_bbox[1]
        
        note_rect_x1 = (width_px / 2) - (sku_width / 2) - note_padding
        note_rect_y1 = sku_y - (sku_height / 2) - note_padding
        note_rect_x2 = (width_px / 2) + (sku_width / 2) + note_padding
        note_rect_y2 = sku_y + (sku_height / 2) + note_padding

        rect_img = Image.new('RGBA', (width_px, height_px), (0,0,0,0))
        rect_draw = ImageDraw.Draw(rect_img)
        
        shadow_offset = int(8 * scale_factor)
        shadow_color = (0, 0, 0, 70)
        for i in range(shadow_offset, 0, -1):
            blur_alpha = int(shadow_color[3] * (1 - i / shadow_offset))
            rect_draw.rectangle(
                (note_rect_x1 + i, note_rect_y1 + i, note_rect_x2 + i, note_rect_y2 + i),
                fill=(shadow_color[0], shadow_color[1], shadow_color[2], blur_alpha)
            )

        top_color = (255, 255, 224)
        bottom_color = (255, 255, 200)
        for y in range(int(note_rect_y1), int(note_rect_y2)):
            ratio = (y - note_rect_y1) / (note_rect_y2 - note_rect_y1)
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            rect_draw.line([(note_rect_x1, y), (note_rect_x2, y)], fill=(r, g, b))

        corner_size = int(20 * scale_factor)
        corner_x = note_rect_x2
        corner_y = note_rect_y1
        rect_draw.polygon(
            [(corner_x, corner_y), (corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)],
            fill=bottom_color
        )
        rect_draw.polygon(
            [(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size), (corner_x - corner_size, corner_y + corner_size)],
            fill=(200, 200, 160)
        )
        rect_draw.line([(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)], fill=(255,255,255,150), width=1)
        
        rotated_rect = rect_img.rotate(-2, expand=False, resample=Image.Resampling.BICUBIC, center=(width_px/2, sku_y))
        img.paste(rotated_rect, (0,0), rotated_rect)
        # For school theme, text is always black on the note
        draw.text((width_px / 2, sku_y), sku_text, font=sku_font, fill="black", anchor="mm")
    else:
        draw.text((width_px / 2, sku_y), sku_text, font=sku_font, fill=sku_color, anchor="mm")


    name_text = item_data.get('Name', 'N/A')
    name_area_width = width_px - (2 * margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    bbox = name_font.getbbox("Ag")
    line_height = bbox[3] - bbox[1]
    total_text_height = len(wrapped_lines) * line_height
    
    max_line_width = 0
    for line in wrapped_lines:
        line_width = name_font.getbbox(line)[2]
        if line_width > max_line_width:
            max_line_width = line_width

    middle_area_height = bottom_sep_y - top_sep_y
    start_y = top_sep_y + (middle_area_height - total_text_height) / 2

    # --- Sticky Note for Name ---
    if theme.get('draw_school_icons'):
        note_padding = 15 * scale_factor
        note_rect_x1 = (width_px / 2) - (max_line_width / 2) - note_padding
        note_rect_y1 = start_y - note_padding
        note_rect_x2 = (width_px / 2) + (max_line_width / 2) + note_padding
        note_rect_y2 = start_y + total_text_height + note_padding
        
        rect_img = Image.new('RGBA', (width_px, height_px), (0,0,0,0))
        rect_draw = ImageDraw.Draw(rect_img)
        
        shadow_offset = int(8 * scale_factor)
        shadow_color = (0, 0, 0, 70)
        for i in range(shadow_offset, 0, -1):
            blur_alpha = int(shadow_color[3] * (1 - i / shadow_offset))
            rect_draw.rectangle(
                (note_rect_x1 + i, note_rect_y1 + i, note_rect_x2 + i, note_rect_y2 + i),
                fill=(shadow_color[0], shadow_color[1], shadow_color[2], blur_alpha)
            )

        top_color = (255, 255, 224)
        bottom_color = (255, 255, 200)
        for y in range(int(note_rect_y1), int(note_rect_y2)):
            ratio = (y - note_rect_y1) / (note_rect_y2 - note_rect_y1)
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            rect_draw.line([(note_rect_x1, y), (note_rect_x2, y)], fill=(r, g, b))

        corner_size = int(20 * scale_factor)
        corner_x = note_rect_x2
        corner_y = note_rect_y1
        rect_draw.polygon(
            [(corner_x, corner_y), (corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)],
            fill=bottom_color
        )
        rect_draw.polygon(
            [(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size), (corner_x - corner_size, corner_y + corner_size)],
            fill=(200, 200, 160)
        )
        rect_draw.line([(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)], fill=(255,255,255,150), width=1)

        rotated_rect = rect_img.rotate(2, expand=False, resample=Image.Resampling.BICUBIC, center=(width_px/2, start_y + total_text_height/2))
        img.paste(rotated_rect, (0,0), rotated_rect)
        
        for i, line in enumerate(wrapped_lines):
            y_pos = start_y + (i * line_height)
            # For school theme, text is always black on the note
            draw.text((width_px / 2, y_pos), line, font=name_font, fill="black", anchor="ma", align='center')
    else:
        for i, line in enumerate(wrapped_lines):
            y_pos = start_y + (i * line_height)
            draw.text((width_px / 2, y_pos), line, font=name_font, fill=name_color, anchor="ma", align='center')


    price_y = bottom_sep_y + (height_px - bottom_sep_y) / 2
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()

    display_price = ""
    is_on_sale = False
    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        is_on_sale = sale_val > 0 and sale_val != regular_val

        if is_on_sale:
            display_price = sale_price
        elif regular_val > 0:
            display_price = regular_price
        elif sale_val > 0: # Fallback if only sale price exists
             display_price = sale_price
    except (ValueError, TypeError):
        display_price = regular_price or sale_price
        is_on_sale = False

    if display_price:
        price_text = str(display_price)
        gel_text = "₾"
        price_bbox = price_font.getbbox(price_text)
        price_height = price_bbox[3] - price_bbox[1]
        price_width = price_bbox[2]
        gel_width = gel_font.getbbox(gel_text)[2]
        spacing = int(5 * scale_factor)
        
        # --- Back to School Theme Price Logic ---
        if theme.get('draw_school_icons'):
            if is_on_sale and regular_price:
                # --- ON SALE LOGIC ---
                strikethrough_font_size = int(BASE_ACC_PRICE_FONT_SIZE * 0.75 * scale_factor)
                strikethrough_font = get_font(PRIMARY_FONT_PATH, strikethrough_font_size)
                gel_font_strikethrough = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, strikethrough_font_size)

                old_price_text = str(regular_price)
                old_price_width = strikethrough_font.getbbox(old_price_text)[2]
                old_gel_width = gel_font_strikethrough.getbbox(gel_text)[2]
                old_total_width = old_gel_width + spacing + old_price_width

                new_price_width = gel_width + spacing + price_width
                
                price_spacing = int(15 * scale_factor)
                # Recalculate total width to remove the checkmark
                total_sale_width = old_total_width + price_spacing + new_price_width

                note_padding = 15 * scale_factor
                note_rect_x1 = (width_px / 2) - (total_sale_width / 2) - note_padding
                note_rect_y1 = price_y - (price_height / 2) - note_padding
                note_rect_x2 = (width_px / 2) + (total_sale_width / 2) + note_padding
                note_rect_y2 = price_y + (price_height / 2) + note_padding
                
                rect_img = Image.new('RGBA', (width_px, height_px), (0,0,0,0))
                rect_draw = ImageDraw.Draw(rect_img)
                shadow_offset = int(8 * scale_factor)
                shadow_color = (0, 0, 0, 70)
                # Create a blurred shadow by drawing multiple transparent rectangles
                for i in range(shadow_offset, 0, -1):
                    blur_alpha = int(shadow_color[3] * (1 - i / shadow_offset))
                    rect_draw.rectangle(
                        (note_rect_x1 + i, note_rect_y1 + i, note_rect_x2 + i, note_rect_y2 + i),
                        fill=(shadow_color[0], shadow_color[1], shadow_color[2], blur_alpha)
                    )

                # Note Body with Gradient
                top_color = (255, 255, 224)  # #FFFFE0
                bottom_color = (255, 255, 200)
                for y in range(int(note_rect_y1), int(note_rect_y2)):
                    ratio = (y - note_rect_y1) / (note_rect_y2 - note_rect_y1)
                    r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                    g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                    b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                    rect_draw.line([(note_rect_x1, y), (note_rect_x2, y)], fill=(r, g, b))

                # Folded Corner Effect
                corner_size = int(20 * scale_factor)
                corner_x = note_rect_x2
                corner_y = note_rect_y1

                # The part of the note that is "under" the fold
                rect_draw.polygon(
                    [(corner_x, corner_y), (corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)],
                    fill=bottom_color  # Darker part of the gradient
                )
                # The fold itself
                rect_draw.polygon(
                    [(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size), (corner_x - corner_size, corner_y + corner_size)],
                    fill=(200, 200, 160) # A darker shade for the fold
                )
                # A light line to simulate the edge
                rect_draw.line([(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)], fill=(255,255,255,150), width=1)
                
                rotated_rect = rect_img.rotate(-3, expand=False, resample=Image.Resampling.BICUBIC, center=(width_px/2, price_y))
                img.paste(rotated_rect, (0,0), rotated_rect)

                start_x = (width_px - total_sale_width) / 2
                
                draw.text((start_x, price_y), gel_text, font=gel_font_strikethrough, fill="black", anchor="lm")
                draw.text((start_x + old_gel_width + spacing, price_y), old_price_text, font=strikethrough_font, fill="black", anchor="lm")

                scribble_y_base = price_y
                amplitude = 4 * scale_factor
                frequency = (2 * math.pi * 2) / old_total_width
                scribble_points = []
                num_points = int(old_total_width * 2)
                if num_points > 0:
                    for i in range(num_points + 1):
                        x = start_x + (i / num_points) * old_total_width
                        y = scribble_y_base + amplitude * math.sin(frequency * (i / num_points) * old_total_width)
                        scribble_points.append((x, y))
                    draw.line(scribble_points, fill="#D32F2F", width=int(3 * scale_factor))

                new_price_x = start_x + old_total_width + price_spacing
                draw.text((new_price_x, price_y), gel_text, font=gel_font, fill="black", anchor="lm")
                draw.text((new_price_x + gel_width + spacing, price_y), price_text, font=price_font, fill="black", anchor="lm")
                
                # Checkmark completely removed.
            else:
                # --- NOT ON SALE LOGIC (FOR SCHOOL THEME) ---
                total_width = gel_width + spacing + price_width
                
                note_padding = 15 * scale_factor
                note_rect_x1 = (width_px / 2) - (total_width / 2) - note_padding
                note_rect_y1 = price_y - (price_height / 2) - note_padding
                note_rect_x2 = (width_px / 2) + (total_width / 2) + note_padding
                note_rect_y2 = price_y + (price_height / 2) + note_padding
                
                rect_img = Image.new('RGBA', (width_px, height_px), (0,0,0,0))
                rect_draw = ImageDraw.Draw(rect_img)
                shadow_offset = int(8 * scale_factor)
                shadow_color = (0, 0, 0, 70)
                # Create a blurred shadow by drawing multiple transparent rectangles
                for i in range(shadow_offset, 0, -1):
                    blur_alpha = int(shadow_color[3] * (1 - i / shadow_offset))
                    rect_draw.rectangle(
                        (note_rect_x1 + i, note_rect_y1 + i, note_rect_x2 + i, note_rect_y2 + i),
                        fill=(shadow_color[0], shadow_color[1], shadow_color[2], blur_alpha)
                    )

                # Note Body with Gradient
                top_color = (255, 255, 224)  # #FFFFE0
                bottom_color = (255, 255, 200)
                for y in range(int(note_rect_y1), int(note_rect_y2)):
                    ratio = (y - note_rect_y1) / (note_rect_y2 - note_rect_y1)
                    r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                    g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                    b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                    rect_draw.line([(note_rect_x1, y), (note_rect_x2, y)], fill=(r, g, b))

                # Folded Corner Effect
                corner_size = int(20 * scale_factor)
                corner_x = note_rect_x2
                corner_y = note_rect_y1

                # The part of the note that is "under" the fold
                rect_draw.polygon(
                    [(corner_x, corner_y), (corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)],
                    fill=bottom_color  # Darker part of the gradient
                )
                # The fold itself
                rect_draw.polygon(
                    [(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size), (corner_x - corner_size, corner_y + corner_size)],
                    fill=(200, 200, 160) # A darker shade for the fold
                )
                # A light line to simulate the edge
                rect_draw.line([(corner_x - corner_size, corner_y), (corner_x, corner_y + corner_size)], fill=(255,255,255,150), width=1)

                rotated_rect = rect_img.rotate(-3, expand=False, resample=Image.Resampling.BICUBIC, center=(width_px/2, price_y))
                img.paste(rotated_rect, (0,0), rotated_rect)

                start_x = (width_px - total_width) / 2
                # Draw the price in black
                draw.text((start_x, price_y), gel_text, font=gel_font, fill="black", anchor="lm")
                draw.text((start_x + gel_width + spacing, price_y), price_text, font=price_font, fill="black", anchor="lm")

        # --- Default Sale & Regular Price Logic ---
        else:
            price_color_override = None

            final_price_color = price_color_override or price_color
            total_width = gel_width + spacing + price_width
            start_x = (width_px - total_width) / 2

            # Draw the price text over the pill
            draw.text((start_x, price_y), gel_text, font=gel_font, fill=final_price_color, anchor="lm")
            draw.text((start_x + gel_width + spacing, price_y), price_text, font=price_font, fill=final_price_color, anchor="lm")

            # For default theme, previous price is not shown as per request.

    # --- THEME SPECIFIC ELEMENTS ---
    if theme.get('draw_school_icons'):
        _draw_school_theme_elements(img, draw, width_px, height_px, scale_factor)

    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=border_width)
    return img


def _create_keyboard_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """Creates a special price tag for keyboards with a unique design."""
    # Use the new dynamic background
    img = _create_dynamic_background(width_px, height_px)
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Colors and Fonts ---
    text_color = "#000000"
    price_color = theme.get('price_color', '#D32F2F')
    border_color = "#AAAAAA"

    # Base font sizes for this specific layout
    base_name_size = 110
    base_price_size = 120
    base_strikethrough_size = 80
    base_info_size = 45

    # Scaling fonts based on tag area
    current_area = width_cm * height_cm
    base_area = 17 * 5.7
    scale_factor = math.sqrt(current_area / base_area)

    name_font = get_font(PRIMARY_FONT_BOLD_PATH, base_name_size * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_size * scale_factor, is_bold=True)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, base_strikethrough_size * scale_factor)
    info_font = get_font(PRIMARY_FONT_PATH, base_info_size * scale_factor)
    info_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, base_info_size * scale_factor, is_bold=True)
    gel_font = get_font(GEL_FONT_PATH, base_price_size * scale_factor, is_bold=True)
    gel_font_strikethrough = get_font(GEL_FONT_PATH, base_strikethrough_size * scale_factor)

    # --- Layout ---
    margin = 0.03 * width_px
    right_panel_width = 0.35 * width_px
    left_panel_width = width_px - right_panel_width
    separator_x = left_panel_width

    # Draw a subtle vertical separator
    draw.line([(separator_x, margin), (separator_x, height_px - margin)], fill=border_color, width=2)

    # --- Prepare Specs and Clean Name ---
    key_specs_values = []
    all_specs = item_data.get('all_specs', [])
    spec_keywords = ['mechanical', 'switch', 'layout', 'type', 'technology', 'wired', 'wireless']
    for spec in all_specs:
        if any(keyword in spec.lower() for keyword in spec_keywords):
            if ':' in spec:
                label, value = spec.split(':', 1)
                key_specs_values.append(value.strip())
            else:
                key_specs_values.append(spec)

    # Remove duplicates while preserving order and take the first 4
    unique_specs = list(dict.fromkeys(key_specs_values))
    displayed_specs = unique_specs[:4]

    # Clean the name based on the displayed specs
    name_text = item_data.get('Name', 'N/A')
    display_name = name_text
    for spec_val in displayed_specs:
        # Split multi-word specs and clean each word from the name
        for word in spec_val.split():
            # Use word boundaries (\b) to avoid removing parts of words
            pattern = r'\b' + re.escape(word) + r'\b'
            display_name = re.sub(pattern, '', display_name, flags=re.IGNORECASE)

    # Clean up extra whitespace that may result from removal
    display_name = ' '.join(display_name.split())


    # --- Left Panel (Product Name) ---
    wrapped_lines = wrap_text(display_name, name_font, left_panel_width - (2 * margin))

    ascent, descent = name_font.getmetrics()
    line_height = ascent + descent
    total_text_height = len(wrapped_lines) * line_height
    y_start = (height_px - total_text_height) / 2

    left_panel_center_x = left_panel_width / 2
    for i, line in enumerate(wrapped_lines):
        y = y_start + i * line_height
        draw.text((left_panel_center_x, y), line, font=name_font, fill=text_color, anchor="ms", align='center')

    # --- Right Panel (Logo, Price, SKU, P/N) ---

    # --- Logo ---
    logo_to_use = theme.get("logo_path", "assets/logo.png")
    logo_area_height = height_px * 0.20
    right_panel_center_x = separator_x + (right_panel_width / 2)

    try:
        with Image.open(logo_to_use).convert("RGBA") as logo:
            logo.thumbnail((right_panel_width * 0.7, logo_area_height), Image.Resampling.LANCZOS)
            logo_x = int(right_panel_center_x - logo.width / 2)
            logo_y = int(margin)
            img.paste(logo, (logo_x, logo_y), logo)
    except FileNotFoundError:
        print(f"Warning: Logo file not found at '{logo_to_use}'")

    # --- Price ---
    price_y_start = logo_area_height + margin
    price_area_height = height_px - price_y_start - (height_px * 0.3)  # Avoid footer
    price_y = price_y_start + (price_area_height / 2)

    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()
    is_on_sale = False

    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        is_on_sale = sale_val > 0 and sale_val != regular_val

        # Helper to draw price with GEL symbol
        def draw_price(x, y, price_val, font, gel_font, color, anchor, strikethrough=False):
            price_str = str(price_val)
            gel_str = "₾"
            price_width = font.getbbox(price_str)[2]
            gel_width = gel_font.getbbox(gel_str)[2]
            spacing = int(5 * scale_factor)
            total_width = gel_width + spacing + price_width
            
            if anchor == "mm":
                start_x = x - total_width / 2
            else: # Add other anchors if needed
                start_x = x
            
            draw.text((start_x, y), gel_str, font=gel_font, fill=color, anchor="lm")
            draw.text((start_x + gel_width + spacing, y), price_str, font=font, fill=color, anchor="lm")
            
            if strikethrough:
                bbox = (start_x, y - font.getbbox("A")[3]/2, start_x + total_width, y + font.getbbox("A")[3]/2)
                draw.line([(bbox[0], (bbox[1] + bbox[3]) / 2), (bbox[2], (bbox[1] + bbox[3]) / 2)], fill=color, width=3)


        # Condition: sale price is valid, greater than zero, and different from regular price
        if is_on_sale:
            draw_price(right_panel_center_x, price_y, sale_price, price_font, gel_font, price_color, "mm")
            if regular_val > 0:
                strikethrough_y = price_y - (base_strikethrough_size * scale_factor * 1.2)
                draw_price(right_panel_center_x, strikethrough_y, regular_price, strikethrough_font, gel_font_strikethrough, text_color, "mm", strikethrough=True)

        elif regular_val > 0:
            draw_price(right_panel_center_x, price_y, regular_price, price_font, gel_font, price_color, "mm")
        elif sale_val > 0: # Fallback if only sale price exists
            draw_price(right_panel_center_x, price_y, sale_price, price_font, gel_font, price_color, "mm")

    except (ValueError, TypeError):
        # Fallback for non-numeric data - this part is tricky with the new helper, will keep it simple
        if regular_price:
             draw.text((right_panel_center_x, price_y), f"₾{regular_price}", font=price_font, fill=price_color, anchor="mm")
        elif sale_price:
            draw.text((right_panel_center_x, price_y), f"₾{sale_price}", font=price_font, fill=price_color, anchor="mm")

    # --- Footer Info (SKU, P/N) ---
    translator = Translator()
    info_y_start = height_px - margin
    info_line_height = base_info_size * scale_factor * 1.2

    sku_label_text = translator.get_spec_label("SKU", language) + ": "
    sku_value = item_data.get('SKU', 'N/A')
    sku_y = info_y_start - info_line_height

    sku_label_font = info_font_bold
    if contains_georgian(sku_label_text):
        sku_label_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, base_info_size * scale_factor, is_bold=True)

    # Draw value first to get its right edge
    value_bbox = draw.textbbox((width_px - margin, sku_y), sku_value, font=info_font, anchor="rs")
    draw.text((width_px - margin, sku_y), sku_value, font=info_font, fill=text_color, anchor="rs")
    
    # Draw label to the left of the value
    label_x = value_bbox[0] - 5
    draw.text((label_x, sku_y), sku_label_text, font=sku_label_font, fill=price_color, anchor="rs")

    part_number = item_data.get('part_number', '')
    if part_number:
        pn_label = "P/N: "
        pn_value = part_number
        pn_y = info_y_start
        draw.text((width_px - margin, pn_y), pn_value, font=info_font, fill=text_color, anchor="rs")
        pn_value_bbox = draw.textbbox((width_px - margin, pn_y), pn_value, font=info_font, anchor="rs")
        draw.text((pn_value_bbox[0] - 5, pn_y), pn_label, font=info_font_bold, fill=price_color, anchor="rs")

    # --- Optional Specs & Red Accent Line ---
    line_y = y_start + total_text_height + (margin / 2)
    # Use a straight line instead of a curve
    start_p = (margin, line_y)
    end_p = (separator_x - margin, line_y)
    draw.line([start_p, end_p], fill=price_color, width=int(3 * scale_factor))


    if displayed_specs:
        spec_text = " | ".join(displayed_specs)
        spec_font = get_font(PRIMARY_FONT_PATH, base_info_size * 0.9 * scale_factor)
        spec_y = line_y + margin + (10 * scale_factor)
        draw.text((left_panel_center_x, spec_y), spec_text, font=spec_font, fill=text_color, anchor="ms",
                  align='center')

    # --- Sale Overlay ---
    if is_on_sale or is_special:
        # For the keyboard layout, move the sale star to the footer area
        star_center_x = separator_x + (right_panel_width / 4)
        # Vertically center it on the SKU line for consistent placement
        star_center_y = sku_y
        _draw_sale_overlay(img, draw, width_px, height_px, scale_factor, theme, language,
                           center_x=star_center_x, center_y=star_center_y, is_special=is_special)

    # --- Final Border ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline=border_color, width=3)

    return img


def _draw_school_theme_elements(img, draw, width_px, height_px, scale_factor):
    """Draws the 'Back To School' theme icons on the tag."""
    if not all([create_laptop_icon, create_book_icon, create_ruler_icon]):
        print("Warning: School icon creation functions are not available.")
        return

    icon_size = int(90 * scale_factor) # Increased size
    padding = int(10 * scale_factor)

    # Create and rotate icons
    laptop_icon = create_laptop_icon((icon_size, icon_size)).rotate(15, expand=True, resample=Image.Resampling.BICUBIC)
    book_icon = create_book_icon((icon_size, icon_size)).rotate(-15, expand=True, resample=Image.Resampling.BICUBIC)
    ruler_icon = create_ruler_icon((icon_size, icon_size)).rotate(10, expand=True, resample=Image.Resampling.BICUBIC)

    # Top-left
    img.paste(laptop_icon, (padding, padding), laptop_icon)
    # Top-right
    img.paste(book_icon, (width_px - book_icon.width - padding, padding), book_icon)
    # Bottom-left
    img.paste(ruler_icon, (padding, height_px - ruler_icon.height - padding), ruler_icon)


def _create_grid_background(width, height, color="#2E7D32", line_color=(255, 255, 255, 160)):
    """Creates a green background with a white grid, like a blackboard."""
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    spacing = 60 # Increased spacing from 30 to 60
    # Draw vertical lines
    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=line_color, width=4)
    # Draw horizontal lines
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=line_color, width=4)
        
    return img


def _create_modern_brand_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """Creates a special price tag for brands with a modern, 3D design."""
    # --- Config ---
    bg_color = theme.get('bg_color', '#FFFFFF')
    text_color = theme.get('text_color', 'black')
    logo_path = theme.get('accessory_logo_path')
    brand_name = theme.get('brand_name', '')

    # --- Scaling ---
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    # --- Fonts ---
    base_name_font_size = 70
    base_price_font_size = 90
    base_sku_font_size = 65

    name_font = get_font(PRIMARY_FONT_BOLD_PATH, base_name_font_size * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_font_size * scale_factor, is_bold=True)
    gel_font = get_font(GEL_FONT_PATH, base_price_font_size * scale_factor, is_bold=True)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, base_sku_font_size * scale_factor, is_bold=True)

    # --- Background ---
    img = Image.new('RGB', (width_px, height_px), bg_color)
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Main Content Tile (3D Effect) ---
    margin = 0.05 * width_px
    radius = 25 * scale_factor
    shadow_offset = 12 * scale_factor
    shadow_color = (0, 0, 0, 60)

    tile_bbox = (margin, margin, width_px - margin, height_px - margin)

    # Draw shadow first
    draw.rounded_rectangle(
        [(tile_bbox[0] + shadow_offset, tile_bbox[1] + shadow_offset),
         (tile_bbox[2] + shadow_offset, tile_bbox[3] + shadow_offset)],
        radius=radius, fill=shadow_color
    )
    # Draw main tile
    draw.rounded_rectangle(tile_bbox, radius=radius, fill='white', outline=(230, 230, 230), width=2)

    # --- Content Layout ---
    content_margin = margin * 1.8

    # --- 1. Logo ---
    logo_area_height = height_px * 0.25
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo.thumbnail((width_px * 0.6, logo_area_height), Image.Resampling.LANCZOS)
                logo_x = int((width_px - logo.width) / 2)
                logo_y = int(content_margin)
                img.paste(logo, (logo_x, logo_y), logo)
                y_cursor = logo_y + logo.height
        except FileNotFoundError:
            print(f"Warning: Brand logo not found at {logo_path}")
            y_cursor = content_margin
    else:
        y_cursor = content_margin

    # --- 2. Item Name ---
    name_text_raw = item_data.get('Name', 'N/A')
    # Filter out the brand name
    if brand_name:
        name_text = re.sub(fr'\b{brand_name}\b', '', name_text_raw, flags=re.IGNORECASE).strip()
    else:
        name_text = name_text_raw
    name_text = ' '.join(name_text.split())  # Clean up extra spaces

    name_area_width = width_px - (2 * content_margin)

    # --- Font size adjustment loop ---
    current_name_font_size = base_name_font_size * scale_factor
    name_font = get_font(PRIMARY_FONT_BOLD_PATH, current_name_font_size, is_bold=True)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    while len(wrapped_lines) > 2 and current_name_font_size > 20:  # Set a minimum font size
        current_name_font_size -= 2  # Decrease font size
        name_font = get_font(PRIMARY_FONT_BOLD_PATH, current_name_font_size, is_bold=True)
        wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    # If it's still too long, truncate to 2 lines.
    if len(wrapped_lines) > 2:
        wrapped_lines = wrapped_lines[:2]


    ascent, descent = name_font.getmetrics()
    line_height = ascent + descent
    total_text_height = len(wrapped_lines) * line_height
    
    # Center the name block vertically between logo and footer
    footer_height = height_px * 0.25
    available_space = (height_px - footer_height) - y_cursor
    name_y_start = y_cursor + (available_space - total_text_height) / 2

    for i, line in enumerate(wrapped_lines):
        y = name_y_start + i * line_height
        draw.text((width_px / 2, y), line, font=name_font, fill=text_color, anchor="ma", align='center')

    # --- 3. Footer (SKU and Price) ---
    footer_y_start = height_px - margin - footer_height
    footer_center_y = footer_y_start + footer_height / 2

    # SKU on the left (bold, no "SKU:" prefix)
    sku_text = item_data.get('SKU', 'N/A')
    draw.text((content_margin, footer_center_y), sku_text, font=sku_font, fill=text_color, anchor="lm")

    # Price on the right (simplified logic)
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()
    display_price = ""
    
    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        
        if sale_val > 0:
            display_price = sale_price
        elif regular_val > 0:
            display_price = regular_price
            
    except (ValueError, TypeError):
        display_price = sale_price or regular_price

    if display_price:
        price_x = width_px - content_margin
        price_text = str(display_price)
        gel_text = "₾"
        price_width = price_font.getbbox(price_text)[2]
        gel_width = gel_font.getbbox(gel_text)[2]
        spacing = int(5 * scale_factor)
        draw.text((price_x, footer_center_y), price_text, font=price_font, fill=text_color, anchor="rm")
        draw.text((price_x - price_width - spacing, footer_center_y), gel_text, font=gel_font, fill=text_color, anchor="rm")

    # --- Final Border ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=max(2, int(5 * scale_factor)))

    return img


def _create_modern_brand_tag_large(item_data, width_px, height_px, width_cm, height_cm, theme, language, layout_settings, is_special=False, is_dual=False):
    """Creates a completely redesigned, modern, and visually pleasing price tag."""
    translator = Translator()
    # --- 1. Config, Scaling, and Fonts ---
    theme_bg_color = theme.get('bg_color')
    bg_color = theme_bg_color if theme_bg_color else '#F1F3F5'  # Use theme BG, fallback to light gray
    card_color = '#FFFFFF'
    text_color = '#212529'
    spec_text_color = '#495057'
    strikethrough_color = '#6C757D'
    price_color = theme.get('bg_color', '#D90429')  # Use theme BG color for price, fallback to Red
    brand_color = theme.get('accessory_accent_color', '#007BFF')
    line_color = theme.get('bg_color', brand_color)

    # Scaling based on area
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / (10 * 7))  # Base on a 10x7cm tag

    # Apply scaling from layout settings, with defaults
    name_font_size = 55 * scale_factor * layout_settings.get('title_scale', 1.0)
    spec_font_size = 24 * scale_factor * layout_settings.get('spec_scale', 1.0) # Significantly smaller
    price_font_size = 70 * scale_factor * layout_settings.get('price_scale', 1.0)
    strikethrough_price_font_size = 45 * scale_factor * layout_settings.get('price_scale', 1.0)
    footer_font_size = 26 * scale_factor * layout_settings.get('sku_scale', 1.0)

    name_font = get_font(PRIMARY_FONT_BOLD_PATH, name_font_size, is_bold=True)
    spec_font_regular = get_font(PRIMARY_FONT_PATH, spec_font_size)
    spec_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, spec_font_size, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, price_font_size, is_bold=True)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, strikethrough_price_font_size)
    gel_font = get_font(GEL_FONT_PATH, price_font_size, is_bold=True)
    gel_font_strikethrough = get_font(GEL_FONT_PATH, strikethrough_price_font_size)
    footer_font = get_font(PRIMARY_FONT_PATH, footer_font_size)

    # --- 2. Initial Setup ---
    img = Image.new('RGB', (width_px, height_px), bg_color)
    img = img.convert('RGBA')
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- 3. Main Content Card (with shadow) ---
    card_margin = int(width_px * 0.02) # Reduced margin
    card_radius = 20 * scale_factor
    shadow_offset = int(10 * scale_factor)
    shadow_color = (0, 0, 0, 50)

    card_box = (card_margin, card_margin, width_px - card_margin, height_px - card_margin)

    # Draw shadow
    shadow_box = (card_box[0] + shadow_offset, card_box[1] + shadow_offset, card_box[2] + shadow_offset, card_box[3] + shadow_offset)
    draw.rounded_rectangle(shadow_box, radius=card_radius, fill=shadow_color)

    # Draw main card
    draw.rounded_rectangle(card_box, radius=card_radius, fill=card_color)

    # --- 4. Header, Logo, and Accent Line ---
    content_padding = card_margin * 2
    header_height = height_px * 0.15

    # Draw Brand Logo (from theme) on the left
    brand_logo_path = theme.get('accessory_logo_path')
    if brand_logo_path:
        try:
            with Image.open(brand_logo_path).convert("RGBA") as logo:
                logo_h = header_height * 0.6
                logo.thumbnail((width_px * 0.4, logo_h), Image.Resampling.LANCZOS)
                logo_x = int(content_padding)
                logo_y = int(card_margin + (header_height - logo.height) / 2)
                
                tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
                tmp.paste(logo, (logo_x, logo_y))
                img = Image.alpha_composite(img, tmp)
                draw = ImageDraw.Draw(img, 'RGBA') # Recreate draw object
        except FileNotFoundError:
            print(f"Warning: Brand logo not found at {brand_logo_path}")

    # Draw Company Logo (general) on the right
    logo_to_use = resource_path("assets/logo-geo.png") if language == 'ka' else resource_path("assets/logo.png")
    try:
        with Image.open(logo_to_use).convert("RGBA") as logo:
            logo_h = header_height * 0.7
            logo.thumbnail((width_px * 0.5, logo_h), Image.Resampling.LANCZOS)
            logo_x = int((width_px - card_margin) - logo.width - (card_margin * 0.2))
            logo_y = int(card_margin + (header_height - logo.height) / 2)
            
            tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
            tmp.paste(logo, (logo_x, logo_y))
            img = Image.alpha_composite(img, tmp)
            draw = ImageDraw.Draw(img, 'RGBA') # Recreate draw object
    except FileNotFoundError:
        print(f"Warning: Main logo not found at {logo_to_use}")

    y_cursor = card_margin + header_height
    accent_line_y = y_cursor
    draw.line([(card_margin, accent_line_y), (width_px - card_margin, accent_line_y)], fill=line_color, width=int(4 * scale_factor))
    y_cursor += int(4 * scale_factor) + content_padding * 0.2 # Reduced space

    # --- 5. Product Name ---
    name_text_raw = item_data.get('Name', 'N/A')
    brand_name = theme.get('brand_name', '')
    if brand_name and name_text_raw.lower().startswith(brand_name.lower()):
        name_text = name_text_raw[len(brand_name):].strip()
    else:
        name_text = re.sub(fr'\b{brand_name}\b', '', name_text_raw, flags=re.IGNORECASE).strip()
    name_text = ' '.join(name_text.split())

    name_area_width = width_px - (2 * content_padding)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)
    ascent, descent = name_font.getmetrics()
    line_height = ascent + descent
    for line in wrapped_lines:
        draw.text((content_padding, y_cursor), line, font=name_font, fill=text_color, anchor="la")
        y_cursor += line_height
    y_cursor += content_padding * 0.2 # Reduced space

    # --- 6. Specifications (Two-Column Layout) ---
    spec_ascent, spec_descent = spec_font_regular.getmetrics()
    spec_line_height = spec_ascent + spec_descent
    spec_line_spacing = int(6 * scale_factor)
    icon_size = int(spec_font_size * 1.1)
    icon_padding = int(10 * scale_factor)
    
    all_specs = item_data.get('all_specs', [])
    warranty_spec = None
    other_specs = []
    temp_warranty_specs = []
    for spec in all_specs:
        if 'warranty' in spec.lower():
            temp_warranty_specs.append(spec)
        else:
            icon_path = get_icon_path_for_spec(spec)
            if 'info.svg' not in icon_path:
                other_specs.append(spec)
    
    if temp_warranty_specs:
        warranty_spec = temp_warranty_specs[0] # Use the first for the footer

    final_material_spec = None
    # Special handling for 14.8x8cm tag size to ensure 'Material Details' is the last spec
    if width_cm == 14.8 and height_cm == 8:
        material_spec_value = "See Description"  # Default value
        spec_to_remove = None

        # Find if a material-related spec already exists to preserve its value
        for spec in other_specs:
            if 'material' in spec.lower().split(':')[0]:
                if ':' in spec:
                    material_spec_value = spec.split(':', 1)[1].strip()
                spec_to_remove = spec
                break

        if spec_to_remove:
            other_specs.remove(spec_to_remove)

        final_material_spec = f"Material Details: {material_spec_value}"

    footer_height = height_px * 0.18
    max_y_for_specs = (height_px - card_margin) - footer_height
    
    # --- Column Layout Calculations ---
    mid_x = width_px / 2
    col_width = mid_x - content_padding - (card_margin / 2)

    # Helper to calculate spec height
    def get_real_spec_height(spec_text, column_width):
        icon_area_width = icon_size + icon_padding
        if ':' in spec_text:
            label, value = spec_text.split(':', 1)
            translated_label = translator.get_spec_label(label.strip(), language)
            label_text = translated_label + ': '
            label_font = spec_font_bold
            if contains_georgian(translated_label):
                label_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, spec_font_size, is_bold=True)
            label_width = label_font.getbbox(label_text)[2]
            remaining_width = column_width - icon_area_width - label_width
            wrapped_values = wrap_text(value.strip(), spec_font_regular, remaining_width)
            num_lines = max(1, len(wrapped_values))
            return num_lines * (spec_line_height + spec_line_spacing) - spec_line_spacing
        else:
            return spec_line_height

    # Reserve space for Material Details spec if applicable
    if final_material_spec:
        material_spec_height = get_real_spec_height(final_material_spec, col_width)
        max_y_for_specs -= material_spec_height

    # Distribute specs into two columns sequentially
    col1_specs, col2_specs = [], []
    col1_height, col2_height = 0, 0
    
    temp_specs = other_specs
    remaining_specs = []

    # Fill column 1 first
    for spec in temp_specs:
        h = get_real_spec_height(spec, col_width) + spec_line_spacing
        if y_cursor + col1_height + h < max_y_for_specs:
            col1_specs.append(spec)
            col1_height += h
        else:
            remaining_specs.append(spec)

    # Fill column 2 with the rest
    for spec in remaining_specs:
        h = get_real_spec_height(spec, col_width) + spec_line_spacing
        if y_cursor + col2_height + h < max_y_for_specs:
            col2_specs.append(spec)
            col2_height += h

    # Add the Material Details spec at the very end for the specific tag size
    if final_material_spec:
        col2_specs.append(final_material_spec)

    # --- Draw Specs in Two Columns ---
    spec_start_y = y_cursor

    def draw_spec_column(specs, start_x, column_width):
        nonlocal img, draw
        y_pos = spec_start_y
        for spec in specs:
            icon_x = int(start_x)
            icon_y = int(y_pos + (spec_line_height - icon_size) / 2)
            icon_path = get_icon_path_for_spec(spec)
            if any(icon_name in icon_path for icon_name in ['max-weight.svg', 'ruler-dimension-line-height.svg']):
                icon_img = load_image_path(icon_path)
            else:
                icon_img = load_image_path(icon_path, color=line_color)

            if icon_img:
                try:
                    icon_img.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
                    rgba_icon = icon_img.convert('RGBA')
                    tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    tmp.paste(rgba_icon, (icon_x, icon_y))
                    img = Image.alpha_composite(img, tmp)
                    draw = ImageDraw.Draw(img, 'RGBA')
                except Exception as e:
                    print(f"Could not process icon {icon_path}: {e}")

            label_x = icon_x + icon_size + icon_padding
            if ':' in spec:
                label, value = spec.split(':', 1)
                value = value.strip()
                translated_label = translator.get_spec_label(label.strip(), language)
                label_text = translated_label + ': '
                
                label_font = spec_font_bold
                if contains_georgian(translated_label):
                    label_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, spec_font_size, is_bold=True)
                
                draw.text((label_x, y_pos + spec_ascent), label_text, font=label_font, fill=spec_text_color, anchor='ls')
                value_x = label_x + label_font.getbbox(label_text)[2]
                
                remaining_width = (start_x + column_width) - value_x
                wrapped_values = wrap_text(value, spec_font_regular, remaining_width)
                
                current_line_y = y_pos
                for i, line in enumerate(wrapped_values):
                    draw.text((value_x, current_line_y + spec_ascent), line, font=spec_font_regular, fill=text_color, anchor='ls')
                    if i < len(wrapped_values) - 1:
                        current_line_y += spec_line_height + spec_line_spacing
                y_pos = current_line_y + spec_line_height + spec_line_spacing
            else:
                spec_font = spec_font_regular
                if contains_georgian(spec):
                    spec_font = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, spec_font_size)
                draw.text((label_x, y_pos + spec_ascent), spec, font=spec_font, fill=text_color, anchor='ls')
                y_pos += spec_line_height + spec_line_spacing
        return y_pos

    y1 = draw_spec_column(col1_specs, content_padding, col_width)
    y2 = draw_spec_column(col2_specs, mid_x, col_width)

    # Draw vertical separator if both columns have content
    if col1_specs and col2_specs:
        separator_x = mid_x - (card_margin / 2)
        max_y = max(y1, y2) - spec_line_spacing
        draw.line([(separator_x, spec_start_y), (separator_x, max_y)], fill='#DEE2E6', width=3)

    # --- 7. Footer ---
    footer_y_start = (height_px - card_margin) - footer_height
    footer_center_y = footer_y_start + footer_height / 2
    price_y_offset = -int(10 * scale_factor)
    price_y = footer_center_y + price_y_offset
    draw.line([(card_margin, footer_y_start), (width_px - card_margin, footer_y_start)], fill='#DEE2E6', width=3)

    # Price handling
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()
    is_on_sale = False
    if sale_price and regular_price:
        try:
            sale_val = float(sale_price.replace(',', '.'))
            regular_val = float(regular_price.replace(',', '.'))
            if sale_val > 0 and sale_val < regular_val:
                is_on_sale = True
        except ValueError:
            is_on_sale = False

    price_x = content_padding
    if is_on_sale:
        # Draw sale price (large, red)
        sale_price_text = str(sale_price)
        gel_text = "₾"
        gel_width = gel_font.getbbox(gel_text)[2]
        spacing = int(8 * scale_factor)
        draw.text((price_x, price_y), gel_text, font=gel_font, fill=price_color, anchor="lm")
        draw.text((price_x + gel_width + spacing, price_y), sale_price_text, font=price_font, fill=price_color, anchor="lm")
        sale_price_width = price_font.getbbox(sale_price_text)[2]
        
        # Draw old price (smaller, gray, strikethrough)
        old_price_x = price_x + gel_width + spacing + sale_price_width + (15 * scale_factor)
        old_price_text = str(regular_price)
        old_gel_width = gel_font_strikethrough.getbbox(gel_text)[2]
        draw.text((old_price_x, price_y), gel_text, font=gel_font_strikethrough, fill=strikethrough_color, anchor="lm")
        draw.text((old_price_x + old_gel_width + spacing, price_y), old_price_text, font=strikethrough_font, fill=strikethrough_color, anchor="lm")
        
        # Strikethrough line
        line_start_x = old_price_x
        line_end_x = old_price_x + old_gel_width + spacing + strikethrough_font.getbbox(old_price_text)[2]
        draw.line([(line_start_x, price_y), (line_end_x, price_y)], fill=strikethrough_color, width=int(3 * scale_factor))

    else:
        # Default price drawing
        display_price = sale_price or regular_price
        if display_price:
            price_text = str(display_price)
            gel_text = "₾"
            gel_width = gel_font.getbbox(gel_text)[2]
            spacing = int(8 * scale_factor)
            draw.text((price_x, price_y), gel_text, font=gel_font, fill=price_color, anchor="lm")
            draw.text((price_x + gel_width + spacing, price_y), price_text, font=price_font, fill=price_color, anchor="lm")

    # --- Warranty ---
    if warranty_spec:
        value_part = ""
        if ':' in warranty_spec:
            _, value_part = warranty_spec.split(':', 1)
            value_part = value_part.strip()
        else:
            value_part = warranty_spec.strip()

        # Only draw the warranty if the value part contains a digit (e.g., "1 Year", "12 Months")
        if any(char.isdigit() for char in value_part):
            icon_size = int(footer_font_size * 1)
            icon_padding = int(10 * scale_factor)
            icon_path = get_icon_path_for_spec('warranty') # Directly use 'warranty' to get the path
            icon_img = load_image_path(icon_path, color=line_color)

            warranty_font_size = footer_font_size * 0.75
            warranty_font = get_font(PRIMARY_FONT_PATH, warranty_font_size)

            warranty_y = price_y + (price_font_size * 0.8)

            icon_x = int(price_x)
            ascent, descent = warranty_font.getmetrics()
            line_height = ascent + descent
            icon_y = int(warranty_y - (line_height/2) + (line_height - icon_size) / 2)

            if icon_img:
                try:
                    icon_img.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
                    rgba_icon = icon_img.convert('RGBA')
                    tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    tmp.paste(rgba_icon, (icon_x, icon_y))
                    img = Image.alpha_composite(img, tmp)
                    draw = ImageDraw.Draw(img, 'RGBA')  # Recreate draw object
                except Exception as e:
                    print(f"Could not process icon {icon_path}: {e}")

            label_x = icon_x + icon_size + icon_padding

            if ':' in warranty_spec:
                label, value = warranty_spec.split(':', 1)
                value = value.strip()

                parts = value.split()
                number = ""
                unit = ""
                if len(parts) >= 2:
                    number = parts[0]
                    unit = parts[1]

                warranty_text = ""
                if unit.lower().startswith('year'):
                    if language == 'ka':
                        translated_warranty = translator.get_spec_label('Warranty', language)
                        warranty_text = f"{number} წლიანი {translated_warranty}"
                    else:
                        if number == '1':
                            translated_unit = translator.get_spec_label("Year", language)
                        else:
                            translated_unit = translator.get_spec_label("Years", language)
                        
                        translated_warranty = translator.get_spec_label('Warranty', language)
                        warranty_text = f"{number} {translated_unit} {translated_warranty}"
                else:
                    # Fallback for other units like "Month" or if parsing fails
                    translated_warranty = translator.get_spec_label('Warranty', language)
                    warranty_text = f"{value} {translated_warranty}"

                if contains_georgian(warranty_text):
                    warranty_font = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, warranty_font_size)

                draw.text((label_x, warranty_y), warranty_text, font=warranty_font, fill=text_color, anchor='lm')
            else:
                # Fallback for just text
                draw.text((label_x, warranty_y), warranty_spec, font=warranty_font, fill=text_color, anchor='lm')

    # --- QR Code ---
    qr_url = item_data.get('qr_url')
    if qr_url:
        qr_size = int(footer_height * 0.9)
        qr_x = int((width_px - qr_size) / 2)
        qr_y = int(footer_y_start + (footer_height - qr_size) / 2)
        _draw_qr_code(img, qr_url, (qr_x, qr_y), qr_size)

    # SKU and P/N on the right
    sku_text = f"SKU: {item_data.get('SKU', 'N/A')}"
    part_number = item_data.get('part_number', '')
    pn_text = f"P/N: {part_number}" if part_number else ""
    
    if pn_text:
        pn_y = footer_center_y - (footer_font_size * 0.6)
        sku_y = footer_center_y + (footer_font_size * 0.6)
        draw.text((width_px - content_padding, pn_y), pn_text, font=footer_font, fill=spec_text_color, anchor="rs")
        draw.text((width_px - content_padding, sku_y), sku_text, font=footer_font, fill=spec_text_color, anchor="rs")
        y_pos_for_turnaround = sku_y + footer_font_size # Increased vertical spacing
    else:
        sku_y = footer_center_y
        draw.text((width_px - content_padding, sku_y), sku_text, font=footer_font, fill=spec_text_color, anchor="rm")
        y_pos_for_turnaround = sku_y + footer_font_size # Increased vertical spacing

    # Add turnaround text and arrow
    if is_dual:
        turnaround_font_size = footer_font_size * 0.8
        if language == 'en':
            turnaround_text = "იხილეთ ქართული ვერსია"
            turnaround_font = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, turnaround_font_size)
        else: # language == 'ka'
            turnaround_text = "See English Version"
            turnaround_font = get_font(PRIMARY_FONT_PATH, turnaround_font_size)

        try:
            arrow_icon_path = resource_path("assets/arrow.png")
            with Image.open(arrow_icon_path) as arrow_icon:
                text_height = turnaround_font.getbbox(turnaround_text)[3] - turnaround_font.getbbox(turnaround_text)[1]
                arrow_size = int(text_height * 1.5)
                arrow_icon.thumbnail((arrow_size, arrow_size), Image.Resampling.LANCZOS)
                rgba_arrow = arrow_icon.convert('RGBA')

                # Position and draw arrow first, on the far right
                right_edge = width_px - content_padding
                padding = int(8 * scale_factor)
                arrow_x = right_edge - rgba_arrow.width
                arrow_y = int(y_pos_for_turnaround - (rgba_arrow.height / 2))

                tmp = Image.new('RGBA', img.size, (0, 0, 0, 0))
                tmp.paste(rgba_arrow, (arrow_x, arrow_y))
                img = Image.alpha_composite(img, tmp)
                draw = ImageDraw.Draw(img, 'RGBA')

                # Then, draw text to the left of the arrow
                text_x = arrow_x - padding
                draw.text((text_x, y_pos_for_turnaround), turnaround_text, font=turnaround_font, fill=spec_text_color, anchor="rm")

        except FileNotFoundError:
            # Fallback if arrow not found: draw text only
            print("Warning: assets/arrow.png not found.")
            draw.text((width_px - content_padding, y_pos_for_turnaround), turnaround_text, font=turnaround_font, fill=spec_text_color, anchor="rm")

    # --- 8. Final Border (90-degree corners) ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='#ADB5BD', width=max(1, int(2 * scale_factor)))

    return img.convert('RGB')


def create_price_tag(item_data, size_config, theme, layout_settings=None, language='en', is_special=False, background_cache=None, is_dual=False):
    if layout_settings is None:
        layout_settings = get_default_layout_settings()

    width_cm, height_cm = size_config['dims']
    width_px, height_px = cm_to_pixels(width_cm), cm_to_pixels(height_cm)

    # --- ROUTING TO CORRECT TAG GENERATOR ---
    if theme.get('design') == 'modern_brand':
        if width_cm == 6 and height_cm == 3.5:
            return _create_modern_brand_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
        else:
            return _create_modern_brand_tag_large(item_data, width_px, height_px, width_cm, height_cm, theme, language, layout_settings, is_special, is_dual=is_dual)
    if size_config.get('design') == 'keyboard':
        return _create_keyboard_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=is_special)
    if size_config.get('is_accessory_style', False):
        return _create_accessory_tag(item_data, width_px, height_px, width_cm, height_cm, theme, background_cache=background_cache)

    # --- BACKGROUND ---
    if theme.get('background_grid'):
        img = _create_grid_background(width_px, height_px, color=theme.get('background_color', '#2E7D32'))
    elif theme.get('background_snow'):
        # This is a placeholder for the original snow logic if you want to merge it.
        # For now, we'll just use the dynamic background for Winter theme too.
        img = _create_dynamic_background(width_px, height_px)
    else:
        img = _create_dynamic_background(width_px, height_px)

    translator = Translator()

    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    # Apply scaling from layout settings
    title_font_size = BASE_TITLE_FONT_SIZE * scale_factor * layout_settings.get('title_scale', 1.0)
    spec_font_size = BASE_SPEC_FONT_SIZE * scale_factor * layout_settings.get('spec_scale', 1.0)
    sku_font_size = BASE_FOOTER_SKU_FONT_SIZE * scale_factor * layout_settings.get('sku_scale', 1.0)
    price_font_size = BASE_FOOTER_PRICE_FONT_SIZE * scale_factor * layout_settings.get('price_scale', 1.0)
    strikethrough_font_size = BASE_STRIKETHROUGH_FONT_SIZE * scale_factor * layout_settings.get('price_scale', 1.0)
    pn_font_size = BASE_PN_FONT_SIZE * scale_factor * layout_settings.get('pn_scale', 1.0)
    logo_scale_factor = layout_settings.get('logo_scale', 1.0)

    title_font = get_font(PRIMARY_FONT_BOLD_PATH, title_font_size, is_bold=True)
    spec_font_regular = get_font(PRIMARY_FONT_PATH, spec_font_size)
    spec_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, spec_font_size, is_bold=True)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, sku_font_size, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, price_font_size, is_bold=True)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, strikethrough_font_size)
    part_num_font = get_font(PRIMARY_FONT_PATH, pn_font_size)
    gel_font = get_font(GEL_FONT_PATH, price_font_size, is_bold=True)
    gel_font_strikethrough = get_font(GEL_FONT_PATH, strikethrough_font_size)

    border_width = max(2, int(5 * scale_factor))
    line_width = max(1, int(3 * scale_factor))

    text_color = theme.get("text_color", "black")
    price_color = theme.get('price_color', '#D32F2F')
    strikethrough_color = theme.get("strikethrough_color", "black")
    logo_to_use = theme.get("logo_path_ka", "assets/logo-geo.png") if language == 'ka' else theme.get("logo_path",
                                                                                                      "assets/logo.png")
    
    draw = ImageDraw.Draw(img, 'RGBA')
    margin = 0.05 * width_px

    # --- Determine if on sale for layout adjustments ---
    sale_price_str = item_data.get('Sale price', '').strip()
    regular_price_str = item_data.get('Regular price', '').strip()
    is_on_sale = False
    try:
        sale_val = float(sale_price_str.replace(',', '.')) if sale_price_str else 0
        regular_val = float(regular_price_str.replace(',', '.')) if regular_price_str else 0
        is_on_sale = sale_val > 0 and sale_val != regular_val
    except (ValueError, TypeError):
        is_on_sale = False  # Ensure it's false if prices are not valid numbers

    # --- HEADER & TITLE ---
    y_cursor = 0.0
    logo_area_height = 0.12 * height_px
    y_cursor += logo_area_height
    y_cursor += -0.06 * height_px  # Title top padding

    title_text = item_data.get('Name', 'N/A')
    title_area_width = width_px - (2 * margin)
    if is_on_sale or is_special:
        title_area_width *= 0.85  # Reduce width to avoid star
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

    y_cursor += 0.07 * height_px  # Title separator padding
    # Use a straight line instead of a curve
    start_p = (margin, y_cursor)
    end_p = (width_px - margin, y_cursor)
    draw.line([start_p, end_p], fill=text_color, width=line_width)
    y_cursor += 0.02 * height_px + (10 * scale_factor) # Separator to specs padding

    # --- DYNAMIC SPECIFICATIONS ---
    footer_height = 0.14 * height_px
    footer_area_top = height_px - footer_height - border_width
    max_y_for_specs = footer_area_top - (0.02 * height_px)

    all_specs = item_data.get('all_specs', [])
    warranty_spec = None
    other_specs = []
    for spec in all_specs:
        if 'warranty' in spec.lower() and warranty_spec is None:
            warranty_spec = spec
        else:
            icon_path = get_icon_path_for_spec(spec)
            if 'info.svg' not in icon_path:
                other_specs.append(spec)

    spec_ascent, spec_descent = spec_font_regular.getmetrics()
    spec_line_height = spec_ascent + spec_descent
    spec_line_spacing = int(4 * scale_factor)

    # Helper function to accurately calculate the height of a spec line
    def get_real_spec_height(spec_text):
        icon_x = int(margin + 20 * scale_factor)
        icon_size = int(spec_font_size)
        # Use a fixed-width for the emoji area based on font size for consistency
        label_x = icon_x + icon_size + int(10 * scale_factor)

        if ':' in spec_text:
            label, value = spec_text.split(':', 1)
            translated_label = translator.get_spec_label(label.strip(), language)
            label_text = translated_label + ': '
            label_width = spec_font_bold.getbbox(label_text)[2]
            value_x = label_x + label_width
            remaining_width = width_px - value_x - margin
            wrapped_values = wrap_text(value.strip(), spec_font_regular, remaining_width)
            num_lines = max(1, len(wrapped_values))
            return num_lines * (spec_line_height + spec_line_spacing)
        else:
            return spec_line_height + spec_line_spacing

    # Determine which specs can fit
    drawable_specs = []
    current_spec_height = 0
    for spec in other_specs:
        h = get_real_spec_height(spec)
        if y_cursor + current_spec_height + h < max_y_for_specs:
            drawable_specs.append(spec)
            current_spec_height += h

    if warranty_spec:
        h = get_real_spec_height(warranty_spec)
        if y_cursor + current_spec_height + h < max_y_for_specs:
            drawable_specs.append(warranty_spec)
        elif drawable_specs:
            last_spec_h = get_real_spec_height(drawable_specs[-1])
            if y_cursor + current_spec_height - last_spec_h + h < max_y_for_specs:
                drawable_specs[-1] = warranty_spec

    # Draw the determined specs
    for spec in drawable_specs:
        icon_size = int(spec_font_size)
        icon_x = int(margin + 20 * scale_factor)
        icon_y = int(y_cursor + (spec_line_height - icon_size) / 2)

        icon_path = get_icon_path_for_spec(spec)
        icon_img = load_image_path(icon_path)
        if icon_img:
            icon_img = icon_img.convert("RGBA")
            icon_img.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
            img.paste(icon_img, (icon_x, icon_y), icon_img)
        else:
            print(f"Warning: Icon not found or could not be loaded at {icon_path}")

        # Use a fixed-width for the icon area based on font size for consistency
        label_x = icon_x + icon_size + int(10 * scale_factor)

        if ':' in spec:
            label, value = spec.split(':', 1)
            value = value.strip()
            translated_label = translator.get_spec_label(label.strip(), language)
            label_text = translated_label + ': '

            # Choose font based on content
            label_font = spec_font_bold # Default to Montserrat
            if contains_georgian(translated_label):
                label_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, spec_font_size, is_bold=True)

            draw.text((label_x, y_cursor + spec_ascent), label_text, font=label_font, fill=text_color, anchor='ls')
            
            value_x = label_x + label_font.getbbox(label_text)[2]
            remaining_width = width_px - value_x - margin
            
            wrapped_values = wrap_text(value, spec_font_regular, remaining_width)
            for i, line in enumerate(wrapped_values):
                draw.text((value_x, y_cursor + spec_ascent), line, font=spec_font_regular, fill=text_color, anchor='ls')
                if i < len(wrapped_values) - 1:
                    y_cursor += spec_line_height + spec_line_spacing
        else:
            # Also handle non-key-value specs that might be in Georgian
            spec_font = spec_font_regular
            if contains_georgian(spec):
                spec_font = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, spec_font_size)
            draw.text((label_x, y_cursor + spec_ascent), spec, font=spec_font, fill=text_color, anchor='ls')
        y_cursor += spec_line_height + spec_line_spacing

    # --- FOOTER ---
    footer_area_top = height_px - footer_height - border_width
    draw.line([(margin, footer_area_top), (width_px - margin, footer_area_top)], fill=text_color, width=line_width)
    footer_center_y = footer_area_top + (height_px - footer_area_top - border_width) / 2

    sku_label_text = translator.get_spec_label("SKU", language) + ": "
    sku_value_text = item_data.get('SKU', 'N/A')

    sku_label_font = sku_font  # Default to Montserrat Bold
    if contains_georgian(sku_label_text):
        sku_label_font = get_font(FALLBACK_FONT_GEORGIAN_BOLD, sku_font_size, is_bold=True)

    # Draw label
    draw.text((margin, footer_center_y), sku_label_text, font=sku_label_font, fill=text_color, anchor="lm")

    # Calculate where to draw the value
    label_bbox = draw.textbbox((margin, footer_center_y), sku_label_text, font=sku_label_font, anchor="lm")
    value_x = label_bbox[2] + (5 * scale_factor)

    # Draw value
    draw.text((value_x, footer_center_y), sku_value_text, font=sku_font, fill=text_color, anchor="lm")

    price_x = width_px - margin
    price_y = footer_center_y

    # --- Price Drawing Logic ---
    try:
        # Note: is_on_sale is already calculated at the top of the function
        sale_val = float(sale_price_str.replace(',', '.')) if sale_price_str else 0
        regular_val = float(regular_price_str.replace(',', '.')) if regular_price_str else 0

        # --- 1. Calculate Bounding Boxes without drawing ---
        def get_composite_bbox(price_val, p_font, g_font):
            price_str = str(price_val)
            gel_str = "₾"
            price_w = p_font.getbbox(price_str)[2] - p_font.getbbox(price_str)[0]
            gel_w = g_font.getbbox(gel_str)[2] - g_font.getbbox(gel_str)[0]
            spacing = int(5 * scale_factor)
            total_w = gel_w + spacing + price_w
            ascent, descent = p_font.getmetrics()
            total_h = ascent + descent
            return total_w, total_h

        sale_bbox_w, sale_bbox_h = 0, 0
        orig_bbox_w, orig_bbox_h = 0, 0
        total_width_of_prices = 0
        
        if is_on_sale:
            sale_bbox_w, sale_bbox_h = get_composite_bbox(sale_price_str, price_font, gel_font)
            total_width_of_prices += sale_bbox_w
            if regular_val > 0:
                orig_bbox_w, orig_bbox_h = get_composite_bbox(regular_price_str, strikethrough_font, gel_font_strikethrough)
                total_width_of_prices += orig_bbox_w + (20 * scale_factor)
        elif regular_val > 0:
            sale_bbox_w, sale_bbox_h = get_composite_bbox(regular_price_str, price_font, gel_font)
            total_width_of_prices += sale_bbox_w
        elif sale_val > 0:
            sale_bbox_w, sale_bbox_h = get_composite_bbox(sale_price_str, price_font, gel_font)
            total_width_of_prices += sale_bbox_w

        # --- 3. Draw Text ---
        def draw_composite_price(x, y, price_val, p_font, g_font, color, anchor, is_strikethrough=False):
            price_str = str(price_val)
            gel_str = "₾"
            price_w = p_font.getbbox(price_str)[2] - p_font.getbbox(price_str)[0]
            gel_w = g_font.getbbox(gel_str)[2] - g_font.getbbox(gel_str)[0]
            spacing = int(5 * scale_factor)
            total_w = gel_w + spacing + price_w
            
            start_x = x - total_w if anchor == 'rm' else x

            draw.text((start_x, y), gel_str, font=g_font, fill=color, anchor='lm')
            draw.text((start_x + gel_w + spacing, y), price_str, font=p_font, fill=color, anchor='lm')
            
            if is_strikethrough:
                ascent, descent = p_font.getmetrics()
                line_y = y
                draw.line([(start_x, line_y), (start_x + total_w, line_y)], fill=color, width=line_width)
            
            return start_x

        if is_on_sale:
            sale_x_left = draw_composite_price(price_x, price_y, sale_price_str, price_font, gel_font, price_color, 'rm')
            if regular_val > 0:
                orig_x_right = sale_x_left - (20 * scale_factor)
                draw_composite_price(orig_x_right, price_y, regular_price_str, strikethrough_font, gel_font_strikethrough, strikethrough_color, 'rm', is_strikethrough=True)
        elif regular_val > 0:
            draw_composite_price(price_x, price_y, regular_price_str, price_font, gel_font, price_color, 'rm')
        elif sale_val > 0:
            draw_composite_price(price_x, price_y, sale_price_str, price_font, gel_font, price_color, 'rm')

    except (ValueError, TypeError):
        # Fallback for non-numeric data
        if regular_price_str:
            draw.text((price_x, price_y), f"₾{regular_price_str}", font=price_font, fill=price_color, anchor='rm')
        elif sale_price_str:
            draw.text((price_x, price_y), f"₾{sale_price_str}", font=price_font, fill=price_color, anchor='rm')

    # --- LOGO & P/N ---
    logo_top_y = 0.03 * height_px
    try:
        with Image.open(logo_to_use).convert("RGBA") as logo:
            logo_h = int((logo_area_height - (0.03 * height_px)) * logo_scale_factor)
            logo_w = int(logo_h * (logo.width / logo.height))
            logo.thumbnail((logo_w, logo_h), Image.Resampling.LANCZOS)
            img.paste(logo, (int((width_px - logo.width) / 2),
                             int(logo_top_y + (logo_area_height - logo_top_y - logo.height) / 2)), logo)
    except FileNotFoundError:
        print(f"Warning: Logo file not found at '{logo_to_use}'")

    part_number = item_data.get('part_number', '')
    if part_number:
        pn_text = f"P/N: {part_number}"
        pn_y = logo_top_y + (logo_area_height - logo_top_y) / 2
        draw.text((margin, pn_y), pn_text, font=part_num_font, fill=text_color, anchor="lm")

    # --- Sale Overlay ---
    if is_on_sale or is_special:
        _draw_sale_overlay(img, draw, width_px, height_px, scale_factor, theme, language, is_special=is_special)

    # --- THEME SPECIFIC ELEMENTS ---
    if theme.get('draw_school_icons'):
        _draw_school_theme_elements(img, draw, width_px, height_px, scale_factor)

    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=border_width)
    return img