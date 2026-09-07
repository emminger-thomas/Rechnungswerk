"""CSV/XLSX customer import with auto column-mapping and validation.

Implements SPEC.md 4.1: upload .xlsx/.csv, auto-map German column headers,
validate rows (VAT ID checksum, email syntax) before committing.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field

import pandas as pd
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from stdnum.eu import vat as eu_vat

from customers.models import Customer

# Target Customer field -> accepted (normalized, lowercased) header aliases.
FIELD_ALIASES: dict[str, list[str]] = {
    "name": ["name", "kundenname", "firma", "firmenname", "unternehmen"],
    "contact_person": ["ansprechpartner", "kontakt", "contact"],
    "street": ["strasse", "straße", "adresse", "street"],
    "zip_code": ["plz", "postleitzahl", "zip"],
    "city": ["ort", "stadt", "city"],
    "country": ["land", "country"],
    "vat_id": ["ust-idnr", "ust-idnr.", "ustid", "ustidnr", "vat id", "vatid"],
    "leitweg_id": ["leitweg-id", "leitwegid"],
    "email": ["e-mail", "email", "mail"],
    "phone": ["telefon", "tel", "phone"],
}

REQUIRED_FIELDS = ("name", "zip_code", "city")

_email_validator = EmailValidator()


def _normalize_header(header: str) -> str:
    return str(header).strip().lower()


def _load_dataframe(file_obj, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_obj.read()), dtype=str, keep_default_na=False)
    return pd.read_excel(io.BytesIO(file_obj.read()), dtype=str, engine="openpyxl").fillna("")


def auto_map_columns(columns: list[str]) -> tuple[dict[str, str], list[str]]:
    """Map source column names to Customer fields.

    Returns (mapping: {source_column: target_field}, unmapped_columns).
    """
    mapping: dict[str, str] = {}
    unmapped: list[str] = []
    for column in columns:
        normalized = _normalize_header(column)
        matched_field = None
        for field_name, aliases in FIELD_ALIASES.items():
            if normalized in aliases:
                matched_field = field_name
                break
        if matched_field and matched_field not in mapping.values():
            mapping[column] = matched_field
        else:
            unmapped.append(column)
    return mapping, unmapped


def validate_row(data: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for required in REQUIRED_FIELDS:
        if not data.get(required):
            errors.append(f"Pflichtfeld '{required}' fehlt")

    vat_id = (data.get("vat_id") or "").strip()
    if vat_id:
        try:
            if not eu_vat.is_valid(vat_id):
                errors.append(f"USt-IdNr. '{vat_id}' ist ungültig (Prüfziffernfehler)")
        except Exception:
            errors.append(f"USt-IdNr. '{vat_id}' konnte nicht geprüft werden")

    email = (data.get("email") or "").strip()
    if email:
        try:
            _email_validator(email)
        except DjangoValidationError:
            errors.append(f"E-Mail-Adresse '{email}' ist ungültig")

    return errors


@dataclass
class ImportPreviewRow:
    data: dict[str, str]
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass
class ImportPreview:
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    rows: list[ImportPreviewRow]

    @property
    def valid_count(self) -> int:
        return sum(1 for row in self.rows if row.is_valid)


def build_preview(
    file_obj, filename: str, column_overrides: dict[str, str] | None = None
) -> ImportPreview:
    """Parse the uploaded file and return a validated preview.

    column_overrides lets the frontend correct auto-mapping guesses, e.g.
    {"Straße 1": "street"}.
    """
    df = _load_dataframe(file_obj, filename)
    mapping, unmapped = auto_map_columns(list(df.columns))
    if column_overrides:
        for source_column, target_field in column_overrides.items():
            if source_column in df.columns:
                mapping[source_column] = target_field
                if source_column in unmapped:
                    unmapped.remove(source_column)

    rows: list[ImportPreviewRow] = []
    for _, series in df.iterrows():
        row_data: dict[str, str] = {}
        for source_column, target_field in mapping.items():
            row_data[target_field] = str(series.get(source_column, "") or "").strip()
        row_data.setdefault("country", "DE")
        errors = validate_row(row_data)
        rows.append(ImportPreviewRow(data=row_data, errors=errors))

    return ImportPreview(mapped_columns=mapping, unmapped_columns=unmapped, rows=rows)


def commit_import(preview: ImportPreview) -> int:
    """Bulk-create Customer rows for every valid row in the preview."""
    valid_rows = [row.data for row in preview.rows if row.is_valid]
    customers = [
        Customer(
            name=row["name"],
            contact_person=row.get("contact_person", ""),
            street=row.get("street", ""),
            zip_code=row["zip_code"],
            city=row["city"],
            country=row.get("country") or "DE",
            vat_id=row.get("vat_id", ""),
            leitweg_id=row.get("leitweg_id", ""),
            email=row.get("email", ""),
            phone=row.get("phone", ""),
        )
        for row in valid_rows
    ]
    Customer.objects.bulk_create(customers)
    return len(customers)
