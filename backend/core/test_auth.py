from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def login(client):
    return client.post("/api/auth/token/", {"username": "organizer", "password": "unused"})


def age_token(token, hours):
    Token.objects.filter(pk=token.pk).update(created=timezone.now() - timedelta(hours=hours))


def client_with(token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


def test_expired_token_is_rejected_and_deleted(organizer, settings):
    token = Token.objects.create(user=organizer)
    age_token(token, settings.TOKEN_TTL_HOURS + 1)
    response = client_with(token).get("/api/events/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired."
    assert not Token.objects.filter(pk=token.pk).exists()


def test_token_just_inside_its_lifetime_still_works(organizer, settings):
    token = Token.objects.create(user=organizer)
    age_token(token, settings.TOKEN_TTL_HOURS - 1)
    assert client_with(token).get("/api/events/").status_code == 200


def test_login_reuses_a_valid_token_and_replaces_an_expired_one(organizer, settings):
    client = APIClient()
    first = login(client).json()["token"]
    assert login(client).json()["token"] == first

    age_token(Token.objects.get(key=first), settings.TOKEN_TTL_HOURS + 1)
    assert login(client).json()["token"] != first


def test_login_works_even_when_a_stale_token_is_sent(organizer, settings):
    token = Token.objects.create(user=organizer)
    age_token(token, settings.TOKEN_TTL_HOURS + 1)
    assert login(client_with(token)).status_code == 200


def test_logout_deletes_the_token(organizer):
    token = Token.objects.create(user=organizer)
    client = client_with(token)
    assert client.post("/api/auth/logout/").status_code == 204
    assert client.get("/api/events/").status_code == 401


def test_logout_requires_a_token():
    assert APIClient().post("/api/auth/logout/").status_code == 401
