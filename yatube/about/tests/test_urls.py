from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница /about/tech/ доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {'/about/author/': 'about/author.html',
                               '/about/tech/': 'about/tech.html'}

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
