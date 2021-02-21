import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_bitch)
            s.case('y', view_your_bitches)
            s.case('b', book_a_room)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a room')
    print('[A]dd a bitch')
    print('View [y]our bitch')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_bitch():
    print(' ****************** Add a bitch **************** ')
    if not state.active_account:
        error_msg("You must log in first to add a bitch")
        return

    name = input("What is your bitch's name? ")
    if not name:
        error_msg('cancelled')
        return

    functions = input("Functions? ")
    is_cruel = input("Is your bitch want cruel sex [y]es, [n]o? ").lower().startswith('y')

    bitch = svc.add_bitch(state.active_account, name, functions, is_cruel)
    state.reload_account()
    success_msg('Created {} with id {}'.format(bitch.name, bitch.id))


def view_your_bitches():
    print(' ****************** Your bitches **************** ')
    if not state.active_account:
        error_msg("You must log in first to view your snakes")
        return

    bitches = svc.get_bitches_for_user(state.active_account.id)
    print("You have {} bitches.".format(len(bitches)))
    for s in bitches:
        print(" * {} is a {} that is {}cruel.".format(
            s.name,
            s.functions,
            '' if s.is_cruel else 'not '
        ))


def book_a_room():
    print(' ****************** Book a room **************** ')
    if not state.active_account:
        error_msg("You must log in first to book a cage")
        return

    bitches = svc.get_bitches_for_user(state.active_account.id)
    if not bitches:
        error_msg('You must first [a]dd a bitch before you can book a room.')
        return

    print("Let's start by finding available rooms.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        error_msg('cancelled')
        return

    checkin = parser.parse(
        start_text
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(bitches):
        print('{}. {} (cruel: {})'.format(
            idx + 1,
            s.name,
            'yes' if s.is_cruel else 'no'
        ))

    bitch = bitches[int(input('Which bitch do you want to book (number)')) - 1]

    rooms = svc.get_available_rooms(checkin, checkout, bitch)

    print("There are {} rooms available in that time.".format(len(rooms)))
    for idx, c in enumerate(rooms):
        print(" {}. {} with {}m milf: {}, has instruments: {}.".format(
            idx + 1,
            c.name,
            'yes' if c.is_milf else 'no',
            'yes' if c.has_instruments else 'no'))

    if not rooms:
        error_msg("Sorry, no rooms are available for that date.")
        return

    room = rooms[int(input('Which room do you want to book (number)')) - 1]
    svc.book_room(state.active_account, bitch, room, checkin, checkout)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(room.name, bitches.name, room.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a room")
        return

    bitches = {s.id: s for s in svc.get_bitches_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        # noinspection PyUnresolvedReferences
        print(' * Bitch: {} is booked at {} from {} for {} days.'.format(
            bitches.get(b.guest_bitch_id).name,
            b.room.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
