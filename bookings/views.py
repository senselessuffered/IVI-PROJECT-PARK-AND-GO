from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, RedirectView, TemplateView

from bookings.models import Booking


class BookingListView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-012
    template_name = "bookings/booking_list.html"


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"


class BookingCreateView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-014
    template_name = "bookings/booking_form.html"


class BookingUpdateView(LoginRequiredMixin, TemplateView):
    # TODO PIXELS-015
    template_name = "bookings/booking_form.html"


class BookingCancelView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-016
    url = "/orders/"


class BookingDeleteView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-017
    url = "/orders/"