import ast
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
texts = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
audios = json.loads((ROOT / "content/i18n/en/audios.json").read_text(encoding="utf-8"))

source_path = ROOT / "tools/implement_2026_review_corrections.py"
tree = ast.parse(source_path.read_text(encoding="utf-8"))
values = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {"TEXT_UPDATES", "REMOVE_IDS", "LABEL_ABOVE_IDS", "FILL_DISPLAY_PAGES"}:
                values[target.id] = ast.literal_eval(node.value)

assert [p["page_number"] for p in pages] == list(range(1, len(pages) + 1))
assert len(pages) == 140
assert json.loads((ROOT / "assets/config.json").read_text())["bundleVersion"] == "17"

for entry in pages:
    path = ROOT / entry["href"]
    assert path.exists(), path
    markup = path.read_text(encoding="utf-8")
    assert f'<meta name="page-section-id" content="{entry["page_number"]}"' in markup
    ids = re.findall(r'data-id="([^"]+)"', markup)
    assert len(ids) == len(set(ids)), f"duplicate narration IDs in {path.name}"

all_markup = "\n".join((ROOT / p["href"]).read_text(encoding="utf-8") for p in pages)
for text_id, expected in values["TEXT_UPDATES"].items():
    assert texts[text_id] == expected
    pattern = re.compile(
        rf'<(?P<tag>[A-Za-z0-9]+)\b[^>]*data-id="{re.escape(text_id)}"[^>]*>(.*?)</(?P=tag)>',
        re.DOTALL,
    )
    match = pattern.search(all_markup)
    assert match, f"missing inline text {text_id}"
    inline = re.sub(r"\s+", " ", html.unescape(re.sub(r"<br\s*/?>", "\n", match.group(2)))).strip()
    normalized_expected = re.sub(r"\s+", " ", expected).strip()
    assert inline == normalized_expected, f"inline/localized mismatch {text_id}: {inline!r}"
    filename = audios.get(text_id)
    assert filename and (ROOT / "content/i18n/en/audio" / filename.split("?", 1)[0]).stat().st_size > 1000, text_id

for text_id in values["REMOVE_IDS"]:
    assert text_id not in texts
    assert text_id not in audios
    assert f'data-id="{text_id}"' not in all_markup

for text_id in values["LABEL_ABOVE_IDS"]:
    if text_id in all_markup:
        tag = re.search(rf'<[^>]*data-id="{re.escape(text_id)}"[^>]*>', all_markup)
        assert tag and "adt-label-above" in tag.group(0)

assert sum("data-adt-fill-style" in (ROOT / p["href"]).read_text(encoding="utf-8") for p in pages) >= 9

assert "Figure 10 shows the parts of an ear" in texts["pg034_n0011"]
assert "pg028_n0013" in audios and "pg028_n0015" in audios
assert "↑ means up" in texts["pg094_n0005"]
assert all((ROOT / "content/i18n/en/audio" / audios[x].split("?", 1)[0]).read_bytes()[:3] in {b"ID3", b"\xff\xf3\x80", b"\xff\xf3\xc0", b"\xff\xfb\x90"} for x in values["TEXT_UPDATES"])
assert all_markup.count("<textarea") == 37

print("PASS: 132-row review implementation is synchronized across text, HTML, layout and narration.")
