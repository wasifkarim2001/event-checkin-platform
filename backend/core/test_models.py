import threading

import pytest
from django.db import IntegrityError, connection, transaction

from .models import CODE_ALPHABET, CODE_LENGTH, Attendee, CheckIn, Event


def test_attendee_gets_readable_unique_code(ticket_type):
    a = Attendee.objects.create(ticket_type=ticket_type, name="A", email="a@example.com")
    b = Attendee.objects.create(ticket_type=ticket_type, name="B", email="b@example.com")
    assert len(a.code) == CODE_LENGTH
    assert set(a.code) <= set(CODE_ALPHABET)
    assert a.code != b.code


def test_second_checkin_is_rejected_by_database(attendee):
    CheckIn.objects.create(attendee=attendee)
    with pytest.raises(IntegrityError):
        CheckIn.objects.create(attendee=attendee)


def test_same_email_twice_on_a_ticket_type_is_rejected_case_insensitively(attendee):
    with pytest.raises(IntegrityError):
        Attendee.objects.create(
            ticket_type=attendee.ticket_type, name="Ada again", email="ADA@example.com"
        )


def test_event_cannot_end_before_it_starts(event):
    with pytest.raises(IntegrityError):
        Event.objects.create(
            owner=event.owner, name="Backwards", starts_at=event.ends_at, ends_at=event.starts_at
        )


@pytest.mark.django_db(transaction=True)
def test_concurrent_checkins_only_one_succeeds(attendee):
    # Two threads, two DB connections, released at the same moment.
    barrier = threading.Barrier(2)
    results = []

    def check_in():
        try:
            barrier.wait()
            with transaction.atomic():
                CheckIn.objects.create(attendee_id=attendee.pk)
            results.append("ok")
        except IntegrityError:
            results.append("rejected")
        finally:
            connection.close()

    threads = [threading.Thread(target=check_in) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(results) == ["ok", "rejected"]
    assert CheckIn.objects.filter(attendee=attendee).count() == 1


@pytest.mark.parametrize("model", ["event", "tickettype", "attendee", "checkin"])
def test_admin_changelist_renders(admin_client, attendee, model):
    CheckIn.objects.create(attendee=attendee)
    response = admin_client.get(f"/admin/core/{model}/")
    assert response.status_code == 200
