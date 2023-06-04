import datetime

from peewee import *

db = SqliteDatabase('HotelFinderUsers.db')


class BaseModel(Model):
    class Meta:
        database = db  # соединение с базой, из шаблона выше


class History(BaseModel):
    id = PrimaryKeyField(unique=True)
    user_id = IntegerField()
    date = DateTimeField(default=datetime.datetime.now)
    country = TextField()
    city = TextField()
    check_in = DateTimeField()
    check_out = DateTimeField()
    command = TextField()

    class Meta:
        db_table = 'History'


class Hotel(BaseModel):
    id = PrimaryKeyField()
    history_id = ForeignKeyField(History)
    hotel_name = TextField()
    distance = FloatField()
    price = IntegerField()
    address = TextField()
    site = TextField()

    class Meta:
        db_table = 'Hotels'






