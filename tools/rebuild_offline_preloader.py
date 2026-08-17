import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELOADER = ROOT / "assets/offline-preloader.js"

source = PRELOADER.read_text(encoding="utf-8")
match = re.search(r"var INLINE = (\{.*?\});\n\s*var ", source, re.DOTALL)
if not match:
    raise RuntimeError("Could not find the embedded offline content map")

old = json.loads(match.group(1))
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
bundle_version = json.loads((ROOT / "assets/config.json").read_text(encoding="utf-8"))["bundleVersion"]

priority = [
    "./assets/config.json",
    "./assets/sign-language-page-player.js",
    "./content/pages.json",
    "./content/toc.json",
    "./content/navigation/nav.html",
    "./index.html",
    *[f'./{page["href"]}' for page in pages],
]
extras = [key for key in old if not key.endswith(".html") and key not in priority]

inline = {}
for key in [*priority, *extras]:
    path = ROOT / key.removeprefix("./")
    if not path.exists():
        continue
    if path.suffix == ".json":
        inline[key] = json.loads(path.read_text(encoding="utf-8"))
    else:
        inline[key] = path.read_text(encoding="utf-8")

encoded = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
updated = source[: match.start(1)] + encoded + source[match.end(1) :]
PRELOADER.write_text(updated, encoding="utf-8")

for page in pages:
    path = ROOT / page["href"]
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"assets/offline-preloader\.js(?:\?v=\d+)?", f"assets/offline-preloader.js?v={bundle_version}", html)
    html = re.sub(r"assets/fonts\.css(?:\?v=\d+)?", f"assets/fonts.css?v={bundle_version}", html)
    sign_script = f'<script src="./assets/sign-language-page-player.js?v={bundle_version}"></script>'
    if "assets/sign-language-page-player.js" in html:
        html = re.sub(
            r'<script src="\./assets/sign-language-page-player\.js(?:\?v=\d+)?"></script>',
            sign_script,
            html,
        )
    else:
        html = re.sub(
            r'(?P<indent>\s*)<script src="\./assets/scorm\.js"></script>',
            lambda match: (
                f'{match.group("indent")}{sign_script}'
                f'{match.group("indent")}<script src="./assets/scorm.js"></script>'
            ),
            html,
            count=1,
        )
    path.write_text(html, encoding="utf-8")

print(f"Embedded {len(pages)} consecutive pages with bundle version {bundle_version}.")
