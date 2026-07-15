from django import forms

from bookings.models import Booking
from spots.models import ParkingSpot


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ('date', 'parking_spot', 'start_time', 'end_time')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.HiddenInput(),
            'end_time': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parking_spot'].queryset = ParkingSpot.objects.filter(is_active=True)
