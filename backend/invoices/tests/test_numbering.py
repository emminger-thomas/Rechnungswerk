import threading

from django.test import TransactionTestCase

from invoices.numbering import get_next_number
from invoices.services.finalize import finalize_invoice
from tenants.current import get_current_tenant

from .factories import make_company_settings, make_invoice_with_item


class NumberingSequenceTests(TransactionTestCase):
    def setUp(self):
        make_company_settings()
        self.tenant = get_current_tenant()

    def test_sequential_finalize_has_no_gaps(self):
        numbers = []
        for _ in range(5):
            invoice = make_invoice_with_item()
            finalized = finalize_invoice(invoice)
            numbers.append(finalized.invoice_number)

        suffixes = sorted(int(n.rsplit("-", 1)[1]) for n in numbers)
        self.assertEqual(suffixes, list(range(suffixes[0], suffixes[0] + 5)))

    def test_concurrent_numbering_has_no_duplicates(self):
        results: list[str] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def worker():
            try:
                number = get_next_number(self.tenant, "CONC", year=2099)
                with lock:
                    results.append(number)
            except Exception as exc:  # pragma: no cover - failure path
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), len(set(results)), "duplicate numbers issued")
        suffixes = sorted(int(n.rsplit("-", 1)[1]) for n in results)
        self.assertEqual(suffixes, list(range(1, 21)), "gaps or duplicates in sequence")
