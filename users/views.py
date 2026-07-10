from django.views.generic import CreateView
from django.urls import reverse_lazy
from users.forms import RegisterForm

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
