from rest_framework.exceptions import APIException


class GoBDLockError(Exception):
    """Raised when code attempts to mutate or delete a GoBD-locked invoice."""


class GoBDLockAPIError(APIException):
    status_code = 403
    default_detail = (
        "GoBD-Verletzung: Finalisierte Rechnungen dürfen nicht geändert oder "
        "gelöscht werden. Bitte erstellen Sie eine Stornorechnung."
    )
    default_code = "gobd_locked"


class InvalidInvoiceError(Exception):
    """Raised when an invoice fails EN 16931 / § 14 UStG pre-finalize validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))
