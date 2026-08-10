import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
texts = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
audios = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))

page27 = (ROOT / "pg027_sec002.html").read_text(encoding="utf-8")
shape_labels = {
    "pg027_n0022": ("a", "shape_pg027_im004_crop_v1.png"),
    "pg027_n0024": ("b", "shape_pg027_im003.png"),
    "pg027_n0026": ("c", "shape_pg027_im002.png"),
    "pg027_n0028": ("d", "shape_pg027_im005_crop_v1.png"),
    "pg027_n0030": ("e", "shape_pg027_im006.png"),
}
for text_id, (letter, filename) in shape_labels.items():
    assert page27.index(f'data-id="{text_id}"') < page27.index(filename)
    assert texts[text_id] == f"({letter})"
    assert (ROOT / "content/i18n/en/audio" / audios[text_id]).stat().st_size > 1000
assert page27.count("shape_pg027_") == 5

page46 = (ROOT / "pg046_sec001.html").read_text(encoding="utf-8")
assert "images/pg046_figure3_reference.png" in page46
assert 'class="sr-only"' in page46

page48 = (ROOT / "pg048_sec001.html").read_text(encoding="utf-8")
assert "images/pg048_figure6_reference.png" in page48
assert "text-3xl" not in page48

page61 = (ROOT / "pg061_sec003.html").read_text(encoding="utf-8")
assert "min-h-[980px]" not in page61
assert not re.search(r'<section[^>]*\bmin-h-screen\b', page61)
assert "mt-auto flex items-end" not in page61
assert "flex flex-col gap-3 container" in page61

for text_id in ("pg046_im001", "pg048_im002"):
    assert (ROOT / "content/i18n/en/audio" / audios[text_id]).stat().st_size > 1000

print("PASS: visual QA round three diagrams, labels, spacing and typography are synchronized.")
