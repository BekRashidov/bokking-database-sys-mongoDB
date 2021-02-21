import datetime
import mongoengine

from data.bookings import Booking


class Room(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    is_milf = mongoengine.BooleanField(required=True)
    has_instruments = mongoengine.BooleanField(required=True)
    allow_deepthroat = mongoengine.BooleanField(default=False)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'rooms'
    }
