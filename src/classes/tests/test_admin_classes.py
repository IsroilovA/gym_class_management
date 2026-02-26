import pytest
from django.test import Client
from src.classes.admin import GymClassAdmin
from django.contrib.admin.sites import AdminSite
from src.classes.models import GymClass

pytestmark = pytest.mark.integration

def test_trainer_admin_changelist_accessible_to_staff(admin_client, trainer_factory):
    trainer = trainer_factory()
    response = admin_client.get('/admin/classes/trainer/')
    assert response.status_code == 200
    assert trainer.first_name.encode() in response.content

def test_trainer_admin_not_accessible_to_non_staff(user_factory):
    user = user_factory()
    client = Client()
    client.login(username=user.username, password='testpass123')
    response = client.get('/admin/classes/trainer/')
    assert response.status_code == 302
    assert response.url.startswith('/admin/login/')

def test_gym_class_admin_changelist_accessible_to_staff(admin_client, gym_class_factory, booking_factory):
    gc = gym_class_factory(max_capacity=10)
    booking_factory(gym_class=gc)
    booking_factory(gym_class=gc)
    
    response = admin_client.get('/admin/classes/gymclass/')
    
    assert response.status_code == 200
    assert gc.name.encode() in response.content

def test_gym_class_admin_not_accessible_to_non_staff(user_factory):
    user = user_factory()
    client = Client()
    client.login(username=user.username, password='testpass123')
    
    response = client.get('/admin/classes/gymclass/')
    assert response.status_code == 302
    assert response.url.startswith('/admin/login/')

def test_gym_class_admin_display_methods(admin_client, gym_class_factory, booking_factory):
    """Test that get_booking_count and get_available_spots work correctly."""
    gc = gym_class_factory(max_capacity=5)
    booking_factory(gym_class=gc)
    booking_factory(gym_class=gc)
    
    admin_site = AdminSite()
    admin_instance = GymClassAdmin(GymClass, admin_site)

    from django.test import RequestFactory
    request = RequestFactory().get('/admin/classes/gymclass/')
    
    qs = admin_instance.get_queryset(request)
    obj = qs.get(pk=gc.pk)

    assert admin_instance.get_booking_count(obj) == 2
    assert admin_instance.get_available_spots(obj) == 3

    # Access the admin to verify it renders without errors
    response = admin_client.get('/admin/classes/gymclass/')
    assert response.status_code == 200
