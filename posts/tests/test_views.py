import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page, Paginator
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()


def get_field_context(context, field_type):
    for field in context.keys():
        if field not in ('user',
                         'request') and type(context[field]) == field_type:
            return context[field]
    return


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(username='vlad')
        cls.user_2 = User.objects.create(username='test')
        # Создадим запись в БД для проверки доступности адреса
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-slug',
            description='Описание'
        )
        cls.group_2 = Group.objects.create(
            title='Заголовок тестовой задачи второй группы',
            slug='second-slug',
            description='Описание второй группы'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user,
            image=cls.image,
        )
        posts = [Post(text='Текст',
                      group=cls.group, author=cls.user) for i in range(12)]
        Post.objects.bulk_create(posts)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.my_cache = caches['default']
        self.my_cache.clear()
        self.my_cache.close()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'posts/new_post.html': reverse('new_post'),
            'group.html': reverse('group',
                                  kwargs={'slug': ViewsTests.group.slug}),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_uses_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_uses_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': ViewsTests.group.slug})
        )
        self.assertEqual(response.context.get('group'), self.group)
        paginator_context = get_field_context(response.context, Paginator)
        assert paginator_context is not None, (
            'Проверьте, что передали паджинатор  типа `Paginator`'
        )
        group_context = get_field_context(response.context, Group)
        assert group_context is not None, (
            'Проверьте, что передали руппу типа `Group`'
        )
        page_context = get_field_context(response.context, Page)
        assert page_context is not None, (
            'Проверьте, что передали Page типа `Page`'
        )
        obj_list = ViewsTests.group.posts.order_by('-pub_date').all()[:10]
        expected_object_list = list(obj_list)
        self.assertEqual(expected_object_list,
                         response.context.get('page').object_list)

    def test_index_page_uses_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        obj_list = Post.objects.order_by('-pub_date').all()[:10]
        expected_object_list = list(obj_list)
        self.assertEqual(expected_object_list,
                         response.context.get('page').object_list)

    def test_username_post_id_edit_uses_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user, 'post_id': ViewsTests.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_username_uses_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile',
            kwargs={'username': self.user}))
        obj_list = self.user.posts.order_by('-pub_date').all()[:10]
        expected_object_list = list(obj_list)
        self.assertEqual(expected_object_list,
                         response.context.get('page').object_list)

    def test_username_post_id_uses_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post',
            kwargs={'username': self.user, 'post_id': ViewsTests.post.pk}))
        self.assertEqual(response.context.get('post'), self.post)

    def post_in_group(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': ViewsTests.group.slug})
        )
        self.assertIn(self.post, response.context['page'])

    def test_group2_has_no_post(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': ViewsTests.group_2.slug})
        )
        self.assertNotIn(self.post, response.context['page'])

    def test_padginator(self):
        """Паджинатор передает установленное количество постов"""
        response = self.guest_client.get(reverse('index'))
        post_quantity = len(response.context.get('page').object_list)
        self.assertEqual(post_quantity, 10)

    def test_cache_index_page(self):
        response_1 = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Hi',
            author=self.user
        )
        response_2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(response_1.content, response_2.content)
        self.my_cache.clear()
        response_3 = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(response_2.content, response_3.content)

    def test_follow_authorized(self):
        """Авторизованный пользователь может подписываться"""
        self.authorized_client_2.get(reverse(
            'profile_follow',
            kwargs={'username': self.user}))
        exist = Follow.objects.filter(user=self.user_2).exists()
        self.assertTrue(exist)

    def test_unfollow_authorized(self):
        """Авторизованный пользователь может отписываться"""
        self.authorized_client_2.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.user}))
        not_exist = Follow.objects.filter(user=self.user_2).exists()
        self.assertFalse(not_exist)

    def test_show_follow_posts(self):
        """Посты подписки видны в избранном"""
        self.authorized_client_2.get(reverse(
            'profile_follow',
            kwargs={'username': self.user}))
        response = self.authorized_client_2.get(reverse('follow_index'))
        obj_list = Post.objects.order_by('-pub_date').all()[:10]
        expected_object_list = list(obj_list)
        self.assertEqual(expected_object_list,
                         response.context.get('page').object_list)

    def test_dont_show_unfollow_posts(self):
        """Посты без подписки не видны в избранном"""
        user_3 = User.objects.create(username='somebody')
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(user_3)
        Post.objects.create(
            text='ABC',
            author=user_3,
        )
        self.authorized_client_2.get(reverse(
            'profile_follow',
            kwargs={'username': user_3}))
        response = self.authorized_client_2.get(reverse('follow_index'))
        object = response.context.get('page').object_list
        self.assertEqual(len(object), 1)
        self.assertEqual(object[0].text, 'ABC')
