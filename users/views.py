from django.views.generic import TemplateView


class RegisterView(TemplateView):
    template_name = 'users/register.html'
