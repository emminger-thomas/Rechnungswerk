from django.db import models
from solo.models import SingletonModel


class CompanySettings(SingletonModel):
    company_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2, default="DE")
    tax_number = models.CharField("Steuernummer", max_length=50, blank=True)
    vat_id = models.CharField("USt-IdNr.", max_length=50, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    bic = models.CharField(max_length=11, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_small_business = models.BooleanField(
        "Kleinunternehmerregelung (§19 UStG)", default=False
    )
    default_due_days = models.PositiveIntegerField(default=14)
    invoice_number_prefix = models.CharField(max_length=10, default="RE")
    storno_number_prefix = models.CharField(max_length=10, default="ST")
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    class Meta:
        verbose_name = "Firmeneinstellungen"

    def __str__(self):
        return self.company_name or "Firmeneinstellungen"
