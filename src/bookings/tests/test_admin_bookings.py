import pytest
from django.test import Client
from django.contrib.admin.sites import AdminSite
from src.bookings.models import Booking
from src.bookings.admin import BookingAdmin

pytestmark = pytest.mark.integration

def test_booking_admin_changelist_accessible_to_staff(admin_client, booking_factory):
    booking_factory()
    response = admin_client.get('/admin/bookings/booking/')
    assert response.status_code == 200

def test_booking_admin_not_accessible_to_non_staff(user_factory, booking_factory):
    user = user_factory()
    client = Client()
    client.login(username=user.username, password='testpass123')
    response = client.get('/admin/bookings/booking/')
    assert response.status_code == 302
    assert response.url.startswith('/admin/login/')

def test_booking_admin_changelist_view_includes_report_url(admin_client, booking_factory):
    booking_factory()
    response = admin_client.get('/admin/bookings/booking/')
    assert response.status_code == 200
    assert 'report_url' in response.context
    assert response.context['report_url'] == 'report/'

def test_cancel_selected_bookings_action(admin_client, booking_factory):
    b1 = booking_factory()
    b2 = booking_factory()
    b3 = booking_factory()
    
    response = admin_client.post('/admin/bookings/booking/', {
        'action': 'cancel_selected_bookings',
        '_selected_action': [b1.pk, b2.pk],
    })
    
    assert response.status_code == 302  # redirect after action
    assert Booking.objects.filter(pk=b1.pk).count() == 0
    assert Booking.objects.filter(pk=b2.pk).count() == 0
    assert Booking.objects.filter(pk=b3.pk).count() == 1

def test_report_view_accessible_to_staff(admin_client):
    response = admin_client.get('/admin/bookings/booking/report/')
    assert response.status_code == 200

def test_report_view_not_accessible_to_non_staff(user_factory):
    user = user_factory()
    client = Client()
    client.login(username=user.username, password='testpass123')
    response = client.get('/admin/bookings/booking/report/')
    assert response.status_code == 302
    assert response.url.startswith('/admin/login/')

def test_report_view_context(admin_client, gym_class_factory, booking_factory, user_factory):
    gc = gym_class_factory(max_capacity=2)
    booking_factory(gym_class=gc)
    booking_factory(gym_class=gc)
    
    from src.bookings.models import Booking
    u = user_factory()
    Booking.objects.bulk_create([Booking(member=u, gym_class=gc)])  # over-capacity
    
    response = admin_client.get('/admin/bookings/booking/report/')
    
    assert response.status_code == 200
    classes = response.context['classes']
    gc_from_context = classes.get(pk=gc.pk)
    assert gc_from_context.booking_count == 3
    assert gc_from_context.remaining_spots == 0  # clamped, not -1

def test_get_trainer_returns_trainer_name(admin_client, gym_class_factory, trainer_factory, booking_factory):
    trainer = trainer_factory(first_name='John', last_name='Doe')
    gc = gym_class_factory(trainer=trainer)
    booking = booking_factory(gym_class=gc)
    
    ma = BookingAdmin(model=Booking, admin_site=AdminSite())
    assert ma.get_trainer(booking) == trainer

def test_get_trainer_returns_tba_when_no_trainer(admin_client, gym_class_factory, booking_factory):
    gc = gym_class_factory(trainer=None)
    booking = booking_factory(gym_class=gc)
    
    ma = BookingAdmin(model=Booking, admin_site=AdminSite())
    assert ma.get_trainer(booking) == 'TBA'

def test_get_class_schedule(admin_client, gym_class_factory, booking_factory):
    gc = gym_class_factory()
    booking = booking_factory(gym_class=gc)
    
    ma = BookingAdmin(model=Booking, admin_site=AdminSite())
    assert ma.get_class_schedule(booking) == gc.scheduled_at
