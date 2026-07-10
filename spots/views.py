from django.views.generic import DetailView, ListView

from spots.models import ParkingSpot


class ParkingSpotListView(ListView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_list.html'
    context_object_name = 'spots'


class ParkingSpotDetailView(DetailView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_detail.html'
    context_object_name = 'spot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_bookings'] = (
            self.object.bookings.filter(status='active').select_related('user').order_by('date', 'start_time')
        )
        return context
