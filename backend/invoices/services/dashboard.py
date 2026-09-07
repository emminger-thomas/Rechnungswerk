"""Finanz-Dashboard actions (SPEC.md §4.5): overdue tracking, marking an
invoice as paid, and creating payment reminders (Mahnungen).
"""

from django.db import transaction
from django.utils import timezone

from .. import audit
from ..exceptions import InvalidInvoiceError
from ..models import (
    STATUS_ISSUED,
    STATUS_OVERDUE,
    STATUS_PAID,
    Invoice,
    PaymentReminder,
)

PAYABLE_STATUSES = (STATUS_ISSUED, STATUS_OVERDUE)


def sync_overdue_statuses() -> int:
    """Flips ISSUED invoices past their due_date to OVERDUE.

    Uses a queryset .update() rather than instance.save() so it does not
    trip the GoBD hard lock on Invoice.save() -- this only advances a
    workflow status, it never touches the locked financial content.
    """
    today = timezone.localdate()
    stale = Invoice.objects.filter(status=STATUS_ISSUED, due_date__lt=today)
    invoice_ids = list(stale.values_list("id", flat=True))
    if not invoice_ids:
        return 0
    Invoice.objects.filter(id__in=invoice_ids).update(status=STATUS_OVERDUE)
    for invoice in Invoice.objects.filter(id__in=invoice_ids):
        audit.log_event(invoice, audit.AuditLogEntry.ACTION_MARKED_OVERDUE)
    return len(invoice_ids)


@transaction.atomic
def mark_paid(invoice: Invoice, paid_date, actor: str = "system", source_ip: str | None = None) -> Invoice:
    if invoice.status not in PAYABLE_STATUSES:
        raise InvalidInvoiceError(
            ["Nur offene oder überfällige Rechnungen können als bezahlt markiert werden."]
        )
    invoice.status = STATUS_PAID
    invoice.paid_date = paid_date
    invoice.save(update_fields=["status", "paid_date"], allow_locked_write=True)
    audit.log_event(
        invoice,
        audit.AuditLogEntry.ACTION_MARKED_PAID,
        actor=actor,
        source_ip=source_ip,
        extra={"paid_date": str(paid_date)},
    )
    return invoice


@transaction.atomic
def create_reminder(invoice: Invoice, actor: str = "system", source_ip: str | None = None) -> PaymentReminder:
    if invoice.status not in PAYABLE_STATUSES:
        raise InvalidInvoiceError(
            ["Nur offene oder überfällige Rechnungen können gemahnt werden."]
        )
    level = invoice.reminders.count() + 1
    reminder = PaymentReminder.objects.create(invoice=invoice, level=level)
    audit.log_event(
        invoice,
        audit.AuditLogEntry.ACTION_REMINDER_SENT,
        actor=actor,
        source_ip=source_ip,
        extra={"level": level},
    )
    return reminder
