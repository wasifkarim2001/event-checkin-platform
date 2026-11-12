import threading
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone
from rest_framework.exceptions import APIException

from . import services
from .models import Attendee, TicketType

pytestmark = pytest.mark.django_db


def register(api_as, event, **data):
    return api_as().post(f"/api/public/events/{event.pk}/register/", data, format="json")


def test_public_event_shows_remaining_seats(api_as, attendee):
    event = attendee.ticket_type.event
    response = api_as().get(f"/api/public/events/{event.pk}/")
    assert response.status_code == 200
    assert response.json()["ticket_types"][0]["remaining"] == 99


def test_anonymous_registration_returns_code(api_as, ticket_type):
    response = register(api_as, ticket_type.event, ticket_type=ticket_type.pk, name="Ada", email="ada@example.com")
    assert response.status_code == 201
    assert response.json()["code"] == Attendee.objects.get().code


def test_same_email_on_another_ticket_type_of_same_event_is_409(api_as, attendee):
    event = attendee.ticket_type.event
    vip = TicketType.objects.create(event=event, name="VIP", capacity=5)
    response = register(api_as, event, ticket_type=vip.pk, name="Ada", email="ADA@example.com")
    assert response.status_code == 409


def test_sold_out_is_409(api_as, event):
    tt = TicketType.objects.create(event=event, name="Tiny", capacity=1)
    assert register(api_as, event, ticket_type=tt.pk, name="A", email="a@example.com").status_code == 201
    response = register(api_as, event, ticket_type=tt.pk, name="B", email="b@example.com")
    assert response.status_code == 409
    assert "sold out" in response.json()["detail"]


def test_ticket_type_from_another_event_is_400(api_as, ticket_type, organizer):
    other = ticket_type.event
    other.pk = None
    other.save()
    response = register(api_as, other, ticket_type=ticket_type.pk, name="A", email="a@example.com")
    assert response.status_code == 400


def test_ended_event_is_400(api_as, ticket_type):
    event = ticket_type.event
    event.starts_at = timezone.now() - timedelta(days=2)
    event.ends_at = timezone.now() - timedelta(days=1)
    event.save()
    response = register(api_as, event, ticket_type=ticket_type.pk, name="A", email="a@example.com")
    assert response.status_code == 400


def test_unknown_event_is_404(api_as):
    response = api_as().post("/api/public/events/999/register/", {"ticket_type": 1, "name": "A", "email": "a@example.com"})
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_concurrent_registrations_never_exceed_capacity(event):
    tt = TicketType.objects.create(event=event, name="Last seat", capacity=1)
    barrier = threading.Barrier(2)
    results = []

    def attempt(i):
        try:
            barrier.wait()
            services.register_attendee(event.pk, tt.pk, f"P{i}", f"p{i}@example.com")
            results.append(201)
        except APIException as exc:
            results.append(exc.status_code)
        finally:
            connection.close()

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(results) == [201, 409]
    assert tt.attendees.count() == 1
