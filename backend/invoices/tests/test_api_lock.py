from rest_framework.test import APITestCase

from invoices.services.finalize import finalize_invoice

from .factories import make_company_settings, make_invoice_with_item


class InvoiceApiLockTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_put_on_locked_invoice_returns_403(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        response = self.client.patch(
            f"/api/invoices/{invoice.id}/", {"notes": "nope"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_put_on_draft_invoice_succeeds(self):
        invoice = make_invoice_with_item()
        response = self.client.patch(
            f"/api/invoices/{invoice.id}/", {"notes": "ok"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
