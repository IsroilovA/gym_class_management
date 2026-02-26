from django.conf import settings
from django.db import models


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

    def __str__(self):
        return f'{self.member} \u2192 {self.gym_class}'
