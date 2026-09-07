from django.db import transaction
from rest_framework import serializers

from customers.serializers import CustomerLookupSerializer

from .models import Invoice, InvoiceItem
from .tax import TAX_SCENARIO_CHOICES


class InvoiceItemSerializer(serializers.ModelSerializer):
    tax_scenario = serializers.ChoiceField(choices=TAX_SCENARIO_CHOICES)

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "position_index",
            "description",
            "quantity",
            "unit_label",
            "unit_code",
            "unit_price",
            "tax_scenario",
            "tax_rate",
            "tax_category_code",
            "line_total",
        ]
        read_only_fields = ["id", "unit_code", "tax_category_code", "tax_rate", "line_total"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    customer_detail = CustomerLookupSerializer(source="customer", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "customer",
            "customer_detail",
            "invoice_number",
            "document_type",
            "cancels_invoice",
            "status",
            "is_locked",
            "issue_date",
            "delivery_date",
            "due_date",
            "notes",
            "total_net",
            "total_tax",
            "total_gross",
            "sha256_hash",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "document_type",
            "cancels_invoice",
            "status",
            "is_locked",
            "issue_date",
            "total_net",
            "total_tax",
            "total_gross",
            "sha256_hash",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        if self.instance is not None and self.instance.is_locked:
            raise serializers.ValidationError(
                "GoBD-Verletzung: Finalisierte Rechnungen dürfen nicht geändert werden."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)
        self._replace_items(invoice, items_data)
        invoice.recalculate_totals(save=True)
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            self._replace_items(instance, items_data)
        instance.recalculate_totals(save=True)
        return instance

    def _replace_items(self, invoice, items_data):
        invoice.items.all().delete()
        for index, item_data in enumerate(items_data, start=1):
            item_data.pop("position_index", None)
            InvoiceItem.objects.create(invoice=invoice, position_index=index, **item_data)
