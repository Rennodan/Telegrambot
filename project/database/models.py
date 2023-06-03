from peewee import *

db = SqliteDatabase('HotelFinderUsers.db')


class BaseModel(Model):
    class Meta:
        database = db  # соединение с базой, из шаблона выше


class User(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField()
    name = CharField()
    chat_id = IntegerField()

    class Meta:
        db_table = 'Users'


class RequestHotel(BaseModel):
    id = PrimaryKeyField()
    user_id = ForeignKeyField(User, related_name='requests')
    region_id = IntegerField()
    country = CharField()
    city = CharField()
    sort_type = CharField()
    hotel_amount = IntegerField()
    check_in = DateField()
    check_out = DateField()

    class Meta:
        db_table = 'Requests_of_hotels'

class Hotel(BaseModel):
    id = PrimaryKeyField()
    hotel_id = IntegerField()
    name = CharField()
    distance = FloatField()
    price = IntegerField()
    address = CharField()
    site = CharField()

    class Meta:
        db_table = 'Hotels'

class Request2Hotel(BaseModel):
    id = PrimaryKeyField()
    request_id = ForeignKeyField(RequestHotel, related_name='hotels')
    hotel_id = ForeignKeyField(Hotel, related_name='hotel')
    class Meta:
        db_table = 'Request2Hotels'





if __name__ == '__main__':
    db.create_tables([User, RequestHotel, Request2Hotel, Hotel])

