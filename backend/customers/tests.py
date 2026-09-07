import io

from django.test import TestCase
from rest_framework.test import APITestCase

from customers.services.csv_import import auto_map_columns, build_preview, commit_import, validate_row
from customers.models import Customer
from customers.numbering import get_next_customer_number
from tenants.models import Tenant


def _get_or_create_tenant() -> Tenant:
    # The tenant-backfill migration already seeds exactly one Tenant row
    # even on a fresh (test) database, so get_current_tenant()'s
    # Tenant.objects.get() has something to find; reuse it here instead of
    # creating a second row that would break that single-row invariant.
    tenant = Tenant.objects.first()
    return tenant or Tenant.objects.create(name="Test GmbH")


class AutoMapColumnsTests(TestCase):
    def test_maps_german_headers(self):
        mapping, unmapped = auto_map_columns(
            ["Kundenname", "Straße", "PLZ", "Ort", "USt-IdNr.", "E-Mail", "Extra Spalte"]
        )
        self.assertEqual(mapping["Kundenname"], "name")
        self.assertEqual(mapping["Straße"], "street")
        self.assertEqual(mapping["PLZ"], "zip_code")
        self.assertEqual(mapping["Ort"], "city")
        self.assertEqual(mapping["USt-IdNr."], "vat_id")
        self.assertEqual(mapping["E-Mail"], "email")
        self.assertEqual(unmapped, ["Extra Spalte"])


class ValidateRowTests(TestCase):
    def test_missing_required_field(self):
        errors = validate_row({"name": "", "zip_code": "12345", "city": "Berlin"})
        self.assertTrue(any("name" in e for e in errors))

    def test_invalid_email(self):
        errors = validate_row(
            {"name": "A", "zip_code": "1", "city": "B", "email": "not-an-email"}
        )
        self.assertTrue(any("E-Mail" in e for e in errors))

    def test_valid_row_has_no_errors(self):
        errors = validate_row(
            {"name": "A", "zip_code": "12345", "city": "Berlin", "email": "a@example.com"}
        )
        self.assertEqual(errors, [])


class CsvImportPreviewTests(TestCase):
    def setUp(self):
        _get_or_create_tenant()

    def _csv_file(self, content: str):
        return io.BytesIO(content.encode("utf-8"))

    def test_preview_and_commit(self):
        csv_content = (
            "Kundenname,Straße,PLZ,Ort,E-Mail\n"
            "Mueller GmbH,Hauptstr. 1,10115,Berlin,info@mueller.example\n"
            ",Nebenstr. 2,10117,Berlin,bad-email\n"
        )
        preview = build_preview(self._csv_file(csv_content), "kunden.csv")

        self.assertEqual(preview.valid_count, 1)
        self.assertEqual(len(preview.rows), 2)
        self.assertTrue(preview.rows[0].is_valid)
        self.assertFalse(preview.rows[1].is_valid)

        created = commit_import(preview)
        self.assertEqual(created, 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.first().name, "Mueller GmbH")
        self.assertTrue(Customer.objects.first().customer_number.startswith("K-"))


class CustomerNumberTests(TestCase):
    def test_numbers_are_sequential_and_gap_free(self):
        tenant = Tenant.objects.create(name="Anderer Mandant")
        first = get_next_customer_number(tenant)
        second = get_next_customer_number(tenant)
        self.assertEqual(first, "K-0001")
        self.assertEqual(second, "K-0002")


class CustomerSearchApiTests(APITestCase):
    def setUp(self):
        self.tenant = _get_or_create_tenant()

    def test_search_matches_customer_number(self):
        customer = Customer.objects.create(
            tenant=self.tenant,
            customer_number=get_next_customer_number(self.tenant),
            name="Muster Kunde GmbH",
            street="Kundenweg 1",
            zip_code="10115",
            city="Berlin",
        )

        response = self.client.get(f"/api/customers/search/?q={customer.customer_number}")

        self.assertEqual(response.status_code, 200)
        ids = [row["id"] for row in response.json()]
        self.assertIn(str(customer.id), ids)

    def test_create_via_api_assigns_customer_number(self):
        response = self.client.post(
            "/api/customers/",
            {
                "name": "Neuer Kunde",
                "street": "Teststr. 1",
                "zip_code": "12345",
                "city": "Berlin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["customer_number"].startswith("K-"))
