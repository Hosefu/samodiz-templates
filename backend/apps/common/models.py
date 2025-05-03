"""Базовые модели для всех приложений."""
import uuid
from django.db import models
from django.utils import timezone


class UUIDModel(models.Model):
    """Базовая модель с UUID вместо auto-increment ID."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Модель с отслеживанием времени создания и обновления."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeletableQuerySet(models.QuerySet):
    """QuerySet с поддержкой мягкого удаления."""

    def delete(self):
        """Мягкое удаление - помечает объекты как удаленные."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Физическое удаление из базы данных."""
        return super().delete()

    def active(self):
        """Только активные (не удаленные) записи."""
        return self.filter(is_deleted=False)


class SoftDeletableManager(models.Manager):
    """Менеджер с поддержкой мягкого удаления."""

    def get_queryset(self):
        """По умолчанию возвращает только активные записи."""
        return SoftDeletableQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """Возвращает все записи, включая мягко удаленные."""
        return SoftDeletableQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Возвращает только удаленные записи."""
        return SoftDeletableQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeletableModel(UUIDModel):
    """Базовая модель с поддержкой мягкого удаления."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeletableManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление объекта."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Физическое удаление объекта из базы данных."""
        return super().delete(using=using, keep_parents=keep_parents)


class BaseModel(SoftDeletableModel, TimeStampedModel):
    """
    Объединяет UUID, мягкое удаление и отметки времени.
    
    Рекомендуется использовать эту модель как базовую для всех моделей проекта.
    """

    class Meta:
        abstract = True