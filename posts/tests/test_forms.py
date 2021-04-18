import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(username='vlad')
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            slug='test-slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='Текст сообщения',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse('new_post'),
                                               data=form_data, follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='Текст').exists())
        self.assertEqual(Post.objects.first().group,
                         self.group)
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())

    def test_post_edit(self):
        form_fields = {
            'text': 'Новый текст',
        }
        self.authorized_client.post(reverse(
            'post_edit',
            kwargs={'username': self.user, 'post_id': FormsTests.post.pk}),
            data=form_fields)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Новый текст')
