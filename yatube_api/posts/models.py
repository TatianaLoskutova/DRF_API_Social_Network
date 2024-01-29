from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from rest_framework.exceptions import ValidationError

User = get_user_model()

MAX_VISIBLE_TEXT_LENGTH = 30


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f'Заголовок группы: {self.title[:MAX_VISIBLE_TEXT_LENGTH]}'


class Post(models.Model):
    text = models.TextField(blank=False, verbose_name='Текст публикации')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата и время публикации',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор публикации',
    )
    image = models.ImageField(
        upload_to='posts/', null=True, blank=True, verbose_name='Изображение',
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True,
        null=True, verbose_name='Группа',
    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('pub_date',)

    def __str__(self):
        return f'Автор: {self.author}, ' \
               f'Текст: {self.text[:MAX_VISIBLE_TEXT_LENGTH]}'


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name='Публикация',
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Дата и время комментария',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'Автор: {self.author}, Пост: {self.post}, ' \
               f'Текст: {self.text[:MAX_VISIBLE_TEXT_LENGTH]}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Подписчики',
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=('user', 'following'), name='unique_following')
        ]

    def clean(self):
        if self.user == self.following:
            raise ValidationError(
                'Пользователь не может подписаться на себя самого.'
            )

    def __str__(self):
        return f'{self.user} follows {self.following}'
