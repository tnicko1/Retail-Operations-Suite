import random
from PIL import Image, ImageDraw


def create_winter_theme(width=1000, height=800, filename="themes/winter.png"):
    """
    Generates a simple winter-themed background image with a dark blue
    gradient and snowflakes.
    """
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # --- Create a dark blue gradient ---
    top_color = (10, 20, 40)  # Dark navy blue
    bottom_color = (25, 45, 80)  # Slightly lighter blue
    for y in range(height):
        # Interpolate between the two colors
        r = top_color[0] + (bottom_color[0] - top_color[0]) * y // height
        g = top_color[1] + (bottom_color[1] - top_color[1]) * y // height
        b = top_color[2] + (bottom_color[2] - top_color[2]) * y // height
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # --- Draw random snowflakes ---
    for _ in range(150):  # Number of snowflakes
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(1, 4)
        # Use a light blue/white color with some transparency effect
        opacity = random.randint(100, 220)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(220, 230, 255, opacity)
        )

    print(f"Saving winter theme background to {filename}...")
    img.save(filename)
    print("Done.")


if __name__ == "__main__":
    # Ensure the themes directory exists
    import os

    if not os.path.exists('themes'):
        os.makedirs('themes')

    create_winter_theme()

