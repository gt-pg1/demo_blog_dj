from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Author, Content, Comment


@receiver(post_save, sender=User)
def create_author(sender, instance, created, **kwargs):
    """
    Signal handler function that creates a new record in the related 'Author' table
    after saving a record in the 'User' table.


    Args:
        sender (Type[User]): The sender of the signal (User model class).
        instance (User): The User instance that was saved.
        created (bool): A flag indicating whether the User instance was created or not.
        **kwargs: Additional keyword arguments.


    Returns:
        None
    """
    if created:
        Author.objects.create(user=instance,
                              date_last_active=timezone.now(),
                              phone=None)


@receiver(user_logged_in)
def update_author_last_active_login(sender, user, **kwargs):
    """
    Signal handler function that updates the 'date_last_active' field of the related 'Author' record
    when a user logs in.

    Args:
        sender: The sender of the signal.
        user (User): The User instance that logged in.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    author = Author.objects.get(user=user)
    author.date_last_active = timezone.now()
    author.save()


@receiver(user_logged_out)
def update_author_last_active_logout(sender, user, **kwargs):
    """
    Signal handler function that updates the 'date_last_active' field of the related 'Author' record
    when a user logs out.

    Args:
        sender: The sender of the signal.
        user (User): The User instance that logged out.
        **kwargs: Additional keyword arguments.


    Returns:
        None
    """
    author = Author.objects.get(user=user)
    author.date_last_active = timezone.now()
    author.save()


@receiver(post_save, sender=Content)
def update_author_last_active_content(sender, instance, created, **kwargs):
    """
    Signal handler function that updates the 'date_last_active' field of the related 'Author' record
    when a new Content object is created.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Content): The Content object that was saved.
        created (bool): A boolean value indicating if the Content object was created or updated.

    Returns:
        None
    """
    if created:
        author = instance.author
        author.date_last_active = timezone.now()
        author.save()


@receiver(post_save, sender=Comment)
def update_author_last_active_comment(sender, instance, created, **kwargs):
    """
    Signal handler function that updates the 'date_last_active' field of the related 'Author' record
    when a new Comment object is created.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Comment): The Comment object that was saved.
        created (bool): A boolean value indicating if the Comment object was created or updated.

    Returns:
        None
    """
    if created:
        author = instance.author
        author.date_last_active = timezone.now()
        author.save()


@receiver(pre_save, sender=Content)
def update_author_last_active_edit_content(sender, instance, **kwargs):
    """
    Signal handler function that updates the 'date_last_active' field of the related 'Author' record
    when a Content object is being edited.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Content): The Content object that is being saved.

    Returns:
        None
    """
    try:
        original_instance = Content.objects.get(pk=instance.pk)
    except Content.DoesNotExist:
        return

    author = instance.author
    author.date_last_active = timezone.now()
    author.save()
