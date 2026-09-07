from company.models import CompanySettings
from customers.models import Customer
from customers.numbering import get_next_customer_number
from invoices.models import Invoice, InvoiceItem
from tenants.current import get_current_tenant
from tenants.models import Tenant


def make_tenant() -> Tenant:
    return Tenant.objects.create(name="Test GmbH")


def make_company_settings() -> CompanySettings:
    if not Tenant.objects.exists():
        make_tenant()
    settings_row = CompanySettings.get_solo()
    settings_row.company_name = "Test GmbH"
    settings_row.street = "Teststr. 1"
    settings_row.zip_code = "12345"
    settings_row.city = "Berlin"
    settings_row.country = "DE"
    settings_row.vat_id = "DE136695976"
    settings_row.iban = "DE02120300000000202051"
    settings_row.default_due_days = 14
    settings_row.save()
    return settings_row


def make_customer(**overrides) -> Customer:
    tenant = get_current_tenant()
    defaults = dict(
        tenant=tenant,
        customer_number=get_next_customer_number(tenant),
        name="Test Kunde GmbH",
        street="Kundenweg 1",
        zip_code="10115",
        city="Berlin",
        country="DE",
    )
    defaults.update(overrides)
    return Customer.objects.create(**defaults)


def make_invoice_with_item(customer=None, **item_overrides) -> Invoice:
    customer = customer or make_customer()
    invoice = Invoice.objects.create(tenant=get_current_tenant(), customer=customer)
    item_defaults = dict(
        invoice=invoice,
        position_index=1,
        description="Testleistung",
        quantity=2,
        unit_label="Std.",
        unit_price=100,
        tax_scenario="STANDARD",
    )
    item_defaults.update(item_overrides)
    InvoiceItem.objects.create(**item_defaults)
    invoice.recalculate_totals(save=True)
    return invoice
