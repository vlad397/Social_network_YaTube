from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='vlad')
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='123456789123456789',
            author=cls.user,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = ModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите из списка'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        group = ModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_only_15_symbols(self):
        self.assertEqual(len(self.post.__str__()), 15)
