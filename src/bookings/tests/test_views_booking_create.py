import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch
from django.db import IntegrityError
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.integration

def test_booking_create_anonymous_user(client, gym_class_factory):
    gc = gym_class_factory()
    url = reverse('booking-create', kwargs={'class_id': gc.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

def test_booking_create_success(auth_client, gym_class_factory):
    client, user = auth_client
    gc = gym_class_factory()
    url = reverse('booking-create', kwargs={'class_id': gc.pk})
    
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('booking-list')
    
    messages = list(get_messages(response.wsgi_request))
    assert any('Successfully booked' in str(m) for m in messages)

def test_booking_create_class_not_found(auth_client):
    client, user = auth_client
    url = reverse('booking-create', kwargs={'class_id': 9999})
    response = client.post(url)
    assert response.status_code == 404

def test_booking_create_duplicate_booking(auth_client, gym_class_factory):
    client, user = auth_client
    gc = gym_class_factory()
    url = reverse('booking-create', kwargs={'class_id': gc.pk})
    
    with patch('src.bookings.models.Booking.create_for_member', side_effect=IntegrityError):
        response = client.post(url)
        
    assert response.status_code == 302
    assert response.url == reverse('class-detail', kwargs={'pk': gc.pk})
    
    messages = list(get_messages(response.wsgi_request))
    assert any('You have already booked this class.' in str(m) for m in messages)

def test_booking_create_validation_error(auth_client, gym_class_factory):
    client, user = auth_client
    gc = gym_class_factory()
    url = reverse('booking-create', kwargs={'class_id': gc.pk})
    
    with patch('src.bookings.models.Booking.create_for_member', side_effect=ValidationError(['Cannot book a class that has already started.'])):
        response = client.post(url)
        
    assert response.status_code == 302
    assert response.url == reverse('class-detail', kwargs={'pk': gc.pk})
    
    messages = list(get_messages(response.wsgi_request))
    assert any('Cannot book a class that has already started.' in str(m) for m in messages)
