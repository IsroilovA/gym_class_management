from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Booking(models.Model):
    """Represents a reservation made by a member for a gym class."""

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    gym_class = models.ForeignKey(
        'classes.GymClass',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'gym_class'],
                name='unique_booking',
            ),
        ]

    @classmethod
    def create_for_member(cls, *, member, gym_class):
        """Create a booking atomically while enforcing booking rules."""
        from src.classes.models import GymClass

        with transaction.atomic():
            locked_class = GymClass.objects.select_for_update().get(pk=gym_class.pk)
            cls.validate_booking_rules(member=member, gym_class=locked_class)
            return cls.objects.create(member=member, gym_class=locked_class)

    @classmethod
    def validate_booking_rules(
        cls,
        *,
        member,
        gym_class,
        exclude_booking_id=None,
    ):
        """Validate booking constraints shared by all write paths."""
        if gym_class.scheduled_at <= timezone.now():
            raise ValidationError('Cannot book a class that has already started.')

        duplicate_qs = cls.objects.filter(member=member, gym_class=gym_class)
        if exclude_booking_id:
            duplicate_qs = duplicate_qs.exclude(pk=exclude_booking_id)
        if duplicate_qs.exists():
            raise ValidationError('This member already has a booking for this class.')

        booking_count_qs = cls.objects.filter(gym_class=gym_class)
        if exclude_booking_id:
            booking_count_qs = booking_count_qs.exclude(pk=exclude_booking_id)
        if booking_count_qs.count() >= gym_class.max_capacity:
            raise ValidationError('This class is full.')

    def __str__(self):
        return f'{self.member} \u2192 {self.gym_class}'

    def clean(self):
        super().clean()

        # Guard: FK may not be set yet during form rendering
        if not self.gym_class_id or not self.member_id:
            return

        self.validate_booking_rules(
            member=self.member,
            gym_class=self.gym_class,
            exclude_booking_id=self.pk,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
