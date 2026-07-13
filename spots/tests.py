import datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from bookings.models import Booking
from spots.models import ParkingSpot


@pytest.mark.django_db
class TestParkingSpot:
    def test_str_returns_number(self, parking_spot):
        assert str(parking_spot) == 'A-001'

    def test_list_search_filters_by_number(self, client):
        matching_spot = ParkingSpot.objects.create(number='A-100')
        ParkingSpot.objects.create(number='B-200')

        response = client.get(reverse('spots:list'), {'q': 'A-1'})

        assert response.status_code == 200
        assert list(response.context['spots']) == [matching_spot]

    def test_detail_shows_only_active_bookings(self, client, user, parking_spot):
        active_booking = Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=datetime.date(2026, 7, 11),
            start_time=datetime.time(10),
            end_time=datetime.time(12),
        )
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=datetime.date(2026, 7, 12),
            start_time=datetime.time(10),
            end_time=datetime.time(12),
            status='cancelled',
        )

        response = client.get(reverse('spots:detail', kwargs={'pk': parking_spot.pk}))

        assert response.status_code == 200
        assert list(response.context['active_bookings']) == [active_booking]


@pytest.mark.django_db
class TestParkingSpotCalendar:
    def cell_for_day(self, weeks, day):
        for week in weeks:
            for cell in week:
                if cell and cell['day'] == day:
                    return cell
        return None

    def test_default_period_is_current_month(self, client, parking_spot):
        today = datetime.date.today()

        response = client.get(reverse('spots:calendar', kwargs={'pk': parking_spot.pk}))

        assert response.status_code == 200
        assert response.context['month_date'].year == today.year
        assert response.context['month_date'].month == today.month

    def test_day_without_bookings_is_free(self, client, parking_spot):
        today = datetime.date.today()

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': today.year, 'month': today.month},
        )

        cell = self.cell_for_day(response.context['weeks'], today.day)
        assert cell['status'] == 'free'

    def test_partially_booked_day_is_partial(self, client, user, parking_spot):
        day = datetime.date.today() + datetime.timedelta(days=10)
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=day,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': day.year, 'month': day.month},
        )

        cell = self.cell_for_day(response.context['weeks'], day.day)
        assert cell['status'] == 'partial'

    def test_fully_booked_day_is_full(self, client, user, parking_spot):
        User = get_user_model()
        other = User.objects.create_user(username='other', email='other@example.com', password='password123')
        day = datetime.date.today() + datetime.timedelta(days=11)
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=day,
            start_time=datetime.time(8, 0),
            end_time=datetime.time(16, 0),
        )
        Booking.objects.create(
            user=other,
            parking_spot=parking_spot,
            date=day,
            start_time=datetime.time(16, 0),
            end_time=datetime.time(22, 0),
        )

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': day.year, 'month': day.month},
        )

        cell = self.cell_for_day(response.context['weeks'], day.day)
        assert cell['status'] == 'full'

    def test_cancelled_booking_does_not_affect_status(self, client, user, parking_spot):
        day = datetime.date.today() + datetime.timedelta(days=12)
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=day,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
            status='cancelled',
        )

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': day.year, 'month': day.month},
        )

        cell = self.cell_for_day(response.context['weeks'], day.day)
        assert cell['status'] == 'free'

    def test_invalid_month_returns_404(self, client, parking_spot):
        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': 2026, 'month': 13},
        )

        assert response.status_code == 404

    def test_past_days_are_off(self, client, parking_spot):
        today = datetime.date.today()

        response = client.get(reverse('spots:calendar', kwargs={'pk': parking_spot.pk}))

        for week in response.context['weeks']:
            for cell in week:
                if cell and cell['date'] < today:
                    assert cell['status'] == 'off'

    def test_day_beyond_window_is_off(self, client, parking_spot):
        far = datetime.date.today() + datetime.timedelta(days=40)

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': far.year, 'month': far.month},
        )

        cell = self.cell_for_day(response.context['weeks'], far.day)
        assert cell['status'] == 'off'

    def test_prev_disabled_on_current_month(self, client, parking_spot):
        response = client.get(reverse('spots:calendar', kwargs={'pk': parking_spot.pk}))

        assert response.context['prev_disabled'] is True

    def test_past_month_is_clamped_to_current(self, client, parking_spot):
        today = datetime.date.today()

        response = client.get(
            reverse('spots:calendar', kwargs={'pk': parking_spot.pk}),
            {'year': 2020, 'month': 1},
        )

        assert response.context['month_date'].year == today.year
        assert response.context['month_date'].month == today.month


@pytest.mark.django_db
class TestWeeklyReport:
    def report_url(self):
        return reverse('admin:spots_parkingspot_weekly_report')

    def make_superuser(self):
        User = get_user_model()
        return User.objects.create_superuser(
            username='root', email='root@example.com', password='password123'
        )

    def test_superuser_gets_csv(self, client, parking_spot):
        client.force_login(self.make_superuser())

        response = client.get(self.report_url())

        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']
        assert 'attachment' in response['Content-Disposition']

    def test_report_counts_active_hours(self, client, user, parking_spot):
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=week_start + datetime.timedelta(days=2),
            start_time=datetime.time(10),
            end_time=datetime.time(14),
        )
        client.force_login(self.make_superuser())

        response = client.get(self.report_url())

        content = response.content.decode('utf-8')
        row = next(line for line in content.splitlines() if line.startswith('A-001'))
        cells = row.split(';')
        assert cells[3] == '4'
        assert cells[8] == '4'

    def test_cancelled_booking_not_counted(self, client, user, parking_spot):
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        Booking.objects.create(
            user=user,
            parking_spot=parking_spot,
            date=week_start + datetime.timedelta(days=2),
            start_time=datetime.time(10),
            end_time=datetime.time(14),
            status='cancelled',
        )
        client.force_login(self.make_superuser())

        response = client.get(self.report_url())

        content = response.content.decode('utf-8')
        row = next(line for line in content.splitlines() if line.startswith('A-001'))
        cells = row.split(';')
        assert cells[8] == '0'

    def test_regular_user_denied(self, client, user, parking_spot):
        client.force_login(user)

        response = client.get(self.report_url())

        assert response.status_code in (302, 403)

    def test_anonymous_redirected(self, client, parking_spot):
        response = client.get(self.report_url())

        assert response.status_code == 302
