from django.contrib.auth.models import User
from spots.models import ParkingSpot
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum
from django.core.exceptions import ValidationError

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)    
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    duration_hours = models.FloatField(default=0)
    
    def clean(self):
        daily_hours = (
            Booking.objects.filter(
                user=self.user,
                date=self.date,
            )
            .exclude(status="cancelled")
            .exclude(pk=self.pk)
            .aggregate(total=Sum("duration_hours"))["total"] or 0
        )
        if daily_hours + self.duration_hours > 8:
            raise ValidationError("Суточный лимит превышен!")
        
        week_start = self.date + timedelta(days=self.date.weekday())
        week_end = week_start + timedelta(days=6)

        weekly_hours = (
            Booking.objects.filter(
                user=self.user,
                date__range=(week_start, week_end),
            )
            .exclude(status="cancelled")
            .exclude(pk=self.pk)
            .aggregate(total=Sum("duration_hours"))["total"] or 0
        )
        if weekly_hours + self.duration_hours > 16:
            raise ValidationError("Недельный лимит превышен!")

    def save(self, *args, **kwargs):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        self.duration_hours = (end - start).total_seconds() / 3600
        self.full_clean()
        super().save(*args, **kwargs)
        


class Reminder(models.Model):
    # TODO PIXELS-007
    pass
