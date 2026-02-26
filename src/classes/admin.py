from django.contrib import admin

from .models import GymClass, Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'specialisation', 'created_at']
    search_fields = ['first_name', 'last_name', 'specialisation']
    list_filter = ['specialisation']


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'scheduled_at', 'duration_minutes', 'max_capacity']
    list_filter = ['trainer', 'scheduled_at']
    search_fields = ['name']
    raw_id_fields = ['trainer']
