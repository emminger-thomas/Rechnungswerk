from django.db import migrations


def backfill_tenant(apps, schema_editor):
    Tenant = apps.get_model("tenants", "Tenant")
    Customer = apps.get_model("customers", "Customer")
    CustomerNumberCounter = apps.get_model("customers", "CustomerNumberCounter")
    CompanySettings = apps.get_model("company", "CompanySettings")

    tenant = Tenant.objects.first()
    if tenant is None:
        settings_row = CompanySettings.objects.first()
        name = (settings_row.company_name if settings_row else "") or "Standardmandant"
        tenant = Tenant.objects.create(name=name)

    Customer.objects.filter(tenant__isnull=True).update(tenant=tenant)
    CustomerNumberCounter.objects.filter(tenant__isnull=True).update(tenant=tenant)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0004_customer_tenant_customernumbercounter_tenant"),
        ("tenants", "0001_initial"),
        ("company", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_tenant, noop_reverse),
    ]
