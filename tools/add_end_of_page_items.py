import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES_PATH = ROOT / "content/pages.json"
TEXTS_PATH = ROOT / "content/i18n/en/texts.json"
AUDIOS_PATH = ROOT / "content/i18n/en/audios.json"
SHARED_AUDIO = "end_of_page.mp3?v=1"


pages = json.loads(PAGES_PATH.read_text(encoding="utf-8"))
texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
audios = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))

terminal_pattern = re.compile(
    r"\n?\s*<span[^>]*data-adt-end-of-page[^>]*>.*?</span>\s*",
    re.DOTALL,
)

for page in pages:
    section_id = page["section_id"]
    terminal_id = f"{section_id}_end"
    page_path = ROOT / page["href"]
    html = page_path.read_text(encoding="utf-8")
    html = terminal_pattern.sub("\n", html)
    terminal = (
        f'      <span data-id="{terminal_id}" data-adt-end-of-page="true" '
        'class="sr-only">End of page.</span>\n'
    )
    if "</main>" not in html:
        raise RuntimeError(f"No closing main element in {page_path.name}")
    html = html.replace("</main>", f"{terminal}</main>", 1)
    page_path.write_text(html, encoding="utf-8")

    texts[terminal_id] = "End of page."
    texts[f"{terminal_id}_easy_read"] = "End of page."
    audios[terminal_id] = SHARED_AUDIO
    audios[f"{terminal_id}_easy_read"] = SHARED_AUDIO

TEXTS_PATH.write_text(
    json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
AUDIOS_PATH.write_text(
    json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(f"Added one terminal narration item to {len(pages)} reader sections.")
