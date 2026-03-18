from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Category, Question, Notification, Poll, Comment, PollItem
from unfold.admin import ModelAdmin

class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'type', 'is_staff')
    list_filter = ('type', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal', {'fields': ('full_name', 'email', 'date_of_birth', 'picture', 'password_hint')}),
        ('User permissions',
         {'fields': ('type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'join_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'date_of_birth', 'type', 'password'),
        }),
    )

    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    readonly_fields = ('join_date',)

    def image_preview(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" class="w-10 h-10 rounded-full object-cover" />',
                obj.picture.url
            )
        return "No image"

    image_preview.short_description = 'Preview'


# Register models so they appear in the admin site
admin.site.register(User, ModelAdmin)
admin.site.register(Category, ModelAdmin)
admin.site.register(Question, ModelAdmin)
admin.site.register(Notification, ModelAdmin)
admin.site.register(Poll, ModelAdmin)
admin.site.register(Comment, ModelAdmin)
admin.site.register(PollItem, ModelAdmin)
