from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerLookupSerializer, CustomerSerializer
from .services import csv_import


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(zip_code__icontains=query)
                | Q(city__icontains=query)
                | Q(vat_id__icontains=query)
            )
        return queryset

    @action(detail=False, methods=["get"])
    def search(self, request):
        queryset = self.get_queryset()[:20]
        serializer = CustomerLookupSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"detail": "Keine Datei hochgeladen."}, status=status.HTTP_400_BAD_REQUEST
            )

        dry_run = request.query_params.get("dry_run", "true").lower() != "false"
        column_overrides = request.data.get("column_overrides") or None

        try:
            preview = csv_import.build_preview(
                upload, upload.name, column_overrides=column_overrides
            )
        except Exception as exc:  # malformed file, unsupported format, etc.
            return Response(
                {"detail": f"Datei konnte nicht gelesen werden: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "mapped_columns": preview.mapped_columns,
            "unmapped_columns": preview.unmapped_columns,
            "valid_count": preview.valid_count,
            "total_count": len(preview.rows),
            "rows": [
                {"data": row.data, "errors": row.errors} for row in preview.rows
            ],
        }

        if dry_run:
            return Response(payload)

        created = csv_import.commit_import(preview)
        payload["created_count"] = created
        return Response(payload, status=status.HTTP_201_CREATED)
