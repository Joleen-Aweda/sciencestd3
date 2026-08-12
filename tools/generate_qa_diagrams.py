from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"


def font(size: int, italic: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf" if italic else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf" if italic else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def arrow(draw, start, end, colour, width=5, head=14):
    draw.line([start, end], fill=colour, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        draw.polygon([(x2, y2), (x2 - direction * head, y2 - head // 2), (x2 - direction * head, y2 + head // 2)], fill=colour)
    else:
        direction = 1 if y2 > y1 else -1
        draw.polygon([(x2, y2), (x2 - head // 2, y2 - direction * head), (x2 + head // 2, y2 - direction * head)], fill=colour)


# Page 15: remove only the embedded duplicate letters, retaining the pen and pencil.
pen = Image.open(IMAGES / "pg015_im001.jpg").convert("RGB")
ImageDraw.Draw(pen).rectangle((136, 80, 188, 122), fill="white")
pen.save(IMAGES / "pg015_im001.jpg", quality=95)

pencil = Image.open(IMAGES / "pg015_im005.jpg").convert("RGB")
ImageDraw.Draw(pencil).rectangle((202, 90, 249, 132), fill="white")
pencil.save(IMAGES / "pg015_im005.jpg", quality=95)


# Page 25: bake labels into clean canvases so every leader line meets both target and word.
outer_source = Image.open(IMAGES / "pg025_im001_crop1_crop1_crop1.png").convert("RGBA").crop((0, 0, 522, 310))
ImageDraw.Draw(outer_source).rectangle((455, 250, 522, 310), fill="white")
outer = Image.new("RGBA", (1020, 430), "white")
outer_source = outer_source.resize((626, 372), Image.Resampling.LANCZOS)
outer.paste(outer_source, (197, 26), outer_source)
d = ImageDraw.Draw(outer)
label_font = font(35, italic=True)
d.text((8, 175), "Eyelashes", fill="#262626", font=label_font)
d.line([(174, 204), (208, 229)], fill="#262626", width=3)
d.text((823, 78), "Eyebrows", fill="#262626", font=label_font)
d.text((823, 218), "Eyelids", fill="#262626", font=label_font)
outer.convert("RGB").save(IMAGES / "pg025_outer_labeled.png")

inner_source = Image.open(IMAGES / "pg025_im002_crop_v1.png").convert("RGBA")
inner = Image.new("RGBA", inner_source.size, "white")
inner.paste(inner_source, (0, 0), inner_source)
d = ImageDraw.Draw(inner)
small_font = font(34, italic=True)
d.text((8, 176), "Iris", fill="#262626", font=small_font)
d.text((8, 238), "Pupil", fill="#262626", font=small_font)
d.text((8, 314), "Lens", fill="#262626", font=small_font)
d.text((880, 70), "Retina", fill="#262626", font=small_font)
inner.convert("RGB").save(IMAGES / "pg025_inner_labeled.png")


# Page 46: rebuild Figure 3 from the clean component art, with no black arrow after “Light”.
fig3 = Image.new("RGB", (1600, 846), "white")
d = ImageDraw.Draw(fig3)
plant_top = Image.open(IMAGES / "pg046_im001.jpg").convert("RGB").resize((330, 600), Image.Resampling.LANCZOS)
plant_left = Image.open(IMAGES / "pg046_im002_seg001_v1.png").convert("RGB").resize((330, 600), Image.Resampling.LANCZOS)
plant_right = Image.open(IMAGES / "pg046_im002_seg002_v1.png").convert("RGB").resize((330, 600), Image.Resampling.LANCZOS)
fig3.paste(plant_top, (130, 205))
fig3.paste(plant_left, (635, 205))
fig3.paste(plant_right, (1140, 205))
light_font = font(55, italic=True)
d.text((220, 55), "Light", fill="#111111", font=light_font)
d.text((515, 360), "Light", fill="#111111", font=light_font)
d.text((1480, 360), "Light", fill="#111111", font=light_font, anchor="ra")
fig3.save(IMAGES / "pg046_figure3_reference.png")


# Page 48: rebuild Figure 6 with the original-style arrows aimed at the box hole.
fig6 = Image.new("RGB", (1600, 600), "white")
d = ImageDraw.Draw(fig6)
plant = Image.open(IMAGES / "pg048_im003.jpg").convert("RGB").resize((330, 420), Image.Resampling.LANCZOS)
box = Image.open(IMAGES / "pg048_im002.jpg").convert("RGB").resize((650, 485), Image.Resampling.LANCZOS)
fig6.paste(plant, (120, 145))
fig6.paste(box, (850, 85))
d.text((165, 40), "Light", fill="#222222", font=light_font)
for x in (205, 265, 325):
    arrow(d, (x, 105), (x, 155), "#e6007e", width=5, head=18)
d.text((565, 270), "Light", fill="#222222", font=light_font)
for y in (315, 350, 385):
    arrow(d, (710, y), (845, y), "#e6007e", width=5, head=18)
fig6.save(IMAGES / "pg048_figure6_reference.png")

print("Generated corrected diagrams for pages 15, 25, 46 and 48.")
