from datetime import timedelta

import pytest
from rest_framework.test import APIClient

from .models import Attendee, Event, TicketType

pytestmark = pytest.mark.django_db


def event_payload(**overrides):
    return {
        "name": "PyCon",
        "venue": "Hall A",
        "starts_at": "2030-05-01T09:00:00Z",
        "ends_at": "2030-05-01T17:00:00Z",
        **overrides,
    }


def test_token_login_then_authenticated_request(organizer):
    client = APIClient()
    assert client.get("/api/events/").status_code == 401

    response = client.post("/api/auth/token/", {"username": "organizer", "password": "unused"})
    assert response.status_code == 200
    client.credentials(HTTP_AUTHORIZATION=f"Token {response.json()['token']}")
    assert client.get("/api/events/").status_code == 200


def test_create_event_sets_owner(api_as, organizer):
    response = api_as(organizer).post("/api/events/", event_payload(), format="json")
    assert response.status_code == 201
    assert response.json()["owner"] == "organizer"


def test_event_must_end_after_it_starts(api_as, organizer):
    payload = event_payload(ends_at="2030-05-01T08:00:00Z")
    response = api_as(organizer).post("/api/events/", payload, format="json")
    assert response.status_code == 400
    assert "ends_at" in response.json()


def test_list_shows_only_owned_and_staffed_events(api_as, event, staff_user, outsider):
    Event.objects.create(owner=outsider, name="Other", starts_at=event.starts_at, ends_at=event.ends_at)

    names = [e["name"] for e in api_as(staff_user).get("/api/events/").json()["results"]]
    assert names == ["DevConf"]


def test_outsider_gets_404_not_403(api_as, event, outsider):
    assert api_as(outsider).get(f"/api/events/{event.pk}/").status_code == 404


def test_staff_can_read_but_not_edit(api_as, event, staff_user):
    client = api_as(staff_user)
    assert client.get(f"/api/events/{event.pk}/").status_code == 200
    response = client.patch(f"/api/events/{event.pk}/", {"name": "Hacked"}, format="json")
    assert response.status_code == 403


def test_owner_assigns_staff_by_username(api_as, event, outsider):
    response = api_as(event.owner).patch(
        f"/api/events/{event.pk}/", {"staff": ["outsider"]}, format="json"
    )
    assert response.status_code == 200
    assert list(event.staff.all()) == [outsider]


def test_owner_creates_ticket_type(api_as, event):
    payload = {"event": event.pk, "name": "VIP", "capacity": 10}
    response = api_as(event.owner).post("/api/ticket-types/", payload, format="json")
    assert response.status_code == 201


def test_duplicate_ticket_type_name_is_400(api_as, ticket_type):
    payload = {"event": ticket_type.event_id, "name": ticket_type.name, "capacity": 5}
    response = api_as(ticket_type.event.owner).post("/api/ticket-types/", payload, format="json")
    assert response.status_code == 400


def test_staff_cannot_create_ticket_types(api_as, event, staff_user):
    payload = {"event": event.pk, "name": "VIP", "capacity": 10}
    response = api_as(staff_user).post("/api/ticket-types/", payload, format="json")
    assert response.status_code == 400


def test_capacity_cannot_drop_below_registrations(api_as, attendee):
    tt = attendee.ticket_type
    Attendee.objects.create(ticket_type=tt, name="Bob", email="bob@example.com")
    response = api_as(tt.event.owner).patch(f"/api/ticket-types/{tt.pk}/", {"capacity": 1}, format="json")
    assert response.status_code == 400


def test_ticket_type_cannot_move_to_another_event(api_as, ticket_type):
    owner = ticket_type.event.owner
    start = ticket_type.event.starts_at + timedelta(days=30)
    other = Event.objects.create(owner=owner, name="Other", starts_at=start, ends_at=start + timedelta(hours=1))
    response = api_as(owner).patch(
        f"/api/ticket-types/{ticket_type.pk}/", {"event": other.pk}, format="json"
    )
    assert response.status_code == 400


def test_ticket_type_with_registrations_cannot_be_deleted(api_as, attendee):
    tt = attendee.ticket_type
    assert api_as(tt.event.owner).delete(f"/api/ticket-types/{tt.pk}/").status_code == 409


def test_empty_ticket_type_can_be_deleted(api_as, ticket_type):
    response = api_as(ticket_type.event.owner).delete(f"/api/ticket-types/{ticket_type.pk}/")
    assert response.status_code == 204
    assert not TicketType.objects.exists()


def test_openapi_schema_and_docs_are_served(client):
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/docs/").status_code == 200
