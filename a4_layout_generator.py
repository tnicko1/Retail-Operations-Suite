from PIL import Image
from price_generator import cm_to_pixels

# Standard A4 size in cm
A4_WIDTH_CM, A4_HEIGHT_CM = 21.0, 29.7
DPI = 300


def calculate_layout(tag_width_cm, tag_height_cm):
    """
    Calculates how many tags can fit on a single A4 sheet.

    Returns:
        A dictionary with layout details.
    """
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)
    tag_w_px = cm_to_pixels(tag_width_cm, DPI)
    tag_h_px = cm_to_pixels(tag_height_cm, DPI)

    # Calculate how many fit in portrait orientation
    cols_portrait = a4_w_px // tag_w_px
    rows_portrait = a4_h_px // tag_h_px
    total_portrait = cols_portrait * rows_portrait

    # Calculate how many fit in landscape orientation (by rotating the tags)
    cols_landscape = a4_w_px // tag_h_px
    rows_landscape = a4_h_px // tag_w_px
    total_landscape = cols_landscape * rows_landscape

    # Choose the orientation that fits more tags
    if total_landscape > total_portrait:
        return {
            "total": total_landscape,
            "cols": cols_landscape,
            "rows": rows_landscape,
            "tag_dims": (tag_h_px, tag_w_px),  # Rotated
            "rotated": True
        }
    else:
        return {
            "total": total_portrait,
            "cols": cols_portrait,
            "rows": rows_portrait,
            "tag_dims": (tag_w_px, tag_h_px),  # Normal
            "rotated": False
        }


def create_a4_sheet(tag_images, layout_info):
    """
    Pastes a list of tag images onto a blank A4 sheet.

    Args:
        tag_images (list): A list of PIL Image objects for the tags.
        layout_info (dict): The layout details from calculate_layout.

    Returns:
        PIL.Image: The final A4 sheet image.
    """
    a4_w_px = cm_to_pixels(A4_WIDTH_CM, DPI)
    a4_h_px = cm_to_pixels(A4_HEIGHT_CM, DPI)

    a4_sheet = Image.new('RGB', (a4_w_px, a4_h_px), 'white')

    tag_w, tag_h = layout_info['tag_dims']
    cols, rows = layout_info['cols'], layout_info['rows']

    # Center the grid of tags on the page
    grid_width = cols * tag_w
    grid_height = rows * tag_h
    start_x = (a4_w_px - grid_width) // 2
    start_y = (a4_h_px - grid_height) // 2

    x, y = start_x, start_y
    img_idx = 0

    for _ in range(rows):
        for _ in range(cols):
            if img_idx < len(tag_images):
                tag_img = tag_images[img_idx]
                if layout_info['rotated']:
                    tag_img = tag_img.rotate(90, expand=True)

                a4_sheet.paste(tag_img, (x, y))
                img_idx += 1
            x += tag_w
        x = start_x
        y += tag_h

    return a4_sheet
