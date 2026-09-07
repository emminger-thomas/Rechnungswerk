from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_number", "name", "city", "vat_id", "email", "created_at")
    search_fields = ("customer_number", "name", "zip_code", "city", "vat_id")
