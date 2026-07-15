from django.apps import AppConfig


class BookingsConfig(AppConfig):
    name = 'bookings'

    def ready(self):
        from django.db.models.signals import post_save

        from bookings.models import Booking
        from bookings.signals import schedule_reminder

        post_save.connect(schedule_reminder, sender=Booking)
