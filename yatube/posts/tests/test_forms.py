import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded}

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)

        self.assertRedirects(response, reverse(('posts:profile'),
                             kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        new_post = Post.objects.filter(text='Тестовый текст',
                                       group=self.group.id,
                                       image='posts/small.gif')
        self.assertTrue(new_post.exists())
        new_post.delete()

    def test_cant_create_post_without_text(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': ' '}

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form',
            'text',
            ['Обязательное поле.'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый отредактированный текст'}

        response = self.authorized_client.post(
            reverse(('posts:post_edit'),
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True)

        self.assertRedirects(response, reverse(('posts:post_detail'),
                             kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый отредактированный текст',
            ).exists())

    def test_cant_edit_post_without_text(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': ' '}

        response = self.authorized_client.post(
            reverse(('posts:post_edit'),
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True)

        self.assertEqual(self.post, Post.objects.get(text='Тестовый пост'))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_text_label(self):
        text_label = self.form.fields['text'].label

        self.assertEqual(text_label, 'Текст')

    def test_group_label(self):
        group_label = self.form.fields['group'].label

        self.assertEqual(group_label, 'Группа')


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий',
                     'post': self.post.id,
                     'author': self.user.username}

        self.authorized_client.post(
            reverse(('posts:add_comment'),
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True)
        new_comment = Comment.objects.filter(text='Тестовый комментарий',
                                             author=self.user,
                                             post=self.post)

        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(new_comment.exists())
