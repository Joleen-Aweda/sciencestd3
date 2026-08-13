import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


page19 = read("pg019_sec001.html")
assert page19.count("<line ") == 7

page21 = read("pg021_sec001.html")
assert "3. Explain how science is used in the following areas:" in page21
assert 'data-id="pg021_n0003"' not in page21

with (ROOT / "images/shape_pg027_im005_crop_v1.png").open("rb") as stream:
    assert stream.read(8) == b"\x89PNG\r\n\x1a\n"
    length = struct.unpack(">I", stream.read(4))[0]
    assert stream.read(4) == b"IHDR" and length == 13
    width, height = struct.unpack(">II", stream.read(8))
assert (width, height) == (139, 202)

page34 = read("pg034_sec001.html")
assert "images/pg034_ear_clean.png" in page34
assert "images/pg034_im001_crop1.png" not in page34
assert "FOR ONLINE READING ONLY" not in page34

for name in ("pg038_sec002.html", "pg072_sec001.html"):
    assert ".option-letter{display:none!important}" in read(name)

page39 = read("pg039_sec002.html")
assert 'type="radio"' not in page39 and page39.count('type="text"') == 5
assert "Write your answer in each blank item." in page39

page46 = read("pg046_sec001.html")
assert page46.count("text-[2.8rem]") == 2

page56 = read("pg056_sec001.html")
assert page56.index("pg056_n0009") < page56.index("pg056_im001")
assert page56.index("pg056_n0011") < page56.index("pg056_im002")

page58 = read("pg058_sec001.html")
for label, image in (("pg058_n0026", "pg058_im002"), ("pg058_n0028", "pg058_im001"), ("pg058_n0030", "pg058_im003")):
    assert page58.index(label) < page58.index(image)

assert 'data-id="pg061_n0032" class="text-left text-[3.1rem]' in read("pg061_sec003.html")

page73 = read("pg073_sec002.html")
assert 'type="radio"' not in page73 and page73.count('type="text"') == 4

page75 = read("pg075_sec001.html")
assert 'data-section-id="pg076_sec001"' not in page75
assert page75.index("pg075_n0020") < page75.index("pg076_n0002") < page75.index("pg076_n0004")
assert "border-t border-neutral-300" not in page75

page80 = read("pg080_sec001.html")
assert page80.count("border-l-[14px] border-sky-200") == 3
assert "text-[2.1rem]" not in page80

assert "5. Study the two grasshoppers in the jars after two days." in read("pg086_sec001.html")

page87 = read("pg087_sec002.html")
assert 'type="radio"' not in page87 and page87.count('type="text"') == 5

texts = json.loads(read("content/i18n/en/texts.json"))
expected = {
    "pg021_n0004": "3. Explain how science is used in the following areas:",
    "pg039_n0041": "Write your answer in each blank item.",
    "pg073_n0014": "Write your answer in each blank item.",
    "pg086_n0037": "5. Study the two grasshoppers in the jars after two days.",
    "pg087_n0015": "Section A: Write your answer in each blank item.",
}
for text_id, value in expected.items():
    assert texts[text_id] == value
    audio = ROOT / "content/i18n/en/audio" / f"{text_id}.mp3"
    assert audio.exists() and audio.stat().st_size > 1000

assert json.loads(read("assets/config.json"))["bundleVersion"] == "23"
assert "offline-preloader.js?v=23" in page87

print("PASS: all 16 August 12 QA corrections are present and synchronized.")
