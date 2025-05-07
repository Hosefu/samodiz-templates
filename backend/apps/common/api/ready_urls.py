from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class ReadyCheckView(APIView):
    """
    Эндпоинт для проверки готовности приложения
    """
    permission_classes = []

    def get(self, request):
        return Response({"status": "ready"}, status=status.HTTP_200_OK)


urlpatterns = [
    path('', ReadyCheckView.as_view(), name='ready-check'),
] 