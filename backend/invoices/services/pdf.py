from django.template.loader import render_to_string

from company.models import CompanySettings

from ..tax import legal_notice_for_scenario


def render_invoice_pdf(invoice) -> bytes:
    from weasyprint import HTML  # imported lazily so Django can boot even if

    # the native GTK libs aren't on PATH yet (see settings/dev.py).

    settings_row = CompanySettings.get_solo()
    items = list(invoice.items.all())

    legal_notices = []
    seen = set()
    for item in items:
        notice = legal_notice_for_scenario(item.tax_scenario)
        if notice and notice not in seen:
            legal_notices.append(notice)
            seen.add(notice)

    html = render_to_string(
        "invoices/invoice_pdf.html",
        {
            "invoice": invoice,
            "company": settings_row,
            "customer": invoice.customer,
            "items": items,
            "legal_notices": legal_notices,
            "is_draft": invoice.status == "DRAFT",
        },
    )
    return HTML(string=html).write_pdf()
