"""Create muted, web-ready sign-language videos for all navigation pages."""

from __future__ import annotations

import argparse
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home() / "Desktop" / "17. SCIENCE STD III - Complete"
DEFAULT_OUTPUT = ROOT / "content" / "i18n" / "en" / "video"


def page_number(path: Path) -> int:
    match = re.search(r"(\d+)", path.stem)
    if not match:
        raise ValueError(f"No page number in {path.name}")
    return int(match.group(1))


def encode(source: Path, output_dir: Path) -> tuple[int, Path]:
    number = page_number(source)
    destination = output_dir / f"page_{number:03d}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-loglevel", "error", "-y", "-i", str(source),
            "-map", "0:v:0", "-vf", "scale=-2:480:flags=lanczos,fps=25",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
            "-maxrate", "550k", "-bufsize", "1100k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-an", str(destination),
        ],
        check=True,
    )
    return number, destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    sources = sorted(args.source.glob("*.mp4"), key=page_number)
    numbers = [page_number(path) for path in sources]
    if numbers != list(range(1, 142)):
        raise SystemExit("Expected exactly one source video for every page from 1 to 141")

    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(lambda path: encode(path, args.output), sources))

    total_size = sum(path.stat().st_size for _, path in results)
    print(f"Encoded {len(results)} muted videos ({total_size / 1024**2:.1f} MiB).")


if __name__ == "__main__":
    main()
