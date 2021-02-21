import datetime
import mongoengine


class Bitch(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    functions = mongoengine.StringField(required=True)

    name = mongoengine.StringField(required=True)
    is_cruel = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'bitches'
    }
