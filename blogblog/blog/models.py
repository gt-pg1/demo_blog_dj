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

    Attributes:
        - text (str): The full text of the article.

    Methods:
        - short_text(): Returns a shortened version of the text.
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

    Inherits from:
        - models.Model

    Attributes:
        - user (User): The associated user for the author.
        - date_last_active (DateTimeField): The date and time of the author's last activity.
        - phone (CharField): The author's phone number (optional).
        - date_time_last_post (DateTimeField): The date and time of the author's last content post (optional).

    Methods:
        - __str__(): Returns a string representation of the author.
    """

    user: User

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_last_active = models.DateTimeField()
    phone = models.CharField(max_length=25, null=True, blank=True)
    date_time_last_post = models.DateTimeField(null=True, blank=True)

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

    Inherits from:
        - models.Model
        - ShortTextMixin

    Attributes:
        - id (int): The ID of the content.
        - title (CharField): The title of the content.
        - slug (SlugField): The slug of the content.
        - text (HTMLField): The text of the content (maximum 2000 characters). Instance of the TinyMCE editor.
        - date_time_create (DateTimeField): The date and time of content creation.
        - date_time_edit (DateTimeField): The date and time of content last edit.
        - author (ForeignKey): The author of the content.
        - is_published (BooleanField): The publication status of the content.

    Methods:
        - save(*args, **kwargs): Overrides the default save method to set the creation date, generate a slug,
          and save the instance.
        - unpublish(): Sets the is_published field of the content to False and saves the instance.
        - publish(): Sets the is_published field of the content to True and saves the instance.
        - __str__(): Returns a string representation of the content.

    Returns:
        - str: String representation of the content.

    Note:
        The 2000 character limit for the text field is not reflected in the model because the field is written HTML,
        and the restriction for the user is reflected in characters, not taking into account HTML -
        therefore, the interface and model restrictions will conflict with each other.
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
    Model representing a comment.

    Inherits from:
        - models.Model
        - ShortTextMixin

    Attributes:
        - text (CharField): The text of the comment.
        - date_time_create (DateTimeField): The date and time of comment creation.
        - author (ForeignKey): The author of the comment.
        - content (ForeignKey): The content the comment belongs to.

    Returns:
        None
    """

    text: str

    text = models.CharField(max_length=500, null=False)
    date_time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
