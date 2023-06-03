from telebot.handler_backends import State, StatesGroup

# страна город количествоотелей фото кол-вофото кол-вокомнат взрослых детей возрастдетей дата1 дата2


class UserInfoState(StatesGroup):
    history = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    country = State()
    city = State()
    hotels_amount = State()
    photo = State()
    photos_amount = State()
    rooms_amount = State()
    adults_amount = State()
    children_amount = State()
    age_of_child = State()
    check_in_date = State()
    check_out_date = State()
    waiting_for_r = State()
