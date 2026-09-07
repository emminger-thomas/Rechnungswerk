from django.test import TestCase

from invoices.audit import hash_payload, log_event
from invoices.exceptions import GoBDLockError
from invoices.models import AuditLogEntry
from invoices.services.finalize import cancel_invoice, finalize_invoice

from .factories import make_company_settings, make_invoice_with_item


class AuditTrailTests(TestCase):
    def setUp(self):
        make_company_settings()

    def test_finalize_writes_finalized_entry(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        actions = list(invoice.audit_entries.values_list("action", flat=True))
        self.assertIn(AuditLogEntry.ACTION_FINALIZED, actions)

    def test_cancel_logs_on_both_invoices(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        storno = cancel_invoice(invoice)

        invoice.refresh_from_db()
        self.assertIn(
            AuditLogEntry.ACTION_CANCELLED,
            invoice.audit_entries.values_list("action", flat=True),
        )
        self.assertIn(
            AuditLogEntry.ACTION_FINALIZED,
            storno.audit_entries.values_list("action", flat=True),
        )

    def test_payload_hash_stable_and_sensitive_to_changes(self):
        invoice = make_invoice_with_item()
        entry = log_event(invoice, AuditLogEntry.ACTION_CREATED)
        recomputed = hash_payload(
            {
                "invoice_number": invoice.invoice_number,
                "status": invoice.status,
                "total_net": str(invoice.total_net),
                "total_tax": str(invoice.total_tax),
                "total_gross": str(invoice.total_gross),
                "items": [
                    {
                        "position_index": item.position_index,
                        "description": item.description,
                        "quantity": str(item.quantity),
                        "unit_code": item.unit_code,
                        "unit_price": str(item.unit_price),
                        "tax_rate": str(item.tax_rate),
                        "line_total": str(item.line_total),
                    }
                    for item in invoice.items.all()
                ],
            }
        )
        self.assertEqual(entry.payload_hash, recomputed)

        different_hash = hash_payload({"invoice_number": "different"})
        self.assertNotEqual(entry.payload_hash, different_hash)

    def test_audit_log_entries_are_append_only(self):
        invoice = make_invoice_with_item()
        entry = log_event(invoice, AuditLogEntry.ACTION_CREATED)

        entry.details = {"tampered": True}
        with self.assertRaises(GoBDLockError):
            entry.save()

        with self.assertRaises(GoBDLockError):
            entry.delete()
