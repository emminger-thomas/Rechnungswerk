from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerLookupSerializer(serializers.ModelSerializer):
    """Lightweight payload for the fast search-as-you-type autocomplete."""

    class Meta:
        model = Customer
        fields = ["id", "name", "city", "vat_id", "leitweg_id"]
