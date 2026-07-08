from django.views.generic import TemplateView


class ParkingSpotListView(TemplateView):
    # TODO PIXELS-011
    template_name = 'spots/parkingspot_list.html'
