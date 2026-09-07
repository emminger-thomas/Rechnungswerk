"""Orchestrates SPEC.md §4.3's finalize pipeline and §4.4's storno flow."""

import hashlib
from datetime import timedelta

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from company.models import CompanySettings

from .. import audit
from ..exceptions import InvalidInvoiceError
from ..models import (
    DOCUMENT_TYPE_STORNO,
    STATUS_CANCELLED,
    STATUS_ISSUED,
    Invoice,
    InvoiceItem,
)
from ..numbering import get_next_invoice_number, get_next_storno_number
from .pdf import render_invoice_pdf
from .pdfa3 import embed_zugferd_xml
from .validation import validate_invoice_for_finalize
from .zugferd import build_cii_xml


def finalize_invoice(invoice: Invoice, actor: str = "system", source_ip: str | None = None) -> Invoice:
    errors = validate_invoice_for_finalize(invoice)
    if errors:
        raise InvalidInvoiceError(errors)

    with transaction.atomic():
        invoice.invoice_number = get_next_invoice_number(invoice.tenant)
        invoice.issue_date = timezone.localdate()
        settings_row = CompanySettings.get_solo()
        if invoice.due_date is None:
            invoice.due_date = invoice.issue_date + timedelta(
                days=settings_row.default_due_days
            )
        invoice.recalculate_totals()

        xml_bytes = build_cii_xml(invoice)
        plain_pdf = render_invoice_pdf(invoice)
        pdfa3_bytes = embed_zugferd_xml(plain_pdf, xml_bytes)

        invoice.xml_content = xml_bytes.decode("utf-8")
        invoice.sha256_hash = hashlib.sha256(pdfa3_bytes).hexdigest()
        invoice.pdf_file.save(
            f"{invoice.invoice_number}.pdf", ContentFile(pdfa3_bytes), save=False
        )
        invoice.status = STATUS_ISSUED
        invoice.is_locked = True
        invoice.save(allow_locked_write=True)

        audit.log_event(invoice, audit.AuditLogEntry.ACTION_FINALIZED, actor=actor, source_ip=source_ip)

    return invoice


def cancel_invoice(invoice: Invoice, actor: str = "system", source_ip: str | None = None) -> Invoice:
    if invoice.document_type == DOCUMENT_TYPE_STORNO:
        raise InvalidInvoiceError(["Eine Stornorechnung kann nicht erneut storniert werden."])
    if invoice.status == STATUS_CANCELLED:
        raise InvalidInvoiceError(["Diese Rechnung wurde bereits storniert."])
    if not invoice.is_locked:
        raise InvalidInvoiceError(["Nur finalisierte Rechnungen können storniert werden."])

    with transaction.atomic():
        storno = Invoice(
            tenant=invoice.tenant,
            customer=invoice.customer,
            document_type=DOCUMENT_TYPE_STORNO,
            cancels_invoice=invoice,
            delivery_date=invoice.delivery_date,
            notes=f"Stornorechnung zu {invoice.invoice_number}",
        )
        storno.save()

        for item in invoice.items.all():
            InvoiceItem.objects.create(
                invoice=storno,
                position_index=item.position_index,
                description=item.description,
                quantity=-item.quantity,
                unit_label=item.unit_label,
                unit_price=item.unit_price,
                tax_scenario=item.tax_scenario,
                tax_rate=item.tax_rate,
            )
        storno.recalculate_totals(save=True)

        storno.invoice_number = get_next_storno_number(storno.tenant)
        storno.issue_date = timezone.localdate()
        storno.due_date = storno.issue_date

        xml_bytes = build_cii_xml(storno)
        plain_pdf = render_invoice_pdf(storno)
        pdfa3_bytes = embed_zugferd_xml(plain_pdf, xml_bytes)

        storno.xml_content = xml_bytes.decode("utf-8")
        storno.sha256_hash = hashlib.sha256(pdfa3_bytes).hexdigest()
        storno.pdf_file.save(
            f"{storno.invoice_number}.pdf", ContentFile(pdfa3_bytes), save=False
        )
        storno.status = STATUS_ISSUED
        storno.is_locked = True
        storno.save(allow_locked_write=True)

        audit.log_event(storno, audit.AuditLogEntry.ACTION_CREATED, actor=actor, source_ip=source_ip)
        audit.log_event(storno, audit.AuditLogEntry.ACTION_FINALIZED, actor=actor, source_ip=source_ip)

        invoice.status = STATUS_CANCELLED
        invoice.save(update_fields=["status"], allow_locked_write=True)
        audit.log_event(invoice, audit.AuditLogEntry.ACTION_CANCELLED, actor=actor, source_ip=source_ip, extra={"storno_invoice_number": storno.invoice_number})

    return storno
