"""
Сервис управления шаблонами.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from reversion import revisions

from apps.templates.models.template import Template, Page, Field, FieldVersion


class TemplateManager:
    """Центральный сервис управления шаблонами."""
    
    @staticmethod
    @transaction.atomic
    def create_template_with_structure(data: dict, user) -> Template:
        """Атомарное создание шаблона со всей структурой."""
        try:
            # Создаем шаблон
            template = Template.objects.create(
                name=data['name'],
                owner=user,
                format_id=data['format'],
                unit_id=data['unit'],
                html=data.get('html', ''),
                description=data.get('description', '')
            )
            
            # Создаем страницы
            for page_data in data.get('pages', []):
                page = Page.objects.create(
                    template=template,
                    index=page_data['index'],
                    html=page_data.get('html', ''),
                    width=page_data['width'],
                    height=page_data['height']
                )
                
                # Создаем поля страницы
                for field_data in page_data.get('fields', []):
                    Field.objects.create(
                        template=template,
                        page=page,
                        **field_data
                    )
            
            # Создаем глобальные поля
            for field_data in data.get('global_fields', []):
                Field.objects.create(
                    template=template,
                    page=None,
                    **field_data
                )
            
            # Создаем первую версию структуры полей
            TemplateManager._create_field_version(template, user)
            
            # Создаем начальную версию в reversion
            with revisions.create_revision():
                template.save()
                revisions.set_user(user)
                revisions.set_comment("Initial creation")
            
            return template
            
        except Exception as e:
            # Транзакция автоматически откатится
            raise ValidationError(f"Ошибка создания шаблона: {str(e)}")
    
    @staticmethod
    def _create_field_version(template: Template, user):
        """Создает версию структуры полей."""
        fields_data = []
        for field in template.fields.all():
            fields_data.append({
                'key': field.key,
                'type': field.type,
                'order': field.order,
                'page_index': field.page.index if field.page else None,
                'attributes': field.attributes,
                'is_required': field.is_required,
                'default_value': field.default_value,
                'placeholder': field.placeholder,
                'help_text': field.help_text
            })
        
        version_number = template.field_versions.count() + 1
        FieldVersion.objects.create(
            template=template,
            version_number=version_number,
            fields_snapshot=fields_data,
            created_by=user
        )
    
    @staticmethod
    @transaction.atomic
    def update_template_structure(template: Template, data: dict, user):
        """Обновление структуры шаблона с версионированием."""
        try:
            # Обновляем страницы
            existing_pages = {p.index: p for p in template.pages.all()}
            for page_data in data.get('pages', []):
                page = existing_pages.get(page_data['index'])
                if page:
                    # Обновляем существующую страницу
                    page.html = page_data.get('html', page.html)
                    page.width = page_data.get('width', page.width)
                    page.height = page_data.get('height', page.height)
                    page.save()
                else:
                    # Создаем новую страницу
                    page = Page.objects.create(
                        template=template,
                        index=page_data['index'],
                        html=page_data.get('html', ''),
                        width=page_data['width'],
                        height=page_data['height']
                    )
                
                # Обновляем поля страницы
                existing_fields = {f.key: f for f in page.fields.all()}
                for field_data in page_data.get('fields', []):
                    field = existing_fields.get(field_data['key'])
                    if field:
                        # Обновляем существующее поле
                        for key, value in field_data.items():
                            setattr(field, key, value)
                        field.save()
                    else:
                        # Создаем новое поле
                        Field.objects.create(
                            template=template,
                            page=page,
                            **field_data
                        )
            
            # Обновляем глобальные поля
            existing_global_fields = {f.key: f for f in template.fields.filter(page__isnull=True)}
            for field_data in data.get('global_fields', []):
                field = existing_global_fields.get(field_data['key'])
                if field:
                    # Обновляем существующее поле
                    for key, value in field_data.items():
                        setattr(field, key, value)
                    field.save()
                else:
                    # Создаем новое поле
                    Field.objects.create(
                        template=template,
                        page=None,
                        **field_data
                    )
            
            # Создаем новую версию структуры
            TemplateManager._create_field_version(template, user)
            
            # Создаем версию в reversion
            with revisions.create_revision():
                template.save()
                revisions.set_user(user)
                revisions.set_comment("Structure update")
            
            return template
            
        except Exception as e:
            # Транзакция автоматически откатится
            raise ValidationError(f"Ошибка обновления структуры: {str(e)}")
    
    @staticmethod
    def get_template_structure(template: Template, version: int = None):
        """Получение структуры шаблона."""
        if version:
            # Получаем конкретную версию
            field_version = template.field_versions.filter(version_number=version).first()
            if not field_version:
                raise ValidationError(f"Версия {version} не найдена")
            return field_version.fields_snapshot
        
        # Получаем текущую структуру
        fields_data = []
        for field in template.fields.all().order_by('page', 'order'):
            fields_data.append({
                'key': field.key,
                'type': field.type,
                'order': field.order,
                'page_index': field.page.index if field.page else None,
                'attributes': field.attributes,
                'is_required': field.is_required,
                'default_value': field.default_value,
                'placeholder': field.placeholder,
                'help_text': field.help_text
            })
        
        return fields_data 