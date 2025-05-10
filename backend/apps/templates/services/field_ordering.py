"""
Сервис управления порядком полей.
"""
from typing import Dict, Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.templates.models.template import Field


class FieldOrderingService:
    """Сервис управления порядком полей."""
    
    @staticmethod
    @transaction.atomic
    def reorder_fields(template_id: str, page_id: Optional[str], field_orders: Dict[str, int]):
        """
        Обновляет порядок полей.
        
        Args:
            template_id: ID шаблона
            page_id: ID страницы (None для глобальных полей)
            field_orders: {field_id: new_order, ...}
        """
        # Получаем все поля для данного контекста
        fields_query = Field.objects.filter(template_id=template_id)
        
        if page_id:
            fields_query = fields_query.filter(page_id=page_id)
        else:
            fields_query = fields_query.filter(page__isnull=True)
        
        # Проверяем, что все поля существуют
        existing_fields = set(fields_query.values_list('id', flat=True))
        requested_fields = set(field_orders.keys())
        
        if not requested_fields.issubset(existing_fields):
            raise ValidationError("Некоторые поля не существуют или не принадлежат указанному контексту")
        
        # Проверяем уникальность порядков
        if len(set(field_orders.values())) != len(field_orders):
            raise ValidationError("Порядки полей должны быть уникальными")
        
        # Обновляем порядок
        for field_id, new_order in field_orders.items():
            Field.objects.filter(id=field_id).update(order=new_order)
        
        # Проверяем и нормализуем порядок (на случай пропусков)
        ordered_fields = fields_query.order_by('order')
        for i, field in enumerate(ordered_fields, 1):
            if field.order != i:
                field.order = i
                field.save(update_fields=['order'])
    
    @staticmethod
    def get_field_order(template_id: str, page_id: Optional[str] = None) -> Dict[str, int]:
        """
        Получает текущий порядок полей.
        
        Args:
            template_id: ID шаблона
            page_id: ID страницы (None для глобальных полей)
            
        Returns:
            Dict[str, int]: {field_id: order, ...}
        """
        fields_query = Field.objects.filter(template_id=template_id)
        
        if page_id:
            fields_query = fields_query.filter(page_id=page_id)
        else:
            fields_query = fields_query.filter(page__isnull=True)
        
        return dict(fields_query.values_list('id', 'order'))
    
    @staticmethod
    def move_field(template_id: str, field_id: str, new_position: int, page_id: Optional[str] = None):
        """
        Перемещает поле на новую позицию.
        
        Args:
            template_id: ID шаблона
            field_id: ID поля
            new_position: Новая позиция (1-based)
            page_id: ID страницы (None для глобальных полей)
        """
        fields_query = Field.objects.filter(template_id=template_id)
        
        if page_id:
            fields_query = fields_query.filter(page_id=page_id)
        else:
            fields_query = fields_query.filter(page__isnull=True)
        
        # Получаем текущий порядок
        current_order = dict(fields_query.values_list('id', 'order'))
        
        if field_id not in current_order:
            raise ValidationError("Поле не найдено или не принадлежит указанному контексту")
        
        # Проверяем валидность новой позиции
        if new_position < 1 or new_position > len(current_order):
            raise ValidationError(f"Новая позиция должна быть от 1 до {len(current_order)}")
        
        # Получаем текущую позицию поля
        current_position = current_order[field_id]
        
        # Если позиция не изменилась, ничего не делаем
        if current_position == new_position:
            return
        
        # Обновляем порядок
        with transaction.atomic():
            if current_position < new_position:
                # Сдвигаем поля вверх
                fields_query.filter(
                    order__gt=current_position,
                    order__lte=new_position
                ).update(order=models.F('order') - 1)
            else:
                # Сдвигаем поля вниз
                fields_query.filter(
                    order__gte=new_position,
                    order__lt=current_position
                ).update(order=models.F('order') + 1)
            
            # Устанавливаем новый порядок для поля
            Field.objects.filter(id=field_id).update(order=new_position) 