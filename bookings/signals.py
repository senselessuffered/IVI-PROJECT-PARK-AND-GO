from datetime import datetime, timedelta

from django.utils import timezone

from bookings.models import Reminder


def schedule_reminder(sender, instance, **kwargs):
    start = datetime.combine(instance.date, instance.start_time)
    if timezone.is_naive(start):
        start = timezone.make_aware(start)
    Reminder.objects.update_or_create(
        booking=instance,
        defaults={
            'scheduled_for': start - timedelta(days=1),
            'is_sent': False,
            'sent_at': None,
        },
    )
