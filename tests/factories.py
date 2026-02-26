"""
Standalone factory functions for use outside of pytest fixtures.
These mirror the fixture factories but work without pytest context.
"""
from django.contrib.auth.models import User
from django.utils import timezone

from src.classes.models import GymClass, Trainer
from src.bookings.models import Booking

_counter = 0


def _next_id():
    global _counter
    _counter += 1
    return _counter


def make_user(username=None, password='testpass123', **kwargs):
    if username is None:
        username = f'factoryuser{_next_id()}'
    return User.objects.create_user(username=username, password=password, **kwargs)


def make_trainer(first_name=None, last_name=None, **kwargs):
    if first_name is None:
        first_name = f'First{_next_id()}'
    if last_name is None:
        last_name = f'Last{_next_id()}'
    return Trainer.objects.create(
        first_name=first_name,
        last_name=last_name,
        specialisation=kwargs.pop('specialisation', 'General Fitness'),
        **kwargs,
    )


def make_gym_class(name=None, trainer=None, scheduled_at=None, **kwargs):
    if name is None:
        name = f'FactoryClass{_next_id()}'
    if trainer is None:
        trainer = make_trainer()
    if scheduled_at is None:
        scheduled_at = timezone.now() + timezone.timedelta(days=1)
    return GymClass.objects.create(
        name=name,
        trainer=trainer,
        scheduled_at=scheduled_at,
        max_capacity=kwargs.pop('max_capacity', 10),
        duration_minutes=kwargs.pop('duration_minutes', 60),
        **kwargs,
    )


def make_booking(member=None, gym_class=None, **kwargs):
    if member is None:
        member = make_user()
    if gym_class is None:
        gym_class = make_gym_class()
    return Booking.objects.create(member=member, gym_class=gym_class, **kwargs)
