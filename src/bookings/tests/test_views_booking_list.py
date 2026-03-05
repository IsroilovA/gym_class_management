import pytest
from django.urls import reverse
from django.utils import timezone

from tests.helpers import future_datetime, past_datetime

pytestmark = pytest.mark.integration


def test_booking_list_anonymous_user(client):
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


def test_booking_list_authenticated_user_sees_own(auth_client, user_factory, booking_factory, gym_class_factory):
    client, user = auth_client
    other_user = user_factory()

    upcoming_class = gym_class_factory(scheduled_at=future_datetime(days=1))
    booking1 = booking_factory(member=user, gym_class=upcoming_class)
    booking2 = booking_factory(member=other_user)

    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    upcoming_pks = [b.pk for b in response.context['upcoming_bookings']]
    completed_pks = [b.pk for b in response.context['completed_bookings']]
    all_pks = upcoming_pks + completed_pks
    assert booking1.pk in all_pks
    assert booking2.pk not in all_pks


def test_booking_list_empty(auth_client):
    client, user = auth_client
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['upcoming_bookings']) == 0
    assert len(response.context['completed_bookings']) == 0


def test_booking_list_uses_correct_template(auth_client, booking_factory):
    client, user = auth_client
    booking_factory(member=user)
    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'bookings/booking_list.html' in [t.name for t in response.templates]


def test_booking_list_separates_upcoming_and_completed(auth_client, booking_factory, gym_class_factory):
    """Upcoming bookings (class not yet ended) and completed (class ended) are separated."""
    client, user = auth_client

    upcoming_class = gym_class_factory(
        scheduled_at=future_datetime(days=1),
        duration_minutes=60,
    )
    past_class = gym_class_factory(
        scheduled_at=past_datetime(days=2),
        duration_minutes=60,
    )

    upcoming_booking = booking_factory(member=user, gym_class=upcoming_class)
    completed_booking = booking_factory(member=user, gym_class=past_class)

    url = reverse('booking-list')
    response = client.get(url)
    assert response.status_code == 200

    upcoming_pks = [b.pk for b in response.context['upcoming_bookings']]
    completed_pks = [b.pk for b in response.context['completed_bookings']]

    assert upcoming_booking.pk in upcoming_pks
    assert completed_booking.pk in completed_pks
    assert upcoming_booking.pk not in completed_pks
    assert completed_booking.pk not in upcoming_pks


def test_booking_list_upcoming_ordered_by_scheduled_at_asc(auth_client, booking_factory, gym_class_factory):
    """Upcoming bookings are ordered by scheduled_at ascending (soonest first)."""
    client, user = auth_client

    class_later = gym_class_factory(scheduled_at=future_datetime(days=3), duration_minutes=60)
    class_sooner = gym_class_factory(scheduled_at=future_datetime(days=1), duration_minutes=60)

    booking_later = booking_factory(member=user, gym_class=class_later)
    booking_sooner = booking_factory(member=user, gym_class=class_sooner)

    url = reverse('booking-list')
    response = client.get(url)
    upcoming_pks = [b.pk for b in response.context['upcoming_bookings']]
    assert upcoming_pks == [booking_sooner.pk, booking_later.pk]


def test_booking_list_completed_ordered_by_scheduled_at_desc(auth_client, booking_factory, gym_class_factory):
    """Completed bookings are ordered by scheduled_at descending (most recent first)."""
    client, user = auth_client

    class_older = gym_class_factory(scheduled_at=past_datetime(days=5), duration_minutes=60)
    class_newer = gym_class_factory(scheduled_at=past_datetime(days=2), duration_minutes=60)

    booking_older = booking_factory(member=user, gym_class=class_older)
    booking_newer = booking_factory(member=user, gym_class=class_newer)

    url = reverse('booking-list')
    response = client.get(url)
    completed_pks = [b.pk for b in response.context['completed_bookings']]
    assert completed_pks == [booking_newer.pk, booking_older.pk]


def test_booking_list_completed_section_no_cancel_button(auth_client, booking_factory, gym_class_factory):
    """Completed bookings section must not render cancel controls."""
    client, user = auth_client

    past_class = gym_class_factory(scheduled_at=past_datetime(days=2), duration_minutes=60)
    booking = booking_factory(member=user, gym_class=past_class)

    url = reverse('booking-list')
    response = client.get(url)
    content = response.content.decode()

    cancel_url = reverse('booking-cancel', kwargs={'pk': booking.pk})
    # The cancel URL should not appear in the page at all for completed bookings
    assert cancel_url not in content


def test_booking_list_upcoming_section_has_cancel_button(auth_client, booking_factory, gym_class_factory):
    """Upcoming bookings section must render cancel controls."""
    client, user = auth_client

    upcoming_class = gym_class_factory(scheduled_at=future_datetime(days=1), duration_minutes=60)
    booking = booking_factory(member=user, gym_class=upcoming_class)

    url = reverse('booking-list')
    response = client.get(url)
    content = response.content.decode()

    cancel_url = reverse('booking-cancel', kwargs={'pk': booking.pk})
    assert cancel_url in content
