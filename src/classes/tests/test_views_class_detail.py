import pytest
from django.urls import reverse
from tests.helpers import future_datetime

pytestmark = pytest.mark.integration


def test_class_detail_anonymous_already_booked_is_false(gym_class_factory, client):
    """Anonymous users should see already_booked=False."""
    gc = gym_class_factory(scheduled_at=future_datetime(days=1))
    
    url = reverse('class-detail', kwargs={'pk': gc.pk})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.context['already_booked'] is False


def test_class_detail_authenticated_not_booked(gym_class_factory, auth_client):
    """Authenticated user who has not booked should see already_booked=False."""
    client, user = auth_client
    gc = gym_class_factory(scheduled_at=future_datetime(days=1))
    
    url = reverse('class-detail', kwargs={'pk': gc.pk})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.context['already_booked'] is False


def test_class_detail_authenticated_already_booked(gym_class_factory, booking_factory, auth_client):
    """Authenticated user who has booked should see already_booked=True."""
    client, user = auth_client
    gc = gym_class_factory(scheduled_at=future_datetime(days=1))
    booking_factory(member=user, gym_class=gc)
    
    url = reverse('class-detail', kwargs={'pk': gc.pk})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.context['already_booked'] is True


def test_class_detail_404_for_invalid_pk(client, db):
    """Requesting a non-existent class should return 404."""
    url = reverse('class-detail', kwargs={'pk': 99999})
    response = client.get(url)
    
    assert response.status_code == 404


def test_class_detail_uses_correct_template(gym_class_factory, client):
    """ClassDetailView should use the classes/class_detail.html template."""
    gc = gym_class_factory(scheduled_at=future_datetime(days=1))
    
    url = reverse('class-detail', kwargs={'pk': gc.pk})
    response = client.get(url)
    
    assert 'classes/class_detail.html' in [t.name for t in response.templates]
