import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MERGES = {
    "pg022_sec001.html": ["pg022_sec002.html", "pg022_sec003.html", "pg022_sec004.html"],
    "pg035_sec002.html": ["pg035_sec003.html"],
    "pg037_sec002.html": ["pg037_sec003.html", "pg038_sec001.html"],
    "pg053_sec001.html": ["pg053_sec002.html"],
    "pg061_sec003.html": ["pg062_sec001.html"],
    "pg075_sec001.html": ["pg076_sec001.html"],
    "pg080_sec001.html": ["pg080_sec002.html", "pg080_sec003.html"],
    "pg083_sec002.html": ["pg084_sec001.html"],
    "pg088_sec001.html": ["pg088_sec002.html"],
    "pg096_sec002.html": ["pg097_sec001.html"],
}
ACTIVITY_SOURCE = "pg068_sec002.html"
REMOVED = {source for sources in MERGES.values() for source in sources} | {ACTIVITY_SOURCE}


def section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(<section\b.*?</section>)", text, re.DOTALL)
    if not match:
        raise RuntimeError(f"No section in {path.name}")
    return match.group(1)


def append_sections(target_name: str, source_names: list[str]) -> None:
    path = ROOT / target_name
    text = path.read_text(encoding="utf-8")
    additions = "\n".join(section(ROOT / name) for name in source_names)
    marker = "</div>\n    </main>"
    if marker not in text:
        raise RuntimeError(f"No content closing marker in {target_name}")
    text = text.replace(marker, f"{additions}\n</div>\n    </main>", 1)
    path.write_text(text, encoding="utf-8")


for target, sources in MERGES.items():
    append_sections(target, sources)

# Source pages with a single section may use a fill rule that makes the
# content container a flex row. Merged sections must read from top to bottom.
for target in MERGES:
    path = ROOT / target
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r'(<div\b(?=[^>]*\bid="content")[^>]*\bclass=")([^"]*)"',
        lambda match: f'{match.group(1)}flex flex-col gap-8 {match.group(2)}"',
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Could not make merged layout vertical in {target}")
    path.write_text(text, encoding="utf-8")

# Activity 9 belongs immediately after Figure 22, before the next topic.
activity = section(ROOT / ACTIVITY_SOURCE)
path = ROOT / "pg070_sec001.html"
text = path.read_text(encoding="utf-8")
anchor = '      <div data-id="pg070_n0009"'
if anchor not in text:
    raise RuntimeError("Could not locate the content after Figure 22")
text = text.replace(anchor, f"      {activity}\n\n{anchor}", 1)
path.write_text(text, encoding="utf-8")

# Remove duplicated diagram overlays where the source artwork already contains
# the leader lines/letters.
path = ROOT / "pg025_sec001.html"
text = path.read_text(encoding="utf-8")
text = re.sub(r"\s*<!-- SVG Pointer Lines for Outer Parts -->\s*<svg\b.*?</svg>", "", text, flags=re.DOTALL)
text = re.sub(r"\s*<!-- SVG Pointer Lines for Internal Parts -->\s*<svg\b.*?</svg>", "", text, flags=re.DOTALL)
path.write_text(text, encoding="utf-8")

duplicate_letter_ids = {"pg027_n0022", "pg027_n0024", "pg027_n0026", "pg027_n0028", "pg027_n0030"}
path = ROOT / "pg027_sec002.html"
text = path.read_text(encoding="utf-8")
for text_id in duplicate_letter_ids:
    text = re.sub(rf"<span\b[^>]*data-id=\"{text_id}\"[^>]*>.*?</span>", "", text, flags=re.DOTALL)
path.write_text(text, encoding="utf-8")

# Remove the extra visible option letters; the localized option text already
# starts with (a), (b), (c), or (d).
path = ROOT / "pg073_sec001.html"
text = path.read_text(encoding="utf-8")
text = re.sub(r'\s*<span class="text-\[24px\][^>]*aria-hidden="true">\([a-d]\)</span>', "", text)
path.write_text(text, encoding="utf-8")

# The question strings already contain their numbers.
path = ROOT / "pg093_sec001.html"
text = path.read_text(encoding="utf-8").replace('class="list-decimal ', 'class="list-none ')
path.write_text(text, encoding="utf-8")

# This activity asks learners to investigate; it does not require a written
# answer on this page.
path = ROOT / "pg052_sec002.html"
text = path.read_text(encoding="utf-8")
text = re.sub(r'\s*<div class="mt-8 rounded-\[1\.5rem\].*?</div>', "", text, flags=re.DOTALL)
text = text.replace('data-section-type="activity_open_ended_answer"', 'data-section-type="boxed_text"')
path.write_text(text, encoding="utf-8")

# Directional light labels: arrows point toward the light opening/source.
text_updates = {
    "pg046_n0018": "Light ↓",
    "pg046_n0020": "← Light",
    "pg046_n0022": "Light →",
    "pg048_n0024": "Light →",
}
texts_path = ROOT / "content/i18n/en/texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
for text_id, value in text_updates.items():
    if text_id not in texts:
        raise RuntimeError(f"Unknown text ID: {text_id}")
    texts[text_id] = value
    for html_path in ROOT.glob(f"{text_id[:5]}_sec*.html"):
        html = html_path.read_text(encoding="utf-8")
        html = re.sub(
            rf'(<(?P<tag>\w+)\b[^>]*data-id="{text_id}"[^>]*>).*?(</(?P=tag)>)',
            rf"\1{value}\3", html, flags=re.DOTALL,
        )
        html_path.write_text(html, encoding="utf-8")

# Place Plant B's light label at the left so its right arrow points to the hole.
path = ROOT / "pg048_sec001.html"
text = path.read_text(encoding="utf-8")
text = text.replace('data-id="pg048_n0024" class="', 'data-id="pg048_n0024" class="self-start ml-[8%] ')
path.write_text(text, encoding="utf-8")

# Better directional leaders for Figure 5.
path = ROOT / "pg087_sec001.html"
text = path.read_text(encoding="utf-8")
svg = re.search(r'<svg aria-hidden="true".*?</svg>', text, re.DOTALL)
if svg:
    replacement = '''<svg aria-hidden="true" class="pointer-events-none absolute inset-0 h-full w-full max-sm:hidden" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs><marker id="figure5-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#991b1b"/></marker></defs>
          <g fill="none" stroke="#991b1b" stroke-width="0.65" stroke-linecap="round" marker-end="url(#figure5-arrow)">
            <line x1="22" y1="11" x2="35" y2="31"/>
            <line x1="78" y1="11" x2="65" y2="44"/>
            <line x1="21" y1="88" x2="39" y2="69"/>
            <line x1="79" y1="88" x2="62" y2="70"/>
          </g>
        </svg>'''
    text = text[:svg.start()] + replacement + text[svg.end():]
text = text.replace(
    'left-[47%] top-[77%] text-[1.8rem]',
    'right-[4%] top-[80%] text-[1.8rem]',
).replace(
    'max-lg:left-[59%] max-lg:top-[74%]',
    'max-lg:right-[1%] max-lg:top-[78%]',
)
path.write_text(text, encoding="utf-8")

# Remove dead text/audio keys for the eliminated duplicate shape letters.
audios_path = ROOT / "content/i18n/en/audios.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
for text_id in duplicate_letter_ids:
    texts.pop(text_id, None)
    audios.pop(text_id, None)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Rebuild a strictly consecutive navigation spine, remove merged sources, and
# keep every remaining HTML page's 1-based section index synchronized.
pages_path = ROOT / "content/pages.json"
pages = json.loads(pages_path.read_text(encoding="utf-8"))
pages = [entry for entry in pages if entry["href"] not in REMOVED]
for number, entry in enumerate(pages, 1):
    entry["page_number"] = number
    html_path = ROOT / entry["href"]
    html = html_path.read_text(encoding="utf-8")
    html, count = re.subn(
        r'<meta name="page-section-id" content="\d+"\s*/>',
        f'<meta name="page-section-id" content="{number}" />', html, count=1,
    )
    if count != 1:
        raise RuntimeError(f"Could not renumber {entry['href']}")
    html_path.write_text(html, encoding="utf-8")
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

toc_path = ROOT / "content/toc.json"
toc = json.loads(toc_path.read_text(encoding="utf-8"))
def prune(value):
    if isinstance(value, list):
        return [item for item in (prune(x) for x in value) if item is not None]
    if isinstance(value, dict):
        if value.get("href") in REMOVED:
            return None
        return {key: prune(item) for key, item in value.items()}
    return value
toc_path.write_text(json.dumps(prune(toc), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

manifest_path = ROOT / "imsmanifest.xml"
if manifest_path.exists():
    manifest = manifest_path.read_text(encoding="utf-8")
    for name in REMOVED:
        manifest = re.sub(rf"\s*<resource\b[^>]*href=\"{re.escape(name)}\".*?</resource>", "", manifest, flags=re.DOTALL)
        manifest = re.sub(rf"\s*<file\b[^>]*href=\"{re.escape(name)}\"[^>]*/>", "", manifest)
    manifest_path.write_text(manifest, encoding="utf-8")

for name in REMOVED:
    (ROOT / name).unlink()

config_path = ROOT / "assets/config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["bundleVersion"] = "13"
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for html_path in ROOT.glob("*.html"):
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(r"offline-preloader\.js\?v=\d+", "offline-preloader.js?v=13", html)
    html_path.write_text(html, encoding="utf-8")

print(f"Merged {len(REMOVED)} source pages; navigation now has {len(pages)} consecutive pages.")
