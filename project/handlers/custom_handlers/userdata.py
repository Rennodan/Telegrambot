from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loader import bot
from states.info_from_user import UserInfoState
from project.handlers.custom_handlers.api_connector import list_of_hotels


@bot.message_handler(commands=['bestdeal'])
def best_deal(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.min_price, message.chat.id)
    bot.send_message(message.chat.id, 'Введите минимальную цену отеля', parse_mode=None)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort'] = 'DISTANCE'
        data['sort_type'] = 'bestdeal'


@bot.message_handler(state=UserInfoState.min_price)
def min_price(message: Message) -> None:
    if message.text.isdigit():
        bot.set_state(message.from_user.id, UserInfoState.max_price, message.chat.id)
        bot.send_message(message.chat.id, 'Введите Максимальную цену', parse_mode=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_price'] = int(message.text)
    else:
        bot.send_message(message.chat.id, 'Ошибка ввода. Введите заново', parse_mode=None)


@bot.message_handler(state=UserInfoState.max_price)
def max_price(message: Message) -> None:
    if message.text.isdigit():
        bot.set_state(message.from_user.id, UserInfoState.min_distance, message.chat.id)
        bot.send_message(message.chat.id, 'Введите минимальное расстояние от центра города(от 0 км)', parse_mode=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_price'] = int(message.text)
    else:
        bot.send_message(message.chat.id, 'Ошибка ввода. Введите заново', parse_mode=None)


@bot.message_handler(state=UserInfoState.min_distance)
def min_distance(message: Message) -> None:
    if message.text.isdigit():
        bot.set_state(message.from_user.id, UserInfoState.max_distance, message.chat.id)
        bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра города(км)', parse_mode=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_distance'] = int(message.text)
    else:
        bot.send_message(message.chat.id, 'Ошибка ввода. Введите заново', parse_mode=None)


@bot.message_handler(state=UserInfoState.max_distance)
def max_distance(message: Message) -> None:
    if message.text.isdigit():
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
        bot.send_message(message.chat.id, 'Введите название страны', parse_mode=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_distance'] = int(message.text)
    else:
        bot.send_message(message.chat.id, 'Ошибка ввода. Введите заново', parse_mode=None)


@bot.message_handler(commands=['highprice'])
def high_price(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    bot.send_message(message.chat.id, 'Введите название страны', parse_mode=None)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort'] = 'PRICE_LOW_TO_HIGH'
        data['sort_type'] = 'high'


@bot.message_handler(commands=['lowprice'])
def low_price(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    bot.send_message(message.chat.id, 'Введите название страны', parse_mode=None)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort'] = 'PRICE_LOW_TO_HIGH'
        data['sort_type'] = 'low'


@bot.message_handler(state=UserInfoState.country)
def country_from_chat(message: Message) -> None:
    if all(x.isalpha() or x.isspace() for x in message.text):
        bot.send_message(message.chat.id, 'Введите название города', parse_mode=None)
        bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['country'] = message.text
            data['rooms'] = []
    else:
        bot.send_message(
            message.chat.id,
            'Ошибка. В названии стран не может быть символ кроме букв и пробелов.\n'
            'Введите название страны повторно'
        )


@bot.message_handler(state=UserInfoState.city)
def city_from_chat(message: Message) -> None:
    if all(x.isalpha() or x.isspace() for x in message.text):
        bot.send_message(message.chat.id, 'Введите количество отелей для поиска (Максимум = 10)', parse_mode=None)
        bot.set_state(message.from_user.id, UserInfoState.hotels_amount, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text

    else:
        bot.send_message(
            message.chat.id,
            'Ошибка. В названии городов не может быть символом кроме букв и пробелов.\n'
            'Введите название города повторно'
        )


@bot.message_handler(state=UserInfoState.hotels_amount)
def amount_from_chat(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) > 10:
            max_cap_message = 'Максимальное количество отелей - 10. Будет выведено 10 шт.'
            bot.send_message(message.chat.id, max_cap_message, parse_mode=None)

            bot.send_message(message.chat.id, 'Показать фото?', parse_mode=None)
            bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['resultsSize'] = 10

        elif int(message.text) < 1:
            min_cap_message = 'Минимальное количество отелей - 1.'
            bot.send_message(message.chat.id, min_cap_message, parse_mode=None)

            bot.send_message(message.chat.id, 'Показать фото?', parse_mode=None)
            bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['resultsSize'] = 1
        else:
            bot.send_message(message.chat.id, 'Показать фото?', parse_mode=None)
            bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['resultsSize'] = int(message.text)
    else:
        bot.send_message(
            message.chat.id, 'Ошибка. Сообщение содержит лишние символы\n Введите число повторно от 1 до 10'
        )


@bot.message_handler(state=UserInfoState.photo)
def photo_from_chat(message: Message) -> None:
    if message.text.lower() == 'да' or message.text.lower() == 'yes':
        bot.send_message(message.chat.id, 'Введите количество фото отеля (от 1 до 3)', parse_mode=None)
        bot.set_state(message.from_user.id, UserInfoState.photos_amount, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo'] = True

    elif message.text.lower() == 'нет' or message.text.lower() == 'no':

        bot.send_message(message.chat.id, 'Введите количество комнат. Максимум 8 комнат в одном запросе')
        bot.set_state(message.from_user.id, UserInfoState.rooms_amount, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo'] = False
    else:
        bot.send_message(message.chat.id, 'Я не понимаю. Ответьте, пожалуйста, "Да" или "Нет"')


@bot.message_handler(state=UserInfoState.photos_amount)
def photo_amount_from_chat(message: Message) -> None:  # шаг 5
    if message.text.isdigit():
        if int(message.text) > 3 or int(message.text) < 1:
            bot.send_message(message.chat.id, 'Максимальное количество фото - 3. Будет выведено 3 шт.')

            bot.send_message(message.chat.id, 'Введите количество комнат. Максимум 8 комнат в одном запросе')
            bot.set_state(message.from_user.id, UserInfoState.rooms_amount, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_amount'] = 3
        else:
            bot.send_message(message.chat.id, 'Введите количество комнат. Максимум 8 комнат в одном запросе')
            bot.set_state(message.from_user.id, UserInfoState.rooms_amount, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_amount'] = int(message.text)

    else:
        bot.send_message(message.chat.id, 'Ошибка Ввода. Введите количество фотографий от 1 до 3')


@bot.message_handler(state=UserInfoState.rooms_amount)
def rooms_from_chat(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) > 8:
            bot.send_message(message.chat.id, 'Максимальное количество комнат - 8, в запросе будет 8 комнат')

            bot.send_message(message.chat.id, 'Введите количество взрослых в комнате (Макс. = 14)')
            bot.set_state(message.from_user.id, UserInfoState.adults_amount, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['number_of_rooms'] = 8

        elif int(message.text) < 1:
            bot.send_message(
                message.chat.id,
                'Минимальное количество комнат - 1, в запросе будет 1 комната',
                parse_mode=None
            )

            bot.send_message(message.chat.id, 'Введите количество взрослых в комнате (Макс. = 14)')
            bot.set_state(message.from_user.id, UserInfoState.adults_amount, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['number_of_rooms'] = 1

        else:
            bot.send_message(message.chat.id, 'Введите количество взрослых в комнате (Макс. = 14)')
            bot.set_state(message.from_user.id, UserInfoState.adults_amount, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['number_of_rooms'] = int(message.text)

    else:
        bot.send_message(message.chat.id, 'Ошибка Ввода. Введите количество комнат от 1 до 8')


@bot.message_handler(state=UserInfoState.adults_amount)
def adults_for_room_from_chat(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) > 14:
            bot.send_message(
                message.chat.id,
                f'Максимальное количество взрослых в комнате - 14.\n'
                f'В комнате будет 14 взрослых',
                parse_mode=None
            )

            bot.send_message(message.chat.id, 'Введите количество детей в комнате (Макс. = 6)')
            bot.set_state(message.from_user.id, UserInfoState.children_amount, message.chat.id)

            people = {'adults': 14, 'children': []}
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'].append(people)

        elif int(message.text) < 1:
            bot.send_message(
                message.chat.id,
                f'Минимальное количество взрослых в комнате - 1.\n'
                f'В комнате будет 1 взрослый',
                parse_mode=None
            )

            bot.send_message(message.chat.id, 'Введите количество детей в комнате (Макс. = 6)')
            bot.set_state(message.from_user.id, UserInfoState.children_amount, message.chat.id)

            people = {'adults': 1, 'children': []}
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'].append(people)

        else:
            bot.send_message(message.chat.id, 'Введите количество детей в комнате (Макс. = 6)')
            bot.set_state(message.from_user.id, UserInfoState.children_amount, message.chat.id)

            people = {'adults': int(message.text), 'children': []}
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'].append(people)
    else:
        bot.send_message(
            message.chat.id, 'Ошибка Ввода. Введите количество взрослых в комнате от 1 до 14'
        )


@bot.message_handler(state=UserInfoState.children_amount)
def children_for_room_from_chat(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) > 6:
            bot.send_message(
                message.chat.id,
                f'Максимальное количество детей в комнате - 6, в комнате будет 6 детей',
                parse_mode=None
            )

            bot.send_message(message.chat.id, 'Введите возраст ребенка(0-17 лет)')
            bot.set_state(message.from_user.id, UserInfoState.age_of_child, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['kids_number'] = 6

        elif int(message.text) <= 0:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['number_of_rooms'] -= 1
                if data['number_of_rooms'] > 0:
                    bot.send_message(message.chat.id, 'Введите количество взрослых в следующей комнате (Макс. = 14)')
                    bot.set_state(message.from_user.id, UserInfoState.adults_amount, message.chat.id)

                else:
                    bot.send_message(message.chat.id, 'Введите дату заезда')
                    calendar, step = DetailedTelegramCalendar(calendar_id='checkIn').build()
                    bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)
                    bot.set_state(message.from_user.id, UserInfoState.check_in_date, message.chat.id)

        else:
            bot.send_message(message.chat.id, 'Введите возраст ребенка(0-17 лет)')
            bot.set_state(message.from_user.id, UserInfoState.age_of_child, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['kids_number'] = int(message.text)

    else:
        bot.send_message(
            message.chat.id, 'Ошибка Ввода. Введите количество детей в комнате от 1 до 6'
        )


@bot.message_handler(state=UserInfoState.age_of_child)
def kid_age_from_chat(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) > 17:
            bot.send_message(message.chat.id, 'Возраст выбран более 17, будет указан 17')
            kid = {'age': 17}

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'][-1]['children'].append(kid)
                data['kids_number'] -= 1

                if data['kids_number'] > 0:
                    bot.send_message(message.chat.id, f'Введите возраст ребенка(0-17 лет)')
                else:
                    data['number_of_rooms'] -= 1
                    if data['number_of_rooms'] > 0:
                        bot.send_message(
                            message.chat.id,
                            'Введите количество взрослых в комнате (Макс. = 14)'
                        )
                        bot.set_state(message.from_user.id, UserInfoState.adults_amount, message.chat.id)

                    else:
                        bot.send_message(message.chat.id, 'Введите дату заезда')
                        calendar, step = DetailedTelegramCalendar(calendar_id='checkIn').build()
                        bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)
                        bot.set_state(message.from_user.id, UserInfoState.check_in_date, message.chat.id)

        elif int(message.text) < 0:
            bot.send_message(message.chat.id, 'Возраст не может быть отрицательным, будет указан как 0 лет')
            kid = {'age': 0}
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'][-1]['children'].append(kid)
                data['kids_number'] -= 1

                if data['kids_number'] > 0:
                    bot.send_message(message.chat.id, f'Введите возраст ребенка(0-17 лет)')

                else:
                    data['number_of_rooms'] -= 1
                    if data['number_of_rooms'] > 0:
                        bot.send_message(message.chat.id, f'Введите количество взрослых в комнате (Макс. = 14)')

                    else:
                        bot.send_message(message.chat.id, 'Введите дату заезда')
                        calendar, step = DetailedTelegramCalendar(calendar_id='checkIn').build()
                        bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)
                        bot.set_state(message.from_user.id, UserInfoState.check_in_date, message.chat.id)

        else:
            kid = {'age': int(message.text)}
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['rooms'][-1]['children'].append(kid)
                data['kids_number'] -= 1

                if data['kids_number'] > 0:
                    bot.send_message(message.chat.id, f'Введите возраст ребенка(0-17 лет)')

                else:
                    data['number_of_rooms'] -= 1
                    if data['number_of_rooms'] > 0:
                        bot.send_message(message.chat.id, f'Введите количество взрослых в комнате (Макс. = 14)')

                    else:
                        bot.send_message(message.chat.id, 'Введите дату заезда')
                        calendar, step = DetailedTelegramCalendar(calendar_id='checkIn').build()
                        bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)
                        bot.set_state(message.from_user.id, UserInfoState.check_in_date, message.chat.id)
    else:
        bot.send_message(
            message.chat.id, 'Ошибка Ввода. Введите возраст ребенка от 0 до 17'
        )


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='checkIn'))
def check_in_cal(cal):
    result, key, step = DetailedTelegramCalendar(calendar_id='checkIn').process(cal.data)
    if not result and key:
        bot.edit_message_text(
            f"Select {LSTEP[step]}",
            cal.message.chat.id,
            cal.message.message_id,
            reply_markup=key
        )
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}, как дату заезда",
                              cal.message.chat.id,
                              cal.message.message_id)

        bot.set_state(cal.from_user.id, UserInfoState.check_out_date, cal.message.chat.id)
        bot.send_message(cal.message.chat.id, 'Введите дату выезда')

        calendar, step = DetailedTelegramCalendar(calendar_id='checkOut').build()
        bot.send_message(cal.message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)

        with bot.retrieve_data(cal.from_user.id, cal.message.chat.id) as data:
            data['checkIn'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='checkOut'))
def check_out_cal(cal):
    result, key, step = DetailedTelegramCalendar(calendar_id='checkOut').process(cal.data)
    if not result and key:
        bot.edit_message_text(
            f"Select {LSTEP[step]}",
            cal.message.chat.id,
            cal.message.message_id,
            reply_markup=key
        )
    elif result:
        bot.edit_message_text(
            f"Вы выбрали {result}, как дату выезда",
            cal.message.chat.id,
            cal.message.message_id
        )

        bot.send_message(cal.message.chat.id, 'Ожидайте')
        bot.delete_state(cal.message.from_user.id, cal.message.chat.id)
        bot.set_state(cal.from_user.id, UserInfoState.waiting_for_r, cal.message.chat.id)

        with bot.retrieve_data(cal.from_user.id, cal.message.chat.id) as data:
            data['checkOut'] = result

        last_step(user_id=cal.from_user.id, chat_id=cal.message.chat.id)


def last_step(user_id: int, chat_id: int) -> None:
    bot.send_message(chat_id, '{data}')
    with bot.retrieve_data(user_id, chat_id) as data:
        data['user_id'] = f'{user_id}'
        data['chat_id'] = f'{chat_id}'
        data['site_id'] = 310000033
        data['currency'] = 'USD'
        data['eapid'] = 1
        data['locale'] = 'ru_RU'
        bot.send_message(chat_id, f'{data}')

        list_of_hotels(data)
