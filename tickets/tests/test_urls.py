import pytest
from django.test import override_settings
from rest_framework import status


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_api_root_includes_docs_links_in_debug(client):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == 'Welcome to CineReserve API'
    assert response.json()['docs'] == ['/docs/', '/redoc/']


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_api_root_hides_docs_links_outside_debug(client):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == 'Welcome to CineReserve API'
    assert 'docs' not in response.json()
