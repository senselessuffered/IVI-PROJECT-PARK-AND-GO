from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, RedirectView, TemplateView

from bookings.models import Booking
from core.mixins import SafePaginationMixin


class BookingListView(LoginRequiredMixin, SafePaginationMixin, ListView):
    model = Booking
    context_object_name = 'bookings'
    paginate_by = 8

    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user).select_related('parking_spot')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(parking_spot__number__icontains=query)
        return queryset


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
