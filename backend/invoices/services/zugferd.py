"""Builds the UN/CEFACT CII D16B XML (ZUGFeRD 2.2 / Factur-X, profile
EN 16931 / COMFORT) for an Invoice, per SPEC.md §06's BT-field mapping.

drafthorse's nested "singular" Element fields (e.g. TradeAgreement.seller,
LineItem.settlement) are read-only descriptors: `obj.seller = x` raises
AttributeError. Every nested Element is lazily auto-created on first access
and must be mutated in place (`obj.seller.name = "..."`), never reassigned.
Only Container/MultiField attributes (e.g. tax_registrations, trade_tax)
support `.add(new_instance)`.
"""

from datetime import date
from decimal import Decimal

from drafthorse.models.accounting import ApplicableTradeTax
from drafthorse.models.document import Document
from drafthorse.models.note import IncludedNote
from drafthorse.models.party import TaxRegistration
from drafthorse.models.payment import PaymentMeans, PaymentTerms
from drafthorse.models.tradelines import LineItem

from company.models import CompanySettings

from ..tax import legal_notice_for_scenario

GUIDELINE_EN16931 = "urn:cen.eu:en16931:2017"

TYPE_CODE_INVOICE = "380"
TYPE_CODE_CREDIT_NOTE = "381"

TAX_REGISTRATION_SCHEME_VAT = "VA"
TAX_REGISTRATION_SCHEME_TAX_NUMBER = "FC"


def _tax_registration(tax_number: str, vat_id: str) -> TaxRegistration:
    reg = TaxRegistration()
    if vat_id:
        reg.id = (TAX_REGISTRATION_SCHEME_VAT, vat_id)
    elif tax_number:
        reg.id = (TAX_REGISTRATION_SCHEME_TAX_NUMBER, tax_number)
    return reg


def _fill_seller_party(party, settings_row: CompanySettings) -> None:
    party.name = settings_row.company_name
    party.description = settings_row.company_name
    party.address.postcode = settings_row.zip_code
    party.address.line_one = settings_row.street
    party.address.city_name = settings_row.city
    party.address.country_id = settings_row.country
    if settings_row.vat_id or settings_row.tax_number:
        party.tax_registrations.add(
            _tax_registration(settings_row.tax_number, settings_row.vat_id)
        )


def _fill_buyer_party(party, customer) -> None:
    party.name = customer.name
    party.description = customer.name
    party.address.postcode = customer.zip_code
    party.address.line_one = customer.street
    party.address.city_name = customer.city
    party.address.country_id = customer.country
    if customer.vat_id:
        party.tax_registrations.add(_tax_registration("", customer.vat_id))


def _build_line_item(item) -> LineItem:
    line = LineItem()
    line.document.line_id = str(item.position_index)
    line.product.name = item.description

    line.agreement.net.amount = item.unit_price
    line.delivery.billed_quantity = (item.quantity, item.unit_code)

    line.settlement.trade_tax.type_code = "VAT"
    line.settlement.trade_tax.category_code = item.tax_category_code
    line.settlement.trade_tax.rate_applicable_percent = item.tax_rate
    line.settlement.trade_tax.basis_amount = item.line_total
    line.settlement.trade_tax.calculated_amount = (
        item.line_total * item.tax_rate / 100
    ).quantize(Decimal("0.01"))
    line.settlement.monetary_summation.total_amount = item.line_total

    return line


def build_cii_document(invoice) -> Document:
    settings_row = CompanySettings.get_solo()
    customer = invoice.customer

    document = Document()
    document.context.guideline_parameter.id = GUIDELINE_EN16931

    document.header.id = invoice.invoice_number or ""
    # NOTE: Header.name ("Dokumentenart Freitext") is declared in drafthorse's
    # generic CII model but is NOT part of the EN 16931-restricted XSD subset
    # (ExchangedDocument goes straight from ID to TypeCode there) - setting it
    # fails schema validation, so it is intentionally left unset.
    document.header.type_code = (
        TYPE_CODE_CREDIT_NOTE if invoice.document_type == "STORNO" else TYPE_CODE_INVOICE
    )
    document.header.issue_date_time = invoice.issue_date or date.today()

    seen_notices: set[str] = set()
    for item in invoice.items.all():
        notice = legal_notice_for_scenario(item.tax_scenario)
        if notice and notice not in seen_notices:
            document.header.notes.add(IncludedNote(content=notice))
            seen_notices.add(notice)

    if customer.leitweg_id:
        document.trade.agreement.buyer_reference = customer.leitweg_id
    _fill_seller_party(document.trade.agreement.seller, settings_row)
    _fill_buyer_party(document.trade.agreement.buyer, customer)

    document.trade.delivery.event.occurrence = invoice.delivery_date

    document.trade.settlement.currency_code = "EUR"

    if settings_row.iban:
        means = PaymentMeans()
        means.type_code = "58"  # SEPA credit transfer
        means.payee_account.iban = settings_row.iban
        document.trade.settlement.payment_means.add(means)

    if invoice.due_date:
        terms = PaymentTerms()
        terms.description = "Zahlbar ohne Abzug"
        terms.due = invoice.due_date
        document.trade.settlement.terms.add(terms)

    tax_by_rate: dict[tuple[Decimal, str], Decimal] = {}
    for item in invoice.items.all():
        key = (item.tax_rate, item.tax_category_code)
        tax_by_rate[key] = tax_by_rate.get(key, Decimal("0")) + item.line_total

    for (rate, category_code), basis in tax_by_rate.items():
        trade_tax = ApplicableTradeTax()
        trade_tax.type_code = "VAT"
        trade_tax.category_code = category_code
        trade_tax.rate_applicable_percent = rate
        trade_tax.basis_amount = basis
        trade_tax.calculated_amount = (basis * rate / 100).quantize(Decimal("0.01"))
        document.trade.settlement.trade_tax.add(trade_tax)

    summation = document.trade.settlement.monetary_summation
    summation.line_total = invoice.total_net
    summation.charge_total = Decimal("0.00")
    summation.allowance_total = Decimal("0.00")
    summation.tax_basis_total = invoice.total_net
    summation.tax_total = (invoice.total_tax, "EUR")
    summation.grand_total = invoice.total_gross
    summation.due_amount = invoice.total_gross

    for item in invoice.items.all():
        document.trade.items.add(_build_line_item(item))

    return document


def build_cii_xml(invoice) -> bytes:
    document = build_cii_document(invoice)
    return document.serialize(schema="FACTUR-X_EN16931")
