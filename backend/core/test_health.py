from django.db import OperationalError, connection
import pytest


@pytest.mark.django_db
def test_health_reports_ok(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_returns_503_when_database_is_down(client, monkeypatch):
    def broken_cursor():
        raise OperationalError("connection refused")

    monkeypatch.setattr(connection, "cursor", broken_cursor)
    response = client.get("/health/")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unreachable"}
