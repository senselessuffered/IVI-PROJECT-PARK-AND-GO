import csv
from datetime import datetime, timedelta

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone

from bookings.models import SLOT_END_HOUR, SLOT_START_HOUR, Booking, BookingStatus
from spots.models import ParkingSpot

WEEKLY_AVAILABLE_HOURS = (SLOT_END_HOUR - SLOT_START_HOUR) * 7
REPORT_WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
CSV_BOM = '\N{ZERO WIDTH NO-BREAK SPACE}'


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('number', 'description')
    ordering = ('number',)
    readonly_fields = ('created_at', 'updated_at')
    change_list_template = 'admin/spots/parkingspot/change_list.html'

    def get_urls(self):
        custom = [
            path(
                'weekly-report/',
                self.admin_site.admin_view(self.weekly_report),
                name='spots_parkingspot_weekly_report',
            ),
        ]
        return custom + super().get_urls()

    def weekly_report(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied

        week_start = self._week_start(request.GET.get('start'))
        week_end = week_start + timedelta(days=6)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'occupancy_{week_start:%Y%m%d}_{week_end:%Y%m%d}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(CSV_BOM)

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Место', *REPORT_WEEKDAYS, 'Всего часов', 'Занятость, %'])

        booked = self._booked_hours(week_start, week_end)
        for spot in ParkingSpot.objects.all():
            per_day = [booked.get((spot.id, week_start + timedelta(days=i)), 0) for i in range(7)]
            total = sum(per_day)
            occupancy = round(total / WEEKLY_AVAILABLE_HOURS * 100, 1)
            writer.writerow([spot.number, *per_day, total, f'{occupancy:.1f}'.replace('.', ',')])

        return response

    @staticmethod
    def _week_start(raw):
        today = timezone.localdate()
        parsed = today
        if raw:
            try:
                parsed = datetime.strptime(raw, '%Y-%m-%d').date()
            except ValueError:
                parsed = today
        return parsed - timedelta(days=parsed.weekday())

    @staticmethod
    def _booked_hours(week_start, week_end):
        bookings = Booking.objects.filter(
            status=BookingStatus.ACTIVE,
            date__range=(week_start, week_end),
        )
        booked = {}
        for booking in bookings:
            key = (booking.parking_spot_id, booking.date)
            span = booking.end_time.hour - booking.start_time.hour
            booked[key] = booked.get(key, 0) + span
        return booked
