from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from tinymce.models import HTMLField

from .helpers import to_latin

User._meta.get_field('email')._unique = True


class ShortTextMixin:
    text: str

    def short_text(self):
        soup = BeautifulSoup(self.text, 'html.parser')
        text = soup.get_text(separator=' ')
        return f'{text[:75]}...' if len(text) > 75 else text


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

    title = models.CharField(max_length=120, null=False, blank=False)
    slug = models.SlugField(max_length=180, unique=True, null=False, blank=False)
    text = HTMLField(null=False, verbose_name='Text (maximum 2000 characters)')
    date_time_create = models.DateTimeField(auto_now_add=True)
    date_time_edit = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True, null=False)

    def save(self, *args, **kwargs):
        if not self.date_time_create:
            self.date_time_create = timezone.now()
        if not self.slug:
            date_time = self.date_time_create.strftime("%Y-%m-%d-%H-%M-%S")
            slug = slugify(f'{self.title}-{date_time}', allow_unicode=True)
            self.slug = to_latin(slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Post {self.id} (author: {self.author.user.username})'


class Comment(models.Model, ShortTextMixin):
    text: str

    text = models.CharField(max_length=500, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
