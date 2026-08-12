"""Validate tick-only controls on pages 43 and 44."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
page43 = (ROOT / "pg043_sec001.html").read_text(encoding="utf-8")
page44 = (ROOT / "pg044_sec001.html").read_text(encoding="utf-8")

assert page43.count('type="checkbox"') == 10
assert page44.count('type="checkbox"') == 12
assert 'type="radio"' not in page43 + page44
assert 'type="text"' not in page43 + page44
assert "option-letter" not in page43 + page44
assert '"item-1":true' in page43 and '"item-10":true' in page43
assert '"item-1":true' in page44 and '"item-12":true' in page44
assert page43.count('aria-label="Row ') == 10
assert page44.count('aria-label="') >= 12

print("PASS: pages 43–44 use 22 accessible tick-only controls with boolean answer keys.")
