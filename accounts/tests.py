from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='senha-forte-123',
        )

    def test_common_user_can_login_with_username_and_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'password': 'senha-forte-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertFalse(get_user(self.client).is_superuser)

    def test_common_user_can_login_with_email_and_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'senha-forte-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertFalse(get_user(self.client).is_superuser)

    def test_profile_requires_only_authenticated_common_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('perfil'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user(self.client).is_superuser)
