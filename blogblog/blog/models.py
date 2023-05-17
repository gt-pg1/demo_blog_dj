from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from tinymce.models import HTMLField

from .helpers import to_latin

User._meta.get_field('email')._unique = True


class ShortTextMixin:
    """
    Mixin for shortening the text of an article for convenient display in previews.
    """

    text: str

    def short_text(self):
        """
        Returns a shortened version of the text's.

        The text is reduced to 75 characters, or it is not reduced if it contains fewer characters.
        The BeautifulSoup parser is used to remove unnecessary characters and tags from the HTML.

        Returns:
            str: Shortened text.
        """
        soup = BeautifulSoup(self.text, 'html.parser')
        text = soup.get_text(separator=' ')
        return f'{text[:75]}...' if len(text) > 75 else text


class Author(models.Model):
    """
    Model representing an author.

    An author is associated with a user and contains additional information such as the last active date and phone number.
    """

    user: User

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_last_active = models.DateTimeField()
    phone = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the author.

        If the author's first name or last name is available, it will be included in the string representation.
        Otherwise, the username will be used.

        Returns:
            str: String representation of the author.
        """
        if self.user.first_name or self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        else:
            return f'{self.user.username}'


class Content(models.Model, ShortTextMixin):
    """
    Model representing a content.

    This model includes fields such as title, slug, text, creation date and time, last edit date and time,
    author, and publication status.

    It inherits from the `ShortTextMixin` to provide a method for shortening the text of the article.
    """

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
        """
        Overrides the default save method to set the creation date, generate a slug, and save the instance.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if not self.date_time_create:
            self.date_time_create = timezone.now()
        if not self.slug:
            date_time = self.date_time_create.strftime("%Y-%m-%d-%H-%M-%S")
            slug = slugify(f'{self.title}-{date_time}', allow_unicode=True)
            self.slug = to_latin(slug)
        super().save(*args, **kwargs)

    def unpublish(self):
        """
        Sets the `is_published` field of the content to False and saves the instance.

        Returns:
            None
        """
        self.is_published = False
        self.save()

    def publish(self):
        """
        Sets the `is_published` field of the content to True and saves the instance.

        Returns:
            None
        """
        self.is_published = True
        self.save()

    def __str__(self):
        """
        Returns a string representation of the content.

        This method returns a string in the format "Post <id> (author: <author_username>)",
        where <id> is the ID of the content and <author_username> is the username of the content's author.

        Returns:
            str: String representation of the content.
        """
        return f'Post {self.id} (author: {self.author.user.username})'


class Comment(models.Model, ShortTextMixin):
    """
    Model representing a comments.

    This model stores information about comments made on the content.
    It inherits from the `ShortTextMixin` to provide a method for shortening the text of the comment.
    """

    text: str

    text = models.CharField(max_length=500, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
