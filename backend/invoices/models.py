import uuid

from django.db import models
from django.utils import timezone

from .exceptions import GoBDLockError
from .tax import TAX_SCENARIO_CHOICES, category_code_for_scenario, default_rate_for_scenario
from .unit_codes import unit_code_for_label

STATUS_DRAFT = "DRAFT"
STATUS_ISSUED = "ISSUED"
STATUS_PAID = "PAID"
STATUS_OVERDUE = "OVERDUE"
STATUS_CANCELLED = "CANCELLED"

STATUS_CHOICES = [
    (STATUS_DRAFT, "Entwurf"),
    (STATUS_ISSUED, "Offen"),
    (STATUS_PAID, "Bezahlt"),
    (STATUS_OVERDUE, "Überfällig"),
    (STATUS_CANCELLED, "Storniert"),
]

DOCUMENT_TYPE_INVOICE = "INVOICE"
DOCUMENT_TYPE_STORNO = "STORNO"

DOCUMENT_TYPE_CHOICES = [
    (DOCUMENT_TYPE_INVOICE, "Rechnung"),
    (DOCUMENT_TYPE_STORNO, "Stornorechnung"),
]


class NumberingCounter(models.Model):
    """Backs gap-free sequential invoice numbering (SPEC.md 4.4).

    One row per (series, year), incremented atomically under
    select_for_update() inside the same transaction that finalizes an
    invoice, so a rolled-back finalize never leaves a gap.
    """

    series = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("series", "year")

    def __str__(self):
        return f"{self.series}-{self.year}: {self.last_number}"


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="invoices"
    )
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    document_type = models.CharField(
        max_length=10, choices=DOCUMENT_TYPE_CHOICES, default=DOCUMENT_TYPE_INVOICE
    )
    cancels_invoice = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="storno_documents",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_locked = models.BooleanField(default=False)

    issue_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    total_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    pdf_file = models.FileField(upload_to="invoices/pdf/", blank=True, null=True)
    xml_content = models.TextField(blank=True)
    sha256_hash = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"

    def __str__(self):
        return self.invoice_number or f"Entwurf {self.id}"

    def save(self, *args, allow_locked_write: bool = False, **kwargs):
        if self.pk and not allow_locked_write:
            original = Invoice.objects.filter(pk=self.pk).only("is_locked").first()
            if original and original.is_locked:
                raise GoBDLockError(
                    "GoBD-Verletzung: Finalisierte Rechnungen dürfen nicht "
                    "geändert werden. Bitte erstellen Sie eine Stornorechnung."
                )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_locked:
            raise GoBDLockError(
                "GoBD-Verletzung: Finalisierte Rechnungen dürfen nicht gelöscht werden."
            )
        super().delete(*args, **kwargs)

    def recalculate_totals(self, *, save: bool = False, allow_locked_write: bool = False):
        items = list(self.items.all())
        total_net = sum((item.line_total for item in items), start=0)
        total_tax = sum(
            (item.line_total * item.tax_rate / 100 for item in items), start=0
        )
        self.total_net = total_net
        self.total_tax = total_tax
        self.total_gross = total_net + total_tax
        if save:
            self.save(
                update_fields=["total_net", "total_tax", "total_gross"],
                allow_locked_write=allow_locked_write,
            )


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    position_index = models.PositiveIntegerField()
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_label = models.CharField(max_length=30, default="Std.")
    unit_code = models.CharField(max_length=3, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_scenario = models.CharField(
        max_length=20, choices=TAX_SCENARIO_CHOICES, default="STANDARD"
    )
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19)
    tax_category_code = models.CharField(max_length=2, blank=True)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["position_index"]
        unique_together = ("invoice", "position_index")
        verbose_name = "Rechnungsposition"
        verbose_name_plural = "Rechnungspositionen"

    def save(self, *args, **kwargs):
        self.unit_code = unit_code_for_label(self.unit_label)
        if not self.tax_rate:
            self.tax_rate = default_rate_for_scenario(self.tax_scenario)
        self.tax_category_code = category_code_for_scenario(self.tax_scenario)
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description[:40]} ({self.quantity} {self.unit_label})"


class PaymentReminder(models.Model):
    """A dunning/reminder record (SPEC.md 4.5: 'Zahlungserinnerung / Mahnung').

    Append-only alongside the audit log; only created via
    invoices.services.dashboard.create_reminder().
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, related_name="reminders", on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Zahlungserinnerung"
        verbose_name_plural = "Zahlungserinnerungen"

    def __str__(self):
        return f"Mahnstufe {self.level} für {self.invoice_id}"


class AuditLogEntry(models.Model):
    """Append-only revision log (SPEC.md 8.1). No update/delete route is
    ever exposed for this model; entries are only created via
    invoices.audit.log_event().
    """

    ACTION_CREATED = "CREATED"
    ACTION_FINALIZED = "FINALIZED"
    ACTION_EXPORTED_PDF = "EXPORTED_PDF"
    ACTION_MARKED_PAID = "MARKED_PAID"
    ACTION_REMINDER_SENT = "REMINDER_SENT"
    ACTION_CANCELLED = "CANCELLED"
    ACTION_MARKED_OVERDUE = "MARKED_OVERDUE"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Erstellt"),
        (ACTION_FINALIZED, "Finalisiert"),
        (ACTION_EXPORTED_PDF, "PDF exportiert"),
        (ACTION_MARKED_PAID, "Als bezahlt markiert"),
        (ACTION_REMINDER_SENT, "Zahlungserinnerung erstellt"),
        (ACTION_CANCELLED, "Storniert"),
        (ACTION_MARKED_OVERDUE, "Als überfällig markiert"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, related_name="audit_entries", on_delete=models.PROTECT
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.CharField(max_length=255, default="system")
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    payload_hash = models.CharField(max_length=64)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Revisionsprotokolleintrag"
        verbose_name_plural = "Revisionsprotokoll"

    def save(self, *args, **kwargs):
        if self.pk and AuditLogEntry.objects.filter(pk=self.pk).exists():
            raise GoBDLockError("Audit-Log-Einträge sind unveränderlich (append-only).")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise GoBDLockError("Audit-Log-Einträge dürfen nicht gelöscht werden.")

    def __str__(self):
        return f"{self.action} @ {self.timestamp:%Y-%m-%d %H:%M} ({self.invoice_id})"
