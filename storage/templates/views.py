from rest_framework import viewsets
from .models import Template, GeneratedTemplate
from .serializers import TemplateSerializer, GeneratedTemplateSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import json

class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, JSONParser])
def upload_template_file(request):
    """Generic endpoint for uploading any generated template file"""
    # Check for file
    if 'file' not in request.FILES:
        return Response({'error': 'File not provided'}, status=400)
    
    # Check for template ID and format
    template_id = request.data.get('template_id')
    format_type = request.data.get('format')
    
    if not template_id:
        return Response({'error': 'Template ID is required'}, status=400)
    
    if not format_type:
        return Response({'error': 'Format is required'}, status=400)
    
    # Find template
    try:
        template = Template.objects.get(id=template_id)
    except Template.DoesNotExist:
        return Response({'error': 'Template not found'}, status=404)
    
    # Get file and data
    template_file = request.FILES['file']
    form_data = request.data.get('form_data', '{}')
    
    # Convert form data to JSON if it's a string
    if isinstance(form_data, str):
        try:
            form_data = json.loads(form_data)
        except json.JSONDecodeError:
            form_data = {}
    
    # Save the file to the model
    generated_template = GeneratedTemplate.objects.create(
        template=template,
        file=template_file,
        format=format_type,
        data=form_data
    )
    
    # Return the URL for accessing the file
    return Response({
        'id': generated_template.id,
        'url': generated_template.file.url,
        'format': generated_template.format,
        'created_at': generated_template.created_at
    })

@api_view(['GET'])
def serve_template_file(request, file_id):
    """Serves the generated template file with appropriate headers"""
    template_file = get_object_or_404(GeneratedTemplate, id=file_id)
    
    # Set content type based on format
    content_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'svg': 'image/svg+xml'
    }
    content_type = content_types.get(template_file.format, 'application/octet-stream')
    
    response = FileResponse(template_file.file, content_type=content_type)
    
    # Set as attachment for download with original filename
    filename = template_file.file.name.split('/')[-1]
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response