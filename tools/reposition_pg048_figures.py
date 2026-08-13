from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]

# Figure 5: remove the unused white margin while keeping a small clean border.
plant_source = Image.open(ROOT / "images/pg048_im001_seg001_v2.png").convert("RGB")
white = Image.new("RGB", plant_source.size, "white")
difference = ImageChops.difference(plant_source, white).convert("L")
mask = difference.point(lambda value: 255 if value > 8 else 0)
left, top, right, bottom = mask.getbbox()
padding = 4
crop_box = (
    max(0, left - padding),
    max(0, top - padding),
    min(plant_source.width, right + padding),
    min(plant_source.height, bottom + padding),
)
plant_source.crop(crop_box).save(ROOT / "images/pg048_im001_seg001_v3.png", optimize=True)

# Figure 6: move only the two labels and preserve all arrows and illustrations.
figure_source = Image.open(ROOT / "images/pg048_figure6_reference.png").convert("RGB")
figure = figure_source.copy()
draw = ImageDraw.Draw(figure)
draw.rectangle((145, 35, 305, 100), fill="white")
draw.rectangle((545, 260, 700, 325), fill="white")

font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 56)
draw.text((265, 70), "Light", font=font, fill=(0, 0, 0), anchor="mm")
draw.text((700, 351), "Light", font=font, fill=(0, 0, 0), anchor="rm")
figure.save(ROOT / "images/pg048_figure6_labels_centered.png", optimize=True)

print(f"Figure 5 crop: {crop_box}")
