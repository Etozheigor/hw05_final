from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user2 = User.objects.create_user(username='HasNoName2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост')
        cls.index = reverse('posts:index')
        cls.follow = reverse('posts:follow_index')
        cls.group_list = reverse(('posts:group_list'),
                                 kwargs={'slug': f'{cls.group.slug}'})
        cls.profile = reverse(('posts:profile'),
                              kwargs={'username': f'{cls.user.username}'})
        cls.profile_follow = reverse(
            ('posts:profile_follow'),
            kwargs={'username': f'{cls.user.username}'})
        cls.profile_unfollow = reverse(
            ('posts:profile_unfollow'),
            kwargs={'username': f'{cls.user.username}'})
        cls.detail = reverse(('posts:post_detail'),
                             kwargs={'post_id': f'{cls.post.id}'})
        cls.edit = reverse(('posts:post_edit'),
                           kwargs={'post_id': f'{cls.post.id}'})
        cls.comment = reverse(
            ('posts:add_comment'),
            kwargs={'post_id': f'{cls.post.id}'})
        cls.create = reverse('posts:post_create')
        cls.templates = {
            cls.index: 'posts/index.html',
            cls.follow: 'posts/follow.html',
            cls.group_list: 'posts/group_list.html',
            cls.profile: 'posts/profile.html',
            cls.detail: 'posts/post_detail.html',
            cls.edit: 'posts/create_post.html',
            cls.create: 'posts/create_post.html'}

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_not_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_not_author.force_login(self.user2)

    def test_home_url_available_for_any(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(self.index)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_available_for_any(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(self.group_list)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_username_url_available_for_any(self):
        """Страница /profile/<username>/ доступна любому пользователю."""
        response = self.guest_client.get(self.profile)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_available_for_any(self):
        """Страница /unexisting_page/ недоступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_id_url_available_for_any(self):
        """Страница /posts/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(self.detail)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_available_for_autorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.create)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_url_available_for_autorized(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.follow)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test__edit_url_available_for_author(self):
        """Страница /posts/<post_id>/edit доступна автору."""
        response = self.authorized_client.get(self.edit)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.create, follow=True)

        self.assertRedirects(
            response, f'/auth/login/?next={self.create}')

    def test_edit_url_redirect_anonymous_on_login(self):
        """Страница по адресу /posts/<post_id>/edit перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.edit,
                                         follow=True)

        self.assertRedirects(
            response, (f'/auth/login/?next={self.edit}'),
            status_code=HTTPStatus.FOUND)

    def test_comment_url_redirect_anonymous_on_login(self):
        """Страница по адресу /posts/<post_id>/comment перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.comment,
                                         follow=True)

        self.assertRedirects(
            response, (f'/auth/login/?next={self.comment}'),
            status_code=HTTPStatus.FOUND)

    def test_follow_url_redirect_anonymous_on_login(self):
        """Страница по адресу /follow/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.follow,
                                         follow=True)

        self.assertRedirects(
            response, (f'/auth/login/?next={self.follow}'),
            status_code=HTTPStatus.FOUND)

    def test_profile_follow_url_redirect_anonymous_on_login(self):
        """Страница по адресу /profile/username/follow/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.profile_follow,
                                         follow=True)

        self.assertRedirects(
            response, (f'/auth/login/?next={self.profile_follow}'),
            status_code=HTTPStatus.FOUND)

    def test_profile_unfollow_url_redirect_anonymous_on_login(self):
        """Страница по адресу /profile/username/unfollow/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get(self.profile_unfollow,
                                         follow=True)

        self.assertRedirects(
            response, (f'/auth/login/?next={self.profile_unfollow}'),
            status_code=HTTPStatus.FOUND)

    def test_profile_follow_url_redirect_authorized_on_profile(self):
        """Страница по адресу /profile/username/follow/ перенаправит залогиненного
        пользователя на страницу профиля."""
        response = self.authorized_client.get(self.profile_follow,
                                              follow=True)

        self.assertRedirects(
            response, (self.profile),
            status_code=HTTPStatus.FOUND)

    def test_profile_unfollow_url_redirect_authorized_on_profile(self):
        """Страница по адресу /profile/username/unfollow/ перенаправит залогиненного
        пользователя на страницу профиля."""
        response = self.authorized_client.get(self.profile_unfollow,
                                              follow=True)

        self.assertRedirects(
            response, (self.profile),
            status_code=HTTPStatus.FOUND)

    def test_comment_url_redirect_authorized_on_post_details(self):
        """Страница по адресу /posts/<post_id>/comment перенаправит залогиненного
        пользователя на страницу поста."""
        response = self.authorized_client.get(self.comment,
                                              follow=True)

        self.assertRedirects(
            response, (self.detail),
            status_code=HTTPStatus.FOUND)

    def test_edit_url_redirect_not_author_on_post_id(self):
        """Страница по адресу /posts/<post_id>/edit
        перенаправит не автора на страницу поста."""
        response = self.authorized_not_author.get(self.edit, follow=True)

        self.assertRedirects(
            response, (self.detail),
            status_code=HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for address, template in self.templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
