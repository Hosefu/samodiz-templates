"""
Хелпер для работы с документами.
"""
import logging
from typing import Union, Optional
from datetime import timedelta
from io import BytesIO

from infrastructure.helpers.file_helper import FileHelper
from apps.generation.models import GeneratedDocument, RenderTask

logger = logging.getLogger(__name__)


class DocumentHelper(FileHelper):
    """Хелпер для работы с документами."""
    
    @classmethod
    def get_document_url(
        cls, 
        document: Union[GeneratedDocument, str],
        expires: timedelta = timedelta(hours=24)
    ) -> str:
        """
        Получает подписанный URL для документа.
        
        Args:
            document: Объект документа или строка с путем к файлу
            expires: Время действия подписанной ссылки
            
        Returns:
            str: Подписанный URL для доступа к документу
        """
        # Получаем путь к файлу
        if isinstance(document, GeneratedDocument):
            file_path = document.file
        elif isinstance(document, str):
            file_path = document
        else:
            cls.log_error(f"Unsupported document type: {type(document)}", level='warning')
            return ""
        
        # Генерируем подписанный URL
        return cls.get_presigned_url(file_path, 'documents', expires)
    
    @classmethod
    def find_document(cls, document_id: str) -> Optional[GeneratedDocument]:
        """
        Находит документ по ID.
        
        Args:
            document_id: ID документа
            
        Returns:
            Optional[GeneratedDocument]: Найденный документ или None
        """
        try:
            return GeneratedDocument.objects.get(id=document_id)
        except GeneratedDocument.DoesNotExist:
            cls.log_error(f"Document not found: {document_id}", level='warning')
            return None
        except Exception as e:
            cls.log_error(f"Error finding document {document_id}", e)
            return None
    
    @classmethod
    def create_document(
        cls, 
        task: RenderTask, 
        file_bytes: Union[bytes, BytesIO], 
        file_name: str, 
        content_type: str
    ) -> GeneratedDocument:
        """
        Создает документ в хранилище и записывает в БД.
        
        Args:
            task: Задача рендеринга
            file_bytes: Байты документа
            file_name: Имя файла
            content_type: MIME-тип документа
            
        Returns:
            GeneratedDocument: Созданный документ
        """
        try:
            # Приводим file_bytes к BytesIO если нужно
            if isinstance(file_bytes, bytes):
                file_obj = BytesIO(file_bytes)
            else:
                file_obj = file_bytes
            
            # Загружаем файл в хранилище
            object_name, url = cls.upload_file(
                file_obj=file_obj,
                folder=f"documents/{task.id}",
                filename=file_name,
                mime_type=content_type,
                bucket_type='documents'
            )
            
            # Определяем размер файла
            if hasattr(file_obj, 'getbuffer'):
                size = len(file_obj.getbuffer())
            elif hasattr(file_obj, 'getvalue'):
                size = len(file_obj.getvalue())
            else:
                # Если не можем определить размер
                size = 0
            
            # Создаем запись документа
            document = GeneratedDocument.objects.create(
                task=task,
                file=url,
                size_bytes=size,
                file_name=file_name,
                content_type=content_type
            )
            
            return document
            
        except Exception as e:
            cls.log_error(f"Failed to create document for task {task.id}", e)
            raise


# Создаем синглтон-инстанс для удобного импорта
document_helper = DocumentHelper() 