"""Regenerate the complete English narration with two adult male voices."""

import ast
import json
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from narration_rules import normalize_spoken


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content/i18n/en"
TEXTS = json.loads((I18N / "texts.json").read_text(encoding="utf-8"))
AUDIOS_PATH = I18N / "audios.json"
AUDIOS = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))
AUDIO_DIR = I18N / "audio"
FFMPEG = Path("/tmp/codex-science-audio/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1")


def load_existing_overrides() -> dict[str, str]:
    source = (ROOT / "tools/regenerate_review_audio.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SPOKEN_OVERRIDES"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    return {}


OVERRIDES = load_existing_overrides() | {
    # Blank answer fields remain visible but are never narrated.
    "pg020_n0048": "a. Science that deals with matter in relation to energy is called.",
    "pg020_n0049": "b. Science that deals with matter and its properties is called.",
    "pg021_n0002": "c. Science that deals with plants and animals in their environment is called.",
    # Explicitly pronounce the requested item letters.
    "pg031_n0009": "b",
    "pg033_n0019": "a. Keeping it clean by taking a bath regularly.",
    "pg033_n0021": "b. Using clean water, sponge or brush and soap when bathing.",
    "pg034_n0003": "d. Applying appropriate body oil or jelly after a bath; and",
    "pg034_n0005": "e. Eating nutritious food and drinking enough water.",
    "pg039_n0003": "c. Nose is used for tasting.",
    "pg039_n0005": "d. Tongue is used for feeling.",
    "pg053_n0015": "a", "pg053_n0017": "b", "pg053_n0019": "c",
    "pg053_n0021": "d", "pg053_n0023": "e", "pg053_n0025": "f",
    "pg053_n0027": "g", "pg053_n0029": "h", "pg053_n0031": "i",
    "pg064_n0013": "a. Eagle", "pg064_n0020": "b. Tilapia",
    "pg064_n0027": "c. Goat", "pg064_n0034": "d. Frog",
    "pg064_n0041": "e. Lizard",
    "pg076_n0012": "b",
}


def voice_for(text_id: str) -> str:
    match = re.search(r"(?:pg|gl)(\d+)", text_id)
    number = int(match.group(1)) if match else sum(map(ord, text_id))
    return "Daniel" if number % 2 else "Reed (English (UK))"


def spoken(text_id: str, value: str) -> str:
    value = OVERRIDES.get(text_id, value)
    return normalize_spoken(text_id, value)


missing = [text_id for text_id in AUDIOS if text_id not in TEXTS and text_id not in OVERRIDES]
for text_id in missing:
    AUDIOS.pop(text_id, None)

jobs = sorted((text_id, TEXTS[text_id]) for text_id in AUDIOS if text_id in TEXTS)


def generate(job: tuple[str, str]) -> str:
    text_id, value = job
    if text_id.endswith("_easy_read"):
        base_id = text_id.removesuffix("_easy_read")
        if TEXTS.get(base_id) == value and base_id in AUDIOS:
            shutil.copyfile(AUDIO_DIR / AUDIOS[base_id], AUDIO_DIR / AUDIOS[text_id])
            return text_id
    with tempfile.TemporaryDirectory(prefix="science-male-audio-") as temp:
        aiff = Path(temp) / f"{text_id}.aiff"
        target = AUDIO_DIR / AUDIOS[text_id]
        subprocess.run(
            ["say", "-v", voice_for(text_id), "-r", "155", "-o", str(aiff), "--", spoken(text_id, value)],
            check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [str(FFMPEG), "-y", "-loglevel", "error", "-i", str(aiff),
             "-ar", "24000", "-ac", "1", "-b:a", "128k", str(target)],
            check=True, timeout=180,
        )
    return text_id


if not FFMPEG.is_file():
    raise RuntimeError(f"ffmpeg not found: {FFMPEG}")

with ThreadPoolExecutor(max_workers=12) as pool:
    futures = [pool.submit(generate, job) for job in jobs]
    for index, future in enumerate(as_completed(futures), 1):
        text_id = future.result()
        if index % 100 == 0 or index == len(jobs):
            print(f"[{index}/{len(jobs)}] {text_id}", flush=True)

AUDIOS_PATH.write_text(json.dumps(AUDIOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Regenerated {len(jobs)} files with Daniel and Reed; removed {len(missing)} stale mappings.")
