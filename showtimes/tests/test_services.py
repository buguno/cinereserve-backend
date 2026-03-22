import pytest

from showtimes.services import (
    acquire_seat_lock,
    get_locked_seats,
    get_seat_lock_owner,
    get_seat_lock_ttl,
    release_seat_lock,
)


@pytest.mark.django_db
def test_acquire_seat_lock_sets_owner(showtime, seat, user):
    locked = acquire_seat_lock(showtime.id, seat.id, user.id)

    assert locked is True
    assert get_seat_lock_owner(showtime.id, seat.id) == str(user.id)


@pytest.mark.django_db
def test_acquire_seat_lock_rejects_second_owner(
    showtime, seat, user, another_user
):
    first_lock = acquire_seat_lock(showtime.id, seat.id, user.id)
    second_lock = acquire_seat_lock(showtime.id, seat.id, another_user.id)

    assert first_lock is True
    assert second_lock is False
    assert get_seat_lock_owner(showtime.id, seat.id) == str(user.id)


@pytest.mark.django_db
def test_get_seat_lock_ttl_returns_none_when_lock_does_not_exist(
    showtime, seat
):
    assert get_seat_lock_ttl(showtime.id, seat.id) is None


@pytest.mark.django_db
def test_get_seat_lock_ttl_returns_ttl_for_existing_lock(showtime, seat, user):
    acquire_seat_lock(showtime.id, seat.id, user.id)

    ttl = get_seat_lock_ttl(showtime.id, seat.id)

    assert ttl is not None
    assert ttl > 0


@pytest.mark.django_db
def test_release_seat_lock_succeeds_for_owner(showtime, seat, user):
    acquire_seat_lock(showtime.id, seat.id, user.id)

    released = release_seat_lock(showtime.id, seat.id, user.id)

    assert released is True
    assert get_seat_lock_owner(showtime.id, seat.id) is None


@pytest.mark.django_db
def test_release_seat_lock_fails_for_non_owner(
    showtime, seat, user, another_user
):
    acquire_seat_lock(showtime.id, seat.id, user.id)

    released = release_seat_lock(showtime.id, seat.id, another_user.id)

    assert released is False
    assert get_seat_lock_owner(showtime.id, seat.id) == str(user.id)


@pytest.mark.django_db
def test_get_locked_seats_returns_multiple_locks(
    showtime, seat, another_seat, user, another_user
):
    acquire_seat_lock(showtime.id, seat.id, user.id)
    acquire_seat_lock(showtime.id, another_seat.id, another_user.id)

    locked_seats = get_locked_seats(showtime.id)

    assert locked_seats == {
        seat.id: str(user.id),
        another_seat.id: str(another_user.id),
    }
