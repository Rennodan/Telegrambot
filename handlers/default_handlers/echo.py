from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    """
    Функция отвечающая за эхо бота(ответ юзеру на сообщения без команд)

    :param Message message: Сообщение от пользователя
    :return:
    """
    bot.reply_to(
        message, "Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}"
    )
