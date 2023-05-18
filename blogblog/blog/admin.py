from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .forms import AdminUserCreationForm
from .models import Content, Author, Comment


class UserProfileInline(admin.StackedInline):
    """
    Inline model definition for the Author model.

    Inherits from:
        - admin.StackedInline

    Attributes:
        - model (Author): The model associated with the inline.
        - can_delete (bool): Specifies whether the inline can be deleted.

    Returns:
        None
    """

    model = Author
    can_delete = False


class AuthorAdmin(UserAdmin):
    """
    Custom UserAdmin for managing authors.

    Inherits from:
        - UserAdmin

    Attributes:
        - inlines (list): Specifies the inline models to be displayed and edited at the same time.
        - add_form (AdminUserCreationForm): Specifies the form for adding a new user.
        - add_fieldsets (tuple): Defines the fieldsets for the add form.
        - list_display (list): Specifies the fields to be displayed in the list view of the User model.

    Methods:
        - get_fieldsets(request, obj=None): Returns the fieldsets for the UserAdmin form.

    Returns:
        None
    """

    inlines = [UserProfileInline]
    add_form = AdminUserCreationForm
    add_fieldsets = (
        (None, {
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'phone'
            ),
        }),
    )
    list_display = ['username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'is_active']

    def get_fieldsets(self, request, obj=None):
        """
        Returns the fieldsets for the UserAdmin form.

        This method overrides the default implementation to hide the Permissions block
        for all users except superusers.

        Args:
            request (HttpRequest): The current HTTP request.
            obj (User, optional): The User object being edited, or None if it's a new User.

        Returns:
            list: The list of fieldsets to be displayed in the UserAdmin form.
        """

        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            fieldsets = list(filter(lambda f: f[0] != 'Permissions', fieldsets))
        return fieldsets


admin.site.unregister(User)
admin.site.register(User, AuthorAdmin)


class CommentInline(admin.TabularInline):
    """
    Inline model definition for the Comment model.

    Inherits from:
        - admin.TabularInline

    Attributes:
        - model (Comment): The Comment model to be displayed as an inline model.
        - extra (int): The number of extra empty forms to display.

    Returns:
        None
    """

    model = Comment
    extra = 0


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """
    ModelAdmin class for managing the Content model in the admin panel.

    Inherits from:
        - admin.ModelAdmin

    Attributes:
        - inlines (list): Specifies the inline models to be displayed in the form and edited at the same time.
        - list_display (list): Specifies the fields to be displayed in the list view of the Content model.
        - readonly_fields (list): Specifies the fields that are read-only in the admin panel.
        - list_per_page (int): Specifies the number of items to display per page in the list view.

    Returns:
        None
    """

    inlines = [CommentInline]
    list_display = ['title',
                    'short_text',
                    'date_time_create',
                    'date_time_edit',
                    'author',
                    'is_published']
    readonly_fields = ['slug']
    list_per_page = 20


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    ModelAdmin class for managing the Comment model in the admin panel.

    Inherits from:
        - admin.ModelAdmin

    Attributes:
        - list_display (list): Specifies the fields to be displayed in the list view of the Comment model.
        - list_per_page (int): Specifies the number of items to display per page in the list view.

    Methods:
        - content_link(obj): Generates a link to the post that was commented on.

    Returns:
        None
    """

    list_display = ['short_text',
                    'author',
                    'content_link',
                    'date_time_create']
    list_per_page = 40

    def content_link(self, obj):
        """
        Generates a link to the post that was commented on.

        Args:
            obj (Comment): The Comment object.

        Returns:
            str: HTML link to the post.
        """

        url = reverse('admin:blog_content_change', args=[obj.content.pk])
        return format_html('<a href="{}">{}</a>', url, obj.content)

    content_link.short_description = 'Content'
