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

from PIL import Image
from price_generator import cm_to_pixels

# Standard A4 size in cm
A4_WIDTH_CM, A4_HEIGHT_CM = 21.0, 29.7
DPI = 300

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    if n <= 0: return
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_a4_for_dual_single(tag_en, tag_ka):
    """
    Arranges two tags (EN and KA) on an A4 sheet, stuck together.
    Returns a list of one or two A4 images depending on whether they fit.
    """
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)
    tag_w, tag_h = tag_en.width, tag_en.height

    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')

    # Try to fit side-by-side
    if (tag_w * 2) <= a4_w_px and tag_h <= a4_h_px:
        # Center the combined block of two tags on the full A4 page
        start_x = (a4_w_px - (tag_w * 2)) // 2
        y_pos = (a4_h_px - tag_h) // 2
        a4_sheet.paste(tag_en, (start_x, y_pos))
        a4_sheet.paste(tag_ka, (start_x + tag_w, y_pos))
        return [a4_sheet]

    # Try to fit top-and-bottom
    elif tag_w <= a4_w_px and (tag_h * 2) <= a4_h_px:
        # Center the combined block of two tags on the full A4 page
        x_pos = (a4_w_px - tag_w) // 2
        start_y = (a4_h_px - (tag_h * 2)) // 2
        a4_sheet.paste(tag_en, (x_pos, start_y))
        a4_sheet.paste(tag_ka, (x_pos, start_y + tag_h))
        return [a4_sheet]

    # If they don't fit together, return them on separate A4 sheets
    else:
        a4_en = Image.new('RGB', (a4_w_px, a4_h_px), 'white')
        a4_en.paste(tag_en, ((a4_w_px - tag_w) // 2, (a4_h_px - tag_h) // 2))

        a4_ka = Image.new('RGB', (a4_w_px, a4_h_px), 'white')
        a4_ka.paste(tag_ka, ((a4_w_px - tag_w) // 2, (a4_h_px - tag_h) // 2))
        return [a4_en, a4_ka]


def create_a4_for_single(tag_image):
    """Creates a blank A4 sheet and pastes a single tag in the center."""
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)
    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')
    a4_sheet.paste(tag_image, ((a4_w_px - tag_image.width) // 2, (a4_h_px - tag_image.height) // 2))
    return a4_sheet


def calculate_layout(tag_width_cm, tag_height_cm, margin_h_cm=0.7, margin_v_cm=1.0):
    """
    Calculates how many tags can fit on a single A4 sheet,
    considering safe horizontal and vertical margins from the paper edge.
    """
    # A4 dimensions minus the margin on both sides
    printable_width_cm = A4_WIDTH_CM - (2 * margin_h_cm)
    printable_height_cm = A4_HEIGHT_CM - (2 * margin_v_cm)

    a4_w_px, a4_h_px = cm_to_pixels(printable_width_cm), cm_to_pixels(printable_height_cm)
    tag_w_px, tag_h_px = cm_to_pixels(tag_width_cm), cm_to_pixels(tag_height_cm)

    if tag_w_px <= 0 or tag_h_px <= 0:
        return {"total": 0, "cols": 0, "rows": 0, "tag_dims": (0, 0), "rotated": False}


    # Portrait: Calculate fit
    cols_p, rows_p = a4_w_px // tag_w_px, a4_h_px // tag_h_px
    total_p = cols_p * rows_p

    # Landscape (tags rotated): Calculate fit
    cols_l, rows_l = a4_w_px // tag_h_px, a4_h_px // tag_w_px
    total_l = cols_l * rows_l

    if total_l > total_p:
        return {"total": total_l, "cols": cols_l, "rows": rows_l, "tag_dims": (tag_h_px, tag_w_px), "rotated": True}
    else:
        return {"total": total_p, "cols": cols_p, "rows": rows_p, "tag_dims": (tag_w_px, tag_h_px), "rotated": False}


def create_a4_layouts(tag_images, layout_info, margin_cm=0.5):
    """
    Pastes a list of tag images onto one or more blank A4 sheets for batch printing.
    The grid of tags is centered on each page within a safe margin.
    Returns a list of A4 sheet images.
    """
    a4_w_px, a4_h_px = cm_to_pixels(A4_WIDTH_CM), cm_to_pixels(A4_HEIGHT_CM)
    tag_w, tag_h = layout_info['tag_dims']
    cols, rows = layout_info['cols'], layout_info['rows']
    tags_per_sheet = layout_info['total']

    if tags_per_sheet == 0:
        return []

    # Calculate the total size of the grid
    grid_width, grid_height = cols * tag_w, rows * tag_h

    # Calculate the available printable area based on the margin
    margin_px = cm_to_pixels(margin_cm)
    printable_width = a4_w_px - (2 * margin_px)
    printable_height = a4_h_px - (2 * margin_px)

    # Center the grid on the page.
    start_x = (a4_w_px - grid_width) // 2
    start_y = (a4_h_px - grid_height) // 2

    a4_sheets = []
    for sheet_tags in chunks(tag_images, tags_per_sheet):
        a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')
        x, y = start_x, start_y
        for i, tag_img in enumerate(sheet_tags):
            if i > 0 and i % cols == 0:
                y += tag_h
                x = start_x
            if layout_info['rotated']:
                tag_img = tag_img.rotate(90, expand=True)
            a4_sheet.paste(tag_img, (x, y))
            x += tag_w
        a4_sheets.append(a4_sheet)

    return a4_sheets
