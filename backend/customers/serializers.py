from rest_framework import serializers

from tenants.current import get_current_tenant

from .models import Customer
from .numbering import get_next_customer_number


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_number",
            "name",
            "contact_person",
            "street",
            "zip_code",
            "city",
            "country",
            "vat_id",
            "leitweg_id",
            "email",
            "phone",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "customer_number", "created_at", "updated_at"]

    def create(self, validated_data):
        tenant = get_current_tenant()
        validated_data["tenant"] = tenant
        validated_data["customer_number"] = get_next_customer_number(tenant)
        return super().create(validated_data)


class CustomerLookupSerializer(serializers.ModelSerializer):
    """Lightweight payload for the fast search-as-you-type autocomplete."""

    class Meta:
        model = Customer
        fields = ["id", "customer_number", "name", "city", "vat_id", "leitweg_id"]
