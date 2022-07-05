from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_password_reset_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_password_reset_done_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/done доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_reset_slug_token_url_exists_at_desired_location(self):
        """Страница /auth/reset/<uidb64>/<token>/
         доступна любому пользователю."""
        response = self.guest_client.get('/auth/reset/<uidb64>/<token>/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_reset_done_url_exists_at_desired_location(self):
        """Страница /auth/reset/done/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/reset/done/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_exists_at_desired_location_autorized(self):
        """Страница /auth/password_change/
         доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url_exists_at_desired_location_author(self):
        """Страница /auth/password_change/done/ доступна автору."""
        response = self.authorized_client.get('/auth/password_change/done/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /auth/password_change/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/', follow=True)

        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/'
        )

    def test_password_change_done_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /auth/password_change/done/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/done/',
                                         follow=True)

        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/done/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html'}

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
