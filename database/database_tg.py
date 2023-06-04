from database.models import *
from loader import bot
from keyboards.reply.request_keyboard import gen_markup
# import logging

# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


def save_user(query_from_user: dict, data_about_hotels: dict) -> None:
    db.create_tables([History, Hotel])
    with db:
        request = History.create(
            user_id=query_from_user['user_id'],
            date=query_from_user['message_date'],
            country=query_from_user['country'],
            city=query_from_user['city'],
            check_in=query_from_user['checkIn'],
            check_out=query_from_user['checkOut'],
            command=query_from_user['sort_type']
        )
        for hotel in range(len(data_about_hotels['names_list'])):
            created_hotel = Hotel.create(
                history_id=request,
                hotel_name=data_about_hotels['names_list'][hotel],
                distance=data_about_hotels['distance_list'][hotel],
                price=data_about_hotels['price_list'][hotel],
                address=data_about_hotels['address_list'][hotel],
                site=data_about_hotels['site_url'][hotel]
            )


def get_users_requests(user: int, chat: int) -> None:
    db.create_tables([History, Hotel])
    with db:
        data = History.select().where(History.user_id == chat)
        if len(data) > 0:
            list_of_id = []
            for request in data:
                output_message = f'Запрос №{request.id}\n' \
                                 f'Время запроса: {request.date}' \
                                 f'Страна: {request.country}\n' \
                                 f'Город: {request.city}\n' \
                                 f'Тип сортировки : {request.command}\n' \
                                 f'Дата заезда: {request.check_in}\n' \
                                 f'Дата выезда: {request.check_out}'
                bot.send_message(chat_id=chat, text=output_message)
                list_of_id.append(request.id)
            bot.send_message(
                chat_id=chat,
                text='Выберите нужный запрос',
                parse_mode=None,
                reply_markup=gen_markup(list_of_id)
            )
        else:
            bot.send_message(chat_id=chat, text='История запросов пуста')
            bot.delete_state(user_id=user, chat_id=chat)


def get_required_hotels(user: int, chat: int, request_id: int) -> None:
    data = (Hotel.select(History, Hotel).join(History).where(History.user_id == chat, Hotel.history_id == request_id))
    number_of_hotel = 1
    for hotel in data:
        output_message = f'№{number_of_hotel}\n' \
                         f'Название: {hotel.hotel_name}\n' \
                         f'Сайт отеля: {hotel.site}\n' \
                         f'Расстояние от центра: {hotel.distance}Км.\n' \
                         f'Цена за ночь: {hotel.price}\n' \
                         f'Адрес: {hotel.address}'
        number_of_hotel += 1
        bot.send_message(chat_id=chat, text=output_message)
    bot.delete_state(user_id=user, chat_id=chat)
