from django.contrib import admin

from .models import Attendee, CheckIn, Event, TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "starts_at", "venue", "owner"]
    search_fields = ["name", "venue"]
    inlines = [TicketTypeInline]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "event", "capacity"]
    list_filter = ["event"]


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "code", "ticket_type", "registered_at"]
    list_filter = ["ticket_type__event"]
    search_fields = ["name", "email", "code"]
    readonly_fields = ["code"]


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ["attendee", "checked_in_at", "checked_in_by"]
    list_filter = ["attendee__ticket_type__event"]
    raw_id_fields = ["attendee"]
