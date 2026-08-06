import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def replace(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path}: {old!r}")
    p.write_text(text.replace(old, new), encoding="utf-8")

text_updates = {
    "pg051_n0017": "Observe Figure 8(a).",
    "pg052_n0004": "Observe Figure 8(b).",
    "pg067_n0008": "Observe Figure 19.",
    "pg069_n0006": "Observe Figure 21.",
    "pg069_n0018": "Observe Figure 22.",
    "pg071_n0005": "Observe Figure 23.",
    "pg092_n0011": "Observe Figure 2.",
    "pg103_n0010": "Observe Figure 8.",
}
texts_path = ROOT / "content/i18n/en/texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
for key, value in text_updates.items():
    texts[key] = value
    if f"{key}_easy_read" in texts:
        texts[f"{key}_easy_read"] = value
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html_updates = {
    "pg051_sec001.html": ("below is Figure 8(a).", "Observe Figure 8(a)."),
    "pg052_sec001.html": ("&#xa0;Figure 8(b).", "Observe Figure 8(b)."),
    "pg067_sec001.html": ("See Figure 19.", "Observe Figure 19."),
    "pg069_sec001.html": ("Figure 21.</span>", "Observe Figure 21.</span>"),
    "pg071_sec001.html": ("Figure 23.</span>", "Observe Figure 23.</span>"),
    "pg092_sec001.html": ("See Figure 2.</span>", "Observe Figure 2.</span>"),
    "pg103_sec001.html": ("See Figure 8.</span>", "Observe Figure 8.</span>"),
}
for path, pair in html_updates.items():
    replace(path, *pair)
replace("pg069_sec001.html", "Figure 22.</span>", "Observe Figure 22.</span>")

p = ROOT / "pg071_sec002.html"
html = p.read_text(encoding="utf-8")
html = re.sub(r'\s*<div class="flex-shrink-0 pt-1">\s*<div class="flex h-8 w-8[^>]*>\d</div>\s*</div>', "", html)
p.write_text(html, encoding="utf-8")

pages_path = ROOT / "content/pages.json"
pages = json.loads(pages_path.read_text(encoding="utf-8"))
pages = [entry for entry in pages if entry.get("section_id") != "pg040_sec001"]
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for index, entry in enumerate(pages, start=1):
    page_path = ROOT / entry["href"]
    if page_path.exists():
        html = page_path.read_text(encoding="utf-8")
        html = re.sub(r'(<meta name="page-section-id" content=")\d+("\s*/>)', rf"\g<1>{index}\2", html, count=1)
        page_path.write_text(html, encoding="utf-8")

toc_path = ROOT / "content/toc.json"
toc = json.loads(toc_path.read_text(encoding="utf-8"))
toc = [entry for entry in toc if (ROOT / entry.get("href", "")).exists() and entry.get("section_id") != "pg040_sec001"]
toc_path.write_text(json.dumps(toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

manifest_path = ROOT / "imsmanifest.xml"
manifest = manifest_path.read_text(encoding="utf-8")
manifest = re.sub(r'^\s*<file href="pg040_sec001\.html"/>\s*\n', "", manifest, flags=re.M)
manifest_path.write_text(manifest, encoding="utf-8")
