from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Attendee, Event, TicketType
from .serializers import (
    AttendeeSerializer,
    CheckInRequestSerializer,
    CheckInSerializer,
    EventSerializer,
    EventStatsSerializer,
    PublicEventSerializer,
    RegistrationResultSerializer,
    RegistrationSerializer,
    TicketTypeSerializer,
)


class IsEventOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        event = obj if isinstance(obj, Event) else obj.event
        return event.owner == request.user


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation
            return Event.objects.none()
        # Events the user neither owns nor staffs are invisible: 404, not 403.
        return (
            Event.objects.visible_to(self.request.user)
            .select_related("owner")
            .prefetch_related("staff", "ticket_types")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(request=CheckInRequestSerializer, responses={201: CheckInSerializer})
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def checkins(self, request, pk=None):
        event = self.get_object()
        data = CheckInRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        checkin = services.check_in(event, data.validated_data["code"], request.user)
        return Response(CheckInSerializer(checkin).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses=AttendeeSerializer(many=True),
        parameters=[
            OpenApiParameter("search", str, description="Name, email or code contains"),
            OpenApiParameter("checked_in", bool),
        ],
    )
    @action(detail=True, methods=["get"])
    def attendees(self, request, pk=None):
        event = self.get_object()
        qs = (
            Attendee.objects.filter(ticket_type__event=event)
            .select_related("ticket_type", "checkin")
            .order_by("name", "id")
        )
        if search := request.query_params.get("search"):
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(code__iexact=search))
        checked_in = request.query_params.get("checked_in")
        if checked_in in ("true", "false"):
            qs = qs.filter(checkin__isnull=(checked_in == "false"))
        page = self.paginate_queryset(qs)
        return self.get_paginated_response(AttendeeSerializer(page, many=True).data)

    @extend_schema(responses=EventStatsSerializer)
    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        event = self.get_object()
        rows = list(
            event.ticket_types.order_by("name")
            .annotate(registered=Count("attendees"), checked_in=Count("attendees__checkin"))
            .values("id", "name", "capacity", "registered", "checked_in")
        )
        totals = {k: sum(r[k] for r in rows) for k in ("capacity", "registered", "checked_in")}
        return Response({**totals, "ticket_types": rows})


class TicketTypeViewSet(viewsets.ModelViewSet):
    serializer_class = TicketTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsEventOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TicketType.objects.none()
        events = Event.objects.visible_to(self.request.user)
        return TicketType.objects.filter(event__in=events).select_related("event")

    def destroy(self, request, *args, **kwargs):
        ticket_type = self.get_object()
        if ticket_type.attendees.exists():
            raise services.Conflict("Ticket type has registrations and can't be deleted.")
        return super().destroy(request, *args, **kwargs)


class PublicEventView(generics.RetrieveAPIView):
    serializer_class = PublicEventSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    queryset = Event.objects.prefetch_related(
        Prefetch(
            "ticket_types",
            queryset=TicketType.objects.order_by("name").annotate(registered=Count("attendees")),
        )
    )


class RegisterView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(responses={201: RegistrationResultSerializer})
    def post(self, request, pk):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data
        attendee = services.register_attendee(pk, v["ticket_type"], v["name"], v["email"])
        return Response(RegistrationResultSerializer(attendee).data, status=status.HTTP_201_CREATED)
