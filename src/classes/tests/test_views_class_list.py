import pytest
from django.urls import reverse
from tests.helpers import future_datetime, past_datetime

pytestmark = pytest.mark.integration


def test_class_list_shows_only_future_classes(gym_class_factory, client):
    """Only classes scheduled in the future should appear in the list."""
    future_class = gym_class_factory(name='Future Yoga', scheduled_at=future_datetime(days=1))
    past_class = gym_class_factory(name='Past Yoga', scheduled_at=past_datetime(days=1))
    
    url = reverse('class-list')
    response = client.get(url)
    
    assert response.status_code == 200
    class_names = [obj.name for obj in response.context['object_list']]
    assert 'Future Yoga' in class_names
    assert 'Past Yoga' not in class_names


def test_class_list_empty_when_no_future_classes(gym_class_factory, client):
    """When all classes are in the past, the list should be empty."""
    gym_class_factory(scheduled_at=past_datetime(days=1))
    
    url = reverse('class-list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert len(response.context['object_list']) == 0


def test_class_list_annotates_booking_count(gym_class_factory, booking_factory, client):
    """Each class in the list should have a booking_count annotation."""
    gc = gym_class_factory(scheduled_at=future_datetime(days=1), max_capacity=10)
    booking_factory(gym_class=gc)
    booking_factory(gym_class=gc)
    
    url = reverse('class-list')
    response = client.get(url)
    
    classes = list(response.context['object_list'])
    assert len(classes) == 1
    assert hasattr(classes[0], 'booking_count')
    assert classes[0].booking_count == 2


def test_class_list_uses_correct_template(gym_class_factory, client):
    """ClassListView should use the classes/class_list.html template."""
    gym_class_factory(scheduled_at=future_datetime(days=1))
    
    url = reverse('class-list')
    response = client.get(url)
    
    assert 'classes/class_list.html' in [t.name for t in response.templates]
