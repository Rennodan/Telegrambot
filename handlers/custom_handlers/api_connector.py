from loader import bot
import requests
from config_data.config import RAPID_API_KEY
from database.database_tg import save_user


def get_region_id(q: dict, headers: dict) -> None or int:
    """
              Функция запроса API locations/v3/search

              Необходима для получения id Региона для последующих запросов

               :param dict headers: Заголовок HTTP для запроса к API
               :param dict q: Данные от пользователя
               :return: возвращает или id региона, или None
           """
    url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

    querystring = {'q': f'{q["country"]} {q["city"]}', 'locale': f'{q["locale"]}', 'siteid': f'{q["site_id"]}'}
    response = requests.get(url, headers=headers, params=querystring, timeout=20)
    if response.status_code == requests.codes.ok:
        result = response.json()
        if len(result['sr']) == 0:  # если в городе нет отелей доступных на сайте hotels.com(например Россия)
            return None
        else:
            return result['sr'][0]['gaiaId']


def post_hotel_detail(property_id: int, query: dict, hotel_data: dict, headers: dict) -> None:
    """
           Функция запроса API properties/v2/detail

           Необходима для получения галереи отеля и адреса

            :param dict headers: Заголовок HTTP для запроса к API
            :param dict hotel_data: словарь для данных об отеле
            :param dict query: Данные от пользователя
            :param int property_id: id Отеля на сайте Hotels.com
            :return: None
        """
    url = 'https://hotels4.p.rapidapi.com/properties/v2/detail'

    payload = {
        'currency': query['currency'],
        'eapid': query['eapid'],
        'locale': query['locale'],
        'siteId': query['site_id'],
        'propertyId': property_id
    }

    response = requests.post(url, json=payload, headers=headers, timeout=20)
    if response.status_code == requests.codes.ok:

        result = response.json()
        hotel_data['address_list'].append(
            result['data']['propertyInfo']['summary']['location']['address']['addressLine']
        )
        if query['photo']:
            photo_of_h = []
            for i in range(query['photo_amount']):
                photo_of_h.append(result['data']['propertyInfo']['propertyGallery']['images'][i]['image']['url'])
            hotel_data['photo_list'].append(photo_of_h)
    else:
        bot.send_message(query['chat_id'], 'Произошла ошибка при запросе')
        print('ошибка', response.status_code)
        bot.delete_state(query['user_id'], query['chat_id'])
        return None


def send_hotels_to_user(query: dict, data_about_hotels: dict) -> None:
    """
        Функция ответа пользователю

        Функция отправляет данные отелей пользователю в чат и вызывает функцию сохранения их в базу данных
        После удаляет состояние пользователя.
        :param dict data_about_hotels: Данные об отелях
        :param dict query: Данные от пользователя
        :return: None
    """
    bot.send_message(query['chat_id'], text='Список доступных отелей')
    for hotel in range(len(data_about_hotels['names_list'])):
        output_message = f'№{hotel + 1}\n' \
                         f'Название: {data_about_hotels["names_list"][hotel]}\n' \
                         f'Сайт отеля: {data_about_hotels["site_url"][hotel]}\n' \
                         f'Расстояние от центра: {data_about_hotels["distance_list"][hotel]}Км.\n' \
                         f'Цена за ночь: {data_about_hotels["price_list"][hotel]}\n' \
                         f'Адрес: {data_about_hotels["address_list"][hotel]}'
        bot.send_message(query['chat_id'], output_message)
        if query['photo']:
            for photo in range(len(data_about_hotels['photo_list'][hotel])):
                bot.send_photo(query['chat_id'], f'{data_about_hotels["photo_list"][hotel][photo]}')
    save_user(query_from_user=query, data_about_hotels=data_about_hotels)
    bot.delete_state(user_id=query['user_id'], chat_id=query['chat_id'])


def list_of_hotels(query: dict) -> None:
    """
        Функция основного запроса к API

        Функция вызывает функцию get_region_id и записывает полученный результат в переменную.
        Далее передаёт эту переменную и данные собранные с пользователя в функцию create_payload.
        И в зависимости от созданного payload производит запрос. Переводит полученные данные в json формат.
        Далее происходит парсинг json, и распределение данных по спискам внутри созданного словаря, и к каждому отелю
        выполняется дополнительных запрос вызовом функции post_hotel_detail.
        Вызывается функция send_hotels_to_user

        :param dict query: данные от пользователя
        :return: None
    """
    headers = {
        'X-RapidAPI-Key': f'{RAPID_API_KEY}',
        'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
    }

    region_id = get_region_id(q=query, headers=headers)

    if region_id is None:
        bot.send_message(query['chat_id'], 'К сожаление для данного региона ничего не найдено')
        bot.delete_state(query['user_id'], query['chat_id'])
        return None
    query['region_id'] = region_id

    payload = create_payload(query=query, region_id=region_id)

    url = 'https://hotels4.p.rapidapi.com/properties/v2/list'
    response = requests.post(url, json=payload, headers=headers, timeout=20)

    if response.status_code == requests.codes.ok:
        result = response.json()
        data_about_hotels = {
            'property_id_list': [],
            'names_list': [],
            'distance_list': [],
            'price_list': [],
            'address_list': [],
            'site_url': [],
            'photo_list': []

        }
        if query['sort_type'] == 'high_price':
            for hotel in range(-1, -(query['resultsSize']), -1):
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
                data_about_hotels['property_id_list'].append(property_id)

                data_about_hotels['site_url'].append(f'https://www.hotels.com/h{property_id}.Hotel-Information')

                post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels, headers=headers)

            send_hotels_to_user(query=query, data_about_hotels=data_about_hotels)

        elif query['sort_type'] == 'bestdeal':

            count_of_hotels = query['resultsSize']
            for hotel in range(len(result['data']['propertySearch']['properties'])):
                if count_of_hotels == 0:
                    break
                distance = \
                    result['data']['propertySearch']['properties'][hotel]['destinationInfo']['distanceFromDestination'][
                        'value']

                if query['min_distance'] <= distance <= query['max_distance']:
                    count_of_hotels -= 1
                    data_about_hotels['names_list'].append(
                        result['data']['propertySearch']['properties'][hotel]['name'])

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

                    post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels,
                                      headers=headers)
                else:
                    continue

            send_hotels_to_user(query=query, data_about_hotels=data_about_hotels)
        else:
            for hotel in range(len(result['data']['propertySearch']['properties'])):
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

                data_about_hotels['property_id_list'].append(property_id)
                data_about_hotels['site_url'].append(f'https://www.hotels.com/h{property_id}.Hotel-Information')

                post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels, headers=headers)

            send_hotels_to_user(query=query, data_about_hotels=data_about_hotels)
    else:
        bot.send_message(query['chat_id'], 'Произошла ошибка при запросе')
        print('ошибка', response.status_code)
        bot.delete_state(query['user_id'], query['chat_id'])
        return None


# number_in_list name price optional(photo max=3)
def create_payload(query: dict, region_id: int) -> dict:
    """
            Функция создания payload для API

            Функция собирает данные полученные от пользователя и подставляет их в JSON формат запроса
            :param int region_id: id региона
            :param dict query: данные полученные от пользователя
            :return: dict payload: данные для запроса в API
        """
    # PRICE_RELEVANT (Price + our picks)|REVIEW (Guest rating)|DISTANCE (Distance from downtown)|
    # PRICE_LOW_TO_HIGH (Price)|PROPERTY_CLASS (Star rating)|RECOMMENDED (Recommended) Виды сортировок
    if query['sort_type'] == 'high_price':
        hotel_filter = {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
        result_size = 200
    elif query['sort_type'] == 'low_price':
        hotel_filter = {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
        result_size = query['resultsSize']
    else:
        hotel_filter = {
            'availableFilter': 'SHOW_AVAILABLE_ONLY',
            'price': {
                'max': query['max_price'],
                'min': query['min_price']
            }
        }
        result_size = 200

    payload = {
        'currency': f'{query["currency"]}',
        'eapid': query["eapid"],
        'locale': f'{query["locale"]}',
        'siteId': query["site_id"],
        'destination': {
            'regionId': f'{region_id}'
        },
        'checkInDate': {
            'day': query['checkIn'].day,
            'month': query['checkIn'].month,
            'year': query['checkIn'].year
        },
        'checkOutDate': {
            'day': query['checkOut'].day,
            'month': query['checkOut'].month,
            'year': query['checkOut'].year
        },
        'rooms': query['rooms'],
        'resultsStartingIndex': 0,
        'resultsSize': result_size,
        'sort': query['sort'],
        'filters': hotel_filter
    }

    return payload
