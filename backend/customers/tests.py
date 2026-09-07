import io

from django.test import TestCase

from customers.services.csv_import import auto_map_columns, build_preview, commit_import, validate_row
from customers.models import Customer


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
