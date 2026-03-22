import pytest
from rest_framework import status

from movies.models import Movie
from showtimes.models import Showtime
from showtimes.services import acquire_seat_lock
from tickets.models import Ticket


@pytest.mark.django_db
def test_list_showtimes_returns_public_paginated_response(
    api_client,
    showtime,
):
    response = api_client.get('/api/showtimes/')

    assert response.status_code == status.HTTP_200_OK
    assert 'count' in response.data
    assert 'next' in response.data
    assert 'previous' in response.data
    assert 'results' in response.data
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == showtime.id


@pytest.mark.django_db
def test_list_showtimes_filters_by_movie(api_client, showtime, room, faker):
    other_movie = Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=100,
        release_date=faker.date_object(),
        is_active=True,
    )
    other_showtime = Showtime.objects.create(
        movie=other_movie,
        room=room,
        start_time=showtime.start_time,
    )

    response = api_client.get(f'/api/showtimes/?movie_id={showtime.movie.id}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == showtime.id
    assert response.data['results'][0]['id'] != other_showtime.id


@pytest.mark.django_db
def test_seat_map_returns_available_seats(
    api_client, showtime, seat, another_seat
):
    response = api_client.get(f'/api/showtimes/{showtime.id}/seat-map/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    first_seat = response.data[0]
    assert first_seat['status'] == 'available'
    assert first_seat['is_locked_by_me'] is False
    assert first_seat['lock_ttl_seconds'] is None


@pytest.mark.django_db
def test_seat_map_returns_reserved_seat_for_lock_owner(
    api_client,
    user,
    showtime,
    seat,
):
    api_client.force_authenticate(user=user)
    acquire_seat_lock(showtime.id, seat.id, user.id)

    response = api_client.get(f'/api/showtimes/{showtime.id}/seat-map/')

    assert response.status_code == status.HTTP_200_OK

    reserved_seat = next(
        item for item in response.data if item['seat_id'] == seat.id
    )
    assert reserved_seat['status'] == 'reserved'
    assert reserved_seat['is_locked_by_me'] is True
    assert reserved_seat['lock_ttl_seconds'] is not None


@pytest.mark.django_db
def test_seat_map_returns_reserved_seat_for_other_user(
    api_client,
    user,
    another_user,
    showtime,
    seat,
):
    acquire_seat_lock(showtime.id, seat.id, user.id)
    api_client.force_authenticate(user=another_user)

    response = api_client.get(f'/api/showtimes/{showtime.id}/seat-map/')

    assert response.status_code == status.HTTP_200_OK

    reserved_seat = next(
        item for item in response.data if item['seat_id'] == seat.id
    )
    assert reserved_seat['status'] == 'reserved'
    assert reserved_seat['is_locked_by_me'] is False
    assert reserved_seat['lock_ttl_seconds'] is not None


@pytest.mark.django_db
def test_seat_map_returns_purchased_seat(
    api_client,
    user,
    showtime,
    seat,
):
    Ticket.objects.create(
        user=user,
        showtime=showtime,
        seat=seat,
    )

    response = api_client.get(f'/api/showtimes/{showtime.id}/seat-map/')

    assert response.status_code == status.HTTP_200_OK

    purchased_seat = next(
        item for item in response.data if item['seat_id'] == seat.id
    )
    assert purchased_seat['status'] == 'purchased'
    assert purchased_seat['is_locked_by_me'] is False
    assert purchased_seat['lock_ttl_seconds'] is None


@pytest.mark.django_db
def test_reserve_seat_requires_authentication(api_client, showtime, seat):
    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_reserve_seat_successfully(api_client, user, showtime, seat):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Seat reserved successfully.'
    assert response.data['showtime_id'] == showtime.id
    assert response.data['seat_id'] == seat.id
    assert response.data['lock_ttl_seconds'] is not None


@pytest.mark.django_db
def test_reserve_seat_rejects_already_purchased_seat(
    api_client,
    user,
    showtime,
    seat,
):
    Ticket.objects.create(
        user=user,
        showtime=showtime,
        seat=seat,
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data['detail'] == 'This seat has already been purchased.'


@pytest.mark.django_db
def test_reserve_seat_rejects_locked_seat_from_another_user(
    api_client,
    user,
    another_user,
    showtime,
    seat,
):
    acquire_seat_lock(showtime.id, seat.id, user.id)
    api_client.force_authenticate(user=another_user)

    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data['detail'] == 'This seat is temporarily reserved.'
    assert response.data['locked_by_me'] is False
    assert response.data['lock_ttl_seconds'] is not None


@pytest.mark.django_db
def test_reserve_seat_reports_lock_owned_by_same_user(
    api_client,
    user,
    showtime,
    seat,
):
    acquire_seat_lock(showtime.id, seat.id, user.id)
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data['detail'] == 'This seat is temporarily reserved.'
    assert response.data['locked_by_me'] is True
    assert response.data['lock_ttl_seconds'] is not None


@pytest.mark.django_db
def test_reserve_seat_rejects_seat_from_another_room(
    api_client,
    user,
    showtime,
    faker,
):
    from showtimes.models import Room, Seat

    other_room = Room.objects.create(
        name=faker.word(),
        capacity=10,
    )
    foreign_seat = Seat.objects.create(
        room=other_room,
        row='B',
        number=1,
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        f'/api/showtimes/{showtime.id}/reserve-seat/',
        {'seat_id': foreign_seat.id},
        format='json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
