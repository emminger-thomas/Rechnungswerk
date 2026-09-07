"""UN/ECE Recommendation 20 unit-of-measure code mapping (SPEC.md 4.2)."""

UNIT_CODE_MAP: dict[str, str] = {
    "std.": "HUR",
    "std": "HUR",
    "stunden": "HUR",
    "stunde": "HUR",
    "stk.": "C62",
    "stk": "C62",
    "stück": "C62",
    "m²": "MTK",
    "quadratmeter": "MTK",
    "m": "MTR",
    "meter": "MTR",
    "kg": "KGM",
    "kilogramm": "KGM",
    "tag": "DAY",
    "tage": "DAY",
    "pauschal": "XPP",
}

DEFAULT_UNIT_CODE = "C62"


def unit_code_for_label(label: str) -> str:
    return UNIT_CODE_MAP.get((label or "").strip().lower(), DEFAULT_UNIT_CODE)
