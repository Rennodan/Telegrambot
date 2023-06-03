from telebot.types import Message
from loader import bot
from states.info_from_user import UserInfoState
from database.database_tg import get_users_requests


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.history, message.chat.id)
    get_users_requests(user=message.from_user.id, chat=message.chat.id)



@bot.message_handler(state=UserInfoState.history)
def request_hotel(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:

        pass
    else:
        bot.send_message(message.chat.id, 'Ошибка ввода. Введите заново', parse_mode=None)


