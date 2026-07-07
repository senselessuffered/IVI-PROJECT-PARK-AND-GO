from django.views.generic import RedirectView, TemplateView


class BookingListView(TemplateView):
    template_name = 'bookings/booking_list.html'


class BookingCreateView(TemplateView):
    template_name = 'bookings/booking_form.html'


class BookingUpdateView(TemplateView):
    template_name = 'bookings/booking_form.html'


class BookingDetailView(RedirectView):
    url = '/'


class BookingCancelView(RedirectView):
    url = '/'


class BookingDeleteView(RedirectView):
    url = '/'
