from unittest.mock import patch

import pytest

from tickets.models import Ticket
from tickets.tasks import send_ticket_confirmation_email


@pytest.mark.django_db
@patch('tickets.tasks.send_mail')
def test_send_ticket_confirmation_email_calls_send_mail(
    mocked_send_mail,
    user,
    showtime,
    seat,
):
    ticket = Ticket.objects.create(
        user=user,
        showtime=showtime,
        seat=seat,
    )

    send_ticket_confirmation_email(ticket.id)

    mocked_send_mail.assert_called_once()
    _, kwargs = mocked_send_mail.call_args

    assert kwargs['recipient_list'] == [user.email]
    assert kwargs['from_email'] is None
    assert kwargs['fail_silently'] is False
    assert 'CineReserve' in kwargs['subject']
    assert showtime.movie.title in kwargs['message']
    assert str(seat) in kwargs['message']
