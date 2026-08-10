import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
audios = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))

removed = {
    "pg022_sec002.html", "pg022_sec003.html", "pg022_sec004.html", "pg035_sec003.html",
    "pg037_sec003.html", "pg038_sec001.html", "pg053_sec002.html", "pg062_sec001.html",
    "pg068_sec002.html", "pg076_sec001.html", "pg080_sec002.html", "pg080_sec003.html",
    "pg084_sec001.html", "pg088_sec002.html", "pg097_sec001.html",
}
hrefs = [entry["href"] for entry in pages]
assert len(pages) == 140
assert [entry["page_number"] for entry in pages] == list(range(1, 141))
assert not (removed & set(hrefs))
assert all(not (ROOT / name).exists() for name in removed)

for index, entry in enumerate(pages, 1):
    markup = (ROOT / entry["href"]).read_text(encoding="utf-8")
    assert f'<meta name="page-section-id" content="{index}"' in markup
    ids = re.findall(r'data-id="([^"]+)"', markup)
    assert len(ids) == len(set(ids)), entry["href"]

merge_expectations = {
    "pg022_sec001.html": {"pg022_sec001", "pg022_sec002", "pg022_sec003", "pg022_sec004"},
    "pg037_sec002.html": {"pg037_sec002", "pg037_sec003", "pg038_sec001"},
    "pg080_sec001.html": {"pg080_sec001", "pg080_sec002", "pg080_sec003"},
    "pg096_sec002.html": {"pg096_sec002", "pg097_sec001"},
}
for target, section_ids in merge_expectations.items():
    markup = (ROOT / target).read_text(encoding="utf-8")
    assert section_ids <= set(re.findall(r'data-section-id="([^"]+)"', markup))

for target in (
    "pg022_sec001.html", "pg035_sec002.html", "pg037_sec002.html",
    "pg053_sec001.html", "pg061_sec003.html", "pg075_sec001.html",
    "pg080_sec001.html", "pg083_sec002.html", "pg088_sec001.html",
    "pg096_sec002.html",
):
    markup = (ROOT / target).read_text(encoding="utf-8")
    content_tag = re.search(r'<div\b(?=[^>]*\bid="content")[^>]*>', markup).group(0)
    assert "flex flex-col gap-8" in content_tag, target

page70 = (ROOT / "pg070_sec001.html").read_text(encoding="utf-8")
assert page70.index("pg070_n0007") < page70.index("pg068_n0024") < page70.index("pg070_n0009")
assert "<textarea" not in (ROOT / "pg052_sec002.html").read_text(encoding="utf-8")
assert "list-none" in (ROOT / "pg093_sec001.html").read_text(encoding="utf-8")
assert "figure5-arrow" in (ROOT / "pg087_sec001.html").read_text(encoding="utf-8")

for text_id in ("pg027_n0022", "pg027_n0024", "pg027_n0026", "pg027_n0028", "pg027_n0030"):
    assert text_id not in texts and text_id not in audios

requested_audio = {
    "pg020_n0048", "pg020_n0049", "pg021_n0002", "pg031_n0009",
    "pg033_n0019", "pg033_n0021", "pg034_n0003", "pg034_n0005",
    "pg039_n0003", "pg039_n0005", "pg053_n0015", "pg053_n0031",
    "pg064_n0013", "pg064_n0041", "pg076_n0012",
}
for text_id in requested_audio:
    audio = ROOT / "content/i18n/en/audio" / audios[text_id]
    assert audio.stat().st_size > 1000, text_id

assert "Samantha" not in (ROOT / "tools/regenerate_review_audio.py").read_text(encoding="utf-8")
male_source = (ROOT / "tools/regenerate_all_male_audio.py").read_text(encoding="utf-8")
assert '"Daniel"' in male_source and '"Reed (English (UK))"' in male_source

print("PASS: round-two merges, layout corrections, navigation, and male narration are synchronized.")
