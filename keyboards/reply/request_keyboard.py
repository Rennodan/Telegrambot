from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def gen_markup(list_of_id: list) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for request_id in list_of_id:
        markup.add(KeyboardButton(f"{request_id}"))
    return markup

