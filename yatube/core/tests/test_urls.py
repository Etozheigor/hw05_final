from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
