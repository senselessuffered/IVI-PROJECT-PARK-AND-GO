from django.db import models

from core.models import TimeStampedModel


class ParkingSpot(TimeStampedModel):
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('number',)

    def __str__(self):
        return self.number
