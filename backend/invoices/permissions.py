from rest_framework.permissions import BasePermission

from .exceptions import GoBDLockAPIError


DIRECT_MUTATION_METHODS = ("PUT", "PATCH", "DELETE")


class InvoiceNotLocked(BasePermission):
    """Blocks PUT/PATCH/DELETE on a GoBD-locked (ISSUED) invoice with a
    clean 403 before the request reaches the model layer.

    Custom POST actions (finalize/cancel/mark-paid/remind) are exempt: they
    manage the GoBD lock themselves via allow_locked_write=True and are the
    sanctioned way to act on a locked invoice (a storno, a payment-status
    update, a reminder) without mutating its locked content directly.
    """

    def has_object_permission(self, request, view, obj):
        if request.method not in DIRECT_MUTATION_METHODS:
            return True
        if getattr(obj, "is_locked", False):
            raise GoBDLockAPIError()
        return True
