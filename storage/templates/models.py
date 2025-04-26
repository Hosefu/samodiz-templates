# storage/templates/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Расширенная модель пользователя"""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        USER = 'user', _('Regular User')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    
    # Дополнительные поля
    additional_info = models.JSONField(blank=True, null=True)
    preferences = models.JSONField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

class UserGroup(models.Model):
    """Группы пользователей для распределения прав"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        User, 
        related_name='custom_groups', 
        blank=True
    )
    
    def __str__(self):
        return self.name

class TemplatePermission(models.Model):
    """Разрешения доступа к шаблонам"""
    
    class PermissionType(models.TextChoices):
        VIEW = 'view', _('View')
        EDIT = 'edit', _('Edit')
        GENERATE = 'generate', _('Generate')
    
    template = models.ForeignKey('Template', on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_permissions', null=True, blank=True)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='template_permissions', null=True, blank=True)
    permission_type = models.CharField(max_length=10, choices=PermissionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(group__isnull=False),
                name='either_user_or_group_not_null'
            ),
            models.UniqueConstraint(
                fields=['template', 'user', 'permission_type'],
                name='unique_user_template_permission',
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['template', 'group', 'permission_type'],
                name='unique_group_template_permission',
                condition=models.Q(group__isnull=False)
            )
        ]

class Template(models.Model):
    TEMPLATE_TYPES = [
        ('pdf', 'PDF Document'),
        ('png', 'PNG Image'),
        ('svg', 'SVG Vector Image'),
    ]
    
    name = models.TextField()  # техническое имя
    label = models.CharField(max_length=255, default='')  # отображаемое название
    version = models.TextField()
    type = models.CharField(max_length=10, choices=TEMPLATE_TYPES, default='pdf')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_templates', null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.label or self.name

    def has_permission(self, user, permission_type):
        """Проверяет наличие прав у пользователя"""
        if user.is_admin():
            return True
            
        if self.owner == user:
            return True
            
        if self.is_public and permission_type == 'view':
            return True
            
        # Проверяем прямые права пользователя
        if self.permissions.filter(
            user=user,
            permission_type=permission_type
        ).exists():
            return True
            
        # Проверяем групповые права
        user_groups = user.custom_groups.all()
        return self.permissions.filter(
            group__in=user_groups,
            permission_type=permission_type
        ).exists()

class Page(models.Model):
    UNIT_CHOICES = [
        ('mm', 'Millimeters'),
        ('px', 'Pixels'),
    ]
    
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='pages')
    name = models.TextField()
    html = models.TextField()
    width = models.IntegerField()
    height = models.IntegerField()
    units = models.CharField(max_length=5, choices=UNIT_CHOICES, default='mm')
    bleeds = models.IntegerField(null=True, blank=True)  # Optional for PDF

class PageAsset(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='page_assets/')

class Field(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='fields')
    name = models.TextField()
    label = models.TextField()
    required = models.BooleanField(default=False)

class PageSettings(models.Model):
    """Format-specific settings for pages"""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=50)  # e.g. 'dpi', 'transparency'
    value = models.TextField()
    
    class Meta:
        unique_together = ('page', 'key')

class GeneratedTemplate(models.Model):
    """Renamed from GeneratedPdf to support multiple formats"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='generated_templates')
    file = models.FileField(upload_to='generated_templates/')
    format = models.CharField(max_length=10)  # 'pdf', 'png', 'svg'
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(blank=True, null=True)  # Data used to generate the template
    
    def __str__(self):
        return f"{self.format.upper()} для {self.template.name} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"