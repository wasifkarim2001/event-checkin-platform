from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Attendee, CheckIn, Event, TicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "event", "name", "capacity"]

    def validate_event(self, event):
        if event.owner != self.context["request"].user:
            raise serializers.ValidationError("You can only add ticket types to your own events.")
        if self.instance and event != self.instance.event:
            raise serializers.ValidationError("A ticket type can't move to another event.")
        return event

    def validate_capacity(self, capacity):
        if self.instance and capacity < self.instance.attendees.count():
            raise serializers.ValidationError("Capacity can't go below current registrations.")
        return capacity


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    staff = serializers.SlugRelatedField(
        many=True, required=False, slug_field="username", queryset=get_user_model().objects.all()
    )
    ticket_types = TicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "venue", "starts_at", "ends_at", "owner", "staff", "ticket_types", "created_at"]

    def validate(self, attrs):
        starts = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if starts and ends and ends <= starts:
            raise serializers.ValidationError({"ends_at": "Must be after starts_at."})
        return attrs


class PublicTicketTypeSerializer(serializers.ModelSerializer):
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = TicketType
        fields = ["id", "name", "capacity", "remaining"]

    def get_remaining(self, obj) -> int:
        return max(obj.capacity - obj.registered, 0)


class PublicEventSerializer(serializers.ModelSerializer):
    ticket_types = PublicTicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "venue", "starts_at", "ends_at", "ticket_types"]


class RegistrationSerializer(serializers.Serializer):
    ticket_type = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()


class RegistrationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ["code", "name", "email", "ticket_type"]


class AttendeeSerializer(serializers.ModelSerializer):
    ticket_type = serializers.ReadOnlyField(source="ticket_type.name")
    checked_in_at = serializers.DateTimeField(source="checkin.checked_in_at", read_only=True)

    class Meta:
        model = Attendee
        fields = ["id", "name", "email", "code", "ticket_type", "registered_at", "checked_in_at"]


class CheckInRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)


class CheckInSerializer(serializers.ModelSerializer):
    attendee = AttendeeSerializer(read_only=True)
    checked_in_by = serializers.ReadOnlyField(source="checked_in_by.username")

    class Meta:
        model = CheckIn
        fields = ["attendee", "checked_in_at", "checked_in_by"]


class TicketTypeStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    capacity = serializers.IntegerField()
    registered = serializers.IntegerField()
    checked_in = serializers.IntegerField()


class EventStatsSerializer(serializers.Serializer):
    capacity = serializers.IntegerField()
    registered = serializers.IntegerField()
    checked_in = serializers.IntegerField()
    ticket_types = TicketTypeStatsSerializer(many=True)
