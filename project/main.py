import telebot
import requests
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


# 5939382793:AAF08P8dpUqs7thBpAo4iHqxG8npXvjFZbM  @SkillBoxTask_bot SkillboxTask

# 1 Узнать топ самых дешёвых отелей в городе (команда /lowprice).
# Команда /lowprice
# После ввода команды у пользователя запрашивается:
# 1. Город, где будет проводиться поиск.
# 2. Количество отелей, которые необходимо вывести в результате (не больше
# заранее определённого максимума).
# 3. Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)
# a. При положительном ответе пользователь также вводит количество
# необходимых фотографий (не больше заранее определённого
# максимума)

# название отеля,
# 5
# ● адрес,
# ● как далеко расположен от центра,
# ● цена,
# ● N фотографий отеля (если пользователь счёл необходимым их вывод)


# 2 Узнать топ самых дорогих отелей в городе (команда /highprice).
# 3 Узнать топ отелей, наиболее подходящих по цене и расположению от центра
# (самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
# 4 Узнать историю поиска отелей (команда /history).
# 5 Без запущенного скрипта бот на команды (и на что-либо еще) не реагирует.

class HotelFinder:
    def __init__(self):
        self.bot = telebot.TeleBot('5939382793:AAF08P8dpUqs7thBpAo4iHqxG8npXvjFZbM')
        self.headers = {
            'X-RapidAPI-Key': '3f2dcf3234mshbc37a90c7194b33p11e490jsna68749c34d96',
            'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
        }
        self.site_id = 310000033
        self.currency = 'USD'
        self.eapid = 1
        self.locale = 'ru_RU'
        self.checkIn = None
        self.checkOut = None

        @self.bot.message_handler(content_types=['audio', 'sticker', 'photo', 'pinned_message'])
        def error_bot(message: Message):
            self.bot.send_message(message.chat.id, 'Я не понимаю', parse_mode=None)

        # Handle /low_price command
        @self.bot.message_handler(commands=['low_price'])
        def _low_price(message: Message):
            self.get_by_price(message, 'PRICE_LOW_TO_HIGH')

        @self.bot.message_handler(commands=['high_price'])
        def _high_price(message: Message):  # PRICE_HIGHEST_FIRST
            self.get_by_price(message, 'desc')

        @self.bot.message_handler(commands=['best_deal'])
        def _best_deal(message: Message):
            self.get_by_price(message, 'desc')

        @self.bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='checkIn'))
        def check_in_cal(c):
            result, key, step = DetailedTelegramCalendar(calendar_id='checkIn').process(c.data)
            if not result and key:
                self.bot.edit_message_text(f"Select {LSTEP[step]}",
                                           c.message.chat.id,
                                           c.message.message_id,
                                           reply_markup=key)
            elif result:
                self.bot.edit_message_text(f"Вы выбрали {result}, как дату заезда",
                                           c.message.chat.id,
                                           c.message.message_id)
                self.checkIn = result

        @self.bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id='checkOut'))
        def check_out_cal(c):
            result, key, step = DetailedTelegramCalendar(calendar_id='checkOut').process(c.data)
            if not result and key:
                self.bot.edit_message_text(f"Select {LSTEP[step]}",
                                           c.message.chat.id,
                                           c.message.message_id,
                                           reply_markup=key)
            elif result:
                self.bot.edit_message_text(f"Вы выбрали {result}, как дату выезда",
                                           c.message.chat.id,
                                           c.message.message_id)
                self.checkOut = result

    def get_by_price(self, message: Message, order: str):  # шаг 0
        query_from_user = {
            'country': None,
            'city': None,
            'resultsSize': 10,
            'photo': False,
            'photo_amount': 3,
            'sort': order,
            'number_of_rooms': 1,
            'rooms': [],
            'checkInDate': {
                'day': None,
                'month': None,
                'year': None
            },
            'checkOutDate': {
                'day': None,
                'month': None,
                'year': None
            },
        }
        output_message = self.bot.send_message(message.chat.id, 'Введите название страны', parse_mode=None)
        self.bot.register_next_step_handler(output_message, self.country_from_chat, query_from_user)

    # метод(locations/v3/search)
    def get_region_id(self, q: dict):  # 1 шаг получаем id региона он же gaia id по запросу Страна + Город
        url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

        querystring = {'q': f'{q["country"]} {q["city"]}', 'locale': 'en_US', 'siteid': f'{self.site_id}'}
        response = requests.get(url, headers=self.headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            result = response.json()
            if len(result['sr']) == 0:  # если в городе нет отелей доступных на сайте hotels.com(например Россия)
                return None
            else:
                return result['sr'][0]['gaiaId']

    def post_hotel_detail(self, property_id: int, query: dict, hotel_data: dict):
        url = 'https://hotels4.p.rapidapi.com/properties/v2/detail'

        payload = {
            'currency': self.currency,
            'eapid': 1,
            'locale': self.locale,
            'siteId': self.site_id,
            'propertyId': property_id
        }

        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        if response.status_code == requests.codes.ok:
            print('ok')
            result = response.json()
            hotel_data['address_list'].append(
                result['data']['propertyInfo']['summary']['location']['address']['addressLine']
            )
            if query['photo']:
                photo_of_h = []
                for i in range(query['photo_amount']):
                    photo_of_h.append(result['data']['propertyInfo']['propertyGallery']['images'][i]['image']['url'])
                hotel_data['photo_list'].append(photo_of_h)

    def send_hotels_to_user(self, message: Message, data_about_hotels: dict):
        print(data_about_hotels)
        for hotel in range(len(data_about_hotels['names_list'])):
            output_message = f'№{hotel + 1}\n' \
                             f'Название: {data_about_hotels["names_list"][hotel]}\n' \
                             f'Сайт отеля: {data_about_hotels["site_url"][hotel]}\n' \
                             f'Расстояние от центра: {data_about_hotels["distance_list"][hotel]}Км.\n' \
                             f'Цена за ночь: {data_about_hotels["price_list"][hotel]}\n' \
                             f'Адрес: {data_about_hotels["address_list"][hotel]}'
            self.bot.send_message(message.chat.id, output_message)
            for photo in range(len(data_about_hotels['photo_list'][hotel])):
                self.bot.send_photo(message.chat.id, f'{data_about_hotels["photo_list"][hotel][photo]}')

    def list_of_hotels(self, message: Message, query: dict):
        print(query)
        region_id = self.get_region_id(query)
        print(region_id)
        payload = self.create_payload(query=query, region_id=region_id)
        print(payload)

        url = 'https://hotels4.p.rapidapi.com/properties/v2/list'
        response = requests.post(url, json=payload, headers=self.headers, timeout=10)

        if response.status_code == requests.codes.ok:
            result = response.json()
            data_about_hotels = {
                'names_list': [],
                'distance_list': [],
                'price_list': [],
                'address_list': [],
                'site_url': [],
                'photo_list': []

            }

            for hotel in range(query['resultsSize']):
                data_about_hotels['names_list'].append(result['data']['propertySearch']['properties'][hotel]['name'])

                data_about_hotels['distance_list'].append(
                    result
                    ['data']
                    ['propertySearch']
                    ['properties']
                    [hotel]
                    ['destinationInfo']
                    ['distanceFromDestination']
                    ['value']
                )

                data_about_hotels['price_list'].append(
                    result
                    ['data']
                    ['propertySearch']
                    ['properties']
                    [hotel]
                    ['price']
                    ['options']
                    [0]
                    ['formattedDisplayPrice']
                )

                property_id = result['data']['propertySearch']['properties'][hotel]['id']

                data_about_hotels['site_url'].append(f'https://www.hotels.com/h{property_id}.Hotel-Information')

                self.post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels)

            self.send_hotels_to_user(message=message, data_about_hotels=data_about_hotels)
        else:
            print('ошибка')

    def country_from_chat(self, message: Message, query: dict):  # шаг 1
        if all(x.isalpha() or x.isspace() for x in message.text):
            query['country'] = message.text
            output_message = self.bot.send_message(message.chat.id, 'Введите название города', parse_mode=None)
            self.bot.register_next_step_handler(output_message, self.city_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id,
                'Ошибка. В названии стран не может быть символ кроме букв и пробелов.\n'
                'Введите название страны повторно'
            )
            self.bot.register_next_step_handler(output_message, self.country_from_chat, query)

    def city_from_chat(self, message: Message, query: dict):  # шаг 2
        if all(x.isalpha() or x.isspace() for x in message.text):
            query['city'] = message.text
            output_message = self.bot.send_message(
                message.chat.id,
                'Введите количество отелей для поиска (Максимум = 10)',
                parse_mode=None
            )
            self.bot.register_next_step_handler(output_message, self.amount_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id,
                'Ошибка. В названии городов не может быть символом кроме букв и пробелов.\n'
                'Введите название города повторно'
            )
            self.bot.register_next_step_handler(output_message, self.city_from_chat, query)

    def amount_from_chat(self, message: Message, query: dict):  # шаг 3
        if message.text.isdigit():
            if int(message.text) > 10:
                max_cap_message = 'Максимальное количество отелей - 10. Будет выведено 10 шт.'
                query['resultsSize'] = 10
                self.bot.send_message(message.chat.id, max_cap_message, parse_mode=None)
                output_message = self.bot.send_message(
                    message.chat.id,
                    'Показать фото?',
                    parse_mode=None
                )
                self.bot.register_next_step_handler(output_message, self.photo_from_chat, query)
            elif int(message.text) < 1:
                min_cap_message = 'Минимальное количество отелей - 1.'
                query['resultsSize'] = 1
                self.bot.send_message(message.chat.id, min_cap_message, parse_mode=None)
                output_message = self.bot.send_message(
                    message.chat.id,
                    'Показать фото?',
                    parse_mode=None
                )
                self.bot.register_next_step_handler(output_message, self.photo_from_chat, query)
            else:
                query['resultsSize'] = int(message.text)

                output_message = self.bot.send_message(
                    message.chat.id, 'Показать фото?',
                    parse_mode=None
                )
                self.bot.register_next_step_handler(output_message, self.photo_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка. Сообщение содержит лишние символы\n Введите число повторно от 1 до 10'
            )
            self.bot.register_next_step_handler(output_message, self.amount_from_chat, query)

    def photo_from_chat(self, message: Message, query: dict):  # шаг 4
        if message.text.lower() == 'да' or message.text.lower() == 'yes':
            query['photo'] = True

            output_message = self.bot.send_message(
                message.chat.id, 'Введите количество фото отеля (от 1 до 3)',
                parse_mode=None
            )
            self.bot.register_next_step_handler(output_message, self.photo_amount_from_chat, query)
        elif message.text.lower() == 'нет' or message.text.lower() == 'no':
            query['photo'] = False
            output_message = self.bot.send_message(
                message.chat.id,
                'Введите количество комнат. Максимум восемь комнат в одном запросе',
                parse_mode=None
            )
            self.bot.register_next_step_handler(output_message, self.rooms_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Я не понимаю. Ответьте, пожалуйста, "Да" или "Нет"'
            )
            self.bot.register_next_step_handler(output_message, self.photo_from_chat, query)

    def photo_amount_from_chat(self, message: Message, query: dict):  # шаг 5
        if message.text.isdigit():
            if int(message.text) > 3 or int(message.text) < 1:
                self.bot.send_message(
                    message.chat.id,
                    'Максимальное количество фото - 3. Будет выведено 3 шт.',
                    parse_mode=None
                )
                output_message = self.bot.send_message(
                    message.chat.id,
                    'Введите количество комнат. Максимум восемь комнат в одном запросе',
                    parse_mode=None
                )

                self.bot.register_next_step_handler(output_message, self.rooms_from_chat, query)
            else:
                query['photo_amount'] = int(message.text)
                output_message = self.bot.send_message(
                    message.chat.id,
                    'Введите количество комнат',
                    parse_mode=None
                )

                self.bot.register_next_step_handler(output_message, self.rooms_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка Ввода. Введите количество фотографий от 1 до 3'
            )
            self.bot.register_next_step_handler(output_message, self.photo_amount_from_chat, query)

    def rooms_from_chat(self, message: Message, query: dict):  # шаг 5/6
        if message.text.isdigit():
            if int(message.text) > 8:
                query['number_of_rooms'] = 8
                self.bot.send_message(
                    message.chat.id,
                    'Максимальное количество комнат - 8, в запросе будет 8 комнат',
                    parse_mode=None
                )
            elif int(message.text) < 1:
                query['number_of_rooms'] = 1
                self.bot.send_message(
                    message.chat.id,
                    'Минимальное количество комнат - 1, в запросе будет 1 комната',
                    parse_mode=None
                )
            else:
                query['number_of_rooms'] = int(message.text)
            output_message = self.bot.send_message(
                message.chat.id,
                f'Введите количество взрослых в комнате №{len(query["rooms"]) + 1} (Макс. = 14)'
            )
            self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка Ввода. Введите количество комнат от 1 до 8'
            )
            self.bot.register_next_step_handler(output_message, self.rooms_from_chat, query)

    def adults_for_room_from_chat(self, message: Message, query: dict):
        if message.text.isdigit():
            if int(message.text) > 14:
                self.bot.send_message(
                    message.chat.id,
                    f'Максимальное количество взрослых в комнате - 14.\n'
                    f'В комнате №{len(query["rooms"]) + 1} будет 14 взрослых',
                    parse_mode=None
                )

                people = {'adults': 14, 'children': []}
                query['rooms'].append(people)

                output_message = self.bot.send_message(
                    message.chat.id,
                    f'Введите количество детей в комнате №{len(query["rooms"])} (Макс. = 6)'
                )
                self.bot.register_next_step_handler(output_message, self.children_for_room_from_chat, query)
            elif int(message.text) < 1:
                self.bot.send_message(
                    message.chat.id,
                    f'Минимальное количество взрослых в комнате - 1.\n'
                    f'В комнате №{len(query["rooms"]) + 1} будет 1 взрослый',
                    parse_mode=None
                )

                people = {'adults': 1, 'children': []}
                query['rooms'].append(people)

                output_message = self.bot.send_message(
                    message.chat.id,
                    f'Введите количество детей в комнате №{len(query["rooms"])} (Макс. = 6)'
                )
                self.bot.register_next_step_handler(output_message, self.children_for_room_from_chat, query)

            else:
                people = {'adults': int(message.text), 'children': []}
                query['rooms'].append(people)

                output_message = self.bot.send_message(
                    message.chat.id,
                    f'Введите количество детей в комнате №{len(query["rooms"])} (Макс. = 6)'
                )
                self.bot.register_next_step_handler(output_message, self.children_for_room_from_chat, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка Ввода. Введите количество взрослых в комнате от 1 до 14'
            )
            self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)

    def children_for_room_from_chat(self, message: Message, query: dict):
        if message.text.isdigit():
            if int(message.text) > 6:
                self.bot.send_message(
                    message.chat.id,
                    f'Максимальное количество детей в комнате - 6, в комнате будет 6 детей',
                    parse_mode=None
                )
                kids_number = 6
                output_message = self.bot.send_message(
                    message.chat.id,
                    f'Введите возраст ребенка(0-17 лет)'
                )
                self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query, kids_number)

            elif int(message.text) <= 0:
                query['number_of_rooms'] -= 1
                if query['number_of_rooms'] > 0:
                    output_message = self.bot.send_message(
                        message.chat.id,
                        f'Введите количество взрослых в комнате №{len(query["rooms"]) + 1} (Макс. = 14)'
                    )
                    self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)
                else:
                    output_message = self.bot.send_message(
                        message.chat.id,
                        'Введите дату заезда'
                    )
                    self.bot.register_next_step_handler(output_message, self.check_in_date_calendar, query)
            else:
                kids_number = int(message.text)
                output_message = self.bot.send_message(
                    message.chat.id,
                    f'Введите возраст ребенка(0-17 лет)'
                )
                self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query, kids_number)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка Ввода. Введите количество детей в комнате от 1 до 6'
            )
            self.bot.register_next_step_handler(output_message, self.children_for_room_from_chat, query)

    def kid_age_from_chat(self, message: Message, query: dict, kids_number: int):
        if message.text.isdigit():
            if int(message.text) > 17:
                self.bot.send_message(message.chat.id, 'Возраст выбран более 17, будет указан 17')
                kid = {'age': 17}
                query['rooms'][-1]['children'].append(kid)

                kids_number -= 1
                if kids_number > 0:
                    output_message = self.bot.send_message(
                        message.chat.id,
                        f'Введите возраст ребенка(0-17 лет)'
                    )
                    self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query, kids_number)
                else:
                    query['number_of_rooms'] -= 1
                    if query['number_of_rooms'] > 0:
                        output_message = self.bot.send_message(
                            message.chat.id,
                            f'Введите количество взрослых в комнате №{len(query["rooms"]) + 1} (Макс. = 14)'
                        )
                        self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)
                    else:
                        output_message = self.bot.send_message(
                            message.chat.id,
                            'Введите дату заезда'
                        )
                        self.bot.register_next_step_handler(output_message, self.check_in_date_calendar, query)
            elif int(message.text) < 0:
                self.bot.send_message(message.chat.id, 'Возраст не может быть отрицательным, будет указан как 0 лет')
                kid = {'age': 0}
                query['rooms'][-1]['children'].append(kid)

                kids_number -= 1
                if kids_number > 0:
                    output_message = self.bot.send_message(
                        message.chat.id,
                        f'Введите возраст ребенка(0-17 лет)'
                    )
                    self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query, kids_number)
                else:
                    query['number_of_rooms'] -= 1
                    if query['number_of_rooms'] > 0:
                        output_message = self.bot.send_message(
                            message.chat.id,
                            f'Введите количество взрослых в комнате №{len(query["rooms"]) + 1} (Макс. = 14)'
                        )
                        self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)
                    else:
                        output_message = self.bot.send_message(
                            message.chat.id,
                            'Введите дату заезда'
                        )
                        self.bot.register_next_step_handler(output_message, self.check_in_date_calendar, query)

            else:
                kid = {'age': int(message.text)}
                query['rooms'][-1]['children'].append(kid)

                kids_number -= 1
                if kids_number > 0:
                    output_message = self.bot.send_message(
                        message.chat.id,
                        f'Введите возраст ребенка(0-17 лет)'
                    )
                    self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query, kids_number)
                else:
                    query['number_of_rooms'] -= 1
                    if query['number_of_rooms'] > 0:
                        output_message = self.bot.send_message(
                            message.chat.id,
                            f'Введите количество взрослых в комнате №{len(query["rooms"]) + 1} (Макс. = 14)'
                        )
                        self.bot.register_next_step_handler(output_message, self.adults_for_room_from_chat, query)
                    else:
                        self.bot.send_message(
                            message.chat.id,
                            'Введите дату заезда'
                        )
                        self.check_in_date_calendar(message, query)
        else:
            output_message = self.bot.send_message(
                message.chat.id, 'Ошибка Ввода. Введите возраст ребенка от 0 до 17'
            )
            self.bot.register_next_step_handler(output_message, self.kid_age_from_chat, query)

    def check_in_date_calendar(self, message: Message, query: dict):
        calendar, step = DetailedTelegramCalendar(calendar_id='checkIn').build()
        self.bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)

        self.bot.send_message(message.chat.id, 'Введите дату выезда')
        self.check_out_date_calendar(message, query)

    def check_out_date_calendar(self, message: Message, query: dict):
        calendar, step = DetailedTelegramCalendar(calendar_id='checkOut').build()
        self.bot.send_message(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)

        output_message = self.bot.send_message(
            message.chat.id,
            'Отправьте сообщение, чтобы продолжить'
        )
        self.bot.register_next_step_handler(output_message, self.last_step, query)

    def last_step(self, message: Message, query: dict):
        self.bot.send_message(message.chat.id, 'Производится запрос')
        self.list_of_hotels(message=message, query=query)

    # number_in_list name price optional(photo max=3)
    def create_payload(self, query: dict, region_id: int):
        # PRICE_RELEVANT (Price + our picks)|REVIEW (Guest rating)|DISTANCE (Distance from downtown)|
        # PRICE_LOW_TO_HIGH (Price)|PROPERTY_CLASS (Star rating)|RECOMMENDED (Recommended) Виды сортировок
        payload = {
            'currency': f'{self.currency}',
            'eapid': self.eapid,
            'locale': f'{self.locale}',
            'siteId': self.site_id,
            'destination': {
                'regionId': f'{region_id}'
            },
            'checkInDate': {
                'day': self.checkIn.day,
                'month': self.checkIn.month,
                'year': self.checkIn.year
            },
            'checkOutDate': {
                'day': self.checkOut.day,
                'month': self.checkOut.month,
                'year': self.checkOut.year
            },
            'rooms': query['rooms'],
            'resultsStartingIndex': 0,
            'resultsSize': query['resultsSize'],
            'sort': query['sort'],
            'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
        }

        return payload


new_hotel = HotelFinder()


print('Бот запушен')
new_hotel.bot.polling(none_stop=True)
