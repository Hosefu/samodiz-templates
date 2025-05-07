from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class MetricsView(APIView):
    """
    Эндпоинт для получения метрик приложения
    """
    permission_classes = []

    def get(self, request):
        return Response({
            "status": "ok",
            "metrics": {
                "version": "1.0.0",
                "uptime": "0s"  # Здесь можно добавить реальное время работы
            }
        }, status=status.HTTP_200_OK)


urlpatterns = [
    path('', MetricsView.as_view(), name='metrics'),
] 