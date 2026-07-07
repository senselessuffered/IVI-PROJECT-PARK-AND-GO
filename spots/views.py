from django.views.generic import TemplateView


class ParkingSpotListView(TemplateView):
    template_name = 'spots/parkingspot_list.html'
