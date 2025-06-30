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


def calculate_layout(tag_width_cm, tag_height_cm):
    """
    Calculates how many tags can fit on a single A4 sheet.
    """
    a4_w_px, a4_h_px = cm_to_pixels(A4_WIDTH_CM), cm_to_pixels(A4_HEIGHT_CM)
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


def create_a4_sheet(tag_images, layout_info):
    """
    Pastes a list of tag images onto a blank A4 sheet for batch printing.
    The grid of tags is centered on the page.
    """
    a4_w_px, a4_h_px = cm_to_pixels(A4_WIDTH_CM), cm_to_pixels(A4_HEIGHT_CM)
    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')

    tag_w, tag_h = layout_info['tag_dims']
    cols, rows = layout_info['cols'], layout_info['rows']

    # Center the entire grid of tags on the full A4 page.
    grid_width, grid_height = cols * tag_w, rows * tag_h
    start_x, start_y = (a4_w_px - grid_width) // 2, (a4_h_px - grid_height) // 2

    x, y = start_x, start_y
    for i, tag_img in enumerate(tag_images):
        if i > 0 and i % cols == 0:
            y += tag_h
            x = start_x
        if layout_info['rotated']:
            tag_img = tag_img.rotate(90, expand=True)
        a4_sheet.paste(tag_img, (x, y))
        x += tag_w

    return a4_sheet
