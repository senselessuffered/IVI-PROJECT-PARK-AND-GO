from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('private/admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('orders/', include('bookings.urls')),
    path('spots/', include('spots.urls')),
    path('', RedirectView.as_view(pattern_name='spots:list', permanent=False)),
]
