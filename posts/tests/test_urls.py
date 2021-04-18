from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создадим запись в БД для проверки доступности адреса
        cls.user = User.objects.create(username='vlad397')
        cls.user2 = User.objects.create(username='ne_vlad')
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='Текст сообщения',
            author=cls.user,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    # Проверка редиректов
    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/new/'))

    def test_username_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница перенаправит анонимного
        пользователя с /<username>/<post_id>/edit/ на страницу логина.
        """
        response = self.guest_client.get('/vlad397/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/vlad397/1/edit/'))

    def test_username_post_id_edit_url_redirects_user_no_author(self):
        """Страница перенаправит пользователя не автора поста
        с /<username>/<post_id>/edit/ на страницу поста /<username>/<post_id>/.
        """
        response = self.authorized_client2.get('/vlad397/1/edit/')
        self.assertRedirects(
            response, '/vlad397/1/')

    # Проверка вызываемых шаблонов для каждого адреса:
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'posts/new_post.html',
            '/group/test-slug/': 'group.html',
            '/vlad397/1/edit/': 'posts/new_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # Проверка доступности страниц
    def test_pages_avaliable_non_authorized(self):
        """Перечисленные страницы доступны любому пользователю"""
        urls = [
            '/',
            '/group/test-slug/',
            '/vlad397/',
            '/vlad397/1/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_pages_avaliable_authorized(self):
        """Перечисленные страницы доступны авторизованному пользователю"""
        urls = [
            '/',
            '/new/',
            '/group/test-slug/',
            '/vlad397/',
            '/vlad397/1/',
            '/vlad397/1/edit',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def page_not_found(self):
        response = self.authorized_client.get('/no-page', follow=True)
        self.assertEqual(response.status_code, 404)
