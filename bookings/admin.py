from django.contrib import admin
from .models import Booking, Reminder


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "parking_spot", "user", "date", "start_time", "end_time", "status", "created_at")
    list_filter = ("status", "parking_spot", "date")
    search_fields = ("user__username", "user__email", "parking_spot__number")
    date_hierarchy = "date"
    ordering = ("-date", "start_time")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "scheduled_for", "is_sent", "sent_at")
    list_filter = ("is_sent",)
    search_fields = ("booking__id", "booking__user__username")
    readonly_fields = ("created_at", "updated_at")