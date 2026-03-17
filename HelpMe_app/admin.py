from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Category, Question, Notification, Poll, Comment, PollItem


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'type', 'is_staff')
    list_filter = ('type', 'is_staff', 'is_superuser', 'is_active')

    # Sort users into sections
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal', {'fields': ('full_name', 'email', 'date_of_birth', 'picture', 'password_hint')}),
        ('User permissions',
         {'fields': ('type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'join_date')}),
    )

    # Things to check for when creating admin in the admin interface.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'date_of_birth', 'type', 'password'),
        }),
    )

    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    readonly_fields = ('join_date',)

    # Create image preview.
    def image_preview(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 50%;" />',
                               obj.picture.url)
        return "No image found"

    image_preview.short_description = 'Preview'


# Register models so they appear in the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Notification)
admin.site.register(Poll)
admin.site.register(Comment)
admin.site.register(PollItem)
