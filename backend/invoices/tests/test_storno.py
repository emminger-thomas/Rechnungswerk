from django.test import TestCase

from invoices.exceptions import InvalidInvoiceError
from invoices.models import STATUS_CANCELLED, STATUS_ISSUED
from invoices.services.finalize import cancel_invoice, finalize_invoice

from .factories import make_company_settings, make_invoice_with_item


class StornoTests(TestCase):
    def setUp(self):
        make_company_settings()

    def test_cancel_creates_negated_storno_and_preserves_original(self):
        invoice = make_invoice_with_item(quantity=3, unit_price=50)
        finalize_invoice(invoice)
        original_number = invoice.invoice_number
        original_gross = invoice.total_gross

        storno = cancel_invoice(invoice)

        self.assertEqual(storno.invoice_number.split("-")[0], "ST")
        self.assertEqual(storno.cancels_invoice_id, invoice.id)
        self.assertEqual(storno.total_gross, -original_gross)
        self.assertTrue(storno.is_locked)
        self.assertEqual(storno.status, STATUS_ISSUED)

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, STATUS_CANCELLED)
        self.assertTrue(invoice.is_locked)
        self.assertEqual(invoice.invoice_number, original_number)
        self.assertEqual(invoice.total_gross, original_gross)

    def test_cannot_cancel_a_storno(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        storno = cancel_invoice(invoice)

        with self.assertRaises(InvalidInvoiceError):
            cancel_invoice(storno)

    def test_cannot_cancel_a_draft(self):
        invoice = make_invoice_with_item()
        with self.assertRaises(InvalidInvoiceError):
            cancel_invoice(invoice)
