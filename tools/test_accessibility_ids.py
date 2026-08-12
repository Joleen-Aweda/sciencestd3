"""Audit page data IDs, image descriptions, and narration mappings."""

import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
TEXTS = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
AUDIOS = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))
AUDIO_DIR = ROOT / "content/i18n/en/audio"


class PageParser(HTMLParser):
    def __init__(self, page: Path) -> None:
        super().__init__()
        self.page = page
        self.data_ids: list[tuple[str, str]] = []
        self.duplicate_ids: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("data-id"):
            self.data_ids.append((values["data-id"], tag))
        if values.get("data-duplicate-id"):
            self.duplicate_ids.append((values["data-duplicate-id"], tag))
        if tag == "img":
            self.images.append(values)


seen: dict[str, Path] = {}
duplicate_seen: set[str] = set()
image_count = 0
for page in sorted(ROOT.glob("pg*.html")):
    parser = PageParser(page)
    parser.feed(page.read_text(encoding="utf-8"))
    for text_id, tag in parser.data_ids:
        assert text_id not in seen, f"duplicate data-id {text_id}: {seen[text_id]} and {page}"
        seen[text_id] = page
        assert text_id in TEXTS, f"missing localized text for {text_id} in {page.name}"
        assert text_id in AUDIOS, f"missing narration mapping for {text_id} in {page.name}"
    for text_id, tag in parser.duplicate_ids:
        duplicate_seen.add(text_id)
        assert text_id in TEXTS, f"missing duplicate localized text for {text_id} in {page.name}"
        assert text_id in AUDIOS, f"missing duplicate narration mapping for {text_id} in {page.name}"
    for image in parser.images:
        image_count += 1
        text_id = image.get("data-id") or image.get("data-duplicate-id")
        assert text_id, f"image without data ID in {page.name}: {image.get('src')}"
        assert image.get("alt", "").strip(), f"image without alt text in {page.name}: {image.get('src')}"
        assert text_id in TEXTS, f"missing image description {text_id} in {page.name}"
        assert len(TEXTS[text_id].split()) >= 3, f"image description is too short for {text_id}"
        assert TEXTS[text_id].startswith(("Image (", "This image shows", "This diagram shows")), f"image description is not explicit for {text_id}"
        assert image.get("alt", "").strip() == TEXTS[text_id], f"HTML alt/localized description mismatch for {text_id}"
        assert text_id in AUDIOS, f"missing image narration mapping for {text_id}"

for text_id, filename in AUDIOS.items():
    assert filename.endswith("?v=20"), f"audio mapping is not cache-versioned: {text_id} -> {filename}"
    audio = AUDIO_DIR / filename.split("?", 1)[0]
    assert audio.exists(), f"missing narration file for {text_id}: {filename}"
    assert audio.stat().st_size > 1000, f"invalid narration file for {text_id}: {filename}"

assert image_count == 186, f"expected 186 displayed images, found {image_count}"
for required in (
    "pg001_im001", "pg005_im006", "pg008_n0004", "pg009_n0006",
    "pg009_n0008", "pg009_n0010", "pg041_n0013", "pg041_n0014",
    "pg041_n0015", "pg041_n0016", "pg054_n0017", "pg054_n0018",
    "pg054_n0019", "pg054_n0020",
):
    assert required in seen or required in duplicate_seen, f"restored data ID is missing from HTML: {required}"
print(f"PASS: {len(seen)} unique data IDs and {image_count} described images are fully narrated.")
