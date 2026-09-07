import zipfile
from datetime import timedelta
from io import BytesIO

from django.utils import timezone
from rest_framework.test import APITestCase

from invoices.exceptions import InvalidInvoiceError
from invoices.models import STATUS_ISSUED, STATUS_OVERDUE, STATUS_PAID, Invoice
from invoices.services.dashboard import create_reminder, mark_paid, sync_overdue_statuses
from invoices.services.datev_export import build_datev_export
from invoices.services.finalize import finalize_invoice

from .factories import make_company_settings, make_invoice_with_item


class MarkPaidTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_mark_paid_via_api_sets_status_and_paid_date(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        response = self.client.post(
            f"/api/invoices/{invoice.id}/mark-paid/", {"paid_date": "2026-01-15"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, STATUS_PAID)
        self.assertEqual(str(invoice.paid_date), "2026-01-15")

    def test_mark_paid_rejects_draft(self):
        invoice = make_invoice_with_item()
        with self.assertRaises(InvalidInvoiceError):
            mark_paid(invoice, timezone.localdate())


class ReminderTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_create_reminder_increments_level(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)

        first = create_reminder(invoice)
        second = create_reminder(invoice)
        self.assertEqual(first.level, 1)
        self.assertEqual(second.level, 2)
        self.assertEqual(invoice.reminders.count(), 2)

    def test_remind_via_api_rejects_draft(self):
        invoice = make_invoice_with_item()
        response = self.client.post(f"/api/invoices/{invoice.id}/remind/")
        self.assertEqual(response.status_code, 400)


class OverdueSyncTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_sync_flips_past_due_issued_invoice_to_overdue(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        Invoice.objects.filter(pk=invoice.pk).update(
            due_date=timezone.localdate() - timedelta(days=1)
        )

        changed = sync_overdue_statuses()

        invoice.refresh_from_db()
        self.assertEqual(changed, 1)
        self.assertEqual(invoice.status, STATUS_OVERDUE)

    def test_list_endpoint_triggers_overdue_sync(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        Invoice.objects.filter(pk=invoice.pk).update(
            due_date=timezone.localdate() - timedelta(days=1)
        )

        self.client.get("/api/invoices/")

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, STATUS_OVERDUE)


class DatevExportTests(APITestCase):
    def setUp(self):
        make_company_settings()

    def test_export_zip_contains_csv_and_pdf(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        today = timezone.localdate()

        zip_buffer, filename = build_datev_export(today.year, today.month)

        self.assertTrue(filename.startswith("DATEV_Export_"))
        with zipfile.ZipFile(zip_buffer) as archive:
            names = archive.namelist()
            self.assertIn("buchungsliste.csv", names)
            self.assertIn(f"pdf/{invoice.invoice_number}.pdf", names)
            csv_content = archive.read("buchungsliste.csv").decode("utf-8-sig")
            self.assertIn(invoice.invoice_number, csv_content)

    def test_export_endpoint_returns_zip(self):
        invoice = make_invoice_with_item()
        finalize_invoice(invoice)
        today = timezone.localdate()

        response = self.client.get(
            f"/api/export/datev?year={today.year}&month={today.month}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        content = b"".join(response.streaming_content)
        with zipfile.ZipFile(BytesIO(content)) as archive:
            self.assertIn("buchungsliste.csv", archive.namelist())

    def test_export_endpoint_requires_year_and_month(self):
        response = self.client.get("/api/export/datev")
        self.assertEqual(response.status_code, 400)
