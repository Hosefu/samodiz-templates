"""
Модели пользователей и групп системы.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone
from apps.common.models import BaseModel
import uuid


class UserManager(BaseUserManager):
    """Менеджер пользователей с поддержкой email вместо username."""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет пользователя с указанным email и паролем."""
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Пользовательская модель с email в качестве основного идентификатора.
    
    Также включает поля для хранения информации о пользователе и его настройках.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Прочие поля
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Менеджер объектов
    objects = UserManager()
    
    # Поля для входа и отображения
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username or self.email
    
    def get_short_name(self):
        """Возвращает короткое имя пользователя."""
        return self.first_name if self.first_name else self.username or self.email


# Расширяем модель Group для поддержки мягкого удаления и UUID
class ExtendedGroup(models.Model):
    """
    Расширение стандартной модели Group с дополнительными возможностями.
    
    Использует связь один-к-одному вместо наследования для избежания конфликтов полей.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='extended'
    )
    description = models.TextField(blank=True)
    
    # Добавляем поля из BaseModel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['group__name']
    
    def __str__(self):
        return self.group.name
    
    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление объекта."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Физическое удаление объекта из базы данных."""
        return super().delete(using=using, keep_parents=keep_parents)