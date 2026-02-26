from django.urls import path

from src.bookings.views import BookingCancelView, BookingCreateView, BookingListView

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('book/<int:class_id>/', BookingCreateView.as_view(), name='booking-create'),
    path('cancel/<int:pk>/', BookingCancelView.as_view(), name='booking-cancel'),
]
