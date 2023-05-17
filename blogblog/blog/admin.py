from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .forms import AdminUserCreationForm
from .models import Content, Author, Comment


class UserProfileInline(admin.StackedInline):
    """
    Defining the mapping of the model (fields) Author as an inline model
    """
    model = Author
    can_delete = False


class AuthorAdmin(UserAdmin):
    """
    In "inlines" it is specified that the fields of the Author and User models are displayed in the form and edited at the same time
    "add_form" and "add_fieldsets" define the form for adding a new user
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
        Hides the Permissions block for all users except superusers
        """
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            fieldsets = list(filter(lambda f: f[0] != 'Permissions', fieldsets))
        return fieldsets


admin.site.unregister(User)
admin.site.register(User, AuthorAdmin)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
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
    list_display = ['short_text',
                    'author',
                    'content_link',
                    'date_time_create']
    list_per_page = 40

    def content_link(self, obj):
        url = reverse('admin:blog_content_change', args=[obj.content.pk])
        return format_html('<a href="{}">{}</a>', url, obj.content)

    content_link.short_description = 'Content'
