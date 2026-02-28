"""Project URL configuration."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from src.bookings.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('classes/', include('src.classes.urls')),
    path('bookings/', include('src.bookings.urls')),
    path('', RedirectView.as_view(url='/classes/', permanent=False)),
]

# Serve media from Django only in DEBUG mode.
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
