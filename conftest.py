"""Shared fixtures for the entire test suite."""
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from src.classes.models import GymClass, Trainer
from src.bookings.models import Booking


@pytest.fixture
def user_factory(db):
    """Factory fixture that creates User instances."""
    created_users = []
    counter = [0]

    def _create_user(username=None, password='testpass123', **kwargs):
        counter[0] += 1
        if username is None:
            username = f'testuser{counter[0]}'
        user = User.objects.create_user(username=username, password=password, **kwargs)
        created_users.append(user)
        return user

    return _create_user


@pytest.fixture
def trainer_factory(db):
    """Factory fixture that creates Trainer instances."""
    counter = [0]

    def _create_trainer(first_name=None, last_name=None, **kwargs):
        counter[0] += 1
        if first_name is None:
            first_name = f'TrainerFirst{counter[0]}'
        if last_name is None:
            last_name = f'TrainerLast{counter[0]}'
        return Trainer.objects.create(
            first_name=first_name,
            last_name=last_name,
            specialisation=kwargs.pop('specialisation', 'General Fitness'),
            **kwargs,
        )

    return _create_trainer


@pytest.fixture
def gym_class_factory(db, trainer_factory):
    """Factory fixture that creates GymClass instances."""
    counter = [0]

    def _create_gym_class(name=None, scheduled_at=None, **kwargs):
        counter[0] += 1
        if name is None:
            name = f'TestClass{counter[0]}'
        if 'trainer' not in kwargs:
            kwargs['trainer'] = trainer_factory()
        if scheduled_at is None:
            scheduled_at = timezone.now() + timezone.timedelta(days=1)
        return GymClass.objects.create(
            name=name,
            scheduled_at=scheduled_at,
            max_capacity=kwargs.pop('max_capacity', 10),
            duration_minutes=kwargs.pop('duration_minutes', 60),
            **kwargs,
        )

    return _create_gym_class


@pytest.fixture
def booking_factory(db, user_factory, gym_class_factory):
    """Factory fixture that creates Booking instances directly (bypassing validation)."""
    def _create_booking(member=None, gym_class=None, **kwargs):
        if member is None:
            member = user_factory()
        if gym_class is None:
            gym_class = gym_class_factory()
        # Direct ORM create to bypass model validation (for test setup purposes)
        booking = Booking(member=member, gym_class=gym_class, **kwargs)
        Booking.objects.bulk_create([booking])
        booking.refresh_from_db()
        return booking

    return _create_booking


@pytest.fixture
def auth_client(db, user_factory):
    """Return a logged-in Django test client and the associated user."""
    user = user_factory()
    client = Client()
    client.login(username=user.username, password='testpass123')
    return client, user

@pytest.fixture
def admin_client(db, user_factory):
    """Return a logged-in Django test client with staff/superuser privileges."""
    from django.test import Client
    user = user_factory(username='admin')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    client = Client()
    client.login(username='admin', password='testpass123')
    return client

