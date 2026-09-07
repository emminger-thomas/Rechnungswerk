import hashlib
import hmac

from django.conf import settings
from django.db import migrations


def backfill_signatures(apps, schema_editor):
    AuditLogEntry = apps.get_model("invoices", "AuditLogEntry")
    key = settings.AUDIT_LOG_SECRET_KEY.encode("utf-8")
    for entry in AuditLogEntry.objects.filter(signature="").iterator():
        message = f"{entry.invoice_id}|{entry.action}|{entry.actor}|{entry.payload_hash}".encode(
            "utf-8"
        )
        entry.signature = hmac.new(key, message, hashlib.sha256).hexdigest()
        entry.save(update_fields=["signature"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0003_auditlogentry_signature"),
    ]

    operations = [
        migrations.RunPython(backfill_signatures, noop_reverse),
    ]
