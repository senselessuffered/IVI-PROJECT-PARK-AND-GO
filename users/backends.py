from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        if username is None or password is None:
            return None
        try:
            user = user_model.objects.get(username__iexact=username)
        except user_model.DoesNotExist:
            try:
                user = user_model.objects.get(email__iexact=username)
            except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
                user_model().set_password(password)
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
