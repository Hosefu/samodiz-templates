from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class HealthCheckView(APIView):
    """
    Эндпоинт для проверки здоровья приложения
    """
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


urlpatterns = [
    path('', HealthCheckView.as_view(), name='health-check'),
] 