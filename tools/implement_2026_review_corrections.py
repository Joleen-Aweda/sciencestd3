import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/en/texts.json"

# Display wording requested by SCIENCE STD 3 COMMENTS (2).docx. Obvious figure
# number slips in the review table are reconciled with the figure on the page.
TEXT_UPDATES = {
    "pg008_n0004": "Figure 1 shows people using scientific tools, including a spring balance and a stethoscope.",
    "pg009_n0003": "Study Figure 2 and its descriptions, then write what you have studied.",
    "pg010_n0003": "Study pictures (a)–(d) and write the type of scientific activity shown in each picture.",
    "pg011_n0010": "Figure 3 shows different branches of science.",
    "pg011_n0021": "Figure 4 shows an environment with cows, goats, trees, grasses, a dog and a human being.",
    "pg013_n0005": "Figure 6 shows examples of matter in solid, liquid and gaseous states.",
    "pg014_n0032": "Items and equipment we use at home include clothes, soap, toothpaste, cooking gas, gas cylinders, tables, food utensils, televisions, fridges, radios and cars. Figure 7 shows items used at home.",
    "pg015_n0010": "Figure 8 shows a pen and a pencil.",
    "pg016_n0004": "Figure 9 shows building materials.",
    "pg017_n0005": "Figure 11 shows a child using a telephone.",
    "pg020_n0047": "Give the answers for the following sentences.",
    "pg023_n0003": "Figure 1 shows human sense organs.",
    "pg024_n0003": "Study Figure 2 and its descriptions, then write the action shown in each picture.",
    "pg024_n0027": "Figure 3 shows the outer parts of the human eye.",
    "pg025_n0008": "Figure 4 shows the internal parts of the human eye.",
    "pg027_n0020": "Study shapes (a) to (e) in Figure 5 and their descriptions, then name the colour of each shape.",
    "pg028_n0006": "Figure 6 shows the taste areas of the tongue.",
    "pg028_n0020": "Each taste is detected mostly at a specific part of the tongue, as explained in Table 2.",
    "pg029_n0052": "1. Collect and arrange in groups the substances listed in Table 3.",
    "pg031_n0022": "Figure 7 shows the nose.",
    "pg032_n0017": "Figure 8 shows the parts of the skin.",
    "pg033_n0003": "Collect the materials listed in Figure 9 and touch each material to feel its texture.",
    "pg034_n0011": "The ear consists of three major parts, namely the outer ear, middle ear and inner ear. Figure 10 shows the parts of an ear.",
    "pg034_n0017": "Figure 10: Parts of an ear",
    "pg042_n0006": "(a) Study Figure 1 and its description, then mention the things you have studied.",
    "pg045_n0010": "Figure 2 shows living things feeding.",
    "pg047_n0008": "Figure 4 shows movement in animals.",
    "pg048_n0018": "Figure 6 shows how plants move towards light.",
    "pg048_n0021": "Light ↓",
    "pg048_n0024": "Light ↓",
    "pg049_n0005": "After one week, take plant B out of the box and study the growth directions of plants A and B.",
    "pg050_n0009": "Figure 7 shows reproduction in living things.",
    "pg051_n0017": "Figure 8(a) shows growth in human beings.",
    "pg052_n0004": "Figure 8(b) shows growth in plants.",
    "pg052_n0009": "Study things in the environment and read online sources to explore the importance of each of the seven characteristics of living things.",
    "pg060_n0021": "Figure 14 shows domestic and wild birds.",
    "pg064_n0050": "Figure 16 shows invertebrates.",
    "pg064_n0061": "(a) Study vertebrates and invertebrates in your environment and list them.",
    "pg065_n0021": "Studying the main parts of a plant",
    "pg066_n0008": "2. Study the plant and identify its parts.",
    "pg066_n0022": "Figure 18 shows the parts of a plant.",
    "pg067_n0008": "Figure 19 shows plants that store food in their roots.",
    "pg067_n0022": "Figure 20 shows plants that store food in their stems.",
    "pg069_n0006": "Figure 21 shows the parts of a flower.",
    "pg069_n0018": "Figure 22 shows non-flowering plants.",
    "pg071_n0005": "Figure 23 shows people caring for plants and animals.",
    "pg076_n0007": "Study Figure 1 and its image descriptions, then answer the questions that follow.",
    "pg078_n0016": "Figure 2 shows the steps of a scientific investigation.",
    "pg084_n0032": "Figure 3 shows a leaf wrapped in a plastic bag.",
    "pg085_n0005": "4. Study what happened.",
    "pg085_n0031": "2. Cover the jars with the lids. Figure 4 shows a stone and a cockroach in covered jars.",
    "pg086_n0008": "5. Study carefully what happens in each jar.",
    "pg090_n0003": "Study Figure 1 and its image descriptions, then answer the questions that follow.",
    "pg092_n0011": "Figure 2 shows a maze game.",
    "pg094_n0009": "Figure 3 shows a path encoding game.",
    "pg094_n0005": "↑ means up,",
    "pg094_n0006": "↓ means down,",
    "pg094_n0007": "← means left, and",
    "pg094_n0008": "→ means right, no matter which direction Tux is facing.",
    "pg095_n0023": "Figure 4 shows a path decoding game.",
    "pg095_n0027": "Figure 4 shows a path decoding game.",
    "pg095_n0026": "↑ means up, ↓ means down, ← means left, and → means right, no matter which direction Tux is facing.",
    "pg099_n0009": "Figure 6 shows a Tower of Hanoi game.",
    "pg101_n0003": "Figure 7(a) shows the beginning of the drawing game.",
    "pg102_n0042": "Study the control panel that has different moves like ‘Go Forward,’",
    "pg102_n0051": "Figure 8 shows a programming maze game.",
}

# Publisher artefacts and content specifically identified as not required.
REMOVE_IDS = {
    "pg015_n0018", "pg025_n0020", "pg025_n0021", "pg039_n0049",
    "pg039_n0050", "pg051_n0021", "pg051_n0022", "pg078_n0018",
    "pg078_n0019", "pg087_n0005", "pg087_n0006", "pg100_n0012", "pg100_n0027", "pg100_n0028",
}

# Picture markers/names requested above their associated pictures.
LABEL_ABOVE_IDS = {
    "pg008_n0007", "pg008_n0009",
    "pg009_n0006", "pg009_n0008", "pg009_n0010", "pg009_n0012",
    "pg010_n0013", "pg010_n0018", "pg010_n0024", "pg010_n0029",
    "pg023_n0006", "pg023_n0008", "pg023_n0010", "pg023_n0012", "pg023_n0014",
    "pg024_n0006", "pg024_n0008", "pg024_n0010",
    "pg027_n0022", "pg027_n0024", "pg027_n0026", "pg027_n0028", "pg027_n0030",
    "pg045_n0018", "pg045_n0020",
    "pg053_n0015", "pg053_n0017", "pg053_n0019", "pg053_n0021", "pg053_n0023",
    "pg053_n0025", "pg053_n0027", "pg053_n0029", "pg053_n0031",
    "pg057_n0016", "pg057_n0018",
    "pg060_n0023", "pg060_n0025", "pg060_n0027", "pg060_n0029",
    "pg064_n0053", "pg064_n0055", "pg064_n0057",
    "pg065_n0011", "pg065_n0013", "pg065_n0015", "pg065_n0017",
    "pg067_n0011", "pg067_n0013", "pg068_n0002", "pg068_n0004",
    "pg070_n0002", "pg070_n0004", "pg071_n0008", "pg071_n0011",
    "pg072_n0015", "pg072_n0018", "pg072_n0021", "pg072_n0024",
    "pg076_n0010", "pg076_n0012", "pg076_n0014",
    "pg099_n0011", "pg099_n0013",
}

FILL_DISPLAY_PAGES = {26, 27, 28, 29, 36, 49, 52, 53, 54, 65, 74, 83, 89, 96, 111, 116, 117, 123, 130, 142}


def update_element(html_text: str, text_id: str, value: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[A-Za-z0-9]+)\b[^>]*\bdata-id="{re.escape(text_id)}"[^>]*>)(.*?)(</(?P=tag)>)',
        re.DOTALL,
    )
    escaped = html.escape(value, quote=False).replace("\n", "<br>")
    updated, count = pattern.subn(lambda m: m.group(1) + escaped + m.group(4), html_text)
    if count == 0:
        raise RuntimeError(f"Could not find HTML element for {text_id}")
    return updated


def remove_elements(html_text: str, text_id: str) -> str:
    pattern = re.compile(
        rf'\s*<(?P<tag>[A-Za-z0-9]+)\b[^>]*\bdata-id="{re.escape(text_id)}"[^>]*>.*?</(?P=tag)>',
        re.DOTALL,
    )
    return pattern.sub("", html_text)


def add_label_class(html_text: str, text_id: str) -> str:
    pattern = re.compile(rf'<[^>]+\bdata-id="{re.escape(text_id)}"[^>]*>')
    def add(match):
        tag = match.group(0)
        class_match = re.search(r'class="([^"]*)"', tag)
        if class_match:
            if "adt-label-above" in class_match.group(1):
                return tag
            return tag[:class_match.end(1)] + " adt-label-above" + tag[class_match.end(1):]
        return tag[:-1] + ' class="adt-label-above">'
    return pattern.sub(add, html_text)


texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
for text_id, value in TEXT_UPDATES.items():
    if text_id not in texts:
        raise RuntimeError(f"Unknown text ID {text_id}")
    texts[text_id] = value
    easy = f"{text_id}_easy_read"
    if easy in texts:
        texts[easy] = value
for text_id in REMOVE_IDS:
    texts.pop(text_id, None)
    texts.pop(f"{text_id}_easy_read", None)
TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
display_numbers = {entry["href"]: entry["page_number"] for entry in pages}
for page_path in sorted(ROOT.glob("pg*_sec*.html")):
    page = page_path.read_text(encoding="utf-8")
    original = page
    page_ids = set(re.findall(r'data-id="([^"]+)"', page))
    for text_id, value in TEXT_UPDATES.items():
        if text_id in page_ids:
            page = update_element(page, text_id, value)
    for text_id in REMOVE_IDS & page_ids:
        page = remove_elements(page, text_id)
    for text_id in LABEL_ABOVE_IDS & page_ids:
        page = add_label_class(page, text_id)

    # A single data-id must produce a single narration item. Responsive duplicate
    # renderings retain their fallback English but do not enter the TTS sequence.
    seen = set()
    def dedupe(match):
        text_id = match.group(1)
        if text_id in seen:
            return f'data-duplicate-id="{text_id}"'
        seen.add(text_id)
        return match.group(0)
    page = re.sub(r'data-id="([^"]+)"', dedupe, page)

    if "adt-label-above" in page and "data-adt-review-styles" not in page:
        style = ('<style data-adt-review-styles>'
                 '*:has(>.adt-label-above){display:flex!important;flex-direction:column!important}'
                 '.adt-label-above{display:block;order:-1;margin-top:0!important;'
                 'margin-bottom:.45rem!important;font-weight:600;text-align:center}'
                 '</style>\n')
        page = page.replace("</head>", style + "</head>")
    if display_numbers.get(page_path.name) in FILL_DISPLAY_PAGES and "data-adt-fill-style" not in page:
        fill_style = ('<style data-adt-fill-style>'
                      '#content{min-height:calc(100vh - 8rem);display:flex;align-items:center}'
                      '#content>section{width:100%}'
                      '</style>\n')
        page = page.replace("</head>", fill_style + "</head>")
    if page != original:
        page_path.write_text(page, encoding="utf-8")

# Remove obsolete narration mappings for removed publisher artefacts.
audios_path = ROOT / "content/i18n/en/audios.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
for text_id in REMOVE_IDS:
    audios.pop(text_id, None)
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Cache-bust every synchronized localization/offline payload.
config_path = ROOT / "assets/config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["bundleVersion"] = str(int(config.get("bundleVersion", "1")) + 1)
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Applied {len(TEXT_UPDATES)} text corrections; removed {len(REMOVE_IDS)} artefact IDs; bundle {config['bundleVersion']}.")
