import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core import mail
from django.core.exceptions import ValidationError
from django.urls import resolve, reverse

from users.backends import EmailOrUsernameBackend
from users.forms import RegisterForm
from users.views import RegisterView

User = get_user_model()

VALID_REGISTER_DATA = {
    'username': 'newuser',
    'email': 'new@example.com',
    'password1': 'StrongPass123',
    'password2': 'StrongPass123',
}


@pytest.mark.django_db
class TestRegisterForm:
    def test_valid_form(self):
        form = RegisterForm(data=VALID_REGISTER_DATA)

        assert form.is_valid()

        user = form.save()

        assert user.username == 'newuser'
        assert user.email == 'new@example.com'

    def test_empty_username(self):
        form = RegisterForm(data={**VALID_REGISTER_DATA, 'username': ''})

        assert not form.is_valid()
        assert 'username' in form.errors

    def test_empty_email(self):
        form = RegisterForm(data={**VALID_REGISTER_DATA, 'email': ''})

        assert not form.is_valid()
        assert 'email' in form.errors

    def test_duplicate_email(self):
        User.objects.create_user(username='user1', email='new@example.com', password='StrongPass123')

        form = RegisterForm(data=VALID_REGISTER_DATA)

        assert not form.is_valid()
        assert 'email' in form.errors

    def test_passwords_not_match(self):
        form = RegisterForm(data={**VALID_REGISTER_DATA, 'password2': 'AnotherPass123'})

        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_duplicate_username(self):
        User.objects.create_user(username='newuser', email='another@example.com', password='StrongPass123')

        form = RegisterForm(data=VALID_REGISTER_DATA)

        assert not form.is_valid()
        assert 'username' in form.errors

    def test_clean_email_success(self):
        form = RegisterForm()
        form.cleaned_data = {'email': 'test@example.com'}

        assert form.clean_email() == 'test@example.com'

    def test_clean_email_validation_error(self):
        User.objects.create_user(username='user', email='test@example.com', password='StrongPass123')

        form = RegisterForm()
        form.cleaned_data = {'email': 'test@example.com'}

        with pytest.raises(ValidationError):
            form.clean_email()


@pytest.mark.django_db
class TestRegisterView:
    def register_data(self):
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }

    def test_get_register_page(self, client):
        response = client.get(reverse('users:register'))

        assert response.status_code == 200
        assert isinstance(response.context['form'], RegisterForm)

    def test_post_valid_data(self, client):
        response = client.post(reverse('users:register'), self.register_data())

        assert response.status_code == 302
        assert response.url == reverse('bookings:list')

    def test_post_invalid_data(self, client):
        data = {**self.register_data(), 'password2': '12345678'}

        response = client.post(reverse('users:register'), data)

        assert response.status_code == 200
        assert 'invalid-feedback' in response.content.decode()

    def test_user_logged_in_after_register(self, client):
        client.post(reverse('users:register'), self.register_data())

        response = client.get(reverse('bookings:list'))

        assert response.wsgi_request.user.is_authenticated

    def test_success_url(self):
        assert str(RegisterView.success_url) == reverse('bookings:list')


class TestUrls:
    def test_login_url(self):
        assert resolve(reverse('users:login')).func.view_class == LoginView

    def test_logout_url(self):
        assert resolve(reverse('users:logout')).func.view_class == LogoutView

    def test_register_url(self):
        assert resolve(reverse('users:register')).func.view_class == RegisterView

    def test_reverse_names(self):
        assert reverse('users:login') == '/accounts/login/'
        assert reverse('users:logout') == '/accounts/logout/'
        assert reverse('users:register') == '/accounts/register/'


@pytest.mark.django_db
class TestEmailOrUsernameBackend:
    def make_user(self):
        return User.objects.create_user(
            username='testuser', email='test@example.com', password='StrongPass123'
        )

    def test_auth_by_username(self):
        user = self.make_user()

        result = EmailOrUsernameBackend().authenticate(None, username='testuser', password='StrongPass123')

        assert result == user

    def test_auth_by_email(self):
        user = self.make_user()

        result = EmailOrUsernameBackend().authenticate(None, username='test@example.com', password='StrongPass123')

        assert result == user

    def test_wrong_password(self):
        self.make_user()

        result = EmailOrUsernameBackend().authenticate(None, username='testuser', password='wrongpass')

        assert result is None

    def test_user_not_exists(self):
        result = EmailOrUsernameBackend().authenticate(None, username='unknown', password='StrongPass123')

        assert result is None

    def test_inactive_user(self):
        user = self.make_user()
        user.is_active = False
        user.save()

        result = EmailOrUsernameBackend().authenticate(None, username='testuser', password='StrongPass123')

        assert result is None

    def test_username_is_none(self):
        self.make_user()

        result = EmailOrUsernameBackend().authenticate(None, username=None, password='StrongPass123')

        assert result is None

    def test_password_is_none(self):
        self.make_user()

        result = EmailOrUsernameBackend().authenticate(None, username='testuser', password=None)

        assert result is None


@pytest.mark.django_db
class TestPasswordReset:
    def make_user(self):
        return User.objects.create_user(username='bob', email='bob@example.com', password='oldpass12345')

    def reset_path_from_email(self, body):
        return re.search(r'/accounts/reset/[^\s]+', body).group(0)

    def test_reset_form_available(self, client):
        response = client.get(reverse('users:password_reset'))

        assert response.status_code == 200

    def test_reset_sends_email_to_known_address(self, client):
        self.make_user()

        response = client.post(reverse('users:password_reset'), {'email': 'bob@example.com'})

        assert response.status_code == 302
        assert response.url == reverse('users:password_reset_done')
        assert len(mail.outbox) == 1
        assert 'bob@example.com' in mail.outbox[0].to

    def test_reset_unknown_email_sends_nothing(self, client):
        self.make_user()

        response = client.post(reverse('users:password_reset'), {'email': 'nobody@example.com'})

        assert response.status_code == 302
        assert len(mail.outbox) == 0

    def test_full_flow_allows_login_with_new_password(self, client):
        user = self.make_user()
        client.post(reverse('users:password_reset'), {'email': 'bob@example.com'})
        confirm_path = self.reset_path_from_email(mail.outbox[0].body)

        set_password_response = client.get(confirm_path)
        assert set_password_response.status_code == 302

        response = client.post(
            set_password_response.url,
            {'new_password1': 'brandnew98765', 'new_password2': 'brandnew98765'},
        )

        assert response.status_code == 302
        assert response.url == reverse('users:password_reset_complete')
        user.refresh_from_db()
        assert user.check_password('brandnew98765')
