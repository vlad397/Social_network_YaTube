from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='vlad')
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
        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user,
        )
        # Создадим большое кол-во постов для проверки паджинатора
        posts = [Post(text='Текст',
                      group=cls.group, author=cls.user) for i in range(12)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_author_exists_at_desired_location(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get(reverse('about:author'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_exists_at_desired_location(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get(reverse('about:tech'), follow=True)
        self.assertEqual(response.status_code, 200)
