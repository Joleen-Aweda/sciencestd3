"""Regenerate the complete English narration with one adult male voice."""

import ast
import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from narration_rules import normalize_spoken


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content/i18n/en"
TEXTS = json.loads((I18N / "texts.json").read_text(encoding="utf-8"))
AUDIOS_PATH = I18N / "audios.json"
AUDIOS = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))
AUDIO_DIR = I18N / "audio"
EDGE_TTS_DIR = Path("/tmp/codex-science-edge-tts")
sys.path.insert(0, str(EDGE_TTS_DIR))
import edge_tts  # type: ignore  # noqa: E402


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


VOICE = "en-US-GuyNeural"
SPEAKING_RATE = "-5%"

# Use the main acknowledgement narrator for every clip. Program names,
# Tanzanian names, image descriptions and Easy Read text must not switch voice.
VOICE_OVERRIDES: dict[str, str] = {}


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
    target = audio_path(text_id)
    with tempfile.TemporaryDirectory(prefix="science-edge-audio-") as temp:
        generated = Path(temp) / target.name
        last_error = None
        for attempt in range(1, 5):
            try:
                asyncio.run(edge_tts.Communicate(
                    spoken(text_id, value), VOICE_OVERRIDES.get(text_id, VOICE), rate=SPEAKING_RATE,
                    connect_timeout=15, receive_timeout=45,
                ).save(str(generated)))
                if generated.stat().st_size <= 1000:
                    raise RuntimeError(f"Invalid narration output: {generated.stat().st_size} bytes")
                generated.replace(target)
                break
            except Exception as error:
                last_error = error
                if attempt == 4:
                    raise RuntimeError(f"Failed to generate {text_id}") from last_error
                time.sleep(attempt * 2)
    return text_id


if not EDGE_TTS_DIR.is_dir():
    raise RuntimeError(f"Edge TTS package not found: {EDGE_TTS_DIR}")

parser = argparse.ArgumentParser()
parser.add_argument("--start-index", type=int, default=0, help="Resume at this zero-based sorted job index")
parser.add_argument("--ids", nargs="*", help="Generate only these narration IDs")
parser.add_argument("--images-only", action="store_true", help="Generate only image-description narration")
parser.add_argument("--manual-edits", action="store_true", help="Generate narration changed by the latest manual text sync")
parser.add_argument("--only-non-edge", action="store_true", help="Resume by generating only files not yet encoded by Edge TTS")
args = parser.parse_args()
if args.manual_edits:
    manual_base_ids = {
        "pg045_n0010", "pg047_n0008", "pg050_n0009", "pg051_n0017",
        "pg052_n0004", "pg060_n0021", "pg064_n0050", "pg066_n0022",
        "pg067_n0008", "pg067_n0022", "pg069_n0006", "pg069_n0017",
        "pg069_n0018", "pg084_n0032", "pg085_n0031", "pg090_n0003",
    }
    manual_ids = manual_base_ids | {text_id + "_easy_read" for text_id in manual_base_ids}
    selected = [job for job in jobs if job[0] in manual_ids]
elif args.images_only:
    selected = [job for job in jobs if "_im" in job[0]]
elif args.ids:
    selected = [job for job in jobs if job[0] in set(args.ids)]
else:
    selected = jobs[args.start_index:]
if args.only_non_edge:
    def is_edge_audio(job: tuple[str, str]) -> bool:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=bit_rate", "-of", "default=nw=1:nk=1",
             str(audio_path(job[0]))], capture_output=True, text=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "48000"
    selected = [job for job in selected if not is_edge_audio(job)]
base_jobs = [job for job in selected if not job[0].endswith("_easy_read")]
easy_jobs = [job for job in selected if job[0].endswith("_easy_read")]
completed = 0 if args.ids or args.images_only or args.manual_edits else args.start_index

# Generate base narration first, then easy-read duplicates, so copies can never
# race a source file that is still being written.
for phase in (base_jobs, easy_jobs):
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(generate, job) for job in phase]
        for future in as_completed(futures):
            text_id = future.result()
            completed += 1
            total = len(selected) if args.ids or args.images_only or args.manual_edits else len(jobs)
            if completed % 100 == 0 or completed == total:
                print(f"[{completed}/{total}] {text_id}", flush=True)

print(f"Regenerated {len(selected)} files with configured voices at rate {SPEAKING_RATE}; preserved all audio mappings and filenames.")
