from django.urls import path

from src.classes.views import ClassDetailView, ClassListView

urlpatterns = [
    path('', ClassListView.as_view(), name='class-list'),
    path('<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
]
