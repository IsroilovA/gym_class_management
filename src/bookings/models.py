from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


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
    def create_for_member(cls, member, gym_class_id):
        """Create a booking atomically while enforcing capacity limits."""
        from src.classes.models import GymClass

        with transaction.atomic():
            gym_class = GymClass.objects.select_for_update().get(pk=gym_class_id)

            duplicate_exists = cls.objects.filter(
                member=member,
                gym_class=gym_class,
            ).exists()
            if duplicate_exists:
                raise ValidationError(
                    'This member already has a booking for this class.'
                )

            current_bookings = cls.objects.filter(gym_class=gym_class).count()
            if current_bookings >= gym_class.max_capacity:
                raise ValidationError('This class is full.')

            return cls.objects.create(member=member, gym_class=gym_class)

    def __str__(self):
        return f'{self.member} \u2192 {self.gym_class}'

    def clean(self):
        super().clean()

        # Guard: FK may not be set yet during form rendering
        if not self.gym_class_id:
            return

        # Capacity check
        current_bookings = (
            Booking.objects.filter(gym_class=self.gym_class)
            .exclude(pk=self.pk)
            .count()
        )
        if current_bookings >= self.gym_class.max_capacity:
            raise ValidationError('This class is full.')

        # Duplicate check
        if not self.member_id:
            return

        duplicate = (
            Booking.objects.filter(member=self.member, gym_class=self.gym_class)
            .exclude(pk=self.pk)
            .exists()
        )
        if duplicate:
            raise ValidationError(
                'This member already has a booking for this class.'
            )
