"""DATEV / Steuerberater-Export (SPEC.md §4.5 & §07): a monthly ZIP of all
issued invoice PDFs plus a CSV Buchungsliste for the accountant.
"""

import csv
import io
import zipfile

from ..models import DOCUMENT_TYPE_STORNO, STATUS_DRAFT, Invoice

CSV_HEADER = [
    "Belegdatum",
    "Belegnummer",
    "Belegtyp",
    "Kunde",
    "USt-IdNr",
    "Netto",
    "Steuer",
    "Brutto",
    "Status",
]


def _invoices_for_month(year: int, month: int):
    return (
        Invoice.objects.select_related("customer")
        .filter(issue_date__year=year, issue_date__month=month)
        .exclude(status=STATUS_DRAFT)
        .order_by("invoice_number")
    )


def build_datev_export(year: int, month: int) -> tuple[io.BytesIO, str]:
    invoices = list(_invoices_for_month(year, month))

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer, delimiter=";")
    writer.writerow(CSV_HEADER)
    for invoice in invoices:
        writer.writerow(
            [
                invoice.issue_date.isoformat() if invoice.issue_date else "",
                invoice.invoice_number or "",
                "Storno" if invoice.document_type == DOCUMENT_TYPE_STORNO else "Rechnung",
                invoice.customer.name,
                invoice.customer.vat_id,
                str(invoice.total_net),
                str(invoice.total_tax),
                str(invoice.total_gross),
                invoice.status,
            ]
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("buchungsliste.csv", csv_buffer.getvalue().encode("utf-8-sig"))
        for invoice in invoices:
            if invoice.pdf_file:
                with invoice.pdf_file.open("rb") as pdf_file:
                    archive.writestr(f"pdf/{invoice.invoice_number}.pdf", pdf_file.read())
    zip_buffer.seek(0)

    filename = f"DATEV_Export_{year:04d}-{month:02d}.zip"
    return zip_buffer, filename
