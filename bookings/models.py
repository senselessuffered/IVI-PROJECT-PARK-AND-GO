from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel
from spots.models import ParkingSpot


class DateTimeCombine(models.Func):
    arg_joiner = ' + '
    template = '(%(expressions)s)'
    output_field = models.DateTimeField()


class TsRange(models.Func):
    function = 'TSRANGE'
    output_field = DateTimeRangeField()


class Booking(TimeStampedModel):
    STATUS_CHOICES = (
        ('active', 'Активна'),
        ('cancelled', 'Отменена'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.PROTECT, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ('-date', 'start_time')
        constraints = [
            ExclusionConstraint(
                name='exclude_overlapping_active_bookings',
                expressions=[
                    ('parking_spot', RangeOperators.EQUAL),
                    (
                        TsRange(
                            DateTimeCombine('date', 'start_time'),
                            DateTimeCombine('date', 'end_time'),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=models.Q(status='active'),
            ),
        ]

    def __str__(self):
        return f'{self.parking_spot} {self.date}'

    @property
    def duration_hours(self):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        return int((end - start).total_seconds() // 3600)

    def clean(self):
        if not self.date or not self.start_time or not self.end_time:
            return

        if self.date < timezone.localdate():
            raise ValidationError('Нельзя бронировать на прошедшую дату.')

        if self.end_time <= self.start_time:
            raise ValidationError('Время окончания должно быть позже начала.')

        active = Booking.objects.filter(status='active').exclude(pk=self.pk)

        if active.filter(
            parking_spot=self.parking_spot,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exists():
            raise ValidationError('Это место уже занято на выбранное время.')

        mine = active.filter(user=self.user)

        day_hours = sum(booking.duration_hours for booking in mine.filter(date=self.date))
        if day_hours + self.duration_hours > 8:
            raise ValidationError('Суточный лимит 8 часов превышен.')

        monday = self.date - timedelta(days=self.date.weekday())
        week = mine.filter(date__range=(monday, monday + timedelta(days=6)))
        week_hours = sum(booking.duration_hours for booking in week)
        if week_hours + self.duration_hours > 16:
            raise ValidationError('Недельный лимит 16 часов превышен.')


class Reminder(TimeStampedModel):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='reminder'
    )
    scheduled_for = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'

    def __str__(self):
        return f'Напоминание для брони #{self.booking.id}'
