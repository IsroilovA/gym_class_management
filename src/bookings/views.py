from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView

from src.bookings.forms import RegistrationForm
from src.bookings.models import Booking
from src.classes.models import GymClass


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'

    def get_queryset(self):
        return (
            Booking.objects.filter(member=self.request.user)
            .select_related('gym_class', 'gym_class__trainer')
        )


class BookingCreateView(LoginRequiredMixin, View):
    def post(self, request, class_id):
        gym_class = get_object_or_404(GymClass, pk=class_id)

        try:
            booking = Booking.create_for_member(
                member=request.user,
                gym_class_id=gym_class.pk,
            )
        except IntegrityError:
            messages.warning(request, 'You have already booked this class.')
            return redirect('class-detail', pk=gym_class.pk)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return redirect('class-detail', pk=gym_class.pk)

        messages.success(request, f'Successfully booked {booking.gym_class.name}!')
        return redirect('booking-list')


class BookingCancelView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('booking-list')

    def get_queryset(self):
        return Booking.objects.filter(member=self.request.user)

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        messages.success(request, f'Booking for {booking.gym_class.name} cancelled.')
        return super().delete(request, *args, **kwargs)
