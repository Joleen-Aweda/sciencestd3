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
assert '"pg047_n0027": "Materials: Two healthy potted plants' in review_audio
assert 'VOICE = "en-US-GuyNeural"' in all_audio
assert 'SPEAKING_RATE = "-5%"' in all_audio
assert "edge_tts.Communicate" in all_audio
assert '"pg001_n0018": "I S B N.' in review_audio
assert '"pg002_n0004": "I S B N.' in review_audio
assert '"pg010_n0024": "Letter c."' in review_audio
assert '"pg037_n0055": "Walk around your home or school compound. And"' in review_audio
assert "Daniel" not in all_audio + review_audio

print("PASS: Roman numerals and en-US-GuyNeural at -5% are configured.")
