from django.contrib import admin, messages

from . import audit
from .models import AuditLogEntry, Invoice, InvoiceItem, PaymentReminder


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
    actions = ["verify_signature"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Integrität prüfen (HMAC-Signatur)")
    def verify_signature(self, request, queryset):
        invalid = [entry for entry in queryset if not audit.verify_entry(entry)]
        if invalid:
            ids = ", ".join(str(entry.id) for entry in invalid)
            self.message_user(
                request,
                f"{len(invalid)} Eintrag/Einträge mit ungültiger Signatur: {ids}",
                level=messages.ERROR,
            )
        else:
            self.message_user(
                request, f"{queryset.count()} Einträge geprüft — alle Signaturen gültig.",
                level=messages.SUCCESS,
            )


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ("invoice", "level", "created_at")
    list_filter = ("level",)
