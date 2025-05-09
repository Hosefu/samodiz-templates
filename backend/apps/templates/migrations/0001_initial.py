# Generated by Django 4.2.8 on 2025-05-10 16:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Имя файла', max_length=255)),
                ('file', models.CharField(help_text='URL в Ceph', max_length=1000)),
                ('size_bytes', models.BigIntegerField(help_text='Размер в байтах')),
                ('mime_type', models.CharField(help_text='MIME-тип файла', max_length=100)),
            ],
            options={
                'verbose_name': 'Ассет',
                'verbose_name_plural': 'Ассеты',
                'ordering': ['template', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('key', models.CharField(help_text='Технический ключ', max_length=100)),
                ('label', models.CharField(help_text='Отображаемое название', max_length=255)),
                ('type', models.CharField(choices=[('string', 'Строка'), ('choices', 'Выбор из списка')], default='string', help_text='Тип поля', max_length=20)),
                ('order', models.PositiveIntegerField(help_text='Порядок отображения поля')),
                ('is_required', models.BooleanField(default=False)),
                ('default_value', models.TextField(blank=True, null=True)),
                ('placeholder', models.CharField(blank=True, max_length=255)),
                ('help_text', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['page', 'order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='FieldChoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('label', models.CharField(help_text='Отображаемое название', max_length=255)),
                ('value', models.CharField(help_text='Значение для шаблона', max_length=255)),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения')),
            ],
            options={
                'ordering': ['field', 'order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='FieldVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('version_number', models.PositiveIntegerField()),
                ('fields_snapshot', models.JSONField(help_text='Снимок структуры полей')),
            ],
            options={
                'ordering': ['-version_number'],
            },
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Название формата (`pdf`, `png`)', max_length=50, unique=True)),
                ('description', models.TextField(blank=True, help_text='Описание формата')),
                ('render_url', models.URLField(help_text='Внутренний URL генератора')),
            ],
            options={
                'verbose_name': 'Формат',
                'verbose_name_plural': 'Форматы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FormatSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Название настройки', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Описание')),
                ('key', models.CharField(help_text='Ключ', max_length=50)),
                ('is_required', models.BooleanField(default=False, help_text='Обязательна?')),
                ('default_value', models.CharField(blank=True, help_text='Значение по умолчанию', max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Настройка формата',
                'verbose_name_plural': 'Настройки форматов',
                'ordering': ['format', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('index', models.PositiveIntegerField(help_text='Порядковый номер (1…)')),
                ('html', models.TextField(help_text='HTML-код страницы')),
                ('width', models.DecimalField(decimal_places=2, help_text='Ширина страницы', max_digits=10)),
                ('height', models.DecimalField(decimal_places=2, help_text='Высота страницы', max_digits=10)),
            ],
            options={
                'verbose_name': 'Страница',
                'verbose_name_plural': 'Страницы',
                'ordering': ['template', 'index'],
            },
        ),
        migrations.CreateModel(
            name='PageSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('value', models.CharField(help_text='Значение для этой страницы', max_length=255)),
            ],
            options={
                'verbose_name': 'Настройка страницы',
                'verbose_name_plural': 'Настройки страниц',
                'ordering': ['page', 'format_setting'],
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Название шаблона', max_length=255)),
                ('is_public', models.BooleanField(default=False, help_text='Опубликовано?')),
                ('description', models.TextField(blank=True, help_text='Описание шаблона')),
                ('html', models.TextField(blank=True, help_text='Base HTML шаблона')),
            ],
            options={
                'verbose_name': 'Шаблон',
                'verbose_name_plural': 'Шаблоны',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TemplatePermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(choices=[('viewer', 'Просмотр'), ('editor', 'Редактирование'), ('owner', 'Владелец')], default='viewer', help_text='Уровень доступа', max_length=10)),
                ('token', models.UUIDField(blank=True, default=uuid.uuid4, help_text='Публичный токен (если grantee=NULL)', null=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Срок действия ссылки', null=True)),
            ],
            options={
                'verbose_name': 'Разрешение на шаблон',
                'verbose_name_plural': 'Разрешения на шаблоны',
                'ordering': ['template', 'role'],
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('key', models.CharField(help_text='Значение единицы измерения (например `mm`, `px`)', max_length=10, unique=True)),
                ('name', models.CharField(help_text='Подпись в UI (`мм`)', max_length=50)),
            ],
            options={
                'verbose_name': 'Единица измерения',
                'verbose_name_plural': 'Единицы измерения',
                'ordering': ['key'],
            },
        ),
    ]
