from django.db import models
from django.core.validators import MinValueValidator


class Trainer(models.Model):
    """Represents a gym trainer employed at the facility."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    specialisation = models.CharField(max_length=200)
    photo = models.ImageField(
        upload_to='trainers/',
        blank=True,
        null=True,
        help_text='Trainer profile photo.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    @property
    def display_name(self):
        """Return a safe trainer name for UI display."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        # Defensive fallback in case template syntax accidentally lands in DB fields.
        if not full_name or '{{' in full_name or '}}' in full_name:
            return 'TBA'
        return full_name

    @property
    def display_initial(self):
        """Return a safe single-letter avatar initial."""
        initial = (self.first_name or '').strip()[:1].upper()
        return initial if initial.isalpha() else 'T'

    def __str__(self):
        return self.display_name


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
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
    )
    max_capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']
        verbose_name_plural = 'Gym classes'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gte=1),
                name='gymclass_duration_minutes_gte_1',
            ),
            models.CheckConstraint(
                condition=models.Q(max_capacity__gte=1),
                name='gymclass_max_capacity_gte_1',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def available_spots(self):
        """Return the number of remaining bookable spots.

        Uses the ``booking_count`` annotation when available to avoid
        an extra query per instance.
        """
        count = getattr(self, 'booking_count', None)
        if count is None:
            count = self.bookings.count()
        return self.max_capacity - count

    @property
    def is_full(self):
        """Return whether the class has no remaining capacity."""
        return self.available_spots <= 0

    @property
    def available_spots_display(self):
        """Return a non-negative availability value for UI display."""
        return max(self.available_spots, 0)
