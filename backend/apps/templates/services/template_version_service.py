"""
Сервис для работы с версиями шаблонов.
"""
import reversion
from reversion.models import Version
from django.contrib.contenttypes.models import ContentType
from apps.templates.models.template import Template
from django.utils import timezone


class TemplateVersionService:
    """Сервис для работы с версиями шаблонов через django-reversion."""
    
    @staticmethod
    def create_version(template, user, comment=""):
        """Создает новую версию шаблона."""
        with reversion.create_revision():
            template.save()
            reversion.set_user(user)
            reversion.set_comment(comment)
    
    @staticmethod
    def get_template_versions(template):
        """Получает все версии шаблона."""
        return Version.objects.get_for_object(template).order_by('-revision__date_created')
    
    @staticmethod
    def get_template_version(template, version_id):
        """Получает конкретную версию шаблона."""
        try:
            versions = Version.objects.get_for_object(template)
            return versions.get(id=version_id)
        except Version.DoesNotExist:
            return None
    
    @staticmethod
    def get_version_data(version):
        """Получает данные версии в структурированном виде."""
        if not version:
            return None
        
        return {
            'id': version.id,
            'date_created': version.revision.date_created,
            'user': {
                'id': str(version.revision.user.id) if version.revision.user else None,
                'email': version.revision.user.email if version.revision.user else None,
                'full_name': version.revision.user.get_full_name() if version.revision.user else None,
            },
            'comment': version.revision.comment,
            'html': version.field_dict.get('html', '')
        }
    
    @staticmethod
    def revert_to_version(template, version_id, user):
        """Откатывает шаблон к указанной версии."""
        version = TemplateVersionService.get_template_version(template, version_id)
        if version:
            with reversion.create_revision():
                version.revision.revert()
                reversion.set_user(user)
                reversion.set_comment(f"Revert to version from {version.revision.date_created}")
                
                # Обновляем шаблон для запуска сигналов
                template.refresh_from_db()
                template.save()
                
                return True
        return False


# Создаем экземпляр для удобного импорта
template_version_service = TemplateVersionService() 