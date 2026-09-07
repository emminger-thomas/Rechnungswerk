import hashlib
import json

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


def log_event(invoice, action: str, actor: str = "system", source_ip: str | None = None, extra: dict | None = None):
    payload_hash = hash_payload(_payload_for(invoice))
    return AuditLogEntry.objects.create(
        invoice=invoice,
        action=action,
        actor=actor,
        source_ip=source_ip,
        payload_hash=payload_hash,
        details=extra or {},
    )
