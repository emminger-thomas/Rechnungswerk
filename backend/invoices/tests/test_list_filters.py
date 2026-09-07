from rest_framework.test import APITestCase

from invoices.services.finalize import finalize_invoice

from .factories import make_company_settings, make_customer, make_invoice_with_item


class InvoiceListFilterTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_status_filter(self):
        draft = make_invoice_with_item()
        issued = make_invoice_with_item()
        finalize_invoice(issued)

        response = self.client.get("/api/invoices/?status=DRAFT")

        ids = [row["id"] for row in response.json()["results"]]
        self.assertIn(str(draft.id), ids)
        self.assertNotIn(str(issued.id), ids)

    def test_month_filter_matches_issue_date(self):
        invoice = make_invoice_with_item()
        finalized = finalize_invoice(invoice)
        month = finalized.issue_date.strftime("%Y-%m")

        response = self.client.get(f"/api/invoices/?month={month}")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertIn(str(finalized.id), ids)

        response = self.client.get("/api/invoices/?month=1999-01")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertNotIn(str(finalized.id), ids)

    def test_month_filter_falls_back_to_delivery_date_for_drafts(self):
        draft = make_invoice_with_item()
        month = draft.delivery_date.strftime("%Y-%m")

        response = self.client.get(f"/api/invoices/?month={month}")

        ids = [row["id"] for row in response.json()["results"]]
        self.assertIn(str(draft.id), ids)

    def test_q_filter_matches_invoice_number_and_customer_name(self):
        customer = make_customer(name="Sonnenschein Elektro GmbH")
        invoice = make_invoice_with_item(customer=customer)
        finalized = finalize_invoice(invoice)
        other = make_invoice_with_item()

        response = self.client.get(f"/api/invoices/?q={finalized.invoice_number}")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertIn(str(finalized.id), ids)
        self.assertNotIn(str(other.id), ids)

        response = self.client.get("/api/invoices/?q=Sonnenschein")
        ids = [row["id"] for row in response.json()["results"]]
        self.assertIn(str(finalized.id), ids)
