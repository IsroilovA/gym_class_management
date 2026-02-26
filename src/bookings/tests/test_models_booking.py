import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from src.bookings.models import Booking
from src.classes.models import GymClass
from tests.helpers import future_datetime, past_datetime


pytestmark = pytest.mark.integration


def test_duplicate_booking_blocked_via_validate_booking_rules(user_factory, gym_class_factory):
    user = user_factory()
    gym_class = gym_class_factory(scheduled_at=future_datetime(days=1))
    
    # Create a booking directly
    Booking.objects.create(member=user, gym_class=gym_class)
    
    with pytest.raises(ValidationError, match='This member already has a booking for this class.'):
        Booking.validate_booking_rules(member=user, gym_class=gym_class)


def test_full_class_blocked_via_validate_booking_rules(user_factory, gym_class_factory):
    gym_class = gym_class_factory(max_capacity=1, scheduled_at=future_datetime(days=1))
    user1 = user_factory()
    user2 = user_factory()
    
    # Fill the class
    Booking.objects.create(member=user1, gym_class=gym_class)
    
    # Try to validate a new booking for user2
    with pytest.raises(ValidationError, match='This class is full.'):
        Booking.validate_booking_rules(member=user2, gym_class=gym_class)


def test_past_class_blocked_via_validate_booking_rules(user_factory, gym_class_factory):
    user = user_factory()
    gym_class = gym_class_factory(scheduled_at=past_datetime(days=1))
    
    # Using the class method should fail
    with pytest.raises(ValidationError, match='Cannot book a class that has already started.'):
        Booking.validate_booking_rules(member=user, gym_class=gym_class)


def test_exclude_booking_id_update_path(booking_factory):
    booking = booking_factory()
    
    # Validation should not raise because the existing booking is excluded
    Booking.validate_booking_rules(
        member=booking.member,
        gym_class=booking.gym_class,
        exclude_booking_id=booking.pk
    )


def test_exclude_booking_id_for_capacity_check(user_factory, gym_class_factory):
    user = user_factory()
    gym_class = gym_class_factory(max_capacity=1, scheduled_at=future_datetime(days=1))
    
    # Create the single booking that fills the class
    booking = Booking.objects.create(member=user, gym_class=gym_class)
    
    # Validation should not raise for the same user when excluding this booking
    Booking.validate_booking_rules(
        member=user,
        gym_class=gym_class,
        exclude_booking_id=booking.pk
    )


def test_create_for_member_success_path(user_factory, gym_class_factory):
    user = user_factory()
    gym_class = gym_class_factory(scheduled_at=future_datetime(days=1))
    
    booking = Booking.create_for_member(member=user, gym_class=gym_class)
    
    assert booking.pk is not None
    assert booking.member == user
    assert booking.gym_class == gym_class


def test_create_for_member_raises_for_non_existent_class(user_factory):
    user = user_factory()
    
    # Create an unsaved dummy class to have a mock ID
    dummy_class = GymClass(pk=9999)
    
    with pytest.raises(GymClass.DoesNotExist):
        Booking.create_for_member(member=user, gym_class=dummy_class)


def test_unique_constraint_integrity_at_db_level(booking_factory):
    booking = booking_factory()
    
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            # bypass model validation to test DB constraint
            booking2 = Booking(member=booking.member, gym_class=booking.gym_class)
            super(Booking, booking2).save()


def test_clean_guard_when_fk_fields_not_set():
    booking = Booking()
    # Should not raise any error since member_id and gym_class_id are not set
    booking.clean()


def test_save_calls_full_clean_validation_error_propagates(user_factory, gym_class_factory):
    user = user_factory()
    past_class = gym_class_factory(scheduled_at=past_datetime(days=1))
    
    # Attempting to save directly with invalid data should propagate ValidationError
    with pytest.raises(ValidationError, match='Cannot book a class that has already started.'):
        Booking(member=user, gym_class=past_class).save()


def test_str_representation(booking_factory):
    booking = booking_factory()
    assert str(booking) == f'{booking.member} → {booking.gym_class}'
