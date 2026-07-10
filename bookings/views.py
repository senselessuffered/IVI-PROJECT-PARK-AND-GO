from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, TemplateView


class BookingListView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-012
    template_name = 'bookings/booking_list.html'


class BookingDetailView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-013
    url = '/orders/'


class BookingCreateView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-014
    template_name = 'bookings/booking_form.html'


class BookingUpdateView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-015
    template_name = 'bookings/booking_form.html'


class BookingCancelView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-016
    url = '/orders/'


class BookingDeleteView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-017
    url = '/orders/'
