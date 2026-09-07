import uuid

from django.db import models


class CustomerNumberCounter(models.Model):
    """Backs sequential Kundennummer assignment (SPEC.md 4.1).

    A single row, incremented atomically under select_for_update() so
    concurrent customer creation (single-record or CSV bulk-import) never
    hands out the same number twice.
    """

    last_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Kundennummer-Zähler: {self.last_number}"


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_number = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    contact_person = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2, default="DE")
    vat_id = models.CharField("USt-IdNr.", max_length=50, blank=True, db_index=True)
    leitweg_id = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"

    def __str__(self):
        return self.name
