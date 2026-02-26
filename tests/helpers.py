"""Shared test helpers and utilities."""
from datetime import timedelta
from django.utils import timezone


def future_datetime(days=1, hours=0):
    """Return a timezone-aware datetime in the future."""
    return timezone.now() + timedelta(days=days, hours=hours)


def past_datetime(days=1, hours=0):
    """Return a timezone-aware datetime in the past."""
    return timezone.now() - timedelta(days=days, hours=hours)
