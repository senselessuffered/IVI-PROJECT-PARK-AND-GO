from django.urls import path
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView

from users import views

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
