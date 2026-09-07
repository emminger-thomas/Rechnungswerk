import datetime

from django.test import TestCase
from lxml import etree

from invoices.numbering import get_next_invoice_number
from invoices.services.zugferd import build_cii_xml

from .factories import make_company_settings, make_invoice_with_item

NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
}


class ZugferdXmlTests(TestCase):
    def setUp(self):
        make_company_settings()

    def _finalized_xml(self, invoice):
        invoice.invoice_number = get_next_invoice_number()
        invoice.issue_date = datetime.date.today()
        invoice.recalculate_totals()
        return build_cii_xml(invoice)

    def test_xml_is_xsd_valid_and_well_formed(self):
        invoice = make_invoice_with_item(quantity=4, unit_price=68)
        xml_bytes = self._finalized_xml(invoice)  # raises if XSD-invalid
        etree.fromstring(xml_bytes)  # raises if not well-formed

    def test_bt_values_present_at_expected_xpaths(self):
        invoice = make_invoice_with_item(quantity=2, unit_price=100)
        xml_bytes = self._finalized_xml(invoice)
        root = etree.fromstring(xml_bytes)

        invoice_id = root.find(".//rsm:ExchangedDocument/ram:ID", NS)
        self.assertEqual(invoice_id.text, invoice.invoice_number)

        type_code = root.find(".//rsm:ExchangedDocument/ram:TypeCode", NS)
        self.assertEqual(type_code.text, "380")

        seller_name = root.find(
            ".//ram:ApplicableHeaderTradeAgreement/ram:SellerTradeParty/ram:Name", NS
        )
        self.assertEqual(seller_name.text, "Test GmbH")

        buyer_name = root.find(
            ".//ram:ApplicableHeaderTradeAgreement/ram:BuyerTradeParty/ram:Name", NS
        )
        self.assertEqual(buyer_name.text, invoice.customer.name)

        grand_total = root.find(
            ".//ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:GrandTotalAmount",
            NS,
        )
        self.assertEqual(grand_total.text, str(invoice.total_gross))

        due_amount = root.find(
            ".//ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:DuePayableAmount",
            NS,
        )
        self.assertEqual(due_amount.text, str(invoice.total_gross))

    def test_small_business_scenario_emits_legal_notice_and_zero_rate(self):
        invoice = make_invoice_with_item(tax_scenario="SMALL_BUSINESS", quantity=1, unit_price=50)
        xml_bytes = self._finalized_xml(invoice)
        root = etree.fromstring(xml_bytes)

        note = root.find(".//rsm:ExchangedDocument/ram:IncludedNote/ram:Content", NS)
        self.assertIsNotNone(note)
        self.assertIn("§ 19 UStG", note.text)

        category = root.find(
            ".//ram:IncludedSupplyChainTradeLineItem/ram:SpecifiedLineTradeSettlement"
            "/ram:ApplicableTradeTax/ram:CategoryCode",
            NS,
        )
        self.assertEqual(category.text, "E")
