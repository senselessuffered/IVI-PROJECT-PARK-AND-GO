import pytest
import datetime

from django.core.exceptions import ValidationError

from bookings.models import Booking

print("BOOKINGS TESTS LOADED")

@pytest.mark.django_db
class TestBookingModel:
    def test_str(self, user, parking_spot):
        booking = Booking.objects.create(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2026, 7, 11),
            start_time = datetime.time(10),
            end_time = datetime.time(12),
        )

        assert str(booking) == f"{parking_spot} 2026-07-11"
    
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
            date = datetime.date(2026, 7, 11),
            start_time = datetime.time(10, 0),
            end_time = datetime.time(12, 0),
        )

        booking = Booking(
            user = user,
            parking_spot = parking_spot,
            date = datetime.date(2026, 7, 11),
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
            date = datetime.date(2026, 7, 11),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2026, 7, 11),
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
            date = datetime.date(2026, 7, 7),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        Booking.objects.create(
            user = user,
            parking_spot = parking_spot,
            date = datetime.date(2026, 7, 8),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(16, 0),
        )

        booking = Booking(
            user = user, 
            parking_spot = parking_spot,
            date = datetime.date(2026, 7, 9),
            start_time = datetime.time(8, 0),
            end_time = datetime.time(9, 0),
        )

        with pytest.raises(ValidationError) as exc:
            booking.clean()

        assert "Недельный лимит" in str(exc.value)



@pytest.mark.django_db
class TestBookingView:
    # TODO PIXELS-021
    pass


@pytest.mark.django_db
class TestBookingForm:
    # TODO PIXELS-022
    pass
