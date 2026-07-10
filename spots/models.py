from django.db import models


class ParkingSpot(models.Model):
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('number',)

    def __str__(self):
        return self.number

