from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def gen_markup(list_of_id: list) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(True, True)
    for request_id in list_of_id:
        markup.add(KeyboardButton(f"{request_id}"))
    return markup

