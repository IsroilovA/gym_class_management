from django.contrib import admin
from django.db.models import Count, F
from django.template.response import TemplateResponse
from django.urls import path

from src.classes.models import GymClass

from .models import Booking


@admin.action(description='Cancel selected bookings')
def cancel_selected_bookings(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f'Successfully cancelled {count} booking(s).')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'member', 'gym_class', 'get_class_schedule', 'get_trainer', 'booked_at',
    ]
    list_filter = ['gym_class', 'gym_class__trainer', 'booked_at']
    search_fields = ['member__username', 'gym_class__name']
    raw_id_fields = ['member', 'gym_class']
    actions = [cancel_selected_bookings]
    date_hierarchy = 'booked_at'
    list_select_related = ['member', 'gym_class', 'gym_class__trainer']
    list_per_page = 25

    @admin.display(description='Class Schedule', ordering='gym_class__scheduled_at')
    def get_class_schedule(self, obj):
        return obj.gym_class.scheduled_at

    @admin.display(description='Trainer', ordering='gym_class__trainer')
    def get_trainer(self, obj):
        return obj.gym_class.trainer or 'TBA'

    def get_urls(self):
        custom_urls = [
            path(
                'report/',
                self.admin_site.admin_view(self.report_view),
                name='bookings_booking_report',
            ),
        ]
        return custom_urls + super().get_urls()

    def report_view(self, request):
        classes = (
            GymClass.objects.select_related('trainer')
            .annotate(booking_count=Count('bookings'))
            .annotate(remaining_spots=F('max_capacity') - F('booking_count'))
            .order_by('scheduled_at')
        )
        context = {
            **self.admin_site.each_context(request),
            'classes': classes,
            'title': 'Bookings Per Class Report',
        }
        return TemplateResponse(
            request, 'admin/bookings/report.html', context
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['report_url'] = 'report/'
        return super().changelist_view(request, extra_context=extra_context)
