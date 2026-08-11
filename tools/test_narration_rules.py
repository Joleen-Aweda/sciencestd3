import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from narration_rules import normalize_spoken


assert normalize_spoken("pg015_n0009", "(ii) Various items") == "Roman two. Various items"
assert normalize_spoken("pg016_n0002", "(iii) Building materials") == "Roman three. Building materials"
assert normalize_spoken("pg016_n0013", "(iv) Equipment") == "Roman four. Equipment"
assert normalize_spoken("pg017_n0004", "(v) Devices") == "Roman five. Devices"
assert normalize_spoken("pg020_n0030", "(i) Medical doctor") == "Roman one. Medical doctor"
assert normalize_spoken("pg053_n0031", "(i)") == "(i)"

all_audio = (ROOT / "tools/regenerate_all_male_audio.py").read_text(encoding="utf-8")
review_audio = (ROOT / "tools/regenerate_review_audio.py").read_text(encoding="utf-8")
assert '"-r", "155"' in all_audio
assert '"-r", "155"' in review_audio
assert '"-r", "165"' not in all_audio + review_audio

print("PASS: Roman numerals and the slightly slower narration rate are configured.")
