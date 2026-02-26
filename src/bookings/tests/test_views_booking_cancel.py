import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from src.bookings.models import Booking

pytestmark = pytest.mark.integration

def test_booking_cancel_anonymous_user(client, booking_factory):
    booking = booking_factory()
    url = reverse('booking-cancel', kwargs={'pk': booking.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

def test_booking_cancel_owner_can_cancel(auth_client, booking_factory):
    client, user = auth_client
    booking = booking_factory(member=user)
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
