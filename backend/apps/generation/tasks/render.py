"""
Задачи Celery для рендеринга документов.
"""
from celery import shared_task
from .base import RenderTaskBase


@shared_task(bind=True, base=RenderTaskBase, time_limit=180, max_retries=3, autoretry_for=(RuntimeError,))
def render_pdf(self, task_id, html, options, renderer_url=None):
    """Генерирует PDF документ."""
    return self._render_document(task_id, html, options, 'pdf', renderer_url)


@shared_task(bind=True, base=RenderTaskBase, time_limit=180, max_retries=3, autoretry_for=(RuntimeError,))
def render_png(self, task_id, html, options, renderer_url=None):
    """Генерирует PNG документ."""
    return self._render_document(task_id, html, options, 'png', renderer_url)


@shared_task(bind=True, base=RenderTaskBase, time_limit=180, max_retries=3, autoretry_for=(RuntimeError,))
def render_svg(self, task_id, html, options, renderer_url=None):
    """Генерирует SVG документ."""
    return self._render_document(task_id, html, options, 'svg', renderer_url)