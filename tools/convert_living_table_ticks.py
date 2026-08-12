"""Convert pages 43–44 living/non-living tables to tick-only controls."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


page43_path = ROOT / "pg043_sec001.html"
page43 = page43_path.read_text(encoding="utf-8")
radio_label = re.compile(
    r'<label class="activity-option[^>]*>\s*'
    r'<div class="option-letter[^>]*>\d+</div>\s*'
    r'<input type="radio"[^>]*data-activity-item="([^"]+)"[^>]*aria-label="([^"]+)"[^>]*>\s*'
    r'<div class="w-7[^>]*></div>\s*'
    r'<div class="feedback-container.*?</div>\s*</div>\s*</label>',
    re.DOTALL,
)


def page43_tick(match: re.Match[str]) -> str:
    item, label = match.groups()
    return (
        '<label class="flex min-h-[96px] cursor-pointer items-center justify-center max-sm:min-h-[82px]">'
        f'<span class="sr-only">{label}</span>'
        f'<input type="checkbox" data-activity-item="{item}" aria-label="{label}" '
        'class="h-9 w-9 cursor-pointer accent-cyan-600 max-sm:h-7 max-sm:w-7">'
        '</label>'
    )


page43, replacements43 = radio_label.subn(page43_tick, page43)
if replacements43 != 10:
    raise RuntimeError(f"Expected to replace 10 page-43 radio controls, replaced {replacements43}")
page43_path.write_text(page43, encoding="utf-8")


page44_path = ROOT / "pg044_sec001.html"
page44 = page44_path.read_text(encoding="utf-8")
text_field = re.compile(
    r'<label for="([^"]+)" class="sr-only" aria-label="([^"]+)"></label>'
    r'<input id="\1" type="text" aria-label="\2" data-activity-item="([^"]+)"[^>]*>'
)


def page44_tick(match: re.Match[str]) -> str:
    field_id, label, item = match.groups()
    return (
        f'<label for="{field_id}" class="flex cursor-pointer items-center justify-center">'
        f'<span class="sr-only">{label}</span>'
        f'<input id="{field_id}" type="checkbox" aria-label="{label}" data-activity-item="{item}" '
        'class="h-9 w-9 cursor-pointer accent-cyan-600 max-sm:h-7 max-sm:w-7">'
        '</label>'
    )


page44, replacements44 = text_field.subn(page44_tick, page44)
if replacements44 != 12:
    raise RuntimeError(f"Expected to replace 12 page-44 blank fields, replaced {replacements44}")
page44 = page44.replace(
    "{\"item-1\":\"Yes\",\"item-2\":\"No\",\"item-3\":\"No\",\"item-4\":\"Yes\",\"item-5\":\"Yes\",\"item-6\":\"No\",\"item-7\":\"Yes\",\"item-8\":\"No\",\"item-9\":\"No\",\"item-10\":\"Yes\",\"item-11\":\"No\",\"item-12\":\"Yes\"}",
    "{\"item-1\":true,\"item-2\":false,\"item-3\":false,\"item-4\":true,\"item-5\":true,\"item-6\":false,\"item-7\":true,\"item-8\":false,\"item-9\":false,\"item-10\":true,\"item-11\":false,\"item-12\":true}",
)
page44_path.write_text(page44, encoding="utf-8")

print("Converted pages 43–44 to 22 tick-only living/non-living controls.")
