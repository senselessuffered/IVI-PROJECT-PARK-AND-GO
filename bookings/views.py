from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from django.views.generic import CreateView, ListView, RedirectView, UpdateView, DetailView, View
from django.shortcuts import get_object_or_404, redirect

from bookings.forms import BookingForm
from bookings.models import Booking
from core.mixins import SafePaginationMixin


def busy_hours_for(parking_spot_id, day, exclude_pk=None):
    if not parking_spot_id or not day:
        return []
    try:
        bookings = Booking.objects.filter(parking_spot_id=parking_spot_id, date=day, status='active')
        if exclude_pk:
            bookings = bookings.exclude(pk=exclude_pk)
        hours = []
        for booking in bookings:
            hours.extend(range(booking.start_time.hour, booking.end_time.hour))
        return hours
    except (ValueError, TypeError, ValidationError):
        return []


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


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related('parking_spot', 'user')
        )


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm

    def get_initial(self):
        initial = super().get_initial()
        spot = self.request.GET.get('spot')
        if spot:
            initial['parking_spot'] = spot
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.user = self.request.user
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        context['busy_hours'] = busy_hours_for(form['parking_spot'].value(), form['date'].value())
        return context

    def get_success_url(self):
        return reverse('bookings:detail', kwargs={'pk': self.object.pk})


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    context_object_name = 'booking'

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)

        if booking.user != self.request.user:
            raise PermissionDenied

        return booking

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.user = self.request.user
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context['form']
        context['busy_hours'] = busy_hours_for(
            form['parking_spot'].value(),
            form['date'].value(),
            exclude_pk=self.object.pk,
        )

        return context

    def get_success_url(self):
        return reverse(
            'bookings:detail',
            kwargs={'pk': self.object.pk},
        )


class BookingCancelView(LoginRequiredMixin, View):

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)

        if booking.user != request.user:
            raise PermissionDenied

        if booking.status == 'active':
            booking.status = 'cancelled'
            booking.save(update_fields=['status'])

        return redirect(
            'bookings:detail',
            pk=booking.pk,
        )

class BookingDeleteView(LoginRequiredMixin, RedirectView):
    # TODO PIXELS-017
    url = '/orders/'
