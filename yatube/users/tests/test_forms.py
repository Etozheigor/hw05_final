from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'username',
            'email': 'test@gmail.com',
            'password1': 'выалаываалжыдв21',
            'password2': 'выалаываалжыдв21'}

        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True)

        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Имя',
                last_name='Фамилия',
                username='username',
                email='test@gmail.com',
            ).exists())
