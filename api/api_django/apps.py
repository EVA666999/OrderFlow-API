from django.apps import AppConfig
import logging



class ApiDjangoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_django"

logger = logging.getLogger(__name__)

class ApiDjangoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_django'
    
    def ready(self):
        """
        Запускается при инициализации приложения
        """
        # Импортируем функцию здесь, чтобы избежать циклических импортов
        try:
            from kafka.utils import ensure_kafka_topics
            # Создаем топик "orders" при запуске приложения
            ensure_kafka_topics(['orders'])
            logger.info("Kafka топики инициализированы")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Kafka топиков: {e}")