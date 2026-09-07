from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from company.views import CompanySettingsView
from customers.views import CustomerViewSet
from invoices.views import InvoiceViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="customer")
router.register("invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/company-settings", CompanySettingsView.as_view(), name="company-settings"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
