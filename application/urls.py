from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/', include('users.urls')),
    path('orders/', include('bookings.urls')),
    path('', include('spots.urls')),
]
