from rest_framework import serializers

from .models import CompanySettings


class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = [
            "company_name",
            "owner_name",
            "street",
            "zip_code",
            "city",
            "country",
            "tax_number",
            "vat_id",
            "iban",
            "bic",
            "bank_name",
            "email",
            "phone",
            "is_small_business",
            "default_due_days",
            "invoice_number_prefix",
            "storno_number_prefix",
            "logo",
        ]
