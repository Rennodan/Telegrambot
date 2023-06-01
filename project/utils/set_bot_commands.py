from telebot.types import BotCommand
from project.config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot):
    [BotCommand(*i) for i in DEFAULT_COMMANDS]
