from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from reviews.models import Review
from tg_bot.bot_instance import bot, ADMIN_CHAT_ID
import logging
import requests
import telebot

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    current_status = instance.status
    previous_status = getattr(instance, '_previous_status', None)

    if current_status == 'pending' and (previous_status != 'pending' or created):
        try:
            text = (
                f"🛒 Новый оплаченный заказ №{instance.id}\n"
                f"Сумма: {instance.total_price} руб.\n"
                f"Статус: {instance.status}\n"
                f"Не забудьте поменять статус заказа на актуальный!"
            )
            bot.send_message(ADMIN_CHAT_ID, text)  # Синхронный вызов!
            logger.info(f"Уведомление о заказе {instance.id} отправлено.")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о заказе: {str(e)}")


@receiver(post_save, sender=Review)
def notify_new_review(sender, instance, created, **kwargs):
    try:
        logger.info(
            f"Сигнал сработал. Отзыв ID={instance.id}, "
            f"Создан: {created}, is_approved={instance.is_approved}"
        )
        if created and not instance.is_approved:
            if not instance.bouquet:
                logger.error("Букет не указан в отзыве!")
                return
            text = (
                f"📝 Новый отзыв на букет {instance.bouquet.name}\n"
                f"Рейтинг: {instance.rating}/5\n"
                f"Не забудьте провести модерацию отзыва и одобрить его публикацию!"
            )
            bot.send_message(ADMIN_CHAT_ID, text)
            logger.info(f"Уведомление о отзыве {instance.id} отправлено.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка подключения к Telegram API: {str(e)}")
    except telebot.apihelper.ApiException as e:
        logger.error(f"Ошибка Telegram API: {str(e)}")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {str(e)}")
