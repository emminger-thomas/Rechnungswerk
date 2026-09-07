"""Sequential Kundennummer assignment (SPEC.md 4.1)."""

from django.db import transaction

from .models import CustomerNumberCounter

CUSTOMER_NUMBER_PREFIX = "K"


def get_next_customer_number() -> str:
    with transaction.atomic():
        counter, _ = CustomerNumberCounter.objects.select_for_update().get_or_create(
            pk=1, defaults={"last_number": 0}
        )
        counter.last_number += 1
        counter.save(update_fields=["last_number"])
        return f"{CUSTOMER_NUMBER_PREFIX}-{counter.last_number:04d}"
