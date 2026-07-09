from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('secure-adm1n/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('spots/', include('spots.urls')),
    path('', include('bookings.urls')),
]
