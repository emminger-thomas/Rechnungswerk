import hashlib
import hmac
import json

from django.conf import settings

from .models import AuditLogEntry


def _payload_for(invoice) -> dict:
    return {
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "total_net": str(invoice.total_net),
        "total_tax": str(invoice.total_tax),
        "total_gross": str(invoice.total_gross),
        "items": [
            {
                "position_index": item.position_index,
                "description": item.description,
                "quantity": str(item.quantity),
                "unit_code": item.unit_code,
                "unit_price": str(item.unit_price),
                "tax_rate": str(item.tax_rate),
                "line_total": str(item.line_total),
            }
            for item in invoice.items.all()
        ],
    }


def hash_payload(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_entry(invoice_id, action: str, actor: str, payload_hash: str) -> str:
    """HMAC-SHA256 over the record's identity + content hash (SPEC.md §08's
    AuditRecord.signature). Unlike payload_hash alone, this can't be
    recomputed by someone with DB write access but without
    settings.AUDIT_LOG_SECRET_KEY, so a tampered row is detectable even if
    both its content and payload_hash were rewritten together.
    """
    message = f"{invoice_id}|{action}|{actor}|{payload_hash}".encode("utf-8")
    return hmac.new(
        settings.AUDIT_LOG_SECRET_KEY.encode("utf-8"), message, hashlib.sha256
    ).hexdigest()


def verify_entry(entry: AuditLogEntry) -> bool:
    expected = sign_entry(entry.invoice_id, entry.action, entry.actor, entry.payload_hash)
    return hmac.compare_digest(expected, entry.signature)


def log_event(invoice, action: str, actor: str = "system", source_ip: str | None = None, extra: dict | None = None):
    payload_hash = hash_payload(_payload_for(invoice))
    signature = sign_entry(invoice.id, action, actor, payload_hash)
    return AuditLogEntry.objects.create(
        invoice=invoice,
        action=action,
        actor=actor,
        source_ip=source_ip,
        payload_hash=payload_hash,
        signature=signature,
        details=extra or {},
    )
