from django.views.generic import DetailView, ListView

from core.mixins import SafePaginationMixin
from spots.models import ParkingSpot


class ParkingSpotListView(SafePaginationMixin, ListView):
    model = ParkingSpot
    template_name = 'spots/parkingspot_list.html'
    context_object_name = 'spots'
    paginate_by = 5

    def get_queryset(self):
        queryset = ParkingSpot.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(number__icontains=query)
        return queryset


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
