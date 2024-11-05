from django.test import TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

class ProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_profile_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_edit_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_edit'), {
            'username': 'newusername',
            'email': 'newemail@example.com'
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')
# Create your tests here.
