from loader import bot
import requests
from config_data.config import RAPID_API_KEY


def get_region_id(q: dict, headers):  # 1 шаг получаем id региона он же gaia id по запросу Страна + Город
    url = 'https://hotels4.p.rapidapi.com/locations/v3/search'

    querystring = {'q': f'{q["country"]} {q["city"]}', 'locale': f'{q["locale"]}', 'siteid': f'{q["site_id"]}'}
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    if response.status_code == requests.codes.ok:
        result = response.json()
        if len(result['sr']) == 0:  # если в городе нет отелей доступных на сайте hotels.com(например Россия)
            return None
        else:
            return result['sr'][0]['gaiaId']


def post_hotel_detail(property_id: int, query: dict, hotel_data: dict, headers: dict):
    url = 'https://hotels4.p.rapidapi.com/properties/v2/detail'

    payload = {
        'currency': query['currency'],
        'eapid': query['eapid'],
        'locale': query['locale'],
        'siteId': query['site_id'],
        'propertyId': property_id
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
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


def send_hotels_to_user(query, data_about_hotels: dict):
    print(data_about_hotels)
    for hotel in range(len(data_about_hotels['names_list'])):
        output_message = f'№{hotel + 1}\n' \
                         f'Название: {data_about_hotels["names_list"][hotel]}\n' \
                         f'Сайт отеля: {data_about_hotels["site_url"][hotel]}\n' \
                         f'Расстояние от центра: {data_about_hotels["distance_list"][hotel]}Км.\n' \
                         f'Цена за ночь: {data_about_hotels["price_list"][hotel]}\n' \
                         f'Адрес: {data_about_hotels["address_list"][hotel]}'
        bot.send_message(query['chat_id'], output_message)
        for photo in range(len(data_about_hotels['photo_list'][hotel])):
            bot.send_photo(query['chat_id'], f'{data_about_hotels["photo_list"][hotel][photo]}')
    bot.delete_state(user_id=query['user_id'], chat_id=query['chat_id'])


def list_of_hotels(query: dict):
    headers = {
        'X-RapidAPI-Key': f'{RAPID_API_KEY}',
        'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
    }

    region_id = get_region_id(q=query, headers=headers)
    print(region_id)
    payload = create_payload(query=query, region_id=region_id)

    print(payload)

    url = 'https://hotels4.p.rapidapi.com/properties/v2/list'
    response = requests.post(url, json=payload, headers=headers, timeout=10)

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
        if query['sort_type'] == 'high':
            for hotel in range(-1, -query['resultsSize'], -1):
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

                post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels, headers=headers)

            send_hotels_to_user(query=query, data_about_hotels=data_about_hotels)
        else:
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

                post_hotel_detail(property_id=property_id, query=query, hotel_data=data_about_hotels, headers=headers)

            send_hotels_to_user(query=query, data_about_hotels=data_about_hotels)
    else:
        print('ошибка')


# number_in_list name price optional(photo max=3)
def create_payload(query: dict, region_id: int) -> dict:
    # PRICE_RELEVANT (Price + our picks)|REVIEW (Guest rating)|DISTANCE (Distance from downtown)|
    # PRICE_LOW_TO_HIGH (Price)|PROPERTY_CLASS (Star rating)|RECOMMENDED (Recommended) Виды сортировок
    if query['sort_type'] == 'high':
        result_size = 200
    else:
        result_size = query['resultsSize']
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
        'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
    }

    return payload
