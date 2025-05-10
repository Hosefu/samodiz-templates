class TemplateDataValidator:
    @staticmethod
    def validate_template_data(template, data):
        """
        Валидирует данные на соответствие полям шаблона.
        
        Args:
            template: Объект шаблона
            data: Данные для валидации
            
        Returns:
            tuple: (is_valid, errors) - флаг валидности и список ошибок
        """
        errors = []
        
        # Получаем все поля шаблона
        fields = template.fields.all()
        
        # Проверяем наличие всех обязательных полей
        for field in fields:
            if field.is_required and (field.key not in data or not data[field.key]):
                errors.append({
                    'field': field.key,
                    'label': field.label,
                    'error': 'Обязательное поле отсутствует'
                })
        
        # Проверяем валидность выбора для полей с выбором
        for field in fields:
            if field.type == 'choices' and field.choices.exists() and field.key in data:
                valid_values = [choice.value for choice in field.choices.all()]
                if data[field.key] not in valid_values:
                    errors.append({
                        'field': field.key,
                        'label': field.label,
                        'error': f'Значение должно быть одним из: {", ".join(valid_values)}'
                    })
        
        return len(errors) == 0, errors 