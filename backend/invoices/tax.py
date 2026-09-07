"""Tax scenario definitions per SPEC.md 4.2: rate, EN 16931 category code,
and the mandatory German legal notice text that must appear on the PDF.
"""

from decimal import Decimal

STANDARD = "STANDARD"
REDUCED = "REDUCED"
SMALL_BUSINESS = "SMALL_BUSINESS"
REVERSE_CHARGE = "REVERSE_CHARGE"

TAX_SCENARIO_CHOICES = [
    (STANDARD, "Standard (19%)"),
    (REDUCED, "Ermäßigt (7%)"),
    (SMALL_BUSINESS, "Kleinunternehmerregelung (§ 19 UStG)"),
    (REVERSE_CHARGE, "Bauleistung (§ 13b UStG, Reverse Charge)"),
]

# scenario -> (default rate, EN16931 tax category code, mandatory legal text or None)
TAX_SCENARIOS: dict[str, tuple[Decimal, str, str | None]] = {
    STANDARD: (Decimal("19.00"), "S", None),
    REDUCED: (Decimal("7.00"), "S", None),
    SMALL_BUSINESS: (
        Decimal("0.00"),
        "E",
        "Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.",
    ),
    REVERSE_CHARGE: (
        Decimal("0.00"),
        "AE",
        "Steuerschuldnerschaft des Leistungsempfängers (Reverse Charge / § 13b UStG).",
    ),
}


def default_rate_for_scenario(scenario: str) -> Decimal:
    return TAX_SCENARIOS[scenario][0]


def category_code_for_scenario(scenario: str) -> str:
    return TAX_SCENARIOS[scenario][1]


def legal_notice_for_scenario(scenario: str) -> str | None:
    return TAX_SCENARIOS[scenario][2]
