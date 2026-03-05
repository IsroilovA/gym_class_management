from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F, ExpressionWrapper, DateTimeField
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView

from src.bookings.forms import RegistrationForm
from src.bookings.models import Booking
from src.classes.models import GymClass


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('class-list')
        return super().dispatch(request, *args, **kwargs)


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'

    def get_queryset(self):
        return (
            Booking.objects.filter(member=self.request.user)
            .select_related('gym_class', 'gym_class__trainer')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        qs = self.get_queryset().annotate(
            end_time=ExpressionWrapper(
                F('gym_class__scheduled_at') + timedelta(minutes=1) * F('gym_class__duration_minutes'),
                output_field=DateTimeField(),
            ),
        )
        context['upcoming_bookings'] = qs.filter(end_time__gt=now).order_by('gym_class__scheduled_at')
        context['completed_bookings'] = qs.filter(end_time__lte=now).order_by('-gym_class__scheduled_at')
        return context


class BookingCreateView(LoginRequiredMixin, View):
    def post(self, request, class_id):
        try:
            booking = Booking.create_for_member(
                member=request.user,
                gym_class_id=class_id,
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
        return Booking.objects.filter(member=self.request.user).select_related('gym_class')

    def form_valid(self, form):
        booking = self.object  # already fetched by BaseDeleteView.post()
        if booking.gym_class.end_time <= timezone.now():
            messages.error(self.request, 'Cannot cancel a booking for a class that has already ended.')
            return redirect('booking-list')
        messages.success(self.request, f'Booking for {booking.gym_class.name} cancelled.')
        return super().form_valid(form)
