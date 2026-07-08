from django.views.generic import TemplateView


class RegisterView(TemplateView):
    # TODO PIXELS-010
    template_name = 'users/register.html'
