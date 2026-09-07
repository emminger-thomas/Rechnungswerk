from django.db import migrations


def backfill_customer_numbers(apps, schema_editor):
    Customer = apps.get_model("customers", "Customer")
    CustomerNumberCounter = apps.get_model("customers", "CustomerNumberCounter")
    counter, _ = CustomerNumberCounter.objects.get_or_create(pk=1, defaults={"last_number": 0})
    for customer in Customer.objects.filter(customer_number="").order_by("created_at"):
        counter.last_number += 1
        customer.customer_number = f"K-{counter.last_number:04d}"
        customer.save(update_fields=["customer_number"])
    counter.save(update_fields=["last_number"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0002_customernumbercounter_customer_customer_number"),
    ]

    operations = [
        migrations.RunPython(backfill_customer_numbers, noop_reverse),
    ]
