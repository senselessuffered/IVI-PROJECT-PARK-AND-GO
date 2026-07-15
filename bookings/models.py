from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import DurationField, ExpressionWrapper, F, Sum
from django.utils import timezone

from core.models import TimeStampedModel
from spots.models import ParkingSpot

MAX_DAILY_BOOKING_HOURS = 8
MAX_WEEKLY_BOOKING_HOURS = 16
DAILY_BOOKING_LIMIT = timedelta(hours=MAX_DAILY_BOOKING_HOURS)
WEEKLY_BOOKING_LIMIT = timedelta(hours=MAX_WEEKLY_BOOKING_HOURS)

SLOT_START_HOUR = 8
SLOT_END_HOUR = 22

MAX_BOOKING_AHEAD_DAYS = 30


class DateTimeCombine(models.Func):
    arg_joiner = ' + '
    template = '(%(expressions)s)'
    output_field = models.DateTimeField()


class TsRange(models.Func):
    function = 'TSRANGE'
    output_field = DateTimeRangeField()


class BookingStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    CANCELLED = 'cancelled', 'Отменена'


class Booking(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.PROTECT, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=16, choices=BookingStatus.choices, default=BookingStatus.ACTIVE)

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
                condition=models.Q(status=BookingStatus.ACTIVE),
            ),
        ]

    def __str__(self):
        return f'{self.parking_spot} {self.date}'

    @property
    def duration_hours(self):
        return int(self.duration.total_seconds() // 3600)

    @property
    def duration(self):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        return end - start

    @property
    def is_active(self):
        return self.status == BookingStatus.ACTIVE

    def clean(self):
        if not self.date or not self.start_time or not self.end_time:
            return

        if self.end_time <= self.start_time:
            raise ValidationError('Время окончания должно быть позже начала.')

        if not self.is_active:
            return

        if self.date < timezone.localdate():
            raise ValidationError('Нельзя бронировать на прошедшую дату.')

        active = Booking.objects.filter(status=BookingStatus.ACTIVE).exclude(pk=self.pk)

        if active.filter(
            parking_spot=self.parking_spot,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exists():
            raise ValidationError('Это место уже занято на выбранное время.')

        mine = active.filter(user=self.user)

        day_duration = self._total_duration(mine.filter(date=self.date))
        if day_duration + self.duration > DAILY_BOOKING_LIMIT:
            raise ValidationError(f'Суточный лимит {MAX_DAILY_BOOKING_HOURS} часов превышен.')

        week_start = self.date - timedelta(days=self.date.weekday())
        week_end = week_start + timedelta(days=6)
        week_duration = self._total_duration(mine.filter(date__range=(week_start, week_end)))
        if week_duration + self.duration > WEEKLY_BOOKING_LIMIT:
            raise ValidationError(f'Недельный лимит {MAX_WEEKLY_BOOKING_HOURS} часов превышен.')

        if self.date > timezone.localdate() + timedelta(days=MAX_BOOKING_AHEAD_DAYS):
            raise ValidationError('Бронировать можно не более чем на месяц вперёд.')

    @staticmethod
    def _total_duration(queryset):
        total = queryset.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('end_time') - F('start_time'),
                    output_field=DurationField(),
                )
            )
        )['total']
        return total or timedelta()


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
