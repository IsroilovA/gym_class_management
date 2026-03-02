from django.db.models import Count
from django.utils import timezone
from django.views.generic import DetailView, ListView

from src.classes.models import GymClass


class ClassListView(ListView):
    model = GymClass
    template_name = 'classes/class_list.html'

    def get_queryset(self):
        qs = GymClass.objects.select_related('trainer').annotate(
            booking_count=Count('members', distinct=True),
        )
        if not self.request.GET.get('show_past'):
            qs = qs.filter(scheduled_at__gte=timezone.now())
        return qs


class ClassDetailView(DetailView):
    model = GymClass
    template_name = 'classes/class_detail.html'

    def get_queryset(self):
        return (
            GymClass.objects.select_related('trainer')
            .annotate(booking_count=Count('members', distinct=True))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['already_booked'] = (
            self.request.user.is_authenticated
            and self.object.members.filter(pk=self.request.user.pk).exists()
        )
        return context
