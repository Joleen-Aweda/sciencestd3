import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS = json.loads((ROOT / "content/i18n/en/texts.json").read_text(encoding="utf-8"))
AUDIOS_PATH = ROOT / "content/i18n/en/audios.json"
AUDIOS = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))
AUDIO_DIR = ROOT / "content/i18n/en/audio"

source = (ROOT / "tools/implement_2026_review_corrections.py").read_text(encoding="utf-8")
tree = ast.parse(source)
updates = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TEXT_UPDATES" for t in node.targets):
        updates = ast.literal_eval(node.value)
        break

# Narration-only corrections: visible typography remains faithful to the book,
# while Roman numerals, abbreviations and parenthesised counts are spoken clearly.
SPOKEN_OVERRIDES = {
    "pg003_n0005_page": "four",
    "pg003_n0007_page": "six",
    "pg005_n0002": "In addition, T I E is grateful to the K Desktop Environment community for allowing the use of simple games content prepared for children between the ages of two and ten years.",
    "pg009_n0021": "Number one. Mention three activities that apply science in daily life.",
    "pg014_n0007": "Number two. Physics deals with the characteristics of living things.",
    "pg014_n0025": "b",
    "pg015_n0009": "Roman two. Various items used in schools, such as chalk, exercise books, pens and books.",
    "pg016_n0002": "Roman three. Building materials such as cement, lime, iron sheets, pipes, steel and tiles.",
    "pg017_n0004": "Roman five. Devices such as telephones and computers used to simplify communication.",
    "pg018_n0007": "Number",
    "pg018_n0014": "one",
    "pg019_n0004": "Number",
    "pg020_n0004": "one",
    "pg020_n0030": "Roman one. Medical doctor",
    "pg020_n0032": "Roman two. Veterinarian",
    "pg020_n0034": "Roman three. Botanist",
    "pg020_n0036": "Roman four. Chemist",
    "pg020_n0038": "Roman five. Pharmacist",
    "pg020_n0040": "Roman six. Engineer",
    "pg021_n0011": "c. In shops",
    "pg029_n0006": "Number",
    "pg030_n0016": "Roman one. Lemon",
    "pg030_n0017": "Roman two. Tomato",
    "pg030_n0019": "Roman one. Sour",
    "pg030_n0021": "Roman two. Umami",
    "pg030_n0026": "Roman one. Orange",
    "pg030_n0027": "Roman two. Sweets",
    "pg030_n0034": "Roman one. Ripe banana",
    "pg030_n0035": "Roman two. Coffee",
    "pg030_n0042": "Roman one. Lemon seeds",
    "pg030_n0043": "Roman two. Orange",
    "pg030_n0050": "Roman one. Tomato",
    "pg030_n0051": "Roman two. Watermelon",
    "pg030_n0058": "Roman one. Lemon",
    "pg030_n0059": "Roman two. Coffee",
    "pg030_n0066": "Roman one. Lemon peel",
    "pg030_n0067": "Roman two. Salt",
    "pg035_n0025": "one",
    "pg036_n0015": "Roman one. Detecting the colour of different flowers in the garden",
    "pg036_n0021": "Roman two. Hearing a song about environmental protection",
    "pg036_n0027": "Roman three. Tasting a bitter medicine",
    "pg036_n0033": "Roman four. Detecting the smell of a burning material",
    "pg043_n0007": "Number",
    "pg044_n0005": "Number",
    "pg059_n0033": "Number",
    "pg064_n0016": "Roman one. Mammals",
    "pg064_n0023": "Roman two. Reptiles",
    "pg064_n0030": "Roman three. Amphibians",
    "pg064_n0037": "Roman four. Birds",
    "pg064_n0044": "Roman five. Fish",
}

# The tongue diagram intentionally places two physical regions for sour and
# salty; narrate each taste name only once.
SKIP_AUDIO_IDS = {"pg028_n0013", "pg028_n0015"}
for text_id in SKIP_AUDIO_IDS:
    AUDIOS.pop(text_id, None)

to_generate = dict(updates)
to_generate.update(SPOKEN_OVERRIDES)

sys.path.insert(0, "/tmp/codex-science-audio")
import imageio_ffmpeg  # type: ignore
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

def spoken(value: str) -> str:
    value = re.sub(r"\[\[blank:[^\]]+\]\]", "", value)
    return value.replace("↑", "up arrow").replace("↓", "down arrow").replace("←", "left arrow").replace("→", "right arrow")

VOICE = "Reed (English (UK))"
SPEAKING_RATE = "140"

with tempfile.TemporaryDirectory(prefix="science-review-audio-") as temp:
    temp_path = Path(temp)
    for index, (text_id, value) in enumerate(sorted(to_generate.items()), start=1):
        if text_id not in TEXTS and text_id not in SPOKEN_OVERRIDES:
            raise RuntimeError(f"No text for audio ID {text_id}")
        aiff = temp_path / f"{text_id}.aiff"
        target = AUDIO_DIR / f"{text_id}.mp3"
        subprocess.run(["say", "-v", VOICE, "-r", SPEAKING_RATE, "-o", str(aiff), spoken(value)], check=True)
        subprocess.run([
            ffmpeg, "-y", "-loglevel", "error", "-i", str(aiff),
            "-ar", "24000", "-ac", "1", "-b:a", "128k", str(target)
        ], check=True)
        AUDIOS[text_id] = target.name + "?v=17"
        print(f"[{index}/{len(to_generate)}] {text_id}")

AUDIOS_PATH.write_text(json.dumps(AUDIOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Regenerated {len(to_generate)} narration files; skipped {len(SKIP_AUDIO_IDS)} repeated diagram labels.")
