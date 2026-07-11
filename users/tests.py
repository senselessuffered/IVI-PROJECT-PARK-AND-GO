from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import resolve, reverse

from users.backends import EmailOrUsernameBackend
from users.forms import RegisterForm
from users.views import RegisterView

User = get_user_model()


class UserModelTests(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_str_method(self):
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
        )

        self.assertEqual(str(user), 'student')

    def test_get_full_name(self):
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов',
        )

        self.assertEqual(user.get_full_name(), 'Иван Иванов')

    def test_get_short_name(self):
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            first_name='Иван',
        )

        self.assertEqual(user.get_short_name(), 'Иван')


class RegisterFormTests(TestCase):

    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }

    def test_valid_form(self):
        form = RegisterForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')

    def test_empty_username(self):
        data = self.valid_data.copy()
        data['username'] = ''

        form = RegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_empty_email(self):
        data = self.valid_data.copy()
        data['email'] = ''

        form = RegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='user1',
            email='new@example.com',
            password='StrongPass123',
        )

        form = RegisterForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_passwords_not_match(self):
        data = self.valid_data.copy()
        data['password2'] = 'AnotherPass123'

        form = RegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user(
            username='newuser',
            email='another@example.com',
            password='StrongPass123',
        )

        form = RegisterForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_clean_email_success(self):
        form = RegisterForm()
        form.cleaned_data = {'email': 'test@example.com'}

        self.assertEqual(form.clean_email(), 'test@example.com')

    def test_clean_email_validation_error(self):
        User.objects.create_user(
            username='user',
            email='test@example.com',
            password='StrongPass123',
        )

        form = RegisterForm()
        form.cleaned_data = {'email': 'test@example.com'}

        with self.assertRaises(ValidationError):
            form.clean_email()


class RegisterViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:register')

        self.data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }

    def test_get_register_page(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], RegisterForm)

    def test_post_valid_data(self):
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bookings:list'))

    def test_post_invalid_data(self):
        data = self.data.copy()
        data['password2'] = '12345678'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid-feedback')

    def test_user_logged_in_after_register(self):
        self.client.post(self.url, self.data)

        response = self.client.get(reverse('bookings:list'))

        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_success_url(self):
        self.assertEqual(str(RegisterView.success_url), reverse('bookings:list'))


class UrlTests(TestCase):

    def test_login_url(self):
        resolver = resolve(reverse('users:login'))

        self.assertEqual(resolver.func.view_class, LoginView)

    def test_logout_url(self):
        resolver = resolve(reverse('users:logout'))

        self.assertEqual(resolver.func.view_class, LogoutView)

    def test_register_url(self):
        resolver = resolve(reverse('users:register'))

        self.assertEqual(resolver.func.view_class, RegisterView)

    def test_reverse_names(self):
        self.assertEqual(reverse('users:login'), '/accounts/login/')
        self.assertEqual(reverse('users:logout'), '/accounts/logout/')
        self.assertEqual(reverse('users:register'), '/accounts/register/')


class EmailOrUsernameBackendTests(TestCase):

    def setUp(self):
        self.backend = EmailOrUsernameBackend()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123',
        )

    def test_auth_by_username(self):
        user = self.backend.authenticate(
            None,
            username='testuser',
            password='StrongPass123',
        )

        self.assertEqual(user, self.user)

    def test_auth_by_email(self):
        user = self.backend.authenticate(
            None,
            username='test@example.com',
            password='StrongPass123',
        )

        self.assertEqual(user, self.user)

    def test_wrong_password(self):
        user = self.backend.authenticate(
            None,
            username='testuser',
            password='wrongpass',
        )

        self.assertIsNone(user)

    def test_user_not_exists(self):
        user = self.backend.authenticate(
            None,
            username='unknown',
            password='StrongPass123',
        )

        self.assertIsNone(user)

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        user = self.backend.authenticate(
            None,
            username='testuser',
            password='StrongPass123',
        )

        self.assertIsNone(user)

    def test_username_is_none(self):
        user = self.backend.authenticate(
            None,
            username=None,
            password='StrongPass123',
        )

        self.assertIsNone(user)

    def test_password_is_none(self):
        user = self.backend.authenticate(
            None,
            username='testuser',
            password=None,
        )

        self.assertIsNone(user)


class IntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123',
        )

    def test_register_login_logout(self):
        self.client.post(
            reverse('users:register'),
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
            },
        )

        response = self.client.get(reverse('bookings:list'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        self.client.logout()

        response = self.client.get(reverse('bookings:list'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_page_available_without_auth(self):
        response = self.client.get(reverse('users:login'))

        self.assertEqual(response.status_code, 200)

    def test_register_page_available_without_auth(self):
        response = self.client.get(reverse('users:register'))

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user(self):
        self.client.login(
            username='testuser',
            password='StrongPass123',
        )

        response = self.client.get(reverse('bookings:list'))

        self.assertTrue(response.wsgi_request.user.is_authenticated)
