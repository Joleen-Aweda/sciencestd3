import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_UPDATES = {
    "pg009_n0003": "Explore Figure 2 and its description, then describe the activities presented.",
    "pg014_n0032": "Items and equipment we use at home include clothes, soap, toothpaste, cooking gas, gas cylinders, tables, food utensils, televisions, fridges, radios and cars. Explore Figure 7 and its description.",
    "pg024_n0003": "Explore Figure 2 and its descriptions, then write the action presented in each picture.",
    "pg027_n0020": "Explore shapes (a) to (e) in Figure 5 and their descriptions, then name the colour of each shape.",
    "pg042_n0006": "(a) Explore Figure 1 and its description, then identify the things presented.",
    "pg051_n0017": "Explore Figure 8(a) and its description.",
    "pg052_n0004": "Explore Figure 8(b) and its description.",
    "pg067_n0008": "Explore Figure 19 and its description.",
    "pg069_n0006": "Explore Figure 21 and its description.",
    "pg069_n0018": "Explore Figure 22 and its description.",
    "pg071_n0005": "Explore Figure 23 and its descriptions.",
    "pg076_n0007": "Explore Figure 1 and its image descriptions, then answer the questions that follow.",
    "pg076_n0018": "1. What information is presented in Figure 1 and its image descriptions? Explain.",
    "pg090_n0003": "Explore Figure 1 and its image descriptions, then answer the questions that follow.",
    "pg090_n0007": "1. Which ICT devices are presented in Figure 1 and its image descriptions?",
    "pg092_n0011": "Explore Figure 2 and its description.",
    "pg097_n0006": "Explore the tower on the right and its description, including the signs on each piece shown in Figure 5.",
    "pg103_n0010": "Explore Figure 8 and its description.",
}

texts_path = ROOT / "content/i18n/en/texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
for text_id, value in TEXT_UPDATES.items():
    if text_id in texts:
        texts[text_id] = value
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value

# Catch any remaining direct visual instruction, including embedded sentences.
for text_id, value in list(texts.items()):
    if not isinstance(value, str):
        continue
    value = re.sub(
        r"\b(?:See|Look at|Observe)\s+Figure\s+([0-9]+(?:\s*\([a-z]\))?)\.",
        r"Explore Figure \1 and its description.",
        value,
        flags=re.IGNORECASE,
    )
    texts[text_id] = value

texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Synchronize the inline HTML fallback text for every updated text ID.
changed = 0
for path in ROOT.glob("pg*.html"):
    source = path.read_text(encoding="utf-8")
    updated = source
    for text_id, value in TEXT_UPDATES.items():
        pattern = re.compile(
            rf'(<[^>]+data-id="{re.escape(text_id)}"[^>]*>)(.*?)(</[^>]+>)',
            re.DOTALL,
        )
        updated, count = pattern.subn(
            lambda match: f"{match.group(1)}{value}{match.group(3)}",
            updated,
            count=1,
        )
        changed += count
    if updated != source:
        path.write_text(updated, encoding="utf-8")

print(f"Synchronized {changed} inclusive figure references in HTML.")
