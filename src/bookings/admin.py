from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['member', 'gym_class', 'booked_at']
    list_filter = ['gym_class', 'booked_at']
    search_fields = ['member__username', 'gym_class__name']
    raw_id_fields = ['member', 'gym_class']
