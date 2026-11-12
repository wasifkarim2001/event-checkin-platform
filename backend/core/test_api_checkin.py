import pytest

from .models import Attendee, CheckIn, Event, TicketType

pytestmark = pytest.mark.django_db


def check_in(client, event, code):
    return client.post(f"/api/events/{event.pk}/checkins/", {"code": code}, format="json")


def test_staff_checks_in_by_code_ignoring_case_and_spaces(api_as, attendee, staff_user):
    event = attendee.ticket_type.event
    response = check_in(api_as(staff_user), event, f"  {attendee.code.lower()} ")
    assert response.status_code == 201
    assert response.json()["checked_in_by"] == "staff"
    assert response.json()["attendee"]["code"] == attendee.code


def test_second_checkin_is_409_with_original_time(api_as, attendee, staff_user):
    event = attendee.ticket_type.event
    client = api_as(staff_user)
    first = check_in(client, event, attendee.code)
    second = check_in(client, event, attendee.code)
    assert second.status_code == 409
    assert second.json()["checked_in_at"] == first.json()["checked_in_at"]
    assert CheckIn.objects.count() == 1


def test_unknown_code_is_404(api_as, event, staff_user):
    assert check_in(api_as(staff_user), event, "NOPE2345").status_code == 404


def test_code_from_another_event_is_404(api_as, attendee, staff_user):
    event = attendee.ticket_type.event
    other = Event.objects.create(owner=event.owner, name="Other", starts_at=event.starts_at, ends_at=event.ends_at)
    other.staff.add(staff_user)
    assert check_in(api_as(staff_user), other, attendee.code).status_code == 404


def test_outsider_cannot_check_in(api_as, attendee, outsider):
    event = attendee.ticket_type.event
    assert check_in(api_as(outsider), event, attendee.code).status_code == 404


@pytest.fixture
def crowd(ticket_type):
    vip = TicketType.objects.create(event=ticket_type.event, name="VIP", capacity=5)
    people = [
        Attendee.objects.create(ticket_type=ticket_type, name="Ada", email="ada@example.com"),
        Attendee.objects.create(ticket_type=ticket_type, name="Bob", email="bob@example.com"),
        Attendee.objects.create(ticket_type=vip, name="Cy", email="cy@example.com"),
    ]
    CheckIn.objects.create(attendee=people[0])
    CheckIn.objects.create(attendee=people[2])
    return ticket_type.event


def test_attendee_list_filters(api_as, crowd):
    client = api_as(crowd.owner)
    url = f"/api/events/{crowd.pk}/attendees/"

    body = client.get(url).json()
    assert body["count"] == 3
    names = lambda r: [a["name"] for a in r.json()["results"]]  # noqa: E731
    assert names(client.get(url, {"checked_in": "true"})) == ["Ada", "Cy"]
    assert names(client.get(url, {"checked_in": "false"})) == ["Bob"]
    assert names(client.get(url, {"search": "bob@"})) == ["Bob"]


def test_stats_per_ticket_type(api_as, crowd):
    body = api_as(crowd.owner).get(f"/api/events/{crowd.pk}/stats/").json()
    assert (body["capacity"], body["registered"], body["checked_in"]) == (105, 3, 2)
    per_type = {t["name"]: (t["registered"], t["checked_in"]) for t in body["ticket_types"]}
    assert per_type == {"General": (2, 1), "VIP": (1, 1)}
