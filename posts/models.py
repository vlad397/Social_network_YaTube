from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts",
                              verbose_name='Группа',
                              help_text='Выберите из списка')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение',
                              help_text='Выберите изображение')

    class Meta():
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             blank=True, null=True, related_name="comments",
                             verbose_name='Комментарий',
                             help_text='Напишите комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст комментария')
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta():
        ordering = ["-pub_date"]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
    
    class Meta():
        models.UniqueConstraint(fields=['user', 'author'], name='author-user_unique')