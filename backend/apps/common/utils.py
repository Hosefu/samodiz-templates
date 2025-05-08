from rest_framework.views import exception_handler as drf_exception_handler

def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF.
    Просто вызывает стандартный обработчик.
    """
    return drf_exception_handler(exc, context) 