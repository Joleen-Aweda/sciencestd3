"""Regenerate the complete English narration with one adult male voice."""

import ast
import argparse
import json
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


def audio_path(text_id: str) -> Path:
    """Resolve a cache-versioned audio mapping to its local MP3 path."""
    return AUDIO_DIR / AUDIOS[text_id].split("?", 1)[0]


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


VOICE = "Reed (English (UK))"
SPEAKING_RATE = "140"


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
            shutil.copyfile(audio_path(base_id), audio_path(text_id))
            return text_id
    with tempfile.TemporaryDirectory(prefix="science-male-audio-") as temp:
        aiff = Path(temp) / f"{text_id}.aiff"
        target = audio_path(text_id)
        subprocess.run(
            ["say", "-v", VOICE, "-r", SPEAKING_RATE, "-o", str(aiff), "--", spoken(text_id, value)],
            check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [str(FFMPEG), "-y", "-loglevel", "error", "-i", str(aiff),
             "-ar", "24000", "-ac", "1", "-b:a", "128k", str(target)],
            check=True, timeout=180,
        )
        if target.stat().st_size <= 1000:
            raise RuntimeError(f"Invalid narration output for {text_id}: {target.stat().st_size} bytes")
    return text_id


if not FFMPEG.is_file():
    raise RuntimeError(f"ffmpeg not found: {FFMPEG}")

parser = argparse.ArgumentParser()
parser.add_argument("--start-index", type=int, default=0, help="Resume at this zero-based sorted job index")
parser.add_argument("--ids", nargs="*", help="Generate only these narration IDs")
parser.add_argument("--images-only", action="store_true", help="Generate only image-description narration")
args = parser.parse_args()
if args.images_only:
    selected = [job for job in jobs if "_im" in job[0]]
elif args.ids:
    selected = [job for job in jobs if job[0] in set(args.ids)]
else:
    selected = jobs[args.start_index:]
base_jobs = [job for job in selected if not job[0].endswith("_easy_read")]
easy_jobs = [job for job in selected if job[0].endswith("_easy_read")]
completed = 0 if args.ids or args.images_only else args.start_index

# Generate base narration first, then easy-read duplicates, so copies can never
# race a source file that is still being written.
for phase in (base_jobs, easy_jobs):
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(generate, job) for job in phase]
        for future in as_completed(futures):
            text_id = future.result()
            completed += 1
            total = len(selected) if args.ids or args.images_only else len(jobs)
            if completed % 100 == 0 or completed == total:
                print(f"[{completed}/{total}] {text_id}", flush=True)

AUDIOS_PATH.write_text(json.dumps(AUDIOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Regenerated {len(jobs)} files with {VOICE} at {SPEAKING_RATE} words per minute; removed {len(missing)} stale mappings.")
