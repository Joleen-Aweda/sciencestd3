from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "images/pg046_figure3_reference.png"
TARGET = ROOT / "images/pg046_figure3_labels_centered.png"

source_image = Image.open(SOURCE).convert("RGB")
image = source_image.copy()
draw = ImageDraw.Draw(image)

# Clear the former labels without touching the plant illustrations or arrows.
draw.rectangle((205, 45, 360, 125), fill="white")
draw.rectangle((495, 350, 646, 420), fill="white")
pixels = image.load()
source_pixels = source_image.load()
for y in range(350, 425):
    # Reconstruct the narrow part of the illustration hidden by the old label.
    replacement = source_pixels[1348, y]
    for x in range(1355, 1372):
        red, green, blue = pixels[x, y]
        if max(red, green, blue) < 225 and max(red, green, blue) - min(red, green, blue) < 22:
            pixels[x, y] = replacement
    # The rest of the old label sat on the white margin. Preserve only red arrows.
    for x in range(1373, 1495):
        red, green, blue = source_pixels[x, y]
        pixels[x, y] = (red, green, blue) if red > 130 and red > green * 1.25 and red > blue * 1.25 else (255, 255, 255)

# Restore the short box edge that sat behind the former right-hand label.
draw.line((1372, 310, 1372, 414), fill=(25, 25, 25), width=3)
for y in range(350, 425):
    for x in range(1368, 1420):
        red, green, blue = source_pixels[x, y]
        if red > 130 and red > green * 1.25 and red > blue * 1.25:
            pixels[x, y] = (red, green, blue)

font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 56)
draw.text((291, 240), "Light", font=font, fill=(0, 0, 0), anchor="mm")
draw.text((640, 460), "Light", font=font, fill=(0, 0, 0), anchor="rm")
draw.text((1420, 450), "Light", font=font, fill=(0, 0, 0), anchor="lm")

image.save(TARGET, optimize=True)
print(TARGET)
