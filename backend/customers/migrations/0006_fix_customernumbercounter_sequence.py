from django.db import migrations

# customers/migrations/0003_backfill_customer_number.py hardcoded pk=1 when
# creating the (then-singleton) CustomerNumberCounter row, bypassing the
# id column's auto-increment sequence entirely. That left the sequence
# stuck at its initial state while a real id=1 row exists, so the very
# next auto-assigned insert (now routine, since counters are per-tenant)
# collides on id=1. Resync the sequence to the table's actual max id.
SQL = """
SELECT setval(
    pg_get_serial_sequence('customers_customernumbercounter', 'id'),
    COALESCE((SELECT MAX(id) FROM customers_customernumbercounter), 0) + 1,
    false
);
"""


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0005_backfill_tenant"),
    ]

    operations = [
        migrations.RunSQL(SQL, migrations.RunSQL.noop),
    ]
