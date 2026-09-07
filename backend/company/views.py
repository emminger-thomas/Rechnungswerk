from rest_framework.generics import RetrieveUpdateAPIView

from .models import CompanySettings
from .serializers import CompanySettingsSerializer


class CompanySettingsView(RetrieveUpdateAPIView):
    serializer_class = CompanySettingsSerializer

    def get_object(self):
        return CompanySettings.get_solo()
