"""Validate restored IDs and localized values for manual VS Code edits."""

import html
import json
import re
from pathlib import Path

from sync_manual_text_edits import MANUAL_IDS


ROOT = Path(__file__).resolve().parents[1]
TEXTS = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
AUDIOS = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))
MARKUP = "\n".join(page.read_text(encoding="utf-8") for page in sorted(ROOT.glob("pg*.html")))

for text_id in MANUAL_IDS:
    pattern = re.compile(
        rf'<(?P<tag>[A-Za-z0-9]+)\b[^>]*data-id="{re.escape(text_id)}"[^>]*>(.*?)</(?P=tag)>',
        re.DOTALL,
    )
    match = pattern.search(MARKUP)
    assert match, f"missing restored data-id {text_id}"
    inline = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(2)))).strip()
    assert TEXTS[text_id] == inline, f"inline/localized mismatch for {text_id}"
    filename = AUDIOS[text_id].split("?", 1)[0]
    assert (ROOT / "content/i18n/en/audio" / filename).stat().st_size > 1000

print(f"PASS: {len(MANUAL_IDS)} manual text edits have restored IDs, localized text, and narration.")
