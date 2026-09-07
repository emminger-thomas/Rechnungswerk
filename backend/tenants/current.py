"""Stand-in tenant resolution until request-level auth exists.

Every entry point that creates a new top-level Customer/Invoice calls
get_current_tenant() exactly once; everything downstream (numbering,
finalize, cancel) threads the tenant through from that object's own
.tenant FK instead of re-resolving it. That means the future switch to
real multi-tenancy only touches the call sites listed below, not the
numbering/finalize internals.
"""

from .models import Tenant


def get_current_tenant() -> Tenant:
    return Tenant.objects.get()
