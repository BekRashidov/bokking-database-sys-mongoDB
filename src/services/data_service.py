from typing import List, Optional

import datetime

import bson

from data.bookings import Booking
from data.rooms import Room
from data.bookers import Owner
from data.bitches import Bitch


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_room(active_account: Owner,
                  name, allow_deepthroat, has_instruments, milf,
                  price) -> Room:
    room = Room()

    room.name = name
    room.is_milf = milf
    room.has_instruments = has_instruments
    room.allow_deepthroat = allow_deepthroat
    room.price = price

    room.save()

    account = find_account_by_email(active_account.email)
    account.room_ids.append(room.id)
    account.save()

    return room


def find_rooms_for_user(account: Owner) -> List[Room]:
    query = Room.objects(id__in=account.room_ids)
    rooms = list(query)

    return rooms


def add_available_date(room: Room,
                       start_date: datetime.datetime, days: int) -> Room:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    room = Room.objects(id=room.id).first()
    room.bookings.append(booking)
    room.save()

    return room


def add_bitch(account, name, functions, is_cruel) -> Bitch:
    bitch = Bitch()
    bitch.name = name
    bitch.functions = functions
    bitch.is_cruel = is_cruel
    bitch.save()

    owner = find_account_by_email(account.email)
    owner.bitch_ids.append(bitch.id)
    owner.save()

    return bitch


def get_bitches_for_user(user_id: bson.ObjectId) -> List[Bitch]:
    owner = Owner.objects(id=user_id).first()
    bitches = Bitch.objects(id__in=owner.bitch_ids).all()

    return list(bitches)


def get_available_rooms(checkin: datetime.datetime,
                        checkout: datetime.datetime, bitch: Bitch) -> List[Room]:

    query = Room.objects() \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if bitch.is_cruel:
        query = query.filter(allow_deepthroat=True)

    rooms = query.order_by('price')

    final_rooms = []
    for c in rooms:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
                final_rooms.append(c)

    return final_rooms


def book_room(account, bitch, room, checkin, checkout):
    booking: Optional[Booking] = None

    for b in room.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_bitch_id = bitch.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    room.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_rooms = Room.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_room_to_booking(room, booking):
        booking.room = room
        return booking

    bookings = [
        map_room_to_booking(room, booking)
        for room in booked_rooms
        for booking in room.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
