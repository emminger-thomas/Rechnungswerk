from django.db import transaction
from django.utils import timezone

from company.models import CompanySettings

from .models import NumberingCounter


def get_next_number(prefix: str, year: int | None = None) -> str:
    """Atomically consume the next gap-free number for (prefix, year).

    Must be called inside the same transaction that persists the state
    change consuming this number (e.g. finalizing an invoice), so that a
    rolled-back transaction also rolls back the counter increment and never
    creates a gap.
    """
    year = year or timezone.localdate().year
    with transaction.atomic():
        counter, _ = NumberingCounter.objects.select_for_update().get_or_create(
            series=prefix, year=year, defaults={"last_number": 0}
        )
        counter.last_number += 1
        counter.save(update_fields=["last_number"])
        return f"{prefix}-{year}-{counter.last_number:04d}"


def get_next_invoice_number() -> str:
    settings_row = CompanySettings.get_solo()
    return get_next_number(settings_row.invoice_number_prefix)


def get_next_storno_number() -> str:
    settings_row = CompanySettings.get_solo()
    return get_next_number(settings_row.storno_number_prefix)
