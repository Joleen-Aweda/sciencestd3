import re


ROMAN_WORDS = {
    "i": "one",
    "ii": "two",
    "iii": "three",
    "iv": "four",
    "v": "five",
    "vi": "six",
    "vii": "seven",
    "viii": "eight",
    "ix": "nine",
    "x": "ten",
}

# These are genuine Roman-one list items. Other isolated “(i)” entries, such
# as the ninth answer option on page 53, remain the spoken letter i.
ROMAN_ONE_IDS = {
    "pg014_n0031",
    "pg020_n0030",
    "pg030_n0016", "pg030_n0019", "pg030_n0026", "pg030_n0034",
    "pg030_n0042", "pg030_n0050", "pg030_n0058", "pg030_n0066",
    "pg036_n0015",
    "pg064_n0016",
}


def normalize_spoken(text_id: str, value: str) -> str:
    value = re.sub(r"\[\[blank:[^\]]+\]\]", "", value)
    value = value.replace("↑", "up arrow").replace("↓", "down arrow")
    value = value.replace("←", "left arrow").replace("→", "right arrow")

    base_id = text_id.removesuffix("_easy_read")

    def roman(match: re.Match[str]) -> str:
        token = match.group(1).lower()
        if token != "i" or base_id in ROMAN_ONE_IDS:
            return f"Roman {ROMAN_WORDS[token]}."
        return match.group(0)

    value = re.sub(r"\((i|ii|iii|iv|v|vi|vii|viii|ix|x)\)", roman, value, flags=re.IGNORECASE)
    value = re.sub(r"\(([a-h])\)", r"\1.", value, flags=re.IGNORECASE)
    return re.sub(r"\s+([.,;:!?])", r"\1", value).strip()
