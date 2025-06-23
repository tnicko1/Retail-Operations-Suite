from PIL import Image
from price_generator import cm_to_pixels

# Standard A4 size in cm
A4_WIDTH_CM, A4_HEIGHT_CM = 21.0, 29.7
DPI = 300


def create_a4_for_single(tag_image):
    """Creates a blank A4 sheet and pastes a single tag in the center."""
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)

    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')

    # Calculate coordinates to center the tag on the A4 sheet
    paste_x = (a4_w_px - tag_image.width) // 2
    paste_y = (a4_h_px - tag_image.height) // 2

    a4_sheet.paste(tag_image, (paste_x, paste_y))

    return a4_sheet


def calculate_layout(tag_width_cm, tag_height_cm):
    """
    Calculates how many tags can fit on a single A4 sheet.
    """
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)
    tag_w_px = cm_to_pixels(tag_width_cm, DPI)
    tag_h_px = cm_to_pixels(tag_height_cm, DPI)

    # Portrait orientation
    cols_portrait = a4_w_px // tag_w_px
    rows_portrait = a4_h_px // tag_h_px
    total_portrait = cols_portrait * rows_portrait

    # Landscape orientation (tags rotated)
    cols_landscape = a4_w_px // tag_h_px
    rows_landscape = a4_h_px // tag_w_px
    total_landscape = cols_landscape * rows_landscape

    if total_landscape > total_portrait:
        return {
            "total": total_landscape, "cols": cols_landscape, "rows": rows_landscape,
            "tag_dims": (tag_h_px, tag_w_px), "rotated": True
        }
    else:
        return {
            "total": total_portrait, "cols": cols_portrait, "rows": rows_portrait,
            "tag_dims": (tag_w_px, tag_h_px), "rotated": False
        }


def create_a4_sheet(tag_images, layout_info):
    """
    Pastes a list of tag images onto a blank A4 sheet for batch printing.
    """
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)
    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')

    tag_w, tag_h = layout_info['tag_dims']
    cols, rows = layout_info['cols'], layout_info['rows']

    grid_width = cols * tag_w
    grid_height = rows * tag_h
    start_x = (a4_w_px - grid_width) // 2
    start_y = (a4_h_px - grid_height) // 2

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
