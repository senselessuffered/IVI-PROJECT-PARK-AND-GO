import pytest
import datetime

from django.urls import reverse

from bookings.models import Booking
from spots.models import ParkingSpot

from spots.models import ParkingSpot
from spots.templatetags.pagination import pagination_window

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
