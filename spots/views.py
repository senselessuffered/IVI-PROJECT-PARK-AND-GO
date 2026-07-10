from django.views.generic import ListView
from spots.models import ParkingSpot


class ParkingSpotListView(ListView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_list.html'
    context_object_name = 'spots'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        free_spots = ParkingSpot.objects.filter(is_active=True)
        context['free_spots'] = free_spots
        context['free_spots_count'] = free_spots.count()
        return context