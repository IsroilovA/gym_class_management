import pytest
from django.urls import reverse

pytestmark = pytest.mark.integration

def test_booking_list_anonymous_user(client):
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

def test_booking_list_authenticated_user_sees_own(auth_client, user_factory, booking_factory):
    client, user = auth_client
    other_user = user_factory()
    
    booking1 = booking_factory(member=user)
    booking2 = booking_factory(member=other_user)
    
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    assert booking1 in response.context['object_list']
    assert booking2 not in response.context['object_list']

def test_booking_list_empty(auth_client):
    client, user = auth_client
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['object_list']) == 0

def test_booking_list_uses_correct_template(auth_client, booking_factory):
    client, user = auth_client
    booking_factory(member=user)
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'bookings/booking_list.html' in [t.name for t in response.templates]
