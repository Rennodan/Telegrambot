from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def gen_markup(list_of_id: list) -> ReplyKeyboardMarkup:
    """
    Функция создания клавиатуры для выбора запроса

    :param list list_of_id: список айдишников запросов
    :return: ReplyKeyboardMarkup: Клавиатуру с кнопками, на которых написаны номера запросов
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for request_id in list_of_id:
        markup.add(KeyboardButton(f"{request_id}"))
    return markup


def yes_or_no() -> ReplyKeyboardMarkup:
    """
    Функция создания клавиатуры для ответа на вопрос от бота

    :return: ReplyKeyboardMarkup: Клавиатуру с кнопками да, нет
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Да'))
    markup.add(KeyboardButton('Нет'))
    return markup
