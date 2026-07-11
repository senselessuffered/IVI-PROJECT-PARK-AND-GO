from django.contrib import admin

from spots.models import ParkingSpot


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('number', 'description')
    ordering = ('number',)
    readonly_fields = ('created_at', 'updated_at')
