# storage/templates/views.py
import uuid
import json
import logging
import os
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from .models import Template, GeneratedTemplate, Page, PageAsset, TemplatePermission
from .serializers import TemplateSerializer, GeneratedTemplateSerializer, PageSerializer, PageAssetSerializer, TemplatePermissionSerializer
from rest_framework.decorators import api_view, parser_classes, action, permission_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .permissions import IsOwnerOrHasPermission, IsAdminOrReadOnly

# Configure logger
logger = logging.getLogger('template_service')

class TemplateViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateSerializer
    permission_classes = [IsOwnerOrHasPermission]
    
    def get_queryset(self):
        """
        Фильтрация шаблонов на основе прав пользователя:
        1. Администраторы видят все шаблоны
        2. Обычные пользователи видят:
           - свои шаблоны
           - публичные шаблоны
           - шаблоны, к которым у них есть прямой доступ
           - шаблоны, к которым есть доступ у групп пользователя
        """
        user = self.request.user
        
        # Проверка на анонимного пользователя
        if user.is_anonymous:
            return Template.objects.filter(is_public=True)
        
        # Админы видят всё
        if user.is_admin():
            return Template.objects.all()
            
        # Получаем ID групп пользователя
        user_groups = user.custom_groups.all()
        
        # Фильтруем шаблоны
        return Template.objects.filter(
            Q(owner=user) |  # владелец
            Q(is_public=True) |  # публичные
            Q(permissions__user=user, permissions__permission_type='view') |  # с прямым доступом
            Q(permissions__group__in=user_groups, permissions__permission_type='view')  # с групповым доступом
        ).distinct()
    
    def perform_create(self, serializer):
        """При создании шаблона автоматически назначаем текущего пользователя владельцем"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Получение списка разрешений для шаблона"""
        template = self.get_object()
        permissions = TemplatePermission.objects.filter(template=template)
        serializer = TemplatePermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Добавление разрешения для шаблона"""
        template = self.get_object()
        
        # Проверяем, что пользователь - владелец или админ
        if request.user != template.owner and not request.user.is_admin():
            return Response({"detail": "You don't have permission to manage permissions"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        serializer = TemplatePermissionSerializer(data={**request.data, 'template': template.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_permission(self, request, pk=None, permission_id=None):
        """Удаление разрешения"""
        template = self.get_object()
        
        # Проверяем, что пользователь - владелец или админ
        if request.user != template.owner and not request.user.is_admin():
            return Response({"detail": "You don't have permission to manage permissions"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        try:
            permission = TemplatePermission.objects.get(id=permission_id, template=template)
            permission.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TemplatePermission.DoesNotExist:
            return Response({"detail": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        """Override to add detailed logging for template retrieval"""
        logger.info(f"--- TEMPLATE RETRIEVAL START ---")
        logger.info(f"Retrieving template with ID: {kwargs.get('pk')}")
        
        instance = self.get_object()
        
        # Log template details
        logger.info(f"Template found: {instance.name}, Version: {instance.version}, Type: {instance.type}")
        logger.info(f"Template has {instance.pages.count()} pages")
        
        # Log details of each page
        for i, page in enumerate(instance.pages.all()):
            logger.info(f"Page {i+1}: {page.name}, Size: {page.width}x{page.height} {page.units}")
            logger.info(f"Page {i+1} has {page.fields.count()} fields and {page.assets.count()} assets")
            
            # Log fields
            for j, field in enumerate(page.fields.all()):
                logger.debug(f"Field {j+1}: {field.name} (Required: {field.required})")
            
            # Log assets
            for j, asset in enumerate(page.assets.all()):
                logger.debug(f"Asset {j+1}: {asset.file.name} ({asset.file.url})")
                
                # Verify file exists
                file_path = asset.file.path
                if not os.path.exists(file_path):
                    logger.warning(f"Asset file does not exist: {file_path}")
                else:
                    file_size = os.path.getsize(file_path)
                    logger.debug(f"Asset file exists, size: {file_size} bytes")
        
        serializer = self.get_serializer(instance)
        logger.info(f"Template serialized successfully")
        logger.info(f"--- TEMPLATE RETRIEVAL END ---")
        
        return Response(serializer.data)

@api_view(['POST'])
@parser_classes([MultiPartParser, JSONParser])
def upload_template_file(request):
    """Generic endpoint for uploading any generated template file"""
    logger.info(f"--- TEMPLATE UPLOAD START ---")
    
    # Log request data for debugging
    logger.info(f"Upload template request received")
    logger.info(f"File present: {'file' in request.FILES}")
    logger.info(f"Template ID: {request.data.get('template_id')}")
    logger.info(f"Format: {request.data.get('format')}")
    
    # Check for file
    if 'file' not in request.FILES:
        logger.error("Error: File not provided in request")
        return Response({'error': 'File not provided'}, status=400)
    
    # Check for template ID and format
    template_id = request.data.get('template_id')
    format_type = request.data.get('format')
    
    if not template_id:
        logger.error("Error: Template ID is required")
        return Response({'error': 'Template ID is required'}, status=400)
    
    if not format_type:
        logger.error("Error: Format is required")
        return Response({'error': 'Format is required'}, status=400)
    
    # Get file info
    template_file = request.FILES['file']
    logger.info(f"Received file: {template_file.name}, Size: {template_file.size} bytes")
    
    # If file size is suspiciously small, log a warning
    if template_file.size < 100:
        logger.warning(f"WARNING: File size is very small ({template_file.size} bytes). This may not be a valid file.")
        
        # Check file content for debugging
        try:
            content_preview = template_file.read(50)
            template_file.seek(0)  # Reset file pointer after reading
            
            # Convert to hex string for better debugging
            hex_content = ' '.join([f'{b:02x}' for b in content_preview])
            logger.warning(f"File content preview (hex): {hex_content}")
            
            # Check for PDF signature
            if content_preview.startswith(b'%PDF-'):
                logger.info("File appears to be a PDF (has PDF signature)")
            else:
                logger.warning("File does not have PDF signature")
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
    
    # Find template
    try:
        template = Template.objects.get(id=template_id)
        logger.info(f"Template found: {template.name}, Version: {template.version}, Type: {template.type}")
    except Template.DoesNotExist:
        logger.error(f"Template with ID {template_id} not found")
        return Response({'error': 'Template not found'}, status=404)
    
    # Get form data
    form_data = request.data.get('form_data', '{}')
    logger.debug(f"Form data type: {type(form_data)}")
    
    # Generate a unique filename with proper extension
    file_name = f"document_{uuid.uuid4()}.{format_type}"
    logger.info(f"Generated filename: {file_name}")
    
    # Rename the file before saving
    template_file.name = file_name
    
    # Convert form data to JSON if it's a string
    if isinstance(form_data, str):
        try:
            form_data = json.loads(form_data)
            logger.info("Successfully parsed form_data JSON string")
        except json.JSONDecodeError as e:
            logger.warning(f"Error parsing form_data as JSON: {str(e)}")
            form_data = {}
    
    try:
        # Save the file to the model
        logger.info("Creating GeneratedTemplate record in database")
        generated_template = GeneratedTemplate.objects.create(
            template=template,
            file=template_file,
            format=format_type,
            data=form_data
        )
        
        # Verify file was saved correctly
        try:
            if os.path.exists(generated_template.file.path):
                file_size = os.path.getsize(generated_template.file.path)
                logger.info(f"File saved successfully at {generated_template.file.path}, size: {file_size} bytes")
                
                # Additional validation for very small files
                if file_size < 100:
                    logger.warning(f"Saved file is suspiciously small: {file_size} bytes")
            else:
                logger.error(f"File not found at expected path: {generated_template.file.path}")
        except Exception as e:
            logger.error(f"Error checking saved file: {str(e)}")
        
        # Return the URL for accessing the file
        response_data = {
            'id': generated_template.id,
            'url': generated_template.file.url,
            'format': generated_template.format,
            'created_at': generated_template.created_at
        }
        
        logger.info(f"Template uploaded successfully. URL: {response_data['url']}")
        logger.info(f"--- TEMPLATE UPLOAD END ---")
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Error saving template file: {str(e)}")
        return Response({'error': f'Error saving file: {str(e)}'}, status=500)

@api_view(['GET'])
def serve_template_file(request, file_id):
    """Serves the generated template file with appropriate headers"""
    logger.info(f"--- TEMPLATE FILE SERVING START ---")
    logger.info(f"Serving template file with ID: {file_id}")
    
    try:
        template_file = get_object_or_404(GeneratedTemplate, id=file_id)
        logger.info(f"Template file found: {template_file.file.name}, Format: {template_file.format}")
        
        # Check if file exists
        file_path = template_file.file.path
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            return Response({'error': 'File not found'}, status=404)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"File size: {file_size} bytes")
        
        # Set content type based on format
        content_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'svg': 'image/svg+xml'
        }
        content_type = content_types.get(template_file.format, 'application/octet-stream')
        logger.info(f"Using content type: {content_type}")
        
        response = FileResponse(template_file.file, content_type=content_type)
        
        # Set as attachment for download with original filename
        filename = template_file.file.name.split('/')[-1]
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"File served successfully")
        logger.info(f"--- TEMPLATE FILE SERVING END ---")
        
        return response
    
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return Response({'error': f'Error serving file: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([])  # Отключаем проверку аутентификации для этого эндпоинта
def health_check(request):
    """Health check endpoint"""
    logger.info("Health check request received")
    return JsonResponse({'status': 'ok', 'service': 'storage-service'})

@api_view(['GET', 'POST'])
def pages_list_create(request, template_id):
    if request.method == 'GET':
        pages = Page.objects.filter(template_id=template_id)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(template_id=template_id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def page_detail(request, template_id, page_id):
    page = get_object_or_404(Page, template_id=template_id, name=page_id)
    if request.method == 'GET':
        serializer = PageSerializer(page)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        page.delete()
        return Response(status=204)

@api_view(['POST'])
def upload_page_asset(request, template_id, page_id):
    page = get_object_or_404(Page, template_id=template_id, name=page_id)
    if 'file' not in request.FILES:
        return Response({'error': 'File not provided'}, status=400)
    asset = PageAsset.objects.create(page=page, file=request.FILES['file'])
    serializer = PageAssetSerializer(asset)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_page_asset(request, template_id, page_id, asset_id):
    asset = get_object_or_404(PageAsset, id=asset_id, page__template_id=template_id, page__name=page_id)
    asset.delete()
    return Response(status=204)