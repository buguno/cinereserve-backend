import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_register_user_successfully(api_client, faker):
    payload = {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': 'StrongPassword123',
    }

    response = api_client.post('/api/users/register/', payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email=payload['email']).exists()

    user = User.objects.get(email=payload['email'])
    assert user.username == payload['username']
    assert user.check_password(payload['password'])


@pytest.mark.django_db
def test_register_user_rejects_weak_password(api_client, faker):
    payload = {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': '123',
    }

    response = api_client.post('/api/users/register/', payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data
    assert not User.objects.filter(email=payload['email']).exists()


@pytest.mark.django_db
def test_register_user_rejects_duplicate_email(api_client, user, faker):
    payload = {
        'username': faker.user_name(),
        'email': user.email,
        'password': 'StrongPassword123',
    }

    response = api_client.post('/api/users/register/', payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_obtain_jwt_token_successfully(api_client, user):
    payload = {
        'username': user.username,
        'password': 'StrongPassword123',
    }

    response = api_client.post('/api/users/token/', payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_obtain_jwt_token_rejects_invalid_credentials(api_client, user):
    payload = {
        'username': user.username,
        'password': 'wrong-password',
    }

    response = api_client.post('/api/users/token/', payload, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_jwt_token_successfully(api_client, user):
    token_response = api_client.post(
        '/api/users/token/',
        {
            'username': user.username,
            'password': 'StrongPassword123',
        },
        format='json',
    )

    response = api_client.post(
        '/api/users/token/refresh/',
        {'refresh': token_response.data['refresh']},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data


@pytest.mark.django_db
def test_register_endpoint_is_rate_limited(api_client, faker):
    for _ in range(5):
        response = api_client.post(
            '/api/users/register/',
            {
                'username': faker.user_name(),
                'email': faker.email(),
                'password': 'StrongPassword123',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED

    response = api_client.post(
        '/api/users/register/',
        {
            'username': faker.user_name(),
            'email': faker.email(),
            'password': 'StrongPassword123',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_login_endpoint_is_rate_limited(api_client, user):
    for _ in range(5):
        response = api_client.post(
            '/api/users/token/',
            {
                'username': user.username,
                'password': 'StrongPassword123',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK

    response = api_client.post(
        '/api/users/token/',
        {
            'username': user.username,
            'password': 'StrongPassword123',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
