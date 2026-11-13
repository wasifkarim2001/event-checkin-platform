import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def register(client, ticket_type, n):
    return client.post(
        f"/api/public/events/{ticket_type.event.pk}/register/",
        {"ticket_type": ticket_type.pk, "name": f"Guest {n}", "email": f"guest{n}@example.com"},
        format="json",
    )


def test_registration_is_limited_to_20_per_hour_per_ip(ticket_type):
    client = APIClient()
    assert all(register(client, ticket_type, n).status_code == 201 for n in range(20))
    response = register(client, ticket_type, 20)
    assert response.status_code == 429
    assert int(response["Retry-After"]) > 0


def test_login_is_limited_to_5_per_minute_per_ip(organizer):
    client = APIClient()
    wrong = {"username": "organizer", "password": "wrong"}
    assert [client.post("/api/auth/token/", wrong).status_code for _ in range(5)] == [400] * 5
    right = {"username": "organizer", "password": "unused"}
    assert client.post("/api/auth/token/", right).status_code == 429


def test_limit_is_per_client_ip(organizer):
    wrong = {"username": "organizer", "password": "wrong"}
    for _ in range(5):
        APIClient(REMOTE_ADDR="10.0.0.1").post("/api/auth/token/", wrong)
    other = APIClient(REMOTE_ADDR="10.0.0.2").post("/api/auth/token/", wrong)
    assert other.status_code == 400


def test_spoofed_forwarded_for_does_not_reset_the_limit(organizer):
    wrong = {"username": "organizer", "password": "wrong"}
    for n in range(5):
        APIClient(HTTP_X_FORWARDED_FOR=f"203.0.113.{n}").post("/api/auth/token/", wrong)
    response = APIClient(HTTP_X_FORWARDED_FOR="203.0.113.99").post("/api/auth/token/", wrong)
    assert response.status_code == 429
