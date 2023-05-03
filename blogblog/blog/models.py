from django.contrib.auth.models import User
from django.db import models

User._meta.get_field('email')._unique = True


class ShortTextMixin:
    text: str

    def short_text(self):
        return f'{self.text[:75]}...' if len(self.text) > 75 else self.text


class Author(models.Model):
    user: User

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_last_active = models.DateTimeField()
    phone = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        if self.user.first_name or self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        else:
            return f'{self.user.username}'


class Content(models.Model, ShortTextMixin):
    id: int
    text: str

    text = models.TextField(max_length=2000, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    date_time_edit = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True, null=False)

    def __str__(self):
        return f'Post {self.id} (author: {self.author.user.username})'


class Comment(models.Model, ShortTextMixin):
    text: str

    text = models.CharField(max_length=500, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
