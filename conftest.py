from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from movies.models import Movie
from showtimes.models import Room, Seat, Showtime

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def user(faker):
    return User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password='StrongPassword123',
    )


@pytest.fixture
def another_user(faker):
    return User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password='StrongPassword123',
    )


@pytest.fixture
def movie(faker):
    return Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=120,
        release_date=faker.date_object(),
        is_active=True,
    )


@pytest.fixture
def room(faker):
    return Room.objects.create(
        name=faker.word(),
        capacity=20,
    )


@pytest.fixture
def seat(room):
    return Seat.objects.create(
        room=room,
        row='A',
        number=1,
    )


@pytest.fixture
def another_seat(room):
    return Seat.objects.create(
        room=room,
        row='A',
        number=2,
    )


@pytest.fixture
def showtime(movie, room):
    return Showtime.objects.create(
        movie=movie,
        room=room,
        start_time=timezone.now() + timedelta(days=1),
    )
