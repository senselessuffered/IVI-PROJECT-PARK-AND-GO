from django.views.generic import ListView
from spots.models import ParkingSpot


class ParkingSpotListView(ListView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_list.html'
    context_object_name = 'spots'