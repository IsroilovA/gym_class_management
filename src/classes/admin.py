from django.contrib import admin
from django.db.models import Count

from src.bookings.models import Booking

from .models import GymClass, Trainer


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1
    raw_id_fields = ['member']
    readonly_fields = ['booked_at']


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'specialisation', 'created_at']
    search_fields = ['first_name', 'last_name', 'specialisation']
    list_filter = ['specialisation']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    list_per_page = 25


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'trainer', 'scheduled_at', 'duration_minutes',
        'max_capacity', 'get_booking_count', 'get_available_spots',
    ]
    list_filter = ['trainer', 'scheduled_at']
    search_fields = ['name']
    raw_id_fields = ['trainer']
    inlines = [BookingInline]
    date_hierarchy = 'scheduled_at'
    readonly_fields = ['created_at']
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(booking_count=Count('bookings'))

    @admin.display(description='Bookings', ordering='booking_count')
    def get_booking_count(self, obj):
        return obj.booking_count

    @admin.display(description='Available Spots')
    def get_available_spots(self, obj):
        return obj.max_capacity - obj.booking_count
