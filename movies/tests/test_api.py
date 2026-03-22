from datetime import date, timedelta

import pytest
from rest_framework import status

from movies.models import Movie


@pytest.mark.django_db
def test_list_movies_returns_only_active_movies(api_client, faker):
    active_movie = Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=120,
        release_date=date.today(),
        is_active=True,
    )
    Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=90,
        release_date=date.today() + timedelta(days=1),
        is_active=False,
    )

    response = api_client.get('/api/movies/')

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == active_movie.id


@pytest.mark.django_db
def test_list_movies_is_public(api_client, movie):
    response = api_client.get('/api/movies/')

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data


@pytest.mark.django_db
def test_list_movies_is_ordered_by_release_date(api_client, faker):
    older_movie = Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=100,
        release_date=date.today(),
        is_active=True,
    )
    newer_movie = Movie.objects.create(
        title=faker.sentence(nb_words=3),
        description=faker.text(),
        duration_minutes=110,
        release_date=date.today() + timedelta(days=10),
        is_active=True,
    )

    response = api_client.get('/api/movies/')

    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']

    assert results[0]['id'] == older_movie.id
    assert results[1]['id'] == newer_movie.id


@pytest.mark.django_db
def test_list_movies_returns_paginated_response(api_client, faker):
    for index in range(12):
        Movie.objects.create(
            title=f'Movie {index}',
            description=faker.text(),
            duration_minutes=100 + index,
            release_date=date.today() + timedelta(days=index),
            is_active=True,
        )

    response = api_client.get('/api/movies/')

    assert response.status_code == status.HTTP_200_OK
    assert 'count' in response.data
    assert 'next' in response.data
    assert 'previous' in response.data
    assert 'results' in response.data
    assert len(response.data['results']) == 10


@pytest.mark.django_db
def test_list_movies_uses_cached_response(api_client, faker):
    first_movie = Movie.objects.create(
        title='First movie',
        description=faker.text(),
        duration_minutes=100,
        release_date=date.today(),
        is_active=True,
    )

    first_response = api_client.get('/api/movies/')

    assert first_response.status_code == status.HTTP_200_OK
    assert first_response.data['results'][0]['id'] == first_movie.id

    Movie.objects.create(
        title='Second movie',
        description=faker.text(),
        duration_minutes=120,
        release_date=date.today() + timedelta(days=1),
        is_active=True,
    )

    second_response = api_client.get('/api/movies/')

    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.data == first_response.data
