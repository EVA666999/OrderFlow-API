# Текущий файл celery.py выглядит хорошо, но можно добавить несколько улучшений:

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Создаем экземпляр Celery
app = Celery('api')

# Загружаем настройки из объекта Django settings, имя переменных начинается с CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит и регистрирует задачи в приложениях Django
app.autodiscover_tasks()

# Добавим простую задачу для проверки работы Celery
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'Celery is working!'