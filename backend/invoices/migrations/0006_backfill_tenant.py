from django.db import migrations


def backfill_tenant(apps, schema_editor):
    Tenant = apps.get_model("tenants", "Tenant")
    Invoice = apps.get_model("invoices", "Invoice")
    NumberingCounter = apps.get_model("invoices", "NumberingCounter")
    CompanySettings = apps.get_model("company", "CompanySettings")

    tenant = Tenant.objects.first()
    if tenant is None:
        settings_row = CompanySettings.objects.first()
        name = (settings_row.company_name if settings_row else "") or "Standardmandant"
        tenant = Tenant.objects.create(name=name)

    Invoice.objects.filter(tenant__isnull=True).update(tenant=tenant)
    NumberingCounter.objects.filter(tenant__isnull=True).update(tenant=tenant)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0005_alter_numberingcounter_unique_together_and_more"),
        ("tenants", "0001_initial"),
        ("company", "0001_initial"),
        # Ensures the customers-app backfill (which may create the one
        # Tenant row) runs first, so both apps converge on the same tenant
        # instead of each creating their own when run together.
        ("customers", "0005_backfill_tenant"),
    ]

    operations = [
        migrations.RunPython(backfill_tenant, noop_reverse),
    ]
