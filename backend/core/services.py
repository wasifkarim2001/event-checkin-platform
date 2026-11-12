from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .models import Attendee, CheckIn, Event


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict."
    default_code = "conflict"


def register_attendee(event_id, ticket_type_id, name, email):
    with transaction.atomic():
        # Row lock on the event serializes registrations for it, so the
        # capacity count and the duplicate-email check can't race.
        try:
            event = Event.objects.select_for_update().get(pk=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")
        ticket_type = event.ticket_types.filter(pk=ticket_type_id).first()
        if ticket_type is None:
            raise ValidationError({"ticket_type": "Not a ticket type of this event."})
        if event.ends_at <= timezone.now():
            raise ValidationError({"detail": "This event has ended."})
        if Attendee.objects.filter(ticket_type__event=event, email__iexact=email).exists():
            raise Conflict("This email is already registered for this event.")
        if ticket_type.attendees.count() >= ticket_type.capacity:
            raise Conflict("This ticket type is sold out.")
        return Attendee.objects.create(ticket_type=ticket_type, name=name, email=email)


def check_in(event, code, user):
    code = code.strip().upper()
    try:
        attendee = Attendee.objects.select_related("ticket_type").get(
            code=code, ticket_type__event=event
        )
    except Attendee.DoesNotExist:
        raise NotFound("No attendee with this code for this event.")
    try:
        # Savepoint: a failed INSERT must not abort the outer transaction.
        with transaction.atomic():
            return CheckIn.objects.create(attendee=attendee, checked_in_by=user)
    except IntegrityError:
        existing = CheckIn.objects.get(attendee=attendee)
        when = serializers.DateTimeField().to_representation(existing.checked_in_at)
        raise Conflict({"detail": "Already checked in.", "checked_in_at": when})
