from telebot import types


def get_report_type_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton("Выручка", callback_data="revenue"),
        types.InlineKeyboardButton("Прибыль", callback_data="profit"),
        types.InlineKeyboardButton("Заказы", callback_data="orders"),
        types.InlineKeyboardButton("Букеты", callback_data="bouquets"),
        types.InlineKeyboardButton("ТОП пользователей", callback_data="topusers"),
        types.InlineKeyboardButton("ТОП букетов", callback_data="topbouquets"),
    )
    return keyboard


def get_report_period_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton("День", callback_data="day"),
        types.InlineKeyboardButton("Неделя", callback_data="week"),
        types.InlineKeyboardButton("Месяц", callback_data="month"),
    )
    return keyboard
