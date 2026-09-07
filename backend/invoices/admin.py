from django.contrib import admin

from .models import AuditLogEntry, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "status", "is_locked", "total_gross", "created_at")
    list_filter = ("status", "document_type")
    search_fields = ("invoice_number", "customer__name")
    inlines = [InvoiceItemInline]


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ("invoice", "action", "actor", "timestamp")
    list_filter = ("action",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
