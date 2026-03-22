from django.db import IntegrityError, transaction

from showtimes.models import Seat, Showtime
from showtimes.services import get_seat_lock_owner, release_seat_lock
from tickets.models import Ticket
from tickets.tasks import send_ticket_confirmation_email
from users.models import User


class CheckoutError(Exception):
    pass


def checkout_ticket(*, showtime: Showtime, seat: Seat, user: User) -> Ticket:
    lock_owner = get_seat_lock_owner(showtime.id, seat.id)

    if lock_owner != str(user.id):
        raise CheckoutError('You do not hold a valid lock for this seat.')

    try:
        with transaction.atomic():
            ticket = Ticket.objects.create(
                user=user,
                showtime=showtime,
                seat=seat,
            )

            transaction.on_commit(
                lambda: send_ticket_confirmation_email.delay(ticket.id)
            )
    except IntegrityError as exc:
        raise CheckoutError('This seat has already been purchased.') from exc

    release_seat_lock(showtime.id, seat.id, user.id)

    return ticket
