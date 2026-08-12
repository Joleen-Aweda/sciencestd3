"""Synchronize the user's manually edited HTML sentences with i18n text."""

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/en/texts.json"
MANUAL_IDS = (
    "pg045_n0010", "pg047_n0008", "pg050_n0009", "pg051_n0017",
    "pg052_n0004", "pg060_n0021", "pg064_n0050", "pg066_n0022",
    "pg067_n0008", "pg067_n0022", "pg069_n0006", "pg069_n0017",
    "pg069_n0018", "pg084_n0032", "pg085_n0031", "pg090_n0003",
)


def main() -> None:
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    markup = "\n".join(page.read_text(encoding="utf-8") for page in sorted(ROOT.glob("pg*.html")))
    for text_id in MANUAL_IDS:
        pattern = re.compile(
            rf'<(?P<tag>[A-Za-z0-9]+)\b[^>]*data-id="{re.escape(text_id)}"[^>]*>(.*?)</(?P=tag)>',
            re.DOTALL,
        )
        match = pattern.search(markup)
        if not match:
            raise RuntimeError(f"Missing restored HTML data-id: {text_id}")
        value = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(2)))).strip()
        texts[text_id] = value
        easy_read_id = text_id + "_easy_read"
        if easy_read_id in texts:
            texts[easy_read_id] = value

    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synchronized {len(MANUAL_IDS)} manually edited sentences and their easy-read counterparts.")


if __name__ == "__main__":
    main()
