import calendar
from datetime import date, timedelta

from django.http import Http404
from django.utils import timezone
from django.views.generic import DetailView, ListView

from bookings.models import MAX_BOOKING_AHEAD_DAYS, SLOT_END_HOUR, SLOT_START_HOUR, Booking, BookingStatus
from core.mixins import SafePaginationMixin
from spots.models import ParkingSpot

TOTAL_DAILY_SLOTS = SLOT_END_HOUR - SLOT_START_HOUR
WEEKDAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


class ParkingSpotListView(SafePaginationMixin, ListView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_list.html'
    context_object_name = 'spots'
    paginate_by = 5

    def get_queryset(self):
        queryset = ParkingSpot.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(number__icontains=query)
        return queryset


class ParkingSpotDetailView(DetailView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_detail.html'
    context_object_name = 'spot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_bookings'] = (
            self.object.bookings
            .filter(status=BookingStatus.ACTIVE)
            .select_related('user')
            .order_by('date', 'start_time')
        )
        return context


class ParkingSpotCalendarView(DetailView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_calendar.html'
    context_object_name = 'spot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year, month = self._resolve_period()
        first_day = date(year, month, 1)
        today = timezone.localdate()
        max_date = today + timedelta(days=MAX_BOOKING_AHEAD_DAYS)
        busy_hours_by_day = self._busy_hours_by_day(year, month)
        can_book = self.request.user.is_authenticated and self.object.is_active

        weeks = []
        for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
            week_cells = []
            for day in week:
                if day == 0:
                    week_cells.append(None)
                    continue
                cell_date = date(year, month, day)
                in_window = today <= cell_date <= max_date
                if in_window:
                    status = self._day_status(len(busy_hours_by_day.get(day, set())))
                else:
                    status = 'off'
                week_cells.append({
                    'day': day,
                    'date': cell_date,
                    'status': status,
                    'clickable': can_book and in_window,
                })
            weeks.append(week_cells)

        prev_year, prev_month = self._shift_month(year, month, -1)
        next_year, next_month = self._shift_month(year, month, 1)

        context.update({
            'weeks': weeks,
            'weekdays': WEEKDAY_LABELS,
            'month_date': first_day,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
            'prev_disabled': (year, month) <= (today.year, today.month),
            'next_disabled': date(next_year, next_month, 1) > max_date,
        })
        return context

    def _resolve_period(self):
        today = timezone.localdate()
        try:
            year = int(self.request.GET.get('year', today.year))
            month = int(self.request.GET.get('month', today.month))
            date(year, month, 1)
        except ValueError:
            raise Http404
        if (year, month) < (today.year, today.month):
            return today.year, today.month
        return year, month

    def _busy_hours_by_day(self, year, month):
        bookings = Booking.objects.filter(
            parking_spot=self.object,
            status=BookingStatus.ACTIVE,
            date__year=year,
            date__month=month,
        )
        busy_hours_by_day = {}
        for booking in bookings:
            hours = busy_hours_by_day.setdefault(booking.date.day, set())
            hours.update(range(booking.start_time.hour, booking.end_time.hour))
        return busy_hours_by_day

    @staticmethod
    def _day_status(busy_hours_count):
        if busy_hours_count == 0:
            return 'free'
        if busy_hours_count >= TOTAL_DAILY_SLOTS:
            return 'full'
        return 'partial'

    @staticmethod
    def _shift_month(year, month, delta):
        index = year * 12 + (month - 1) + delta
        return index // 12, index % 12 + 1
