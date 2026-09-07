from rest_framework.permissions import SAFE_METHODS, BasePermission

from .exceptions import GoBDLockAPIError


class InvoiceNotLocked(BasePermission):
    """Blocks PUT/PATCH/DELETE on a GoBD-locked (ISSUED) invoice with a
    clean 403 before the request reaches the model layer.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if getattr(obj, "is_locked", False):
            raise GoBDLockAPIError()
        return True
