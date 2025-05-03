"""
Сервис для работы с версиями шаблонов.
"""
import reversion
from reversion.models import Version
from django.contrib.contenttypes.models import ContentType
from apps.templates.models.template import Template


class TemplateVersionService:
    """Сервис для работы с версиями шаблонов."""
    
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
        return Version.objects.get_for_object(template)
    
    @staticmethod
    def get_template_version(template, version_id):
        """Получает конкретную версию шаблона."""
        try:
            return Version.objects.get_for_object(template)[version_id]
        except IndexError:
            return None
    
    @staticmethod
    def revert_to_version(template, version_id, user):
        """Откатывает шаблон к определенной версии."""
        version = TemplateVersionService.get_template_version(template, version_id)
        if version:
            with reversion.create_revision():
                version.revision.revert()
                reversion.set_user(user)
                reversion.set_comment(f"Revert to version {version_id}")
            return True
        return False


# Создаем экземпляр для удобного импорта
template_version_service = TemplateVersionService() 