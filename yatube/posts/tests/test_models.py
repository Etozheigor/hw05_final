from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длиной более пятнадцати символов ')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_name = post.text[:15]

        self.assertEqual(expected_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях объекта поста совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {'text': 'Текст',
                          'pub_date': 'Дата публикации',
                          'author': 'Автор',
                          'group': 'Группа'}

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях объекта поста совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Группа, к которой'
                                     'будет относиться пост'}

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = GroupModelTest.group
        expected_name = group.title

        self.assertEqual(expected_name, str(group))

    def test_verbouse_name(self):
        """verbose_name в полях объекта группы совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {'title': 'Название',
                          'slug': 'имя в url',
                          'description': 'Описание'}

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(group._meta.get_field(field).verbose_name,
                                 expected_value)
