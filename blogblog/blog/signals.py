from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Author, Content, Comment

# All functions here are responsible for the correct track date_last_active
@receiver(post_save, sender=User)
def create_author(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance,
                              date_last_active=timezone.now(),
                              phone=None)


@receiver(user_logged_in)
def update_author_last_active_login(sender, user, request, **kwargs):
    author = Author.objects.get(user=user)
    author.date_last_active = timezone.now()
    author.save()


@receiver(user_logged_out)
def update_author_last_active_logout(sender, user, request, **kwargs):
    author = Author.objects.get(user=user)
    author.date_last_active = timezone.now()
    author.save()


@receiver(post_save, sender=Content)
def update_author_last_active_content(sender, instance, created, **kwargs):
    if created:
        author = instance.author
        author.date_last_active = timezone.now()
        author.save()


@receiver(post_save, sender=Comment)
def update_author_last_active_comment(sender, instance, created, **kwargs):
    if created:
        author = instance.author
        author.date_last_active = timezone.now()
        author.save()


@receiver(pre_save, sender=Content)
def update_author_last_active_edit_content(sender, instance, **kwargs):
    try:
        original_instance = Content.objects.get(pk=instance.pk)
    except Content.DoesNotExist:
        return

    author = instance.author
    author.date_last_active = timezone.now()
    author.save()