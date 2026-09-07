from django.db import transaction
from django.utils import timezone

from company.models import CompanySettings
from tenants.models import Tenant

from .models import NumberingCounter


def get_next_number(tenant: Tenant, prefix: str, year: int | None = None) -> str:
    """Atomically consume the next gap-free number for (tenant, prefix, year).

    Must be called inside the same transaction that persists the state
    change consuming this number (e.g. finalizing an invoice), so that a
    rolled-back transaction also rolls back the counter increment and never
    creates a gap.
    """
    year = year or timezone.localdate().year
    with transaction.atomic():
        counter, _ = NumberingCounter.objects.select_for_update().get_or_create(
            tenant=tenant, series=prefix, year=year, defaults={"last_number": 0}
        )
        counter.last_number += 1
        counter.save(update_fields=["last_number"])
        return f"{prefix}-{year}-{counter.last_number:04d}"


def get_next_invoice_number(tenant: Tenant) -> str:
    settings_row = CompanySettings.get_solo()
    return get_next_number(tenant, settings_row.invoice_number_prefix)


def get_next_storno_number(tenant: Tenant) -> str:
    settings_row = CompanySettings.get_solo()
    return get_next_number(tenant, settings_row.storno_number_prefix)
