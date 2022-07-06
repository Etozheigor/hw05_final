import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.follower_user = User.objects.create_user(username='follower')
        cls.nofollower_user = User.objects.create_user(username='nofollower')
        Follow.objects.create(user=cls.follower_user,
                              author=cls.nofollower_user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded)
        cls.index = reverse('posts:index')
        cls.follow = reverse('posts:follow_index')
        cls.group_list = reverse(
            ('posts:group_list'),
            kwargs={'slug': f'{cls.group.slug}'})
        cls.profile = reverse(
            ('posts:profile'),
            kwargs={'username': f'{cls.user.username}'})
        cls.profile_follow = reverse(
            ('posts:profile_follow'),
            kwargs={'username': f'{cls.user.username}'})
        cls.profile_unfollow = reverse(
            ('posts:profile_unfollow'),
            kwargs={'username': f'{cls.user.username}'})
        cls.detail = reverse(
            ('posts:post_detail'),
            kwargs={'post_id': f'{cls.post.id}'})
        cls.edit = reverse(
            ('posts:post_edit'),
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = Client()
        self.nofollower = Client()
        self.follower.force_login(self.follower_user)
        self.nofollower.force_login(self.nofollower_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index)
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object, self.post)

    def test_follow_page_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        follower_post = Post.objects.create(
            author=self.follower_user,
            text='Тестовый пост подписчика')
        nofollower_post = Post.objects.create(
            author=self.nofollower_user,
            text='Тестовый пост автора')
        follower_response = self.follower.get(self.follow)
        nofollower_response = self.nofollower.get(self.follow)

        self.assertIn(nofollower_post, follower_response.context['page_obj'])
        self.assertNotIn(follower_post,
                         nofollower_response.context['page_obj'])
        self.assertEqual(follower_response.context.get('is_following'),
                         True)
        self.assertEqual(nofollower_response.context.get('is_following'),
                         False)
        follower_post.delete()
        nofollower_post.delete()

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        another_user = User.objects.create_user(username='ZAnotherName')
        another_group = Group.objects.create(
            title='Тестовая группа #2',
            slug='test_2',
            description='Тестовое описание #2')
        post_with_another_group = Post.objects.create(
            author=another_user,
            text='Тестовый пост #2',
            group=another_group)

        response = self.authorized_client.get(self.group_list)
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object, self.post)
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').slug, 'test')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание')
        self.assertNotIn(post_with_another_group, response.context['page_obj'])
        del post_with_another_group

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self_follow = Follow.objects.create(user=self.follower_user,
                                            author=self.follower_user)
        response = self.authorized_client.get(self.profile)
        follower_response = self.follower.get(
            reverse(('posts:profile'),
                    kwargs={'username': f'{self.nofollower_user.username}'}))
        nofollower_response = self.nofollower.get(
            reverse(('posts:profile'),
                    kwargs={'username': f'{self.follower_user.username}'}))
        self_follower_response = self.follower.get(
            reverse(('posts:profile'),
                    kwargs={'username': f'{self.follower_user.username}'}))
        first_object = response.context['page_obj'][0]

        self.assertEqual(follower_response.context.get('following'),
                         True)
        self.assertEqual(nofollower_response.context.get('following'), False)
        self.assertEqual(self_follower_response.context.get('is_self_author'),
                         True)
        self.assertEqual(nofollower_response.context.get('is_self_author'),
                         False)
        self.assertEqual(first_object, self.post)
        self.assertEqual(response.context.get('author').username, 'HasNoName')
        self.assertEqual(response.context.get('author_posts_count'), 1)
        self.assertEqual(response.context.get('is_profile'), True)
        self_follow.delete()

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        comment = Comment.objects.create(text='Тестовый коммент',
                                         post=self.post,
                                         author=self.user)
        response = self.authorized_client.get(self.detail)
        post_object = response.context['post']
        post_text = post_object.text
        post_author = post_object.author.username
        post_image = post_object.image
        form_fields = {
            'text': forms.fields.CharField}

        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_author, f'{self.user}')
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertEqual(response.context.get('comments')[0], comment)
        self.assertEqual(response.context.get('author_posts_count'), 1)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.create)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.edit)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.follower_user = User.objects.create_user(username='follower')
        Follow.objects.create(user=cls.follower_user, author=cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group)
        cls.reverse_names = (
            (reverse('posts:index')),
            (reverse(('posts:group_list'),
                     kwargs={'slug': f'{cls.group.slug}'})),
            (reverse(('posts:profile'),
                     kwargs={'username': f'{cls.user.username}'})),
            reverse('posts:follow_index')
        )

    def setUp(self):
        cache.clear()
        self.follower = Client()
        self.follower.force_login(self.follower_user)

    def test_first_page_contains_ten_records(self):
        """ Проверка: на первой странице должно быть десять постов."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.follower.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """ Проверка: на второй странице должно быть три поста."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.follower.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(author=cls.user,
                                       text='Тестовый текст')
        cls.comment = Comment.objects.create(text='Тестовый коммент',
                                             post=cls.post,
                                             author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_page_show_correct_context(self):
        """Комментарий отображается на странице поста """
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))
        comment_obj = response.context['comments'][0]

        self.assertEqual(comment_obj, self.comment)


class CacheTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_index_page_being_cached(self):
        """Главная страница кэшируется"""
        user = User.objects.create_user(username='TestUser')
        post = Post.objects.create(author=user,
                                   text='Тестовый текст')

        response_content = self.guest_client.get(
            reverse('posts:index')).content
        post.delete()
        response_content_post_delete = self.guest_client.get(
            reverse('posts:index')).content
        cache.clear()
        response_content_cache_delete = self.guest_client.get(
            reverse('posts:index')).content

        self.assertEqual(response_content, response_content_post_delete)
        self.assertNotEqual(response_content, response_content_cache_delete)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_user = User.objects.create_user(username='user')
        cls.user_author = User.objects.create_user(username='author')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.user = Client()
        self.author = Client()
        self.user.force_login(self.user_user)
        self.author.force_login(self.user_author)

    def test_authenticated_user_can_follow(self):
        """Залогиненный пользователь может подписаться на  авторов,
        при этом нельзя подписаться, если он уже подписан"""
        follow_count = Follow.objects.count()

        self.user.get(
            reverse(('posts:profile_follow'),
                    kwargs={'username': f'{self.user_author.username}'}))
        self.user.get(
            reverse(('posts:profile_follow'),
                    kwargs={'username': f'{self.user_author.username}'}))

        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(user=self.user_user,
                                  author=self.user_author).exists())

    def test_authenticated_user_can_unfollow(self):
        """Залогиненный пользователь может отписаться от авторов,
        при этом нельзя отписаться, если он уже отписан"""
        follow_count = Follow.objects.count()

        self.user.get(
            reverse(('posts:profile_follow'),
                    kwargs={'username': f'{self.user_author.username}'}))
        self.user.get(
            reverse(('posts:profile_unfollow'),
                    kwargs={'username': f'{self.user_author.username}'}))
        self.user.get(
            reverse(('posts:profile_unfollow'),
                    kwargs={'username': f'{self.user_author.username}'}))

        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(
            Follow.objects.filter(user=self.user_user,
                                  author=self.user_author).exists())

    def test_authenticated_user_cant_follow_himself(self):
        """Залогиненный пользователь не может подписаться на самого себя"""
        follow_count = Follow.objects.count()

        self.user.get(
            reverse(('posts:profile_follow'),
                    kwargs={'username': f'{self.user_user.username}'}))

        self.assertEqual(Follow.objects.count(), follow_count)
