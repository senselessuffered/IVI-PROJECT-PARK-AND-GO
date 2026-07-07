from django.urls import path
from django.views.generic import RedirectView, TemplateView

from users import views

app_name = 'users'

urlpatterns = [
    path('login/', TemplateView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', RedirectView.as_view(pattern_name='bookings:list'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
