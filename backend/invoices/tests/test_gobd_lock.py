from django.test import TestCase

from invoices.exceptions import GoBDLockError
from invoices.services.finalize import finalize_invoice

from .factories import make_company_settings, make_invoice_with_item


class GoBDLockTests(TestCase):
    def setUp(self):
        make_company_settings()

    def test_draft_invoice_can_be_edited(self):
        invoice = make_invoice_with_item()
        invoice.notes = "updated"
        invoice.save()  # should not raise
        invoice.refresh_from_db()
        self.assertEqual(invoice.notes, "updated")

    def test_finalized_invoice_save_is_blocked(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        invoice.notes = "should fail"
        with self.assertRaises(GoBDLockError):
            invoice.save()

    def test_finalized_invoice_delete_is_blocked(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        with self.assertRaises(GoBDLockError):
            invoice.delete()

    def test_finalized_invoice_fields_unchanged_after_failed_write(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        original_notes = invoice.notes

        invoice.notes = "attempted change"
        with self.assertRaises(GoBDLockError):
            invoice.save()

        invoice.refresh_from_db()
        self.assertEqual(invoice.notes, original_notes)
