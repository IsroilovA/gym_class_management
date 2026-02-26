from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect
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
        try:
            booking = Booking.create_for_member(
                member=request.user,
                gym_class=GymClass(pk=class_id),
            )
        except GymClass.DoesNotExist as exc:
            raise Http404('Class not found.') from exc
        except IntegrityError:
            messages.warning(request, 'You have already booked this class.')
            return redirect('class-detail', pk=class_id)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return redirect('class-detail', pk=class_id)

        messages.success(request, f'Successfully booked {booking.gym_class.name}!')
        return redirect('booking-list')


class BookingCancelView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('booking-list')

    def get_queryset(self):
        return Booking.objects.filter(member=self.request.user)

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        messages.success(request, f'Booking for {booking.gym_class.name} cancelled.')
        booking.delete()
        return redirect(self.success_url)
