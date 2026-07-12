import pytest
from django.contrib.auth import get_user_model

from spots.models import ParkingSpot


@pytest.fixture
def user(db):
    User = get_user_model()

    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="password123"
    )


@pytest.fixture
def parking_spot(db):
    return ParkingSpot.objects.create(
        number="A-001",
        description="Test Parking Spot",
        is_active=True
    )
