from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .forms import AdminUserCreationForm
from .models import Content, Author, Comment


# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = Author
    can_delete = False


class AuthorAdmin(UserAdmin):
    inlines = [UserProfileInline]
    add_form = AdminUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(AuthorAdmin, self).get_inline_instances(request, obj)


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['short_text',
                    'author',
                    'content_link',
                    'date_time_create']

    def content_link(self, obj):
        url = reverse('admin:blog_content_change', args=[obj.content.pk])
        return format_html('<a href="{}">{}</a>', url, obj.content)

    content_link.short_description = 'Content'
