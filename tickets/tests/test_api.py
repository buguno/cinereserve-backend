from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status

from showtimes.models import Room, Seat, Showtime
from showtimes.services import acquire_seat_lock, get_seat_lock_owner
from tickets.models import Ticket


@pytest.mark.django_db
def test_my_tickets_requires_authentication(api_client):
    response = api_client.get('/api/tickets/my-tickets/')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_my_tickets_lists_only_authenticated_user_tickets(
    api_client,
    user,
    another_user,
    showtime,
    seat,
    another_seat,
):
    own_ticket = Ticket.objects.create(
        user=user,
        showtime=showtime,
        seat=seat,
    )
    Ticket.objects.create(
        user=another_user,
        showtime=showtime,
        seat=another_seat,
    )

    api_client.force_authenticate(user=user)
    response = api_client.get('/api/tickets/my-tickets/')

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == own_ticket.id


@pytest.mark.django_db
def test_my_tickets_does_not_allow_post(api_client, user, showtime, seat):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/my-tickets/',
        {
            'showtime': showtime.id,
            'seat': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_checkout_requires_authentication(api_client, showtime, seat):
    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': showtime.id,
            'seat_id': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_checkout_rejects_without_valid_lock(api_client, user, showtime, seat):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': showtime.id,
            'seat_id': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.data['detail']
        == 'You do not hold a valid lock for this seat.'
    )


@pytest.mark.django_db
def test_checkout_rejects_lock_owned_by_another_user(
    api_client,
    user,
    another_user,
    showtime,
    seat,
):
    acquire_seat_lock(showtime.id, seat.id, another_user.id)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': showtime.id,
            'seat_id': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.data['detail']
        == 'You do not hold a valid lock for this seat.'
    )


@pytest.mark.django_db
def test_checkout_rejects_past_showtime(api_client, user, movie, room, seat):
    past_showtime = Showtime.objects.create(
        movie=movie,
        room=room,
        start_time=timezone.now() - timedelta(hours=1),
    )
    acquire_seat_lock(past_showtime.id, seat.id, user.id)

    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': past_showtime.id,
            'seat_id': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data['detail'] == 'You cannot buy tickets for past showtimes.'
    )


@pytest.mark.django_db
def test_checkout_creates_ticket_releases_lock_and_schedules_email(
    api_client,
    user,
    showtime,
    seat,
    django_capture_on_commit_callbacks,
):
    acquire_seat_lock(showtime.id, seat.id, user.id)
    api_client.force_authenticate(user=user)

    with patch(
        'tickets.services.send_ticket_confirmation_email.delay'
    ) as mocked_delay:
        with django_capture_on_commit_callbacks(execute=True) as callbacks:
            response = api_client.post(
                '/api/tickets/checkout/',
                {
                    'showtime_id': showtime.id,
                    'seat_id': seat.id,
                },
                format='json',
            )

    assert response.status_code == status.HTTP_201_CREATED
    assert Ticket.objects.filter(
        user=user,
        showtime=showtime,
        seat=seat,
    ).exists()

    ticket = Ticket.objects.get(user=user, showtime=showtime, seat=seat)

    assert get_seat_lock_owner(showtime.id, seat.id) is None
    assert len(callbacks) == 1
    mocked_delay.assert_called_once_with(ticket.id)


@pytest.mark.django_db
def test_checkout_rejects_already_purchased_seat_even_with_lock(
    api_client,
    user,
    another_user,
    showtime,
    seat,
):
    Ticket.objects.create(
        user=another_user,
        showtime=showtime,
        seat=seat,
    )
    acquire_seat_lock(showtime.id, seat.id, user.id)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': showtime.id,
            'seat_id': seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data['detail'] == 'This seat has already been purchased.'


@pytest.mark.django_db
def test_checkout_rejects_seat_from_another_room(
    api_client,
    user,
    showtime,
    faker,
):
    other_room = Room.objects.create(
        name=faker.word(),
        capacity=10,
    )
    foreign_seat = Seat.objects.create(
        room=other_room,
        row='B',
        number=1,
    )

    acquire_seat_lock(showtime.id, foreign_seat.id, user.id)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/tickets/checkout/',
        {
            'showtime_id': showtime.id,
            'seat_id': foreign_seat.id,
        },
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
