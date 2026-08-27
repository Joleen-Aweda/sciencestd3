import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
audios = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))

assert len(pages) == 141

for page in pages:
    section_id = page["section_id"]
    terminal_id = f"{section_id}_end"
    html = (ROOT / page["href"]).read_text(encoding="utf-8")
    assert html.count('data-adt-end-of-page="true"') == 1, page["href"]
    assert html.index('data-adt-end-of-page="true"') < html.index("</main>"), page["href"]
    assert texts[terminal_id] == "End of page."
    assert texts[f"{terminal_id}_easy_read"] == "End of page."
    assert audios[terminal_id].startswith("end_of_page.mp3")
    assert audios[f"{terminal_id}_easy_read"].startswith("end_of_page.mp3")

chapter_files = [ROOT / page["href"] for page in pages if 119 <= page["page_number"] <= 141]
chapter_html = "\n".join(path.read_text(encoding="utf-8") for path in chapter_files)
assert not re.search(r"\bbackend\b", chapter_html, re.IGNORECASE)
assert "Accessible alternative:" in (ROOT / "pg100_sec002.html").read_text(encoding="utf-8")
assert "Figure 7 shows the original simple drawing game" in (ROOT / "pg101_sec001.html").read_text(encoding="utf-8")

for image_id in (
    "pg090_im001",
    "pg091_im001",
    "pg092_im001_crop1",
    "pg094_im001",
    "pg095_im001",
    "pg097_im001_crop_v1",
    "pg099_im001",
    "pg099_im002",
    "pg101_im001",
    "pg101_im002",
    "pg103_im001_crop1",
):
    description = texts.get(image_id, "")
    assert len(description.split()) >= 12, image_id

print("PASS: final English accessibility checks")
