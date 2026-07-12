import pytest
import datetime
from datetime import date, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from bookings.forms import BookingForm
from bookings.models import Booking
from bookings.views import BookingCreateView, busy_hours_for
from spots.models import ParkingSpot

User = get_user_model()

@pytest.mark.django_db
class TestBookingModel:
    def test_str(self, user, parking_spot):
        booking = Booking.objects.create(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 11),
            start_time = datetime.time(10),
            end_time = datetime.time(12),
        )

        assert str(booking) == f"{parking_spot} 2030-07-11"
    
    def test_duration_hours(self, user, parking_spot):
        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date.today(),
            start_time = datetime.time(9),
            end_time = datetime.time(13),
        )

        assert booking.duration_hours == 4
    
    def test_invalid_time(self, user, parking_spot):
        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date.today(),
            start_time = datetime.time(14),
            end_time = datetime.time(12),
        )

        with pytest.raises(ValidationError):
            booking.clean()
    
    def test_overlap(self, user, parking_spot):
        Booking.objects.create(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 11),
            start_time = datetime.time(10, 0),
            end_time = datetime.time(12, 0),
        )

        booking = Booking(
            user = user,
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 11),
            start_time = datetime.time(11, 0),
            end_time = datetime.time(13, 0),
        )

        with pytest.raises(ValidationError) as exc:
            booking.clean()
        
        assert "занято" in str(exc.value)

    def test_day_limit(self, user, parking_spot):
        Booking.objects.create(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 11),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 11),
            start_time = datetime.time(16, 0),
            end_time = datetime.time(17, 0),
        )

        with pytest.raises(ValidationError) as exc:
            booking.clean()

        assert "Суточный лимит" in str(exc.value)

    def test_week_limit(self, user, parking_spot):
        Booking.objects.create(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 8),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        Booking.objects.create(
            user = user,
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 9),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2030, 7, 10),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(9, 0),
        )

        with pytest.raises(ValidationError) as exc:
            booking.clean()

        assert "Недельный лимит" in str(exc.value)



class BusyHoursTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')

        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10, 0),
            end_time=time(13, 0),
        )

    def test_busy_hours(self):
        hours = busy_hours_for(self.spot.pk, self.booking.date)
        self.assertEqual(hours, [10, 11, 12])

    def test_busy_hours_with_exclude(self):
        hours = busy_hours_for(
            self.spot.pk,
            self.booking.date,
            exclude_pk=self.booking.pk,
        )
        self.assertEqual(hours, [])

    def test_busy_hours_without_spot(self):
        self.assertEqual(
            busy_hours_for(None, self.booking.date),
            [],
        )

    def test_busy_hours_without_date(self):
        self.assertEqual(
            busy_hours_for(self.spot.pk, None),
            [],
        )

    @patch('bookings.views.Booking.objects.filter')
    def test_busy_hours_value_error(self, mocked_filter):
        mocked_filter.side_effect = ValueError
        self.assertEqual(
            busy_hours_for(self.spot.pk, self.booking.date),
            [],
        )

    @patch('bookings.views.Booking.objects.filter')
    def test_busy_hours_type_error(self, mocked_filter):
        mocked_filter.side_effect = TypeError
        self.assertEqual(
            busy_hours_for(self.spot.pk, self.booking.date),
            [],
        )

    @patch('bookings.views.Booking.objects.filter')
    def test_busy_hours_validation_error(self, mocked_filter):
        mocked_filter.side_effect = ValidationError('test')
        self.assertEqual(
            busy_hours_for(self.spot.pk, self.booking.date),
            [],
        )

    def test_busy_hours_with_exclude_no_bookings(self):
        hours = busy_hours_for(
            self.spot.pk,
            self.booking.date,
            exclude_pk=999,
        )
        self.assertEqual(hours, [10, 11, 12])


class BookingListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )

        self.other = User.objects.create_user(
            username='other',
            password='testpass123',
        )

        self.spot1 = ParkingSpot.objects.create(number='A1')
        self.spot2 = ParkingSpot.objects.create(number='B1')

        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot1,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )

        Booking.objects.create(
            user=self.other,
            parking_spot=self.spot2,
            date=date(2030, 1, 2),
            start_time=time(10),
            end_time=time(12),
        )

    def test_requires_login(self):
        response = self.client.get(reverse('bookings:list'))
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_list.html')

    def test_only_user_bookings(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'))
        bookings = response.context['bookings']
        self.assertEqual(bookings.count(), 1)
        self.assertEqual(bookings.first(), self.booking)

    def test_search(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'q': 'A1'})
        self.assertEqual(response.context['bookings'].count(), 1)

    def test_search_empty(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'q': 'ZZZ'})
        self.assertEqual(response.context['bookings'].count(), 0)

    def test_pagination(self):
        Booking.objects.all().delete()
        for i in range(9):
            Booking.objects.create(
                user=self.user,
                parking_spot=ParkingSpot.objects.create(number=f'C{i}'),
                date=date(2030, 1, 1),
                start_time=time(10),
                end_time=time(11),
            )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'))

        self.assertEqual(len(response.context['bookings']), 8)
        self.assertTrue(response.context['is_paginated'])

    def test_pagination_abc_page(self):
        Booking.objects.all().delete()
        for i in range(10):
            Booking.objects.create(
                user=self.user,
                parking_spot=ParkingSpot.objects.create(number=f'D{i}'),
                date=date(2030, 1, 1),
                start_time=time(10),
                end_time=time(11),
            )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'page': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_pagination_negative_page(self):
        Booking.objects.all().delete()
        for i in range(10):
            Booking.objects.create(
                user=self.user,
                parking_spot=ParkingSpot.objects.create(number=f'E{i}'),
                date=date(2030, 1, 1),
                start_time=time(10),
                end_time=time(11),
            )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'page': '-5'})
        self.assertEqual(response.status_code, 200)

    def test_pagination_page_greater_than_max(self):
        Booking.objects.all().delete()
        for i in range(10):
            Booking.objects.create(
                user=self.user,
                parking_spot=ParkingSpot.objects.create(number=f'F{i}'),
                date=date(2030, 1, 1),
                start_time=time(10),
                end_time=time(11),
            )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'page': '999'})
        self.assertEqual(response.status_code, 200)

    def test_last_page(self):
        Booking.objects.all().delete()
        for i in range(9):
            Booking.objects.create(
                user=self.user,
                parking_spot=ParkingSpot.objects.create(number=f'G{i}'),
                date=date(2030, 1, 1),
                start_time=time(10),
                end_time=time(11),
            )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:list'), {'page': 'last'})
        self.assertEqual(len(response.context['bookings']), 1)


class BookingDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')
        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )

    def test_requires_login(self):
        response = self.client.get(
            reverse('bookings:detail', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:detail', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:detail', kwargs={'pk': self.booking.pk})
        )
        self.assertTemplateUsed(response, 'bookings/booking_detail.html')

    def test_context(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:detail', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.context['booking'], self.booking)


class BookingCreateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')

    def test_requires_login(self):
        response = self.client.get(reverse('bookings:create'))
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('bookings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_form.html')

    def test_get_initial_spot(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:create'),
            {'spot': self.spot.pk},
        )
        self.assertEqual(
            response.context['form'].initial['parking_spot'],
            str(self.spot.pk),
        )

    def test_busy_hours_context(self):
        Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(9),
            end_time=time(11),
        )

        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:create'),
            {'spot': self.spot.pk, 'date': '2030-01-01'},
        )
        self.assertIn('busy_hours', response.context)

    def test_create_booking(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(
            reverse('bookings:create'),
            {
                'parking_spot': self.spot.pk,
                'date': '2030-01-01',
                'start_time': '10:00',
                'end_time': '12:00',
            },
        )
        booking = Booking.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('bookings:detail', kwargs={'pk': booking.pk}),
        )

    def test_user_set_automatically(self):
        self.client.login(username='user', password='testpass123')
        self.client.post(
            reverse('bookings:create'),
            {
                'parking_spot': self.spot.pk,
                'date': '2030-01-01',
                'start_time': '10:00',
                'end_time': '12:00',
            },
        )
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.user)

    def test_invalid_post(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(
            reverse('bookings:create'),
            {
                'parking_spot': '',
                'date': '',
                'start_time': '',
                'end_time': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_get_success_url(self):
        self.client.login(username='user', password='testpass123')
        self.client.post(
            reverse('bookings:create'),
            {
                'parking_spot': self.spot.pk,
                'date': '2030-01-01',
                'start_time': '10:00',
                'end_time': '12:00',
            },
        )
        booking = Booking.objects.first()
        view = BookingCreateView()
        view.object = booking
        self.assertEqual(
            view.get_success_url(),
            reverse('bookings:detail', kwargs={'pk': booking.pk})
        )


class BookingUpdateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')
        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )

    def test_requires_login(self):
        response = self.client.get(
            reverse('bookings:edit', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:edit', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_form.html')

    def test_update_booking(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(
            reverse('bookings:edit', kwargs={'pk': self.booking.pk}),
            {
                'parking_spot': self.spot.pk,
                'date': '2030-01-02',
                'start_time': '11:00',
                'end_time': '13:00',
            },
        )
        self.booking.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('bookings:detail', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(self.booking.date.strftime('%Y-%m-%d'), '2030-01-02')
        self.assertEqual(self.booking.start_time.strftime('%H:%M'), '11:00')
        self.assertEqual(self.booking.end_time.strftime('%H:%M'), '13:00')

    def test_permission_denied_on_edit_other_user_booking(self):
        other_user = User.objects.create_user(
            username='other',
            password='testpass123',
        )
        other_booking = Booking.objects.create(
            user=other_user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )
        self.client.login(username='user', password='testpass123')
        response = self.client.get(
            reverse('bookings:edit', kwargs={'pk': other_booking.pk})
        )
        self.assertEqual(response.status_code, 403)


class BookingCancelViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')
        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )

    def test_requires_login(self):
        response = self.client.get(
            reverse('bookings:cancel', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_redirect(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(
            reverse('bookings:cancel', kwargs={'pk': self.booking.pk})
        )
        self.assertRedirects(response, reverse('bookings:detail', kwargs={'pk': self.booking.pk}))


class BookingDeleteViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='testpass123',
        )
        self.spot = ParkingSpot.objects.create(number='A1')
        self.booking = Booking.objects.create(
            user=self.user,
            parking_spot=self.spot,
            date=date(2030, 1, 1),
            start_time=time(10),
            end_time=time(12),
        )

    def test_requires_login(self):
        response = self.client.get(
            reverse('bookings:delete', kwargs={'pk': self.booking.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_redirect(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(
            reverse('bookings:delete', kwargs={'pk': self.booking.pk})
        )
        self.assertRedirects(response, reverse('bookings:list'))


@pytest.mark.django_db
class TestBookingForm:
    # TODO PIXELS-022
    pass
