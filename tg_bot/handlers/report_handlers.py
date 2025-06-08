from tg_bot.bot_instance import bot, ADMIN_CHAT_ID
from tg_bot.keyboards.report_keyboards import (get_report_type_keyboard,
                                               get_report_period_keyboard)
import logging
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from analytics.reports import (
    get_revenue, get_profit, get_order_count,
    get_bouquets_sold, get_top_users, get_top_bouquets
)

logger = logging.getLogger(__name__)
user_states = defaultdict(dict)


def is_admin(chat_id):
    # проверка совпадения chat_id с целевым
    return int(chat_id) == int(ADMIN_CHAT_ID)


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        if not is_admin(message.chat.id):
            logger.warning(f'Неавторизованный доступ к боту от chat_id: {message.chat.id}')
            bot.send_message(message.chat.id, "⛔ Доступ запрещен. Бот доступен только администраторам.")
            return
        try:
            logger.info('Администратор отправил команду /start...')
            bot.send_message(message.chat.id,
                             text='Выберите тип отчета:',
                             reply_markup=get_report_type_keyboard())
            logger.info(f'Клавиатура report_type отправлена администратору.')
        except Exception as e:
            logger.error(f'Сбой - клавиатура report_type не отправлена...\nТекст ошибки: {e}')
    except Exception as e:
        logger.error(f'Ошибка при обработке команды /start: {e}')


@bot.callback_query_handler(func=lambda call: call.data in [
    'revenue', 'profit', 'orders', 'bouquets', 'topusers', 'topbouquets'
])
def handle_report_type(call):
    try:
        if not is_admin(call.message.chat.id):
            logger.warning(f'Неавторизованный callback от chat_id: {call.message.chat.id}')
            bot.answer_callback_query(call.id, "⛔ Доступ запрещен", show_alert=True)
            return
        try:
            logger.info('Сработал handle_report_type...')
            chat_id = call.message.chat.id
            user_states[chat_id]['report_type'] = call.data

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text='Выберите желаемый отчетный период:',
                reply_markup=get_report_period_keyboard()
            )
            logger.info(f'Установлен тип отчета: {call.data} для chat_id: {chat_id}')
        except Exception as e:
            logger.error(f'Ошибка обработки типа отчета: {e}')
    except Exception as e:
        logger.error(f'Ошибка обработки типа отчета: {e}')


@bot.callback_query_handler(func=lambda call: call.data in ['day', 'week', 'month'])
def handle_report_period(call):
    try:
        chat_id = call.message.chat.id
        if not is_admin(chat_id):
            logger.warning(f'Попытка формирования отчета от неавторизованного пользователя: {chat_id}')
            bot.answer_callback_query(call.id, "⛔ Требуются права администратора", show_alert=True)
            return
        try:
            logger.info('Сработал хендлер report_period...')
            chat_id = call.message.chat.id
            report_type = user_states.get(chat_id, {}).get('report_type')

            if not report_type:
                logger.error(f'Тип отчета не найден для chat_id: {chat_id}')
                bot.send_message(chat_id, "Пожалуйста, сначала выберите тип отчета.")
                return

            period = call.data
            now = timezone.now()
            current_tz = timezone.get_current_timezone()

            if period == "day":
                start_date = now.astimezone(current_tz).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif period == "week":
                start_date = (now - timedelta(days=now.weekday())).astimezone(current_tz).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
            elif period == "month":
                start_date = now.astimezone(current_tz).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end_date = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    end_date = now.replace(month=now.month + 1, day=1)
                end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                logger.error(f"Неизвестный период: {period}")
                return

            logger.info('Приступаю к формированию отчета...')
            try:
                report_text = generate_report(report_type, start_date, end_date)
                if report_text:
                    bot.send_message(chat_id, report_text)
                else:
                    logger.info('В переменной report_text ничерта нет...')
            except Exception as e:
                logger.exception('Проблема с формированием report_text...')

            if chat_id in user_states:
                del user_states[chat_id]

        except Exception as e:
            logger.error(f'Ошибка обработки периода: {e}')
            bot.send_message(chat_id, "Произошла ошибка при формировании отчета.")
    except Exception as e:
        logger.error(f'Ошибка обработки периода: {e}')
        bot.send_message(chat_id, "Произошла ошибка при формировании отчета.")


def generate_report(report_type, start_date, end_date):
    if report_type == "revenue":
        return f"Выручка за период: {get_revenue(start_date, end_date)} руб."
    elif report_type == "profit":
        return f"Прибыль за период: {get_profit(start_date, end_date)} руб."
    elif report_type == "orders":
        return f"Количество заказов за период: {get_order_count(start_date, end_date)}"
    elif report_type == "bouquets":
        return f"Проданных букетов за период: {get_bouquets_sold(start_date, end_date)}"
    elif report_type == "topusers":
        top_users = get_top_users(start_date, end_date)
        return f"ТОП-5 пользователей за период:\n" + "\n".join(
            f"{user.name}: {user.order_count} заказов" for user in top_users
        )
    elif report_type == "topbouquets":
        top_bouquets = get_top_bouquets(start_date, end_date)
        return f"ТОП-5 букетов за период:\n" + "\n".join(
            f"{bouquet.name}: {bouquet.total_sold} шт." for bouquet in top_bouquets
        )
    return "Неверный запрос."
