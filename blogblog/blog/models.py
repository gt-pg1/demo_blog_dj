from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage


# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_last_active = models.DateTimeField()
    phone = models.CharField(max_length=25, null=True, blank=True)


class Content(models.Model):
    text = models.TextField(max_length=2000, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    date_time_edit = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True, null=False)


class Comment(models.Model):
    text = models.CharField(max_length=500, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
