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
from translations import Translator
from data_handler import get_default_layout_settings
try:
    from assets.school_icons import create_laptop_icon, create_book_icon, create_ruler_icon
except ImportError:
    # This might happen during packaging, handle gracefully.
    create_laptop_icon = create_book_icon = create_ruler_icon = None


def get_icon_path_for_spec(spec_text):
    """Returns an icon path based on keywords in the specification text."""
    spec_lower = spec_text.lower()
    icon_dir = resource_path("assets/spec_icons")

    # Prioritize specific and important specs first
    if 'chair frame' in spec_lower:
        return os.path.join(icon_dir, 'furniture.png')
    if 'print speed (iso)' in spec_lower:
        return os.path.join(icon_dir, 'print_speed_iso.png')
    if 'print speed' in spec_lower:
        return os.path.join(icon_dir, 'print_speed.png')
    if 'print technology' in spec_lower:
        return os.path.join(icon_dir, 'print_technology.png')
    if 'print resolution' in spec_lower:
        return os.path.join(icon_dir, 'print_resolution.png')
    if 'scan type' in spec_lower:
        return os.path.join(icon_dir, 'scan_type.png')
    if 'mobile printing' in spec_lower:
        return os.path.join(icon_dir, 'mobile_printing.png')
    if 'monthly duty cycle' in spec_lower:
        return os.path.join(icon_dir, 'monthly_duty_cycle.png')
    if 'topology' in spec_lower:
        return os.path.join(icon_dir, 'topology.png')
    if 'waveform type' in spec_lower:
        return os.path.join(icon_dir, 'waveform_type.png')
    if 'output voltage' in spec_lower:
        return os.path.join(icon_dir, 'output_voltage.png')
    if 'output frequency' in spec_lower:
        return os.path.join(icon_dir, 'output_frequency.png')
    if 'output connection count' in spec_lower:
        return os.path.join(icon_dir, 'output_connection_count.png')
    if any(k in spec_lower for k in ['output connection type', 'input connection type']):
        return os.path.join(icon_dir, 'connection_type.png')
    if 'input voltage range' in spec_lower:
        return os.path.join(icon_dir, 'input_voltage_range.png')
    if 'input frequency' in spec_lower:
        return os.path.join(icon_dir, 'input_frequency.png')
    if 'number of batteries' in spec_lower:
        return os.path.join(icon_dir, 'number_of_batteries.png')
    if any(k in spec_lower for k in ['warranty']):
        return os.path.join(icon_dir, 'warranty.png')
    if any(k in spec_lower for k in ['cpu', 'processor', 'chipset', 'cores']):
        return os.path.join(icon_dir, 'cpu.png')
    if any(k in spec_lower for k in ['motherboard', 'socket', 'threads', 'cpucooler']):
        return os.path.join(icon_dir, 'motherboard.png')
    if 'drive bays' in spec_lower:
        return os.path.join(icon_dir, 'drive_bay.png')
    if 'cooler support' in spec_lower:
        return os.path.join(icon_dir, 'cooler.png')
    if 'installed coolers' in spec_lower:
        return os.path.join(icon_dir, 'case_fan.png')
    if 'psu included' in spec_lower:
        return os.path.join(icon_dir, 'psu.png')
    if 'fan support' in spec_lower:
        return os.path.join(icon_dir, 'fan_support.png')
    if 'fans included' in spec_lower:
        return os.path.join(icon_dir, 'accessories.png')
    if 'ports' in spec_lower:
        return os.path.join(icon_dir, 'ports_laptop.png')
    if any(k in spec_lower for k in ['hdmi', 'usb', 'audio jack']):
        return os.path.join(icon_dir, 'ports.png')
    if any(k in spec_lower for k in ['ram', 'memory']):
        return os.path.join(icon_dir, 'ram.png')
    if any(k in spec_lower for k in ['ssd', 'hdd', 'storage']):
        return os.path.join(icon_dir, 'storage.png')
    if any(k in spec_lower for k in ['screen size']):
        return os.path.join(icon_dir, 'dimensions.png')
    if any(k in spec_lower for k in ['panel type']):
        return os.path.join(icon_dir, 'display_details.png')
    if any(k in spec_lower for k in ['resolution']):
        return os.path.join(icon_dir, 'resolution.png')
    if any(k in spec_lower for k in ['refresh rate']):
        return os.path.join(icon_dir, 'refresh_rate.png')
    if any(k in spec_lower for k in ['response time']):
        return os.path.join(icon_dir, 'response_time.png')
    if any(k in spec_lower for k in ['contrast']):
        return os.path.join(icon_dir, 'contrast.png')
    if any(k in spec_lower for k in ['tearing prevention', 'gsync', 'freesync', 'vsync']):
        return os.path.join(icon_dir, 'tearing_prevention.png')
    if any(k in spec_lower for k in ['backlight']):
        return os.path.join(icon_dir, 'backlight.png')
    if any(k in spec_lower for k in ['screen', 'display', 'matrix']):
        return os.path.join(icon_dir, 'screen.png')
    if any(k in spec_lower for k in ['graphics', 'gpu', 'vram']):
        return os.path.join(icon_dir, 'graphics.png')
    if any(k in spec_lower for k in ['battery', 'power', 'wattage', 'mah']):
        return os.path.join(icon_dir, 'battery.png')
    if any(k in spec_lower for k in ['camera', 'webcam']):
        return os.path.join(icon_dir, 'camera.png')
    if any(k in spec_lower for k in ['keyboard', 'mouse']):
        return os.path.join(icon_dir, 'keyboard.png')
    if any(k in spec_lower for k in ['wifi', 'bluetooth', 'nfc']):
        return os.path.join(icon_dir, 'connectivity.png')
    if 'design' in spec_lower:
        return os.path.join(icon_dir, 'design.png')
    if any(k in spec_lower for k in ['max weight', 'weight']):
        return os.path.join(icon_dir, 'weight.png')
    if any(k in spec_lower for k in ['armrest', 'armrests']):
        return os.path.join(icon_dir, 'armrest.png')
    if any(k in spec_lower for k in ['material', 'material(s)']):
        return os.path.join(icon_dir, 'materials.png')
    if 'number of wheels' in spec_lower:
        return os.path.join(icon_dir, 'wheel.png')
    if any(k in spec_lower for k in ['dimensions', 'size']):
        return os.path.join(icon_dir, 'dimensions.png')
    if 'color' in spec_lower:
        return os.path.join(icon_dir, 'color.png')
    if any(k in spec_lower for k in ['os', 'operating system']):
        return os.path.join(icon_dir, 'os.png')
    if any(k in spec_lower for k in ['print', 'scan', 'copy']):
        return os.path.join(icon_dir, 'printer.png')
    if any(k in spec_lower for k in ['brand', 'model', 'barcode', 'partnumber']):
        return os.path.join(icon_dir, 'general.png')
    if any(k in spec_lower for k in ['memorytype', 'memoryspeed', 'maxmemory', 'memorycardsupport', 'opticaldrive']):
        return os.path.join(icon_dir, 'memory_details.png')
    if any(k in spec_lower for k in ['brightness']):
        return os.path.join(icon_dir, 'brightness.png')
    if any(k in spec_lower for k in ['viewing angle']):
        return os.path.join(icon_dir, 'viewing_angle.png')
    if any(k in spec_lower for k in ['refreshrate', 'aspectratio', 'responsetime', 'contrastratio', 'colorgamut']):
        return os.path.join(icon_dir, 'display_details.png')
    if any(k in spec_lower for k in ['interface', 'ethernet', 'network']):
        return os.path.join(icon_dir, 'network.png')
    if any(k in spec_lower for k in ['formfactor', 'case', 'buildmaterial', 'ip_rating']):
        return os.path.join(icon_dir, 'build.png')
    if any(k in spec_lower for k in ['powersupply', 'efficiency', 'modular', 'capacity', 'inputvoltage', 'outputvoltage']):
        return os.path.join(icon_dir, 'power_supply.png')
    if any(k in spec_lower for k in ['audio', 'speakers', 'microphone']):
        return os.path.join(icon_dir, 'audio.png')
    if any(k in spec_lower for k in ['fingerprintsensor', 'facerecognition']):
        return os.path.join(icon_dir, 'security.png')
    if any(k in spec_lower for k in ['supportedos', 'sim_support', 'smartfeatures', 'tuner']):
        return os.path.join(icon_dir, 'features.png')
    if any(k in spec_lower for k in ['functions', 'mobileprinting', 'papersize', 'connector']):
        return os.path.join(icon_dir, 'printer_details.png')
    if any(k in spec_lower for k in ['optical zoom', 'lamp life', 'power consumption', 'mounting']):
        return os.path.join(icon_dir, 'projector.png')
    if any(k in spec_lower for k in ['materials', 'number of wheels', 'armrests', 'maximum weight', 'max weight']):
        return os.path.join(icon_dir, 'furniture.png')
    if any(k in spec_lower for k in ['includedaccessories', 'portability', 'portable design']):
        return os.path.join(icon_dir, 'accessories.png')
    if any(k in spec_lower for k in ['cpu', 'processor', 'chipset', 'cores']):
        return os.path.join(icon_dir, 'cpu.png')
    if any(k in spec_lower for k in ['ram', 'memory']):
        return os.path.join(icon_dir, 'ram.png')
    if any(k in spec_lower for k in ['ssd', 'hdd', 'storage']):
        return os.path.join(icon_dir, 'storage.png')
    if any(k in spec_lower for k in ['screen size']):
        return os.path.join(icon_dir, 'dimensions.png')
    if any(k in spec_lower for k in ['panel type']):
        return os.path.join(icon_dir, 'display_details.png')
    if any(k in spec_lower for k in ['resolution']):
        return os.path.join(icon_dir, 'resolution.png')
    if any(k in spec_lower for k in ['refresh rate']):
        return os.path.join(icon_dir, 'refresh_rate.png')
    if any(k in spec_lower for k in ['response time']):
        return os.path.join(icon_dir, 'response_time.png')
    if any(k in spec_lower for k in ['contrast']):
        return os.path.join(icon_dir, 'contrast.png')
    if any(k in spec_lower for k in ['tearing prevention', 'gsync', 'freesync', 'vsync']):
        return os.path.join(icon_dir, 'tearing_prevention.png')
    if any(k in spec_lower for k in ['backlight']):
        return os.path.join(icon_dir, 'backlight.png')
    if any(k in spec_lower for k in ['screen', 'display', 'matrix']):
        return os.path.join(icon_dir, 'screen.png')
    if any(k in spec_lower for k in ['graphics', 'gpu', 'vram']):
        return os.path.join(icon_dir, 'graphics.png')
    if any(k in spec_lower for k in ['battery', 'power', 'wattage', 'mah']):
        return os.path.join(icon_dir, 'battery.png')
    if any(k in spec_lower for k in ['camera', 'webcam']):
        return os.path.join(icon_dir, 'camera.png')
    if any(k in spec_lower for k in ['keyboard', 'mouse']):
        return os.path.join(icon_dir, 'keyboard.png')
    if any(k in spec_lower for k in ['wifi', 'bluetooth', 'nfc']):
        return os.path.join(icon_dir, 'connectivity.png')
    if 'design' in spec_lower:
        return os.path.join(icon_dir, 'design.png')
    if any(k in spec_lower for k in ['max weight', 'weight']):
        return os.path.join(icon_dir, 'weight.png')
    if any(k in spec_lower for k in ['armrest', 'armrests']):
        return os.path.join(icon_dir, 'armrest.png')
    if any(k in spec_lower for k in ['material', 'material(s)']):
        return os.path.join(icon_dir, 'materials.png')
    if 'number of wheels' in spec_lower:
        return os.path.join(icon_dir, 'wheel.png')
    if any(k in spec_lower for k in ['dimensions', 'size']):
        return os.path.join(icon_dir, 'dimensions.png')
    if 'color' in spec_lower:
        return os.path.join(icon_dir, 'color.png')
    if any(k in spec_lower for k in ['os', 'operating system']):
        return os.path.join(icon_dir, 'os.png')
    if any(k in spec_lower for k in ['print', 'scan', 'copy']):
        return os.path.join(icon_dir, 'printer.png')
    if any(k in spec_lower for k in ['brand', 'model', 'barcode', 'partnumber']):
        return os.path.join(icon_dir, 'general.png')
    if any(k in spec_lower for k in ['memorytype', 'memoryspeed', 'maxmemory', 'memorycardsupport', 'opticaldrive']):
        return os.path.join(icon_dir, 'memory_details.png')
    if any(k in spec_lower for k in ['brightness']):
        return os.path.join(icon_dir, 'brightness.png')
    if any(k in spec_lower for k in ['viewing angle']):
        return os.path.join(icon_dir, 'viewing_angle.png')
    if any(k in spec_lower for k in ['refreshrate', 'aspectratio', 'responsetime', 'contrastratio', 'colorgamut']):
        return os.path.join(icon_dir, 'display_details.png')
    if any(k in spec_lower for k in ['interface', 'ethernet', 'network']):
        return os.path.join(icon_dir, 'network.png')
    if any(k in spec_lower for k in ['formfactor', 'case', 'buildmaterial', 'ip_rating']):
        return os.path.join(icon_dir, 'build.png')
    if any(k in spec_lower for k in ['powersupply', 'efficiency', 'modular', 'capacity', 'inputvoltage', 'outputvoltage']):
        return os.path.join(icon_dir, 'power_supply.png')
    if any(k in spec_lower for k in ['audio', 'speakers', 'microphone']):
        return os.path.join(icon_dir, 'audio.png')
    if any(k in spec_lower for k in ['fingerprintsensor', 'facerecognition']):
        return os.path.join(icon_dir, 'security.png')
    if any(k in spec_lower for k in ['supportedos', 'sim_support', 'smartfeatures', 'tuner']):
        return os.path.join(icon_dir, 'features.png')
    if any(k in spec_lower for k in ['functions', 'mobileprinting', 'papersize', 'connector']):
        return os.path.join(icon_dir, 'printer_details.png')
    if any(k in spec_lower for k in ['optical zoom', 'lamp life', 'power consumption', 'mounting']):
        return os.path.join(icon_dir, 'projector.png')
    if any(k in spec_lower for k in ['materials', 'number of wheels', 'armrests', 'maximum weight', 'max weight']):
        return os.path.join(icon_dir, 'furniture.png')
    if any(k in spec_lower for k in ['includedaccessories', 'portability', 'portable design']):
        return os.path.join(icon_dir, 'accessories.png')
    if any(k in spec_lower for k in ['memorytype', 'memoryspeed', 'maxmemory', 'memorycardsupport', 'opticaldrive']):
        return os.path.join(icon_dir, 'memory_details.png')
    if any(k in spec_lower for k in ['brightness']):
        return os.path.join(icon_dir, 'brightness.png')
    if any(k in spec_lower for k in ['viewing angle']):
        return os.path.join(icon_dir, 'viewing_angle.png')
    if any(k in spec_lower for k in ['refreshrate', 'aspectratio', 'responsetime', 'contrastratio', 'colorgamut']):
        return os.path.join(icon_dir, 'display_details.png')
    if any(k in spec_lower for k in ['interface', 'ethernet', 'network']):
        return os.path.join(icon_dir, 'network.png')
    if any(k in spec_lower for k in ['formfactor', 'case', 'buildmaterial', 'ip_rating']):
        return os.path.join(icon_dir, 'build.png')
    if any(k in spec_lower for k in ['powersupply', 'efficiency', 'modular', 'capacity', 'inputvoltage', 'outputvoltage']):
        return os.path.join(icon_dir, 'power_supply.png')
    if any(k in spec_lower for k in ['audio', 'speakers', 'microphone']):
        return os.path.join(icon_dir, 'audio.png')
    if any(k in spec_lower for k in ['fingerprintsensor', 'facerecognition']):
        return os.path.join(icon_dir, 'security.png')
    if any(k in spec_lower for k in ['supportedos', 'sim_support', 'smartfeatures', 'tuner']):
        return os.path.join(icon_dir, 'features.png')
    if any(k in spec_lower for k in ['functions', 'mobileprinting', 'papersize', 'connector']):
        return os.path.join(icon_dir, 'printer_details.png')
    if any(k in spec_lower for k in ['optical zoom', 'lamp life', 'power consumption', 'mounting']):
        return os.path.join(icon_dir, 'projector.png')
    if any(k in spec_lower for k in ['materials', 'number of wheels', 'armrests', 'maximum weight', 'max weight']):
        return os.path.join(icon_dir, 'furniture.png')
    if any(k in spec_lower for k in ['includedaccessories', 'portability', 'portable design']):
        return os.path.join(icon_dir, 'accessories.png')
    # Default icon if no specific match
    return os.path.join(icon_dir, 'default.png')


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


def _draw_bezier_curve(draw, start_point, end_point, control_point, fill, width):
    """Draws a quadratic Bezier curve."""
    points = []
    for t in range(101):
        t /= 100.0
        x = (1 - t)**2 * start_point[0] + 2 * (1 - t) * t * control_point[0] + t**2 * end_point[0]
        y = (1 - t)**2 * start_point[1] + 2 * (1 - t) * t * control_point[1] + t**2 * end_point[1]
        points.append((x, y))
    draw.line(points, fill=fill, width=width)


def _draw_cosmic_veil_accent(img, width, height):
    """Draws a subtle, semi-transparent nebula effect on a dark background."""
    # Colors with low alpha for subtlety
    c1 = (46, 2, 109, 210)     # Deep Violet
    c2 = (0, 184, 252, 220)    # Electric Blue
    c3 = (255, 0, 122, 205)    # Neon Pink
    colors = [c1, c2, c3]

    for _ in range(4):  # Draw 4 soft glows
        color = random.choice(colors)
        
        # Create a temporary image for the radial gradient
        radius = random.randint(int(width * 0.5), int(width * 0.9))
        glow_img = Image.new('RGBA', (radius * 2, radius * 2), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)

        # Draw concentric circles with decreasing alpha to create a soft glow
        for i in range(radius, 0, -2):
            alpha = int(color[3] * (1 - (i / radius)))
            fill_color = (color[0], color[1], color[2], alpha)
            glow_draw.ellipse([(radius - i, radius - i), (radius + i, radius + i)], fill=fill_color)

        # Paste the glow onto the main draw object at a random position
        paste_x = random.randint(-int(width * 0.6), int(width * 0.3))
        paste_y = random.randint(-int(height * 0.6), int(height * 0.3))
        
        img.paste(glow_img, (paste_x, paste_y), glow_img)


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


def _draw_blood_splatter(draw, width, height):
    """Draws a blood splatter effect in the bottom-left corner."""
    blood_color = (180, 0, 0, 200)
    darker_blood_color = (130, 0, 0, 220)

    # Main splat
    for _ in range(random.randint(15, 25)):
        x = random.gauss(width * 0.1, width * 0.15)
        y = random.gauss(height * 0.9, height * 0.1)
        radius = random.uniform(2, 20)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=blood_color)

    # Smaller droplets
    for _ in range(random.randint(30, 50)):
        x = random.uniform(0, width * 0.5)
        y = random.uniform(height * 0.6, height)
        radius = random.uniform(1, 4)
        if (x - width*0.1)**2 + (y - height*0.9)**2 < (width*0.2)**2: # concentrate near main splat
             draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=darker_blood_color)

    # Drips
    for _ in range(random.randint(3, 5)):
        start_x = random.randint(0, int(width * 0.3))
        start_y = random.randint(int(height * 0.8), height)
        end_y = start_y + random.randint(10, 50)
        end_x = start_x + random.randint(-5, 5)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=darker_blood_color, width=random.randint(2, 4))


def _create_accessory_tag(item_data, width_px, height_px, width_cm, height_cm, theme, background_cache=None):
    # Specialized Legion accessory layout
    if theme.get('accessory_background_style') == 'legion_hex':
        return _create_legion_accessory_tag(item_data, width_px, height_px, width_cm, height_cm, theme, background_cache=background_cache)

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
        # Must be drawn after the main background is set
        if theme.get('accessory_background_style') == 'cosmic_veil':
            _draw_cosmic_veil_accent(img, width_px, height_px)
        
        if background_cache is not None:
            background_cache[sku] = img.copy()

    draw = ImageDraw.Draw(img, 'RGBA')

    # --- ACCENTS ---
    # Must be drawn after the main background is set
    if theme.get('accessory_background_style') == 'cosmic_veil':
        _draw_cosmic_veil_accent(img, width_px, height_px)
    elif theme.get('accessory_background_style') == 'logitech_style':
        header_height = int(0.22 * height_px)
        start_color = (41, 207, 203)  # #29CFCB
        end_color = (0, 128, 112)    # #008070
        for y in range(header_height):
            # Simple linear interpolation
            r = int(start_color[0] + (end_color[0] - start_color[0]) * (y / header_height))
            g = int(start_color[1] + (end_color[1] - start_color[1]) * (y / header_height))
            b = int(start_color[2] + (end_color[2] - start_color[2]) * (y / header_height))
            draw.line([(0, y), (width_px, y)], fill=(r, g, b))
    elif theme.get('accessory_background_style') == 'bloody_style':
        header_height = int(0.22 * height_px)
        start_color = (255, 68, 68)  # Bright Red
        end_color = (170, 0, 0)      # Dark Red
        for y in range(header_height):
            # Simple linear interpolation
            r = int(start_color[0] + (end_color[0] - start_color[0]) * (y / header_height))
            g = int(start_color[1] + (end_color[1] - start_color[1]) * (y / header_height))
            b = int(start_color[2] + (end_color[2] - start_color[2]) * (y / header_height))
            draw.line([(0, y), (width_px, y)], fill=(r, g, b))

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
                if theme.get('accessory_background_style') == 'logitech_style' or theme.get('accessory_background_style') == 'bloody_style':
                    logo_max_h = top_area_height * 0.8
                    logo.thumbnail((width_px, logo_max_h), Image.Resampling.LANCZOS)
                    logo_x = int(margin)
                    logo_y = int((top_area_height - logo.height) / 2)
                else:
                    logo_max_h = top_area_height * 0.8
                    logo.thumbnail((width_px, logo_max_h), Image.Resampling.LANCZOS)
                    logo_x = int(margin)
                    logo_y = int((top_area_height - logo.height) / 2)
                img.paste(logo, (logo_x, logo_y), logo)
        except FileNotFoundError:
            print(f"Warning: Brand logo not found at {logo_path}")


    # Conditionally draw separators
    if not theme.get('draw_school_icons') and theme.get('accessory_background_style') != 'logitech_style' and theme.get('accessory_background_style') != 'bloody_style':
        line_width = max(1, int(2 * scale_factor))
        if theme.get('accessory_background_style') == 'cosmic_veil':
            line_width = max(2, int(4 * scale_factor))  # Make lines thicker for Logitech G

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
    elif theme.get('accessory_background_style') == 'logitech_style' or theme.get('accessory_background_style') == 'bloody_style':
        draw.text((width_px - margin, sku_y), sku_text, font=sku_font, fill='white', anchor="rm")
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
            if theme.get('accessory_background_style') == 'logitech_style' or theme.get('accessory_background_style') == 'bloody_style':
                price_color_override = 'black'

            final_price_color = price_color_override or price_color
            total_width = gel_width + spacing + price_width
            start_x = (width_px - total_width) / 2

            if theme.get('accessory_background_style') == 'logitech_style' or theme.get('accessory_background_style') == 'bloody_style':
                # Create a floating "pill" bubble for the price
                bbox = price_font.getbbox("Ag")
                line_height = bbox[3] - bbox[1]
                padding_x = 25 * scale_factor
                padding_y = 15 * scale_factor
                
                rect_x1 = start_x - padding_x
                rect_y1 = price_y - (line_height / 2) - padding_y
                rect_x2 = start_x + total_width + padding_x
                rect_y2 = price_y + (line_height / 2) + padding_y
                radius = 20 * scale_factor

                # Draw drop shadow
                shadow_offset = 6 * scale_factor
                shadow_color = (0, 0, 0, 80) # Semi-transparent black
                draw.rounded_rectangle(
                    [(rect_x1 + shadow_offset, rect_y1 + shadow_offset), (rect_x2 + shadow_offset, rect_y2 + shadow_offset)],
                    radius=radius,
                    fill=shadow_color
                )
                
                # Draw white pill
                draw.rounded_rectangle(
                    [(rect_x1, rect_y1), (rect_x2, rect_y2)],
                    radius=radius,
                    fill='white',
                    outline=(200, 200, 200),
                    width=1
                )

            # Draw the price text over the pill
            draw.text((start_x, price_y), gel_text, font=gel_font, fill=final_price_color, anchor="lm")
            draw.text((start_x + gel_width + spacing, price_y), price_text, font=price_font, fill=final_price_color, anchor="lm")

            # For default theme, previous price is not shown as per request.

    # --- THEME SPECIFIC ELEMENTS ---
    if theme.get('draw_school_icons'):
        _draw_school_theme_elements(img, draw, width_px, height_px, scale_factor)

    if theme.get('accessory_background_style') == 'bloody_style':
        _draw_blood_splatter(draw, width_px, height_px)

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


def _split_logitech_name(name_text):
    """
    Splits a Logitech product name into a model part and a description part.
    e.g., "Logitech M170 Wireless Mouse" -> ("Logitech M170", "Wireless Mouse")
    """
    words = name_text.split()
    split_index = -1

    # Find the first word with a digit
    for i, word in enumerate(words):
        if any(char.isdigit() for char in word):
            if i < len(words) - 1:
                split_index = i
                break

    # If we found a word with a number, split after it.
    if split_index != -1:
        part1 = " ".join(words[:split_index + 1])
        part2 = " ".join(words[split_index + 1:])
        return part1, part2

    # Fallback: if no number, return the whole name as part1
    return name_text, ""


def _create_logitech_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Config ---
    margin = 0.05 * width_px
    text_color = theme.get('name_color', 'black')
    price_color = "#00b3a4"  # Greenish Teal
    header_color = "#00b3a4"  # Greenish Teal
    logo_path = theme.get('accessory_logo_path')

    # --- Scaling ---
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    # --- Fonts (Increased Sizes) ---
    base_model_font_size = 90  # Increased from 72
    base_desc_font_size = 50   # Increased from 40
    base_price_font_size = 110
    base_strikethrough_font_size = 75
    base_sku_font_size = 65

    model_font = get_font(PRIMARY_FONT_BOLD_PATH, base_model_font_size * scale_factor, is_bold=True)
    desc_font = get_font(PRIMARY_FONT_PATH, base_desc_font_size * scale_factor)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_font_size * scale_factor, is_bold=True)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, base_strikethrough_font_size * scale_factor)
    gel_font = get_font(GEL_FONT_PATH, base_price_font_size * scale_factor, is_bold=True)
    gel_font_strikethrough = get_font(GEL_FONT_PATH, base_strikethrough_font_size * scale_factor)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, base_sku_font_size * scale_factor, is_bold=True)

    # --- 1. Header Bar ---
    header_height = height_px * 0.20
    draw.rectangle([0, 0, width_px, header_height], fill=header_color)

    # --- 2. Logo & SKU (In Header) ---
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo_max_h = header_height * 0.8
                logo.thumbnail((width_px, logo_max_h), Image.Resampling.LANCZOS)
                logo_x = int(margin)
                logo_y = int((header_height - logo.height) / 2)
                img.paste(logo, (logo_x, logo_y), logo)
        except FileNotFoundError:
            print(f"Warning: Logitech logo not found at {logo_path}")

    sku_text = item_data.get('SKU', 'N/A')
    draw.text((width_px - margin, header_height / 2), sku_text, font=sku_font, fill='white', anchor="rm")

    # --- DYNAMIC FONT SIZING & LAYOUT ---
    current_model_font_size = base_model_font_size
    current_desc_font_size = base_desc_font_size

    while True:
        model_font = get_font(PRIMARY_FONT_BOLD_PATH, current_model_font_size * scale_factor, is_bold=True)
        desc_font = get_font(PRIMARY_FONT_PATH, current_desc_font_size * scale_factor)

        # --- Calculate Text Dimensions ---
        name_text = item_data.get('Name', 'N/A')
        model_text, desc_text = _split_logitech_name(name_text)
        text_x = margin
        text_y_start = header_height + (margin * 1.5)

        model_ascent, model_descent = model_font.getmetrics()
        model_line_height = model_ascent + model_descent
        wrapped_model_lines = wrap_text(model_text, model_font, width_px - (2 * margin))

        desc_ascent, desc_descent = desc_font.getmetrics()
        desc_line_height = desc_ascent + desc_descent
        wrapped_desc_lines = wrap_text(desc_text, desc_font, width_px - (2 * margin))

        max_line_width = 0
        for line in wrapped_model_lines:
            line_width = model_font.getbbox(line)[2]
            if line_width > max_line_width: max_line_width = line_width
        for line in wrapped_desc_lines:
            line_width = desc_font.getbbox(line)[2]
            if line_width > max_line_width: max_line_width = line_width

        total_text_height = (len(wrapped_model_lines) * model_line_height) + (len(wrapped_desc_lines) * desc_line_height)
        if wrapped_model_lines and wrapped_desc_lines:
            total_text_height += 5 * scale_factor

        # --- Calculate Text Tile BBox ---
        tile_padding_x = margin * 0.5
        tile_padding_y = margin * 0.4
        tile_x0 = text_x - tile_padding_x
        tile_y0 = text_y_start - tile_padding_y
        tile_x1 = text_x + max_line_width + tile_padding_x
        tile_y1 = text_y_start + total_text_height + tile_padding_y

        # --- Calculate Price Area BBox ---
        price_block_left = width_px
        price_block_top = height_px
        sale_price = item_data.get('Sale price', '').strip()
        regular_price = item_data.get('Regular price', '').strip()
        is_on_sale = False
        display_price = ""
        try:
            sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
            regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
            is_on_sale = sale_val > 0 and sale_val != regular_val
            if is_on_sale: display_price = sale_price
            elif regular_val > 0: display_price = regular_price
            elif sale_val > 0: display_price = sale_price
        except (ValueError, TypeError):
            display_price = regular_price or sale_price
            is_on_sale = False

        if display_price:
            price_x = width_px - margin
            price_y = height_px - margin
            price_width = price_font.getbbox(str(display_price))[2]
            gel_width = gel_font.getbbox("₾")[2]
            spacing = int(5 * scale_factor)
            main_price_total_width = price_width + gel_width + spacing
            price_block_width = main_price_total_width

            if is_on_sale and regular_price:
                old_price_width = strikethrough_font.getbbox(str(regular_price))[2]
                old_gel_width = gel_font_strikethrough.getbbox("₾")[2]
                old_price_total_width = old_price_width + old_gel_width + spacing
                price_block_width = max(main_price_total_width, old_price_total_width)
                strikethrough_y = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])
                price_block_top = strikethrough_y - (strikethrough_font.getmetrics()[0] + strikethrough_font.getmetrics()[1])
            else:
                price_block_top = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])
            price_block_left = price_x - price_block_width

        # --- Check for Overlap ---
        safety_margin = 15 * scale_factor
        overlap = (tile_x1 + safety_margin > price_block_left) and (tile_y1 + safety_margin > price_block_top)

        if not overlap:
            break

        current_model_font_size *= 0.95
        current_desc_font_size *= 0.95

        if current_model_font_size < 20:  # Prevent infinite loop
            break

    # --- 3a. Draw 3D Tile (using final calculated dimensions) ---
    radius = 15 * scale_factor
    shadow_offset = 8 * scale_factor
    shadow_color = (0, 0, 0, 80)
    draw.rounded_rectangle(
        [(tile_x0 + shadow_offset, tile_y0 + shadow_offset), (tile_x1 + shadow_offset, tile_y1 + shadow_offset)],
        radius=radius, fill=shadow_color
    )
    draw.rounded_rectangle(
        [(tile_x0, tile_y0), (tile_x1, tile_y1)],
        radius=radius, fill='white', outline=(220, 220, 220), width=max(1, int(2 * scale_factor))
    )

    # --- 3b. Draw Text on Tile ---
    y_cursor = text_y_start
    for line in wrapped_model_lines:
        draw.text((text_x, y_cursor), line, font=model_font, fill=text_color, anchor="la")
        y_cursor += model_line_height
    if wrapped_model_lines and wrapped_desc_lines:
        y_cursor += 5 * scale_factor
    for line in wrapped_desc_lines:
        draw.text((text_x, y_cursor), line, font=desc_font, fill=text_color, anchor="la")
        y_cursor += desc_line_height

    # --- 4. Price (Bottom Right) ---
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()
    is_on_sale = False
    display_price = ""

    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        is_on_sale = sale_val > 0 and sale_val != regular_val

        if is_on_sale:
            display_price = sale_price
        elif regular_val > 0:
            display_price = regular_price
        elif sale_val > 0:
            display_price = sale_price
    except (ValueError, TypeError):
        display_price = regular_price or sale_price
        is_on_sale = False

    price_x = width_px - margin
    price_y = height_px - margin

    if display_price:
        price_text = str(display_price)
        gel_text = "₾"

        # Draw main price
        price_width = price_font.getbbox(price_text)[2]
        gel_width = gel_font.getbbox(gel_text)[2]
        spacing = int(5 * scale_factor)

        draw.text((price_x, price_y), price_text, font=price_font, fill=price_color, anchor="rs")
        draw.text((price_x - price_width - spacing, price_y), gel_text, font=gel_font, fill=price_color, anchor="rs")

        # Draw strikethrough price if on sale
        if is_on_sale and regular_price:
            old_price_text = str(regular_price)
            old_price_ascent, old_price_descent = strikethrough_font.getmetrics()
            old_price_height = old_price_ascent + old_price_descent

            strikethrough_y = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])

            old_price_width = strikethrough_font.getbbox(old_price_text)[2]
            old_gel_width = gel_font_strikethrough.getbbox(gel_text)[2]

            draw.text((price_x, strikethrough_y), old_price_text, font=strikethrough_font, fill=text_color, anchor="rs")
            draw.text((price_x - old_price_width - spacing, strikethrough_y), gel_text, font=gel_font_strikethrough,
                      fill=text_color, anchor="rs")

            # Draw strikethrough line
            total_old_width = old_price_width + old_gel_width + spacing
            line_y = strikethrough_y - (old_price_height / 2) + old_price_descent
            draw.line([(price_x - total_old_width, line_y), (price_x, line_y)], fill=text_color,
                      width=int(3 * scale_factor))

    # --- Final Border ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=3)

    return img


def _create_bloody_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    img = Image.new('RGB', (width_px, height_px), 'white')

    # --- Paste Blood Splatter Image from file ---
    try:
        splatter_path = resource_path("assets/props/Blood_Splatter.png")
        with Image.open(splatter_path).convert("RGBA") as splatter_img:
            # Scale the splatter to be about 80% of the tag's height
            splatter_h = int(height_px * 0.8)
            splatter_w = int(splatter_img.width * (splatter_h / splatter_img.height))
            splatter_img = splatter_img.resize((splatter_w, splatter_h), Image.Resampling.LANCZOS)

            # Position it in the empty area
            paste_x = int((width_px - splatter_w) / 2 + width_px / 6)
            paste_y = height_px - splatter_h

            # Paste onto a temporary transparent layer
            temp_layer = Image.new('RGBA', img.size, (0,0,0,0))
            temp_layer.paste(splatter_img, (paste_x, paste_y))

            # Composite the splatter layer with the main image
            img = Image.alpha_composite(img.convert("RGBA"), temp_layer).convert("RGB")

    except FileNotFoundError:
        print(f"Warning: Blood splatter image not found at assets/props/Blood_Splatter.png")

    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Config ---
    margin = 0.05 * width_px
    text_color = theme.get('name_color', 'black')
    price_color = "#D32F2F"  # Bloody Red
    header_color = "#000000"  # Black
    logo_path = theme.get('accessory_logo_path')

    # --- Scaling ---
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    # --- Fonts ---
    base_model_font_size = 90
    base_desc_font_size = 50
    base_price_font_size = 110
    base_strikethrough_font_size = 75
    base_sku_font_size = 75

    model_font = get_font(PRIMARY_FONT_BOLD_PATH, base_model_font_size * scale_factor, is_bold=True)
    desc_font = get_font(PRIMARY_FONT_PATH, base_desc_font_size * scale_factor)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_font_size * scale_factor, is_bold=True)
    strikethrough_font = get_font(PRIMARY_FONT_PATH, base_strikethrough_font_size * scale_factor)
    gel_font = get_font(GEL_FONT_PATH, base_price_font_size * scale_factor, is_bold=True)
    gel_font_strikethrough = get_font(GEL_FONT_PATH, base_strikethrough_font_size * scale_factor)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, base_sku_font_size * scale_factor, is_bold=True)

    # --- 1. Header Bar ---
    header_height = height_px * 0.30
    draw.rectangle([0, 0, width_px, header_height], fill=header_color)

    # --- 2. Logo & SKU (In Header) ---
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo_max_h = header_height * 0.85
                logo.thumbnail((width_px, logo_max_h), Image.Resampling.LANCZOS)
                logo_x = int(margin)
                logo_y = int((header_height - logo.height) / 2)
                img.paste(logo, (logo_x, logo_y), logo)
        except FileNotFoundError:
            print(f"Warning: Bloody logo not found at {logo_path}")

    sku_text = item_data.get('SKU', 'N/A')
    draw.text((width_px - margin, header_height / 2), sku_text, font=sku_font, fill='white', anchor="rm")

    # --- DYNAMIC FONT SIZING & LAYOUT (Identical to Logitech style) ---
    current_model_font_size = base_model_font_size
    current_desc_font_size = base_desc_font_size

    while True:
        model_font = get_font(PRIMARY_FONT_BOLD_PATH, current_model_font_size * scale_factor, is_bold=True)
        desc_font = get_font(PRIMARY_FONT_PATH, current_desc_font_size * scale_factor)

        name_text = item_data.get('Name', 'N/A')
        model_text, desc_text = _split_logitech_name(name_text)
        text_x = margin
        text_y_start = header_height + (margin * 1.5)

        model_ascent, model_descent = model_font.getmetrics()
        model_line_height = model_ascent + model_descent
        wrapped_model_lines = wrap_text(model_text, model_font, width_px - (2 * margin))

        desc_ascent, desc_descent = desc_font.getmetrics()
        desc_line_height = desc_ascent + desc_descent
        wrapped_desc_lines = wrap_text(desc_text, desc_font, width_px - (2 * margin))

        max_line_width = 0
        for line in wrapped_model_lines:
            line_width = model_font.getbbox(line)[2]
            if line_width > max_line_width: max_line_width = line_width
        for line in wrapped_desc_lines:
            line_width = desc_font.getbbox(line)[2]
            if line_width > max_line_width: max_line_width = line_width

        total_text_height = (len(wrapped_model_lines) * model_line_height) + (len(wrapped_desc_lines) * desc_line_height)
        if wrapped_model_lines and wrapped_desc_lines:
            total_text_height += 5 * scale_factor

        tile_padding_x = margin * 0.5
        tile_padding_y = margin * 0.4
        tile_x0 = text_x - tile_padding_x
        tile_y0 = text_y_start - tile_padding_y
        tile_x1 = text_x + max_line_width + tile_padding_x
        tile_y1 = text_y_start + total_text_height + tile_padding_y

        price_block_left = width_px
        price_block_top = height_px
        sale_price = item_data.get('Sale price', '').strip()
        regular_price = item_data.get('Regular price', '').strip()
        is_on_sale = False
        display_price = ""
        try:
            sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
            regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
            is_on_sale = sale_val > 0 and sale_val != regular_val
            if is_on_sale: display_price = sale_price
            elif regular_val > 0: display_price = regular_price
            elif sale_val > 0: display_price = sale_price
        except (ValueError, TypeError):
            display_price = regular_price or sale_price
            is_on_sale = False

        if display_price:
            price_x = width_px - margin
            price_y = height_px - margin
            price_width = price_font.getbbox(str(display_price))[2]
            gel_width = gel_font.getbbox("₾")[2]
            spacing = int(5 * scale_factor)
            main_price_total_width = price_width + gel_width + spacing
            price_block_width = main_price_total_width

            if is_on_sale and regular_price:
                old_price_width = strikethrough_font.getbbox(str(regular_price))[2]
                old_gel_width = gel_font_strikethrough.getbbox("₾")[2]
                old_price_total_width = old_price_width + old_gel_width + spacing
                price_block_width = max(main_price_total_width, old_price_total_width)
                strikethrough_y = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])
                price_block_top = strikethrough_y - (strikethrough_font.getmetrics()[0] + strikethrough_font.getmetrics()[1])
            else:
                price_block_top = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])
            price_block_left = price_x - price_block_width

        safety_margin = 15 * scale_factor
        overlap = (tile_x1 + safety_margin > price_block_left) and (tile_y1 + safety_margin > price_block_top)

        if not overlap:
            break

        current_model_font_size *= 0.95
        current_desc_font_size *= 0.95

        if current_model_font_size < 20:
            break

    # --- 3a. Draw 3D Tile ---
    radius = 15 * scale_factor
    shadow_offset = 8 * scale_factor
    shadow_color = (0, 0, 0, 80)
    draw.rounded_rectangle(
        [(tile_x0 + shadow_offset, tile_y0 + shadow_offset), (tile_x1 + shadow_offset, tile_y1 + shadow_offset)],
        radius=radius, fill=shadow_color
    )
    draw.rounded_rectangle(
        [(tile_x0, tile_y0), (tile_x1, tile_y1)],
        radius=radius, fill='white', outline=(220, 220, 220), width=max(1, int(2 * scale_factor))
    )

    # --- 3b. Draw Text on Tile ---
    y_cursor = text_y_start
    for line in wrapped_model_lines:
        draw.text((text_x, y_cursor), line, font=model_font, fill=text_color, anchor="la")
        y_cursor += model_line_height
    if wrapped_model_lines and wrapped_desc_lines:
        y_cursor += 5 * scale_factor
    for line in wrapped_desc_lines:
        draw.text((text_x, y_cursor), line, font=desc_font, fill=text_color, anchor="la")
        y_cursor += desc_line_height

    # --- 4. Price (Bottom Right) ---
    sale_price = item_data.get('Sale price', '').strip()
    regular_price = item_data.get('Regular price', '').strip()
    is_on_sale = False
    display_price = ""

    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        is_on_sale = sale_val > 0 and sale_val != regular_val

        if is_on_sale:
            display_price = sale_price
        elif regular_val > 0:
            display_price = regular_price
        elif sale_val > 0:
            display_price = sale_price
    except (ValueError, TypeError):
        display_price = regular_price or sale_price
        is_on_sale = False

    price_x = width_px - margin
    price_y = height_px - margin

    if display_price:
        price_text = str(display_price)
        gel_text = "₾"

        price_width = price_font.getbbox(price_text)[2]
        gel_width = gel_font.getbbox(gel_text)[2]
        spacing = int(5 * scale_factor)

        draw.text((price_x, price_y), price_text, font=price_font, fill=price_color, anchor="rs")
        draw.text((price_x - price_width - spacing, price_y), gel_text, font=gel_font, fill=price_color, anchor="rs")

        if is_on_sale and regular_price:
            old_price_text = str(regular_price)
            old_price_ascent, old_price_descent = strikethrough_font.getmetrics()
            old_price_height = old_price_ascent + old_price_descent

            strikethrough_y = price_y - (price_font.getmetrics()[0] + price_font.getmetrics()[1])

            old_price_width = strikethrough_font.getbbox(old_price_text)[2]
            old_gel_width = gel_font_strikethrough.getbbox(gel_text)[2]

            draw.text((price_x, strikethrough_y), old_price_text, font=strikethrough_font, fill=text_color, anchor="rs")
            draw.text((price_x - old_price_width - spacing, strikethrough_y), gel_text, font=gel_font_strikethrough,
                      fill=text_color, anchor="rs")

            total_old_width = old_price_width + old_gel_width + spacing
            line_y = strikethrough_y - (old_price_height / 2) + old_price_descent
            draw.line([(price_x - total_old_width, line_y), (price_x, line_y)], fill=text_color,
                      width=int(3 * scale_factor))

    # --- Final Border ---
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=3)

    return img


def _create_baseus_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """Creates a special price tag for Baseus with a modern, 3D design."""
    # --- Config ---
    bg_color = "#FFF100"
    text_color = "black"
    logo_path = theme.get('accessory_logo_path')

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
            print(f"Warning: Baseus logo not found at {logo_path}")
            y_cursor = content_margin
    else:
        y_cursor = content_margin

    # --- 2. Item Name ---
    name_text_raw = item_data.get('Name', 'N/A')
    # Filter out the word "Baseus"
    name_text = re.sub(r'\bBaseus\b', '', name_text_raw, flags=re.IGNORECASE).strip()
    name_text = ' '.join(name_text.split())  # Clean up extra spaces

    name_area_width = width_px - (2 * content_margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

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


def _create_acefast_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """Creates a special price tag for Acefast with a modern, 3D design."""
    # --- Config ---
    bg_color = "white"
    tile_color = "#536C4C"
    text_color = "white"
    logo_path = theme.get('accessory_logo_path')

    # --- Scaling ---
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_AREA)

    # --- Fonts ---
    base_name_font_size = 80
    base_price_font_size = 110
    base_sku_font_size = 65

    name_font = get_font(PRIMARY_FONT_BOLD_PATH, base_name_font_size * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_font_size * scale_factor, is_bold=True)
    gel_font = get_font(GEL_FONT_PATH, base_price_font_size * scale_factor, is_bold=True)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, base_sku_font_size * scale_factor, is_bold=True)

    # --- Background ---
    img = Image.new('RGB', (width_px, height_px), bg_color)
    draw = ImageDraw.Draw(img, 'RGBA')

    # --- Logo (on outer background) ---
    margin = 0.05 * width_px
    logo_area_height = height_px * 0.20
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo.thumbnail((width_px * 0.4, logo_area_height), Image.Resampling.LANCZOS)
                logo_x = int((width_px - logo.width) / 2)
                logo_y = int(margin)
                img.paste(logo, (logo_x, logo_y), logo)
                y_cursor = logo_y + logo.height
        except FileNotFoundError:
            print(f"Warning: Acefast logo not found at {logo_path}")
            y_cursor = margin
    else:
        y_cursor = margin

    # --- Main Content Tile (3D Effect) ---
    radius = 25 * scale_factor
    shadow_offset = 12 * scale_factor
    shadow_color = (0, 0, 0, 60)

    tile_y_start = y_cursor + margin
    tile_bbox = (margin, tile_y_start, width_px - margin, height_px - margin)

    # Draw shadow first
    draw.rounded_rectangle(
        [(tile_bbox[0] + shadow_offset, tile_bbox[1] + shadow_offset),
         (tile_bbox[2] + shadow_offset, tile_bbox[3] + shadow_offset)],
        radius=radius, fill=shadow_color
    )
    # Draw main tile
    draw.rounded_rectangle(tile_bbox, radius=radius, fill=tile_color, outline=(230, 230, 230), width=2)

    # --- Content Layout (inside the tile) ---
    content_margin = margin * 1.8
    
    # --- 2. Item Name ---
    name_text_raw = item_data.get('Name', 'N/A')
    # Filter out the word "Acefast"
    name_text = re.sub(r'\bAcefast\b', '', name_text_raw, flags=re.IGNORECASE).strip()
    name_text = ' '.join(name_text.split())  # Clean up extra spaces

    name_area_width = width_px - (2 * content_margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

    ascent, descent = name_font.getmetrics()
    line_height = ascent + descent
    total_text_height = len(wrapped_lines) * line_height
    
    # Center the name block vertically between top of tile and footer area
    footer_height = height_px * 0.25
    available_space = (height_px - margin - footer_height) - tile_y_start
    name_y_start = tile_y_start + (available_space - total_text_height) / 2

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


def _create_anker_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """Creates a special price tag for Anker with a modern, 3D design."""
    # --- Config ---
    bg_color = "#00A7E1"
    text_color = "black"
    logo_path = theme.get('accessory_logo_path')

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
            print(f"Warning: Anker logo not found at {logo_path}")
            y_cursor = content_margin
    else:
        y_cursor = content_margin

    # --- 2. Item Name ---
    name_text_raw = item_data.get('Name', 'N/A')
    # Filter out the word "Anker"
    name_text = re.sub(r'\bAnker\b', '', name_text_raw, flags=re.IGNORECASE).strip()
    name_text = ' '.join(name_text.split())  # Clean up extra spaces

    name_area_width = width_px - (2 * content_margin)
    wrapped_lines = wrap_text(name_text, name_font, name_area_width)

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


def create_price_tag(item_data, size_config, theme, layout_settings=None, language='en', is_special=False, background_cache=None):
    if layout_settings is None:
        layout_settings = get_default_layout_settings()

    width_cm, height_cm = size_config['dims']
    width_px, height_px = cm_to_pixels(width_cm), cm_to_pixels(height_cm)

    # --- ROUTING TO CORRECT TAG GENERATOR ---
    if theme.get('design') == 'bloody_modern':
        return _create_bloody_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
    if theme.get('design') == 'logitech_modern':
        return _create_logitech_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
    if theme.get('design') == 'epson_modern':
        return _create_epson_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
    if theme.get('design') == 'baseus_modern':
        return _create_baseus_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
    if theme.get('design') == 'acefast_modern':
        return _create_acefast_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
    if theme.get('design') == 'anker_modern':
        return _create_anker_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special)
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
        try:
            with Image.open(icon_path) as icon_img:
                icon_img = icon_img.convert("RGBA")
                icon_img.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
                img.paste(icon_img, (icon_x, icon_y), icon_img)
        except FileNotFoundError:
            print(f"Warning: Icon not found at {icon_path}")

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


def _draw_legion_hex_background(width, height, bg_color=(11, 16, 32), line_color1=(0, 178, 255, 110),
                                line_color2=(0, 107, 255, 90), line_width=4, size_ratio=0.14):
    """
    Creates a dark background with a hexagonal grid pattern using Legion blue tones.
    """
    # Background
    if isinstance(bg_color, str) and bg_color.startswith("#"):
        bg_color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Hex geometry (flat-top orientation)
    s = max(6, int(min(width, height) * size_ratio))  # hex radius/size
    dx = 1.5 * s
    dy = math.sqrt(3) * s

    # Helper to compute hex vertices around center (cx, cy)
    def hex_points(cx, cy, size):
        pts = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = cx + size * math.cos(angle)
            py = cy + size * math.sin(angle)
            pts.append((px, py))
        return pts

    # Tiling
    cols = int(width / dx) + 3
    rows = int(height / dy) + 3
    start_x = -dx
    start_y = -dy

    for col in range(cols):
        x = start_x + col * dx
        y_offset = dy / 2 if (col % 2 == 1) else 0
        for row in range(rows):
            y = start_y + row * dy + y_offset
            pts = hex_points(x, y, s)
            # Alternate colors subtly
            color = line_color1 if ((col + row) % 2 == 0) else line_color2
            # Ensure RGBA
            if isinstance(color, tuple) and len(color) == 3:
                color = color + (110,)
            # Draw edges for better control on width
            for i in range(6):
                p1 = pts[i]
                p2 = pts[(i + 1) % 6]
                draw.line([p1, p2], fill=color, width=line_width)

    return img


def _create_legion_accessory_tag(item_data, width_px, height_px, width_cm, height_cm, theme, background_cache=None):
    """
    Legion accessory tag:
    - Top header with centered Legion logo for contrast
    - Below: Name in a pill (centered)
    - Bottom-left: SKU in a pill
    - Bottom-right: Price (and discounted price if on sale) in a pill
    - Background: Hexagonal grid in Legion blue colors
    """
    # Scaling
    current_area = width_cm * height_cm
    scale_factor = math.sqrt(current_area / BASE_ACC_AREA)

    # Colors and fonts
    logo_path = theme.get('accessory_logo_path')
    name_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_NAME_FONT_SIZE * scale_factor, is_bold=True)
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_SKU_FONT_SIZE * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, BASE_ACC_PRICE_FONT_SIZE * scale_factor, is_bold=True)
    old_price_font = get_font(PRIMARY_FONT_PATH, int(BASE_ACC_PRICE_FONT_SIZE * 0.75 * scale_factor))
    gel_font = get_font(GEL_FONT_PATH, BASE_ACC_PRICE_FONT_SIZE * scale_factor, is_bold=True)
    gel_font_old = get_font(FALLBACK_FONT_GEORGIAN_REGULAR, int(BASE_ACC_PRICE_FONT_SIZE * 0.75 * scale_factor))

    margin_x = 0.06 * width_px
    margin_y = 0.06 * height_px
    border_width = max(2, int(3 * scale_factor))

    # Background (with optional cache) - larger hexes
    sku_value_key = item_data.get('SKU', 'N/A')
    if background_cache is not None and sku_value_key in background_cache:
        img = background_cache[sku_value_key].copy()
    else:
        bg_col = theme.get('legion_bg_color', '#0B1020')
        c1 = theme.get('legion_hex_color1', (0, 178, 255, 110))
        c2 = theme.get('legion_hex_color2', (0, 107, 255, 90))
        # Normalize hex strings to tuples if provided
        def to_rgba(c, default_alpha=110):
            if isinstance(c, str) and c.startswith("#"):
                rgb = tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
                return rgb + (default_alpha,)
            return c
        c1 = to_rgba(c1)
        c2 = to_rgba(c2)
        img = _draw_legion_hex_background(
            width_px, height_px,
            bg_color=bg_col, line_color1=c1, line_color2=c2,
            line_width=max(2, int(5 * scale_factor)),
            size_ratio=0.14
        )
        if background_cache is not None:
            background_cache[sku_value_key] = img.copy()

    draw = ImageDraw.Draw(img, 'RGBA')

    # Helper: draw vertical gradient rectangle
    def draw_vertical_gradient_rect(draw_ctx, bbox, start_color, end_color):
        x0, y0, x1, y1 = map(int, bbox)
        h = max(1, y1 - y0)
        for i in range(h):
            t = i / h
            r = int(start_color[0] * (1 - t) + end_color[0] * t)
            g = int(start_color[1] * (1 - t) + end_color[1] * t)
            b = int(start_color[2] * (1 - t) + end_color[2] * t)
            draw_ctx.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))

    # Helper: draw pill with blue shadows; optionally skip top shadow
    def draw_pill(bbox, radius, fill=(13, 18, 36), outline=(34, 48, 80, 200), shadow=True, skip_top=False):
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        o = ImageDraw.Draw(overlay, 'RGBA')
        x0, y0, x1, y1 = map(int, bbox)
        if shadow:
            shadow_offset = int(6 * scale_factor)
            shadow_color = (0, 122, 255, 160)  # Blue shadow for better print contrast
            # Shadows on all sides (left, right, bottom, top)
            offsets = [( shadow_offset,  0),  # right
                       (-shadow_offset,  0),  # left
                       ( 0,  shadow_offset)]  # bottom
            if not skip_top:
                offsets.append((0, -shadow_offset))  # top
            for dx, dy in offsets:
                o.rounded_rectangle(
                    [(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)],
                    radius=radius, fill=shadow_color
                )
        # Main pill
        o.rounded_rectangle([(x0, y0), (x1, y1)], radius=radius, fill=fill, outline=outline, width=max(1, int(2 * scale_factor)))
        # Paste shadows + pill
        img.paste(overlay, (0, 0), overlay)

    # Helper: gradient text rendering (kept for reference if needed elsewhere)
    def draw_gradient_text(text, font, center_pos=None, left_baseline_pos=None, gradient_colors=((0, 178, 255), (78, 91, 255))):
        # Measure
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= 0 or h <= 0:
            return (0, 0), (0, 0)
        # Mask
        text_img = Image.new('L', (w, h), 0)
        tdraw = ImageDraw.Draw(text_img)
        tdraw.text((-bbox[0], -bbox[1]), text, font=font, fill=255)
        # Gradient
        grad = Image.new('RGBA', (w, h))
        gdraw = ImageDraw.Draw(grad)
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(gradient_colors[0][0] * (1 - t) + gradient_colors[1][0] * t)
            g = int(gradient_colors[0][1] * (1 - t) + gradient_colors[1][1] * t)
            b = int(gradient_colors[0][2] * (1 - t) + gradient_colors[1][2] * t)
            gdraw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        grad.putalpha(text_img)
        # Position
        if center_pos is not None:
            cx, cy = center_pos
            px = int(cx - w / 2)
            py = int(cy - h / 2)
        elif left_baseline_pos is not None:
            lx, by = left_baseline_pos
            ascent, descent = font.getmetrics()
            px = int(lx)
            py = int(by - ascent)
        else:
            return (w, h), (0, 0)
        img.paste(grad, (px, py), grad)
        return (w, h), (px, py)

    # Helper: solid-colored text rendering with same positioning API
    def draw_colored_text(text, font, color, center_pos=None, left_baseline_pos=None):
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= 0 or h <= 0:
            return (0, 0), (0, 0)
        if center_pos is not None:
            cx, cy = center_pos
            px = int(cx - w / 2)
            py = int(cy - h / 2)
        elif left_baseline_pos is not None:
            lx, by = left_baseline_pos
            ascent, _ = font.getmetrics()
            px = int(lx)
            py = int(by - ascent)
        else:
            return (w, h), (0, 0)
        d = ImageDraw.Draw(img, 'RGBA')
        d.text((px, py), text, font=font, fill=color)
        return (w, h), (px, py)

    # Header bar to improve black logo visibility (solid blue)
    header_h = 0.28 * height_px
    header_color = (0, 107, 255)
    draw.rectangle([0, 0, width_px, int(header_h)], fill=header_color)

    # Logo centered in header
    logo_bottom_y = int(margin_y * 0.5)
    if logo_path:
        try:
            with Image.open(logo_path).convert("RGBA") as logo:
                logo_max_h = header_h * 0.7
                logo.thumbnail((int(width_px * 0.8), int(logo_max_h)), Image.Resampling.LANCZOS)
                logo_x = int((width_px - logo.width) / 2)
                logo_y = int((header_h - logo.height) / 2)
                img.paste(logo, (logo_x, logo_y), logo)
                logo_bottom_y = logo_y + logo.height
        except FileNotFoundError:
            print(f"Warning: Brand logo not found at {logo_path}")

    # Name inside pill, centered below header
    name_text = item_data.get('Name', 'N/A')
    name_area_width = width_px - (2 * margin_x)
    name_lines = wrap_text(name_text, name_font, int(name_area_width * 0.9))
    ascent, descent = name_font.getmetrics()
    line_h = ascent + descent
    line_spacing = int(6 * scale_factor)
    total_h = len(name_lines) * line_h + max(0, len(name_lines) - 1) * line_spacing
    pill_pad_x = int(20 * scale_factor)
    pill_pad_y = int(12 * scale_factor)
    pill_w = int(width_px - 2 * margin_x)
    pill_h = int(total_h + 2 * pill_pad_y)
    pill_x0 = int(margin_x)
    pill_x1 = int(width_px - margin_x)
    pill_y0 = int(logo_bottom_y + margin_y * 0.4)
    pill_y1 = int(pill_y0 + pill_h)
    radius = int(22 * scale_factor)
    draw_pill((pill_x0, pill_y0, pill_x1, pill_y1), radius, skip_top=True)

    # Draw solid blue name text lines centered
    blue_text = (0, 178, 255)
    y_cursor = pill_y0 + pill_pad_y + ascent
    for line in name_lines:
        draw_colored_text(line, name_font, blue_text, center_pos=(width_px / 2, y_cursor))
        y_cursor += line_h + line_spacing

    # Bottom-left: SKU in pill (value only)
    sku_text = item_data.get('SKU', 'N/A')
    sku_bbox_w = sku_font.getbbox(sku_text)[2] - sku_font.getbbox(sku_text)[0]
    sku_pill_pad_x = int(16 * scale_factor)
    sku_pill_pad_y = int(10 * scale_factor)
    sku_pill_w = sku_bbox_w + 2 * sku_pill_pad_x
    sku_pill_h = sku_font.getmetrics()[0] + sku_font.getmetrics()[1] + 2 * sku_pill_pad_y
    sku_x0 = int(margin_x)
    sku_y1 = int(height_px - margin_y)
    sku_y0 = int(sku_y1 - sku_pill_h)
    sku_x1 = int(sku_x0 + sku_pill_w)
    draw_pill((sku_x0, sku_y0, sku_x1, sku_y1), int(18 * scale_factor))
    draw_colored_text(sku_text, sku_font, (0, 178, 255), left_baseline_pos=(sku_x0 + sku_pill_pad_x, sku_y1 - sku_pill_pad_y))

    # Bottom-right: Price(s) in pill
    sale_price = str(item_data.get('Sale price', '')).strip()
    regular_price = str(item_data.get('Regular price', '')).strip()
    is_on_sale = False
    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0.0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0.0
        is_on_sale = sale_val > 0 and sale_val != regular_val
    except (ValueError, TypeError):
        is_on_sale = False

    def composite_width(price_str, p_font, gel_f):
        w_price = p_font.getbbox(price_str)[2] - p_font.getbbox(price_str)[0]
        w_gel = gel_f.getbbox("₾")[2] - gel_f.getbbox("₾")[0]
        sp = int(6 * scale_factor)
        return w_gel + sp + w_price, w_gel, w_price, sp

    if is_on_sale and sale_price:
        w_new, w_gel_new, w_price_new, sp_new = composite_width(sale_price, price_font, gel_font)
        w_old, w_gel_old, w_price_old, sp_old = composite_width(regular_price, old_price_font, gel_font_old) if regular_price else (0, 0, 0, 0)
        price_pill_w = max(w_new, w_old) + int(2 * 16 * scale_factor)
        line_gap = int(6 * scale_factor)
        line_h_new = price_font.getmetrics()[0] + price_font.getmetrics()[1]
        line_h_old = old_price_font.getmetrics()[0] + old_price_font.getmetrics()[1]
        price_pill_h = line_h_new + (line_h_old if regular_price else 0) + line_gap + int(2 * 12 * scale_factor)
    else:
        display_val = regular_price if regular_price else sale_price
        w_new, w_gel_new, w_price_new, sp_new = composite_width(display_val, price_font, gel_font) if display_val else (0, 0, 0, 0)
        price_pill_w = w_new + int(2 * 16 * scale_factor)
        line_h_new = price_font.getmetrics()[0] + price_font.getmetrics()[1]
        price_pill_h = line_h_new + int(2 * 12 * scale_factor)

    price_x1 = int(width_px - margin_x)
    price_x0 = int(price_x1 - price_pill_w)
    price_y1 = int(height_px - margin_y)
    price_y0 = int(price_y1 - price_pill_h)
    draw_pill((price_x0, price_y0, price_x1, price_y1), int(18 * scale_factor))

    # Draw price text inside pill (right-aligned within pill)
    def draw_price_line_right(price_str, p_font, gel_f, base_y):
        # total widths
        w_total, w_gel, w_p, sp = composite_width(price_str, p_font, gel_f)
        start_x = price_x1 - int(16 * scale_factor) - w_total
        blue_text = (0, 178, 255)
        # GEL
        draw_colored_text("₾", gel_f, blue_text, left_baseline_pos=(start_x, base_y))
        # Amount
        draw_colored_text(price_str, p_font, blue_text, left_baseline_pos=(start_x + w_gel + sp, base_y))
        return w_total, start_x

    # Baselines
    base_y_main = price_y1 - int(12 * scale_factor)
    if is_on_sale and sale_price:
        # old price above
        base_y_old = base_y_main - (price_font.getmetrics()[0] + price_font.getmetrics()[1]) - int(6 * scale_factor)
        if regular_price:
            _, old_start_x = draw_price_line_right(regular_price, old_price_font, gel_font_old, base_y_old)
            # Strikethrough
            old_total_w, _, _, _ = composite_width(regular_price, old_price_font, gel_font_old)
            asc_old, desc_old = old_price_font.getmetrics()
            strike_y = base_y_old - int((asc_old - desc_old) * 0.35)
            draw.line([(old_start_x, strike_y), (old_start_x + old_total_w, strike_y)],
                      fill=(127, 160, 191, 200), width=max(1, int(2 * scale_factor)))
        draw_price_line_right(sale_price, price_font, gel_font, base_y_main)
    else:
        display_val = regular_price if regular_price else sale_price
        if display_val:
            draw_price_line_right(display_val, price_font, gel_font, base_y_main)

    # Border
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=border_width)
    return img


def _create_epson_modern_tag(item_data, width_px, height_px, width_cm, height_cm, theme, language, is_special=False):
    """
    Epson modern tag:
    - Clean white canvas with a solid Epson-blue header band
    - Centered Epson logo in the header
    - Bold product name area beneath the header
    - Left-aligned compact specs with blue square bullets
    - Bottom-left SKU/P/N line
    - Bottom-right price tile with sale handling (old price above with strikethrough)
    """
    # Colors
    header_color = (0, 100, 168)  # #0064a8
    accent_color = (45, 124, 230) # Lighter accent blue
    text_color = "#0A0A0A"
    price_color = header_color

    # Scaling
    current_area = width_cm * height_cm
    base_area = BASE_AREA
    scale_factor = math.sqrt(current_area / base_area)

    # Fonts
    base_model_font_size = 84
    base_desc_font_size = 46
    base_price_font_size = 118
    base_strike_font_size = 76
    base_info_font_size = 42
    base_sku_font_size = 68  # slightly larger SKU in header

    name_font_bold = get_font(PRIMARY_FONT_BOLD_PATH, base_model_font_size * scale_factor, is_bold=True)
    name_font = get_font(PRIMARY_FONT_BOLD_PATH, base_desc_font_size * scale_factor, is_bold=True)
    price_font = get_font(PRIMARY_FONT_BOLD_PATH, base_price_font_size * scale_factor, is_bold=True)
    strike_font = get_font(PRIMARY_FONT_BOLD_PATH, base_strike_font_size * scale_factor, is_bold=True)
    info_font = get_font(PRIMARY_FONT_BOLD_PATH, base_info_font_size * scale_factor, is_bold=True)
    info_font_bold = info_font
    sku_font = get_font(PRIMARY_FONT_BOLD_PATH, base_sku_font_size * scale_factor, is_bold=True)
    gel_font = get_font(GEL_FONT_PATH, base_price_font_size * scale_factor, is_bold=True)
    gel_font_strike = get_font(GEL_FONT_PATH, base_strike_font_size * scale_factor)

    # Canvas
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img, 'RGBA')

    # Header (white for logo contrast) + underline
    margin = 0.05 * width_px
    header_h = 0.24 * height_px
    draw.rectangle([0, 0, width_px, int(header_h)], fill="white")
    draw.line([(0, int(header_h)), (width_px, int(header_h))], fill=header_color, width=max(2, int(4 * scale_factor)))

    # Logo aligned left in header; SKU in header top-right
    logo_path = theme.get('accessory_logo_path') or theme.get('logo_path') or resource_path("assets/brands/Epson.png")
    try:
        with Image.open(logo_path).convert("RGBA") as logo:
            logo_max_h = header_h * 0.7
            logo.thumbnail((int(width_px * 0.45), int(logo_max_h)), Image.Resampling.LANCZOS)
            lx = int(margin)
            ly = int((header_h - logo.height) / 2)
            img.paste(logo, (lx, ly), logo)
    except FileNotFoundError:
        print(f"Warning: Epson logo not found at {logo_path}")

    # SKU number (no label) in header top-right
    sku_header_val = item_data.get('SKU', 'N/A')
    draw.text((width_px - margin, header_h / 2), sku_header_val, font=sku_font, fill=header_color, anchor="rm")

    # Name area (use full name, bold)
    name_text = item_data.get('Name', 'N/A')

    # Compute wrapping
    name_area_x = margin
    name_area_y = header_h + (0.02 * height_px)
    name_area_w = width_px - (2 * margin)

    name_lines = wrap_text(name_text, name_font_bold, name_area_w)
    # Draw name centered
    y_cursor = name_area_y
    for line in name_lines:
        draw.text((width_px / 2, y_cursor), line, font=name_font_bold, fill=text_color, anchor="ma")
        y_cursor += name_font_bold.getmetrics()[0] + name_font_bold.getmetrics()[1]
    # Underline removed for cleaner look
    pass

    # Specs (left column)
    all_specs = item_data.get('all_specs', [])
    # Choose up to 4 concise specs excluding warranty; append warranty last if fits
    specs = []
    warranty = None
    for s in all_specs:
        if 'warranty' in s.lower():
            if warranty is None:
                warranty = s
            continue
        specs.append(s)
    if warranty:
        specs.append(warranty)
    specs = specs[:4]

    spec_font = get_font(PRIMARY_FONT_BOLD_PATH, (base_info_font_size - 2) * scale_factor, is_bold=True)
    bullet_size = int(12 * scale_factor)
    bullet_gap = int(10 * scale_factor)
    spec_y = y_cursor + (0.02 * height_px)
    for s in specs:
        # bullet
        bx = name_area_x
        by = spec_y + int(spec_font.getmetrics()[0] * 0.15)
        draw.rectangle([bx, by, bx + bullet_size, by + bullet_size], fill=accent_color)
        # text
        sx = bx + bullet_size + bullet_gap
        # translate label if key:value
        if ':' in s:
            label, value = s.split(':', 1)
            label_t = Translator().get_spec_label(label.strip(), language)
            label_text = f"{label_t}:"
            label_f = spec_font if not contains_georgian(label_text) else get_font(FALLBACK_FONT_GEORGIAN_BOLD, (base_info_font_size - 2) * scale_factor, is_bold=True)
            value_f = spec_font if not contains_georgian(value) else get_font(FALLBACK_FONT_GEORGIAN_BOLD, (base_info_font_size - 2) * scale_factor, is_bold=True)
            draw.text((sx, spec_y), label_text, font=label_f, fill=text_color, anchor="la")
            label_w = label_f.getbbox(label_text)[2]
            draw.text((sx + label_w + 6, spec_y), value.strip(), font=value_f, fill=text_color, anchor="la")
        else:
            s_font = spec_font if not contains_georgian(s) else get_font(FALLBACK_FONT_GEORGIAN_BOLD, (base_info_font_size - 2) * scale_factor, is_bold=True)
            draw.text((sx, spec_y), s, font=s_font, fill=text_color, anchor="la")
        spec_y += spec_font.getmetrics()[0] + spec_font.getmetrics()[1] + (4 * scale_factor)

    # Bottom-left: printer icon (larger)
    try:
        printer_icon_path = resource_path("assets/props/Printer.png")
        with Image.open(printer_icon_path).convert("RGBA") as printer_icon:
            icon_h = int(0.36 * height_px)  # ~3x larger than before
            printer_icon.thumbnail((icon_h, icon_h), Image.Resampling.LANCZOS)
            icon_x = int(margin)
            icon_y = int(height_px - margin - printer_icon.height)
            img.paste(printer_icon, (icon_x, icon_y), printer_icon)
    except FileNotFoundError:
        print("Warning: Printer icon not found at assets/props/Printer.png")

    # Price tile (bottom-right)
    sale_price = str(item_data.get('Sale price', '')).strip()
    regular_price = str(item_data.get('Regular price', '')).strip()
    is_on_sale_flag = False
    try:
        sale_val = float(sale_price.replace(',', '.')) if sale_price else 0
        regular_val = float(regular_price.replace(',', '.')) if regular_price else 0
        is_on_sale_flag = sale_val > 0 and sale_val != regular_val
    except (ValueError, TypeError):
        is_on_sale_flag = False

    def composite_width(price_str, p_font, g_font):
        w_price = p_font.getbbox(price_str)[2] - p_font.getbbox(price_str)[0]
        w_gel = g_font.getbbox("₾")[2] - g_font.getbbox("₾")[0]
        spacing = int(6 * scale_factor)
        return w_gel + spacing + w_price, w_gel, w_price, spacing

    # Compute tile size
    if is_on_sale_flag and sale_price:
        w_new, _, _, _ = composite_width(sale_price, price_font, gel_font)
        w_old, _, _, _ = composite_width(regular_price, strike_font, gel_font_strike) if regular_price else (0, 0, 0, 0)
        tile_w = max(w_new, w_old) + int(2 * 18 * scale_factor)
        tile_h = (price_font.getmetrics()[0] + price_font.getmetrics()[1]) + \
                 (strike_font.getmetrics()[0] + strike_font.getmetrics()[1]) + int(2 * 14 * scale_factor)
    else:
        display_val = regular_price if regular_price else sale_price
        w_new, _, _, _ = composite_width(display_val, price_font, gel_font) if display_val else (0, 0, 0, 0)
        tile_w = w_new + int(2 * 18 * scale_factor)
        tile_h = (price_font.getmetrics()[0] + price_font.getmetrics()[1]) + int(2 * 14 * scale_factor)

    tile_x1 = width_px - margin
    tile_x0 = tile_x1 - tile_w
    tile_y1 = height_px - margin
    tile_y0 = tile_y1 - tile_h

    # Draw tile (rounded rectangle with blue outline) + soft blue shadow (updated color)
    radius = int(18 * scale_factor)
    shadow_offset = int(5 * scale_factor)
    draw.rounded_rectangle([(tile_x0 + shadow_offset, tile_y0 + shadow_offset), (tile_x1 + shadow_offset, tile_y1 + shadow_offset)],
                           radius=radius, fill=(0, 100, 168, 90))
    draw.rounded_rectangle([(tile_x0, tile_y0), (tile_x1, tile_y1)], radius=radius,
                           outline=header_color, width=max(2, int(3 * scale_factor)), fill="white")

    # Price drawing (right-aligned inside tile)
    def draw_price_line_right(px_right, base_y, price_str, p_font, g_font, color, strike=False, strike_color=None):
        total_w, w_gel, w_p, spacing = composite_width(price_str, p_font, g_font)
        start_x = px_right - int(18 * scale_factor) - total_w
        draw.text((start_x, base_y), "₾", font=g_font, fill=color, anchor="ls")
        draw.text((start_x + w_gel + spacing, base_y), price_str, font=p_font, fill=color, anchor="ls")
        if strike:
            asc, desc = p_font.getmetrics()
            sy = base_y - int((asc - desc) * 0.35)
            draw.line([(start_x, sy), (start_x + total_w, sy)], fill=strike_color or color, width=max(1, int(2 * scale_factor)))
        return start_x, total_w

    base_y_main = tile_y1 - int(14 * scale_factor)
    if is_on_sale_flag and sale_price:
        base_y_old = base_y_main - (price_font.getmetrics()[0] + price_font.getmetrics()[1]) - int(6 * scale_factor)
        if regular_price:
            draw_price_line_right(tile_x1, base_y_old, regular_price, strike_font, gel_font_strike,
                                  color=(140, 140, 140), strike=True, strike_color=(120, 120, 120))
        draw_price_line_right(tile_x1, base_y_main, sale_price, price_font, gel_font, color=price_color)
    else:
        display_val = regular_price if regular_price else sale_price
        if display_val:
            asc, desc = price_font.getmetrics()
            center_y = (tile_y0 + tile_y1) / 2.0
            base_y_centered = int(center_y + (asc - desc) / 2.0)
            draw_price_line_right(tile_x1, base_y_centered, display_val, price_font, gel_font, color=price_color)

    # No sale overlay for Epson style
    pass

    # Border
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline='black', width=max(2, int(5 * scale_factor)))
    return img
