from rest_framework import viewsets
from .models import Template, GeneratedPdf
from .serializers import TemplateSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
import json

class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, JSONParser])
def upload_pdf(request):
    # Проверка наличия файла
    if 'file' not in request.FILES:
        return Response({'error': 'Файл не предоставлен'}, status=400)
    
    # Проверка наличия ID шаблона
    template_id = request.data.get('template_id')
    if not template_id:
        return Response({'error': 'Требуется ID шаблона'}, status=400)
    
    # Поиск шаблона
    try:
        template = Template.objects.get(id=template_id)
    except Template.DoesNotExist:
        return Response({'error': 'Шаблон не найден'}, status=404)
    
    # Получение данных
    pdf_file = request.FILES['file']
    form_data = request.data.get('form_data', '{}')
    
    # Преобразование формы в JSON, если она строка
    if isinstance(form_data, str):
        try:
            form_data = json.loads(form_data)
        except json.JSONDecodeError:
            form_data = {}
    
    # Сохранение PDF в модель
    generated_pdf = GeneratedPdf.objects.create(
        template=template,
        file=pdf_file,
        data=form_data
    )
    
    # Возвращаем URL для доступа к файлу
    return Response({
        'id': generated_pdf.id,
        'url': generated_pdf.file.url,
        'created_at': generated_pdf.created_at
    })