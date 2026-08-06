import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\bSee\s+Figure\s+([0-9]+(?:\s*\([a-z]\))?)\.", re.IGNORECASE)

changed = 0
for path in [*ROOT.glob("*.html"), ROOT / "content/i18n/en/texts.json"]:
    source = path.read_text(encoding="utf-8")
    updated, count = PATTERN.subn(
        r"Refer to Figure \1 and its description.", source
    )
    if count:
        path.write_text(updated, encoding="utf-8")
        changed += count

print(f"Updated {changed} figure references.")
