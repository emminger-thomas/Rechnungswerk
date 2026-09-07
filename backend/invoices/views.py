from datetime import date

from django.http import FileResponse, HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .exceptions import InvalidInvoiceError
from . import audit
from .models import Invoice
from .permissions import InvoiceNotLocked
from .serializers import InvoiceSerializer
from .services.dashboard import create_reminder, mark_paid as mark_paid_service, sync_overdue_statuses
from .services.datev_export import build_datev_export
from .services.finalize import cancel_invoice, finalize_invoice


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("customer").prefetch_related("items")
    serializer_class = InvoiceSerializer
    permission_classes = [InvoiceNotLocked]

    def get_queryset(self):
        sync_overdue_statuses()
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        invoice = serializer.save()
        audit.log_event(
            invoice, audit.AuditLogEntry.ACTION_CREATED, source_ip=self.request.META.get("REMOTE_ADDR")
        )

    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        invoice = self.get_object()
        try:
            invoice = finalize_invoice(
                invoice, source_ip=request.META.get("REMOTE_ADDR")
            )
        except InvalidInvoiceError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        invoice = self.get_object()
        try:
            storno = cancel_invoice(invoice, source_ip=request.META.get("REMOTE_ADDR"))
        except InvalidInvoiceError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceSerializer(storno).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        invoice = self.get_object()
        if not invoice.pdf_file:
            return Response(
                {"detail": "PDF wurde noch nicht erzeugt (Rechnung nicht finalisiert)."},
                status=status.HTTP_404_NOT_FOUND,
            )
        audit.log_event(
            invoice,
            audit.AuditLogEntry.ACTION_EXPORTED_PDF,
            source_ip=request.META.get("REMOTE_ADDR"),
        )
        return FileResponse(
            invoice.pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{invoice.invoice_number}.pdf",
        )

    @action(detail=True, methods=["get"])
    def xml(self, request, pk=None):
        invoice = self.get_object()
        if not invoice.xml_content:
            return Response(
                {"detail": "XML wurde noch nicht erzeugt (Rechnung nicht finalisiert)."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return HttpResponse(invoice.xml_content, content_type="application/xml")

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        raw_date = request.data.get("paid_date")
        paid_date = date.fromisoformat(raw_date) if raw_date else date.today()
        try:
            invoice = mark_paid_service(
                invoice, paid_date, source_ip=request.META.get("REMOTE_ADDR")
            )
        except InvalidInvoiceError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=["post"])
    def remind(self, request, pk=None):
        invoice = self.get_object()
        try:
            create_reminder(invoice, source_ip=request.META.get("REMOTE_ADDR"))
        except InvalidInvoiceError as exc:
            return Response({"errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceSerializer(invoice).data)


@api_view(["GET"])
def datev_export(request):
    try:
        year = int(request.query_params["year"])
        month = int(request.query_params["month"])
    except (KeyError, ValueError):
        return Response(
            {"detail": "Parameter 'year' und 'month' sind erforderlich (z.B. ?year=2026&month=9)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    zip_buffer, filename = build_datev_export(year, month)
    return FileResponse(
        zip_buffer, content_type="application/zip", as_attachment=True, filename=filename
    )
