import pytest
from django.db import IntegrityError, transaction
from src.classes.models import GymClass
from tests.helpers import future_datetime

@pytest.mark.unit
def test_gym_class_available_spots_with_annotation():
    gym_class = GymClass(name='Test', max_capacity=10, scheduled_at=future_datetime(days=1))
    
    gym_class.booking_count = 3
    assert gym_class.available_spots == 7
    
    gym_class.booking_count = 10
    assert gym_class.available_spots == 0
    
    gym_class.booking_count = 12
    assert gym_class.available_spots == -2

@pytest.mark.integration
def test_gym_class_available_spots_without_annotation_no_bookings(db):
    gym_class = GymClass.objects.create(
        name='Test Class',
        max_capacity=10,
        scheduled_at=future_datetime(days=1),
        duration_minutes=60
    )
    assert gym_class.available_spots == 10

@pytest.mark.integration
def test_gym_class_available_spots_without_annotation_with_bookings(db, booking_factory, gym_class_factory):
    gym_class = gym_class_factory(max_capacity=5)
    booking_factory(gym_class=gym_class)
    booking_factory(gym_class=gym_class)
    assert gym_class.available_spots == 3

@pytest.mark.unit
def test_gym_class_is_full():
    gym_class = GymClass(name='Test', max_capacity=10, scheduled_at=future_datetime(days=1))
    
    gym_class.booking_count = 9
    assert gym_class.is_full is False
    
    gym_class.booking_count = 10
    assert gym_class.is_full is True
    
    gym_class.booking_count = 11
    assert gym_class.is_full is True

@pytest.mark.unit
def test_gym_class_available_spots_display():
    gym_class = GymClass(name='Test', max_capacity=10, scheduled_at=future_datetime(days=1))
    
    gym_class.booking_count = 5
    assert gym_class.available_spots_display == 5
    
    gym_class.booking_count = 10
    assert gym_class.available_spots_display == 0
    
    gym_class.booking_count = 12
    assert gym_class.available_spots_display == 0

@pytest.mark.integration
def test_gym_class_duration_minutes_constraint(db):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            GymClass.objects.create(
                name='Test Class',
                max_capacity=10,
                scheduled_at=future_datetime(days=1),
                duration_minutes=0
            )

@pytest.mark.integration
def test_gym_class_max_capacity_constraint(db):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            GymClass.objects.create(
                name='Test Class',
                max_capacity=0,
                scheduled_at=future_datetime(days=1),
                duration_minutes=60
            )

@pytest.mark.integration
def test_gym_class_valid_constraints(db):
    gym_class = GymClass.objects.create(
        name='Test Class',
        max_capacity=1,
        scheduled_at=future_datetime(days=1),
        duration_minutes=1
    )
    assert gym_class.id is not None
    assert gym_class.max_capacity == 1
    assert gym_class.duration_minutes == 1

@pytest.mark.unit
def test_gym_class_str():
    gym_class = GymClass(name='Pilates', max_capacity=10, scheduled_at=future_datetime(days=1))
    assert str(gym_class) == 'Pilates'
