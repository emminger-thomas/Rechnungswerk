import uuid

from django.db import models


class Tenant(models.Model):
    """A billable account (one Handwerksbetrieb).

    Deployment is single-tenant today (see tenants/current.py), but every
    data-carrying model already has a tenant FK so the future move to real
    multi-tenancy only requires wiring auth to resolve the tenant per
    request, not another schema/backfill migration.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mandant"
        verbose_name_plural = "Mandanten"

    def __str__(self):
        return self.name
