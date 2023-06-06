from telebot.types import Message

from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message) -> None:
    """
    Ответ на команду start

    :param message:
    :return: None
    """
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
