import pytest
from datetime import timedelta
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone

from src.bookings.models import Booking
from tests.helpers import future_datetime, past_datetime

pytestmark = pytest.mark.integration


def test_booking_cancel_anonymous_user(client, booking_factory):
    booking = booking_factory()
    url = reverse('booking-cancel', kwargs={'pk': booking.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


def test_booking_cancel_owner_can_cancel(auth_client, booking_factory, gym_class_factory):
    client, user = auth_client
    upcoming_class = gym_class_factory(scheduled_at=future_datetime(days=1), duration_minutes=60)
    booking = booking_factory(member=user, gym_class=upcoming_class)
    url = reverse('booking-cancel', kwargs={'pk': booking.pk})

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('booking-list')

    assert not Booking.objects.filter(pk=booking.pk).exists()

    messages = list(get_messages(response.wsgi_request))
    assert any('cancelled' in str(m) for m in messages)


def test_booking_cancel_non_owner_cannot_cancel(auth_client, user_factory, booking_factory):
    client, user = auth_client
    other_user = user_factory()
    booking = booking_factory(member=other_user)

    url = reverse('booking-cancel', kwargs={'pk': booking.pk})
    response = client.post(url)
    assert response.status_code == 404
    assert Booking.objects.filter(pk=booking.pk).exists()


def test_booking_cancel_non_existent(auth_client):
    client, user = auth_client
    url = reverse('booking-cancel', kwargs={'pk': 9999})
    response = client.post(url)
    assert response.status_code == 404


def test_booking_cancel_completed_class_rejected(auth_client, booking_factory, gym_class_factory):
    """Cancellation of a booking whose class has already ended must be rejected."""
    client, user = auth_client
    past_class = gym_class_factory(
        scheduled_at=past_datetime(days=2),
        duration_minutes=60,
    )
    booking = booking_factory(member=user, gym_class=past_class)
    url = reverse('booking-cancel', kwargs={'pk': booking.pk})

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('booking-list')

    # Booking must still exist
    assert Booking.objects.filter(pk=booking.pk).exists()

    msgs = list(get_messages(response.wsgi_request))
    assert any('already ended' in str(m) for m in msgs)


def test_booking_cancel_class_in_progress_allowed(auth_client, booking_factory, gym_class_factory):
    """Cancellation is allowed while the class is still in progress (end_time > now)."""
    client, user = auth_client
    # Class started 30 minutes ago, lasts 120 minutes => end_time is 90 min from now
    in_progress_class = gym_class_factory(
        scheduled_at=timezone.now() - timedelta(minutes=30),
        duration_minutes=120,
    )
    booking = booking_factory(member=user, gym_class=in_progress_class)
    url = reverse('booking-cancel', kwargs={'pk': booking.pk})

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('booking-list')

    # Booking should be deleted
    assert not Booking.objects.filter(pk=booking.pk).exists()
