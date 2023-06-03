from database.models import *
from loader import bot
from keyboards.reply.request_keyboard import gen_markup
import logging

# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


def save_user(query_from_user: dict, data_about_hotels: dict) -> None:
    with db:
        db.create_tables([User, RequestHotel, Request2Hotel, Hotel])
        new_user, created_user = User.get_or_create(
            user_id=query_from_user["user_id"],
            name=query_from_user['username'],
            chat_id=query_from_user['chat_id']
        )
        if new_user:
            new_request = RequestHotel.create(
                user_id=new_user,
                region_id=query_from_user['region_id'],
                country=query_from_user['country'],
                city=query_from_user['city'],
                sort_type=query_from_user['sort_type'],
                hotel_amount=len(data_about_hotels['names_list']),
                check_in=query_from_user['checkIn'],
                check_out=query_from_user['checkOut']
            )
        else:
            new_request = RequestHotel.create(
                user_id=created_user,
                region_id=query_from_user['region_id'],
                country=query_from_user['country'],
                city=query_from_user['city'],
                sort_type=query_from_user['sort_type'],
                hotel_amount=len(data_about_hotels['names_list']),
                check_in=query_from_user['checkIn'],
                check_out=query_from_user['checkOut']
            )
        for hotel in range(len(data_about_hotels['names_list'])):
            new_hotel, created_hotel = Hotel.get_or_create(
                hotel_id=data_about_hotels['property_id_list'][hotel],
                name=data_about_hotels['names_list'][hotel],
                distance=data_about_hotels['distance_list'][hotel],
                price=data_about_hotels['price_list'][hotel],
                address=data_about_hotels['address_list'][hotel],
                site=data_about_hotels['site_url'][hotel]
            )
            if new_hotel:
                request_to_hotel = Request2Hotel.create(
                    request_id=new_request,
                    hotel_id=new_hotel
                )
            else:
                request_to_hotel = Request2Hotel.create(
                    request_id=new_request,
                    hotel_id=created_hotel
                )



def get_users_requests(user: int, chat: int) -> None:
    db.create_tables([User, RequestHotel, Request2Hotel, Hotel])
    print('pepe')
    required_user = User.get_or_none(User.user_id == user, User.chat_id == chat)
    if required_user is not None:
        data = [x for x in required_user.requests]
        list_of_id = []
        for request in data:
            output_message = f'Запрос №{request.id}\n' \
                             f'Страна: {request.country}\n' \
                             f'Город: {request.city}\n' \
                             f'Количество Отелей в запросе: {request.hotel_amount}\n' \
                             f'Тип сортировки : {request.sort_type}\n' \
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
        bot.send_message(chat_id=chat, text='Вы ещё не делали запросов. История поиска пуста')
        bot.delete_state(user_id=user, chat_id=chat)


def get_required_hotels(user, chat, request_id):
    db.create_tables([User, RequestHotel, Request2Hotel, Hotel])

    query = User.select()\
        .join(RequestHotel, on=RequestHotel.user_id)\
        .join(Request2Hotel, on=RequestHotel.id)\
        .join(Hotel, on=Request2Hotel.hotel_id)\
        .where(User.user_id == user, User.chat_id == chat, RequestHotel.id == request_id)

    print(query.get())
    for hotel in query:

        print(hotel.name)

    # data = [x for x in required_user.Select()]
    # for request in data:
    #     output_message = f'Запрос №{request.id}\n' \
    #                      f'Страна: {request.country}\n' \
    #                      f'Город: {request.city}\n' \
    #                      f'Количество Отелей в запросе: {request.hotel_amount}\n' \
    #                      f'Тип сортировки : {request.sort_type}\n' \
    #                      f'Дата заезда: {request.check_in}\n' \
    #                      f'Дата выезда: {request.check_out}'
    #     bot.send_message(chat_id=chat, text=output_message)


get_required_hotels(1682183415, 1682183415, 2)