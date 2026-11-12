import secrets

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone

# No 0/O, 1/I/L: codes get read aloud and typed at the door.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 8


def generate_checkin_code():
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


class Event(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="events"
    )
    name = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]
        indexes = [models.Index(fields=["starts_at"], name="event_starts_at_idx")]
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")), name="event_ends_after_start"
            ),
        ]

    def __str__(self):
        return self.name


class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ["event", "name"]
        constraints = [
            models.UniqueConstraint(fields=["event", "name"], name="tickettype_unique_name_per_event"),
            models.CheckConstraint(condition=Q(capacity__gte=1), name="tickettype_capacity_positive"),
        ]

    def __str__(self):
        return f"{self.event.name}: {self.name}"


class Attendee(models.Model):
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, related_name="attendees"
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    code = models.CharField(
        max_length=CODE_LENGTH, unique=True, default=generate_checkin_code, editable=False
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["registered_at"]
        constraints = [
            models.UniqueConstraint(
                F("ticket_type"), Lower("email"), name="attendee_unique_email_per_ticket_type"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class CheckIn(models.Model):
    # OneToOne = UNIQUE(attendee_id): the database rejects a second check-in.
    attendee = models.OneToOneField(
        Attendee, on_delete=models.CASCADE, related_name="checkin"
    )
    checked_in_at = models.DateTimeField(default=timezone.now)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkins",
    )

    def __str__(self):
        return f"{self.attendee} at {self.checked_in_at:%Y-%m-%d %H:%M}"
