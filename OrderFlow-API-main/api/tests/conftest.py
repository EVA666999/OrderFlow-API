import os
import django
import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Инициализируем Django
django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def test_image():
    """Создает тестовое изображение"""
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=b'fake-image-content',
        content_type='image/jpeg'
    )

@pytest.fixture
def test_video():
    """Создает тестовое видео"""
    return SimpleUploadedFile(
        name='test_video.mp4',
        content=b'fake-video-content',
        content_type='video/mp4'
    ) 