"""Standardize every displayed image description and HTML alt fallback."""

import html
import json
import re
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/en/texts.json"
TEXTS = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
IMG_RE = re.compile(r"<img\b[^>]*>", re.DOTALL)
ID_RE = re.compile(r'data-(?:id|duplicate-id)="([^"]+)"')
ALT_RE = re.compile(r'alt="[^"]*"', re.DOTALL)
NEARBY_ID_RE = re.compile(r'data-(?:id|duplicate-id)="([^"]+)"')
LETTER_RE = re.compile(r"^\(([a-z])\)$", re.IGNORECASE)
LABELED_RE = re.compile(r",?\s*(?:and\s+)?labeled\s*\(([a-z])\)\.?$", re.IGNORECASE)


def nearby_letter(markup: str, start: int, end: int) -> Optional[str]:
    after_limit = markup.find("<img", end)
    after = markup[end:(after_limit if 0 <= after_limit <= end + 900 else end + 900)]
    for text_id in NEARBY_ID_RE.findall(after):
        match = LETTER_RE.fullmatch(TEXTS.get(text_id, "").strip())
        if match:
            return match.group(1).lower()
    before_start = max(markup.rfind("<img", 0, start), start - 900)
    before = markup[before_start:start]
    candidates = []
    for text_id in NEARBY_ID_RE.findall(before):
        match = LETTER_RE.fullmatch(TEXTS.get(text_id, "").strip())
        if match:
            candidates.append(match.group(1).lower())
    return candidates[-1] if candidates else None


def lowercase_opening(description: str) -> str:
    if description.startswith("An "):
        return "an " + description[3:]
    if description.startswith("A "):
        return "a " + description[2:]
    if description.startswith("The "):
        return "the " + description[4:]
    return description[:1].lower() + description[1:]


def standardize(description: str, label: Optional[str]) -> str:
    description = description.strip()
    labeled = LABELED_RE.search(description)
    if labeled:
        label = labeled.group(1).lower()
        description = LABELED_RE.sub(".", description).strip()
    description = description.rstrip(".") + "."
    lower = description.lower()
    if label:
        return f"Image ({label}). {description}"
    if lower.startswith("diagram of "):
        return "This diagram shows " + lowercase_opening(description[len("Diagram of "):])
    if lower.startswith("cross-section of "):
        return "This diagram shows a cross-section of " + description[len("Cross-section of "):]
    if lower.startswith("labeled cross-section of "):
        return "This diagram shows a labeled cross-section of " + description[len("Labeled cross-section of "):]
    return f"This image shows the following. {description}"


descriptions: dict[str, str] = {}
pages: dict[Path, str] = {}
for page in sorted(ROOT.glob("pg*.html")):
    markup = page.read_text(encoding="utf-8")
    pages[page] = markup
    for match in IMG_RE.finditer(markup):
        id_match = ID_RE.search(match.group(0))
        if not id_match:
            continue
        text_id = id_match.group(1)
        if text_id in descriptions:
            continue
        original = TEXTS[text_id]
        descriptions[text_id] = standardize(original, nearby_letter(markup, match.start(), match.end()))

for text_id, description in descriptions.items():
    TEXTS[text_id] = description

TEXTS_PATH.write_text(json.dumps(TEXTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for page, markup in pages.items():
    def replace_alt(match: re.Match[str]) -> str:
        tag = match.group(0)
        id_match = ID_RE.search(tag)
        if not id_match:
            return tag
        description = descriptions[id_match.group(1)]
        escaped = html.escape(description, quote=True)
        replacement = f'alt="{escaped}"'
        return ALT_RE.sub(replacement, tag) if ALT_RE.search(tag) else tag[:-1] + f" {replacement}>"

    updated = IMG_RE.sub(replace_alt, markup)
    page.write_text(updated, encoding="utf-8")

print(f"Standardized {len(descriptions)} unique descriptions across {len(pages)} page files.")
