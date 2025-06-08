import logging
from django.apps import AppConfig


class TgBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tg_bot'

    def ready(self):
        logger = logging.getLogger(__name__)
        logger.info('Инициализация tg_bot...')
        import tg_bot.signals
        logger.info('Сигналы импортированы...')
