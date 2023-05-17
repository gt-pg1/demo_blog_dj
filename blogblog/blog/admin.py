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

    Defines the mapping of the Author model fields as an inline model.
    """
    model = Author
    can_delete = False


class AuthorAdmin(UserAdmin):
    """
    Custom UserAdmin for managing authors.

    In "inlines", it is specified that the fields of the Author and User models
    are displayed in the form and edited at the same time.

    "add_form" and "add_fieldsets" define the form for adding a new user.

    Overrides the get_fieldsets method to hide the Permissions block for all users
    except superusers.
    """
    inlines = [UserProfileInline]
    add_form = AdminUserCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
        }),
    )

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

    Defines the mapping of the Comment model fields as an inline model.
    """
    model = Comment
    extra = 0


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """
    ModelAdmin class for managing Content model in the admin panel.

    Sets the display options for the Content model on the admin panel.

    In "inlines", it is specified that the fields of the Comment and Content models
    are displayed in the form and edited at the same time.
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
    ModelAdmin class for managing Comment model in the admin panel.

    Sets the display options for the Comment model on the admin panel.
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
