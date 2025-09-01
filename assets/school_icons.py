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

from PIL import Image, ImageDraw

import random

def create_laptop_icon(size=(100, 100)):
    """Creates a simple, stylized laptop icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Laptop base
    draw.rectangle([10, 60, 90, 65], fill='#B0BEC5') # Light grey base
    # Laptop screen
    draw.rectangle([20, 20, 80, 58], fill='#37474F', outline='#B0BEC5', width=2) # Dark screen, grey border
    # Screen content (simple lines)
    draw.line([25, 25, 75, 25], fill='#80DEEA', width=3) # Cyan line
    draw.line([25, 35, 65, 35], fill='#80DEEA', width=3)
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

from PIL import Image, ImageDraw

def create_laptop_icon(size=(100, 100)):
    """Creates a simple, stylized laptop icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Laptop base
    draw.rectangle([10, 60, 90, 65], fill='#B0BEC5') # Light grey base
    # Laptop screen
    draw.rectangle([20, 20, 80, 58], fill='#37474F', outline='#B0BEC5', width=2) # Dark screen, grey border
    # Screen content (simple lines)
    draw.line([25, 25, 75, 25], fill='#80DEEA', width=3) # Cyan line
    draw.line([25, 35, 65, 35], fill='#80DEEA', width=3)
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

from PIL import Image, ImageDraw

def create_laptop_icon(size=(100, 100)):
    """Creates a simple, stylized laptop icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Laptop base
    draw.rectangle([10, 60, 90, 65], fill='#B0BEC5') # Light grey base
    # Laptop screen
    draw.rectangle([20, 20, 80, 58], fill='#37474F', outline='#B0BEC5', width=2) # Dark screen, grey border
    # Screen content (simple lines)
    draw.line([25, 25, 75, 25], fill='#80DEEA', width=3) # Cyan line
    draw.line([25, 35, 65, 35], fill='#80DEEA', width=3)
    draw.line([25, 45, 55, 45], fill='#80DEEA', width=3)

    return img

def create_book_icon(size=(100, 100)):
    """Creates a simple, stylized open book icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Book cover
    draw.rectangle([15, 20, 85, 80], fill='#4A90E2') # Blue cover
    # Pages
    draw.rectangle([20, 25, 80, 75], fill='white')
    # Center line
    draw.line([50, 25, 50, 75], fill='#D3D3D3', width=2)
    # Text lines simulation
    for y in range(30, 75, 8):
        draw.line([25, y, 48, y], fill='#A9A9A9', width=1)
        draw.line([52, y, 75, y], fill='#A9A9A9', width=1)

    return img

def create_ruler_icon(size=(100, 100)):
    """Creates a simple, stylized ruler icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Ruler body
    draw.rectangle([10, 40, 90, 60], fill='#FFC107') # Amber color

    # Markings
    for i in range(10, 91, 10):
        y_start = 40
        if (i // 10) % 2 == 0:
             y_start = 45 # Longer mark
        draw.line([i, y_start, i, 60], fill='black', width=2)

    return img

def create_checkmark_icon(size=(100, 100), color='#4CAF50'):
    """Creates a simple, green checkmark icon that scales properly."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    width, height = size
    scale_factor = min(width, height) / 100.0
    pen_width = max(1, int(12 * scale_factor))

    points = [
        (20 * scale_factor, 50 * scale_factor),
        (40 * scale_factor, 70 * scale_factor),
        (80 * scale_factor, 30 * scale_factor)
    ]
    draw.line(points, fill=color, width=pen_width, joint='round')

    return img

    return img

def create_book_icon(size=(100, 100)):
    """Creates a simple, stylized open book icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Book cover
    draw.rectangle([15, 20, 85, 80], fill='#4A90E2') # Blue cover
    # Pages
    draw.rectangle([20, 25, 80, 75], fill='white')
    # Center line
    draw.line([50, 25, 50, 75], fill='#D3D3D3', width=2)
    # Text lines simulation
    for y in range(30, 75, 8):
        draw.line([25, y, 48, y], fill='#A9A9A9', width=1)
        draw.line([52, y, 75, y], fill='#A9A9A9', width=1)

    return img

def create_ruler_icon(size=(100, 100)):
    """Creates a simple, stylized ruler icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Ruler body
    draw.rectangle([10, 40, 90, 60], fill='#FFC107') # Amber color

    # Markings
    for i in range(10, 91, 10):
        y_start = 40
        if (i // 10) % 2 == 0:
             y_start = 45 # Longer mark
        draw.line([i, y_start, i, 60], fill='black', width=2)

    return img



    return img

def create_book_icon(size=(100, 100)):
    """Creates a simple, stylized open book icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Book cover
    draw.rectangle([15, 20, 85, 80], fill='#4A90E2') # Blue cover
    # Pages
    draw.rectangle([20, 25, 80, 75], fill='white')
    # Center line
    draw.line([50, 25, 50, 75], fill='#D3D3D3', width=2)
    # Text lines simulation
    for y in range(30, 75, 8):
        draw.line([25, y, 48, y], fill='#A9A9A9', width=1)
        draw.line([52, y, 75, y], fill='#A9A9A9', width=1)

    return img

def create_ruler_icon(size=(100, 100)):
    """Creates a simple, stylized ruler icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Ruler body
    draw.rectangle([10, 40, 90, 60], fill='#FFC107') # Amber color

    # Markings
    for i in range(10, 91, 10):
        y_start = 40
        if (i // 10) % 2 == 0:
             y_start = 45 # Longer mark
        draw.line([i, y_start, i, 60], fill='black', width=2)

    return img

def create_checkmark_icon(size=(100, 100), color='#2E7D32'):
    """Creates a stylized, sketchy checkmark icon inside a circle."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    width, height = size
    scale_factor = min(width, height) / 100.0

    # --- Circle Background ---
    center_x, center_y = width / 2, height / 2
    radius = min(center_x, center_y) * 0.9
    # Draw a slightly thicker, off-white circle to look like a sticker
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill='#F5F5F5',
        outline='#E0E0E0',
        width=max(1, int(2 * scale_factor))
    )

    # --- Sketchy Checkmark ---
    pen_width = max(2, int(10 * scale_factor))
    points = [
        (width * 0.25, height * 0.5),
        (width * 0.45, height * 0.7),
        (width * 0.75, height * 0.3)
    ]

    # Draw multiple lines with slight offsets to create a sketchy effect
    for _ in range(3):
        offset_points = [
            (p[0] + random.uniform(-2, 2) * scale_factor, p[1] + random.uniform(-2, 2) * scale_factor)
            for p in points
        ]
        draw.line(offset_points, fill=color, width=pen_width, joint='round')

    return img
