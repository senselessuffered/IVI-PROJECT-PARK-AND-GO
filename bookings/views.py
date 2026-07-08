from django.views.generic import RedirectView, TemplateView


class BookingListView(TemplateView):
    # TODO PIXELS-012
    template_name = 'bookings/booking_list.html'


class BookingDetailView(RedirectView):
    # TODO PIXELS-013
    url = '/'


class BookingCreateView(TemplateView):
    # TODO PIXELS-014
    template_name = 'bookings/booking_form.html'


class BookingUpdateView(TemplateView):
    # TODO PIXELS-015
    template_name = 'bookings/booking_form.html'


class BookingCancelView(RedirectView):
    # TODO PIXELS-016
    url = '/'


class BookingDeleteView(RedirectView):
    # TODO PIXELS-017
    url = '/'
