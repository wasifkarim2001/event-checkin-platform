from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Attendee, Event, TicketType


@pytest.fixture
def organizer(db):
    return get_user_model().objects.create_user(username="organizer", password="unused")


@pytest.fixture
def event(organizer):
    start = timezone.now() + timedelta(days=7)
    return Event.objects.create(
        owner=organizer, name="DevConf", starts_at=start, ends_at=start + timedelta(hours=8)
    )


@pytest.fixture
def ticket_type(event):
    return TicketType.objects.create(event=event, name="General", capacity=100)


@pytest.fixture
def attendee(ticket_type):
    return Attendee.objects.create(ticket_type=ticket_type, name="Ada", email="ada@example.com")
