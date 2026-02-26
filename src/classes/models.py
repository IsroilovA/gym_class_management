from django.db import models


class Trainer(models.Model):
    """Represents a gym trainer employed at the facility."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    specialisation = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class GymClass(models.Model):
    """Represents a single scheduled gym class session."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gym_classes',
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    max_capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']
        verbose_name_plural = 'Gym classes'

    def __str__(self):
        return self.name

    @property
    def available_spots(self):
        """Return the number of remaining bookable spots."""
        return self.max_capacity - self.bookings.count()
