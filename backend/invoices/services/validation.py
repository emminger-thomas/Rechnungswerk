"""Pre-finalize validation per § 14 UStG / EN 16931 (SPEC.md 4.3 step 1)."""

from company.models import CompanySettings


def validate_invoice_for_finalize(invoice) -> list[str]:
    errors: list[str] = []

    customer = invoice.customer
    if not customer.name:
        errors.append("Kundenname fehlt")
    if not customer.street or not customer.zip_code or not customer.city:
        errors.append("Vollständige Anschrift des Kunden erforderlich (EN 16931)")

    settings_row = CompanySettings.get_solo()
    if not settings_row.company_name:
        errors.append("Firmenname in den Firmeneinstellungen fehlt")
    if not settings_row.tax_number and not settings_row.vat_id:
        errors.append("Steuernummer oder USt-IdNr. des Ausstellers erforderlich")
    if not settings_row.street or not settings_row.zip_code or not settings_row.city:
        errors.append("Vollständige Anschrift des Ausstellers erforderlich (EN 16931)")

    items = list(invoice.items.all())
    if not items:
        errors.append("Mindestens eine Position erforderlich")

    if invoice.is_locked:
        errors.append("Rechnung ist bereits finalisiert")

    return errors
