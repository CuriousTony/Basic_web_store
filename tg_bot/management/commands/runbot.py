from django.core.management.base import BaseCommand
from requests.exceptions import ReadTimeout, ConnectionError
from tg_bot.handlers import report_handlers
from tg_bot.bot_instance import bot
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускает Telegram бота в режиме прослушивания команд'

    def handle(self, *args, **options):
        try:
            bot.infinity_polling(interval=0, timeout=30, long_polling_timeout=30)
        except (ReadTimeout, ConnectionError) as e:
            logger.error(f"Сетевая ошибка: {e}. Перезапуск через 10 секунд...")
