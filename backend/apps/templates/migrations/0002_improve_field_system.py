"""
Миграция для улучшения системы полей.
"""
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings


def migrate_field_types(apps, schema_editor):
    """Миграция данных из старой системы в новую."""
    Field = apps.get_model('templates', 'Field')
    
    for field in Field.objects.all():
        if field.is_choices:
            field.type = 'choice'
            field.attributes = {'choices': field.choices or []}
        else:
            field.type = 'text'  # Default type
        field.save()


class Migration(migrations.Migration):
    dependencies = [
        ('templates', '0001_initial'),
    ]
    
    operations = [
        # Добавляем новые поля
        migrations.AddField(
            model_name='field',
            name='type',
            field=models.CharField(
                choices=[
                    ('text', 'Текст'),
                    ('number', 'Число'),
                    ('email', 'Email'),
                    ('phone', 'Телефон'),
                    ('date', 'Дата'),
                    ('choice', 'Выбор из списка'),
                    ('multi_choice', 'Множественный выбор'),
                    ('file', 'Файл'),
                    ('url', 'URL'),
                    ('textarea', 'Многострочный текст'),
                ],
                default='text',
                help_text='Тип поля',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Порядок отображения поля'
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='placeholder',
            field=models.CharField(
                blank=True,
                help_text='Подсказка в поле ввода',
                max_length=255
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='help_text',
            field=models.TextField(
                blank=True,
                help_text='Текст подсказки'
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='attributes',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Дополнительные атрибуты: choices, min/max, pattern, etc.'
            ),
        ),
        
        # Изменяем тип поля default_value
        migrations.AlterField(
            model_name='field',
            name='default_value',
            field=models.TextField(
                blank=True,
                help_text='Значение по умолчанию',
                null=True
            ),
        ),
        
        # Добавляем модель версий полей
        migrations.CreateModel(
            name='FieldVersion',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('created_at', models.DateTimeField(
                    default=django.utils.timezone.now,
                    editable=False
                )),
                ('updated_at', models.DateTimeField(
                    auto_now=True
                )),
                ('version_number', models.PositiveIntegerField()),
                ('fields_snapshot', models.JSONField(
                    help_text='Снимок структуры полей'
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL
                )),
                ('template', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='field_versions',
                    to='templates.template'
                )),
            ],
            options={
                'ordering': ['-version_number'],
                'unique_together': {('template', 'version_number')},
            },
        ),
        
        # Мигрируем данные
        migrations.RunPython(migrate_field_types),
        
        # Удаляем старые поля
        migrations.RemoveField(
            model_name='field',
            name='is_choices',
        ),
        migrations.RemoveField(
            model_name='field',
            name='choices',
        ),
        
        # Обновляем уникальные ограничения
        migrations.AlterUniqueTogether(
            name='field',
            unique_together={('template', 'page', 'key'), ('template', 'page', 'order')},
        ),
        
        # Обновляем сортировку
        migrations.AlterModelOptions(
            name='field',
            options={'ordering': ['page', 'order', 'created_at']},
        ),
    ] 