# api/celery.py
import os
from celery import Celery

# Указываем Django настройки для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Создаем приложение Celery
app = Celery('api')

# Конфигурация из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит все задачи в приложении
app.autodiscover_tasks()

# Экспортируем приложение для использования в других частях проекта
__all__ = ('app',)
