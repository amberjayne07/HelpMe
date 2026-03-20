from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline
from .models import User, Category, Question, Comment, Notification, Poll, PollItem, Vote


# Helper to create delete button. Material icons are used in unfold :)

def get_delete_button(obj):
    url = reverse(
        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete',
        args=[obj.pk]
    )
    return format_html(
        '<a href="{}" style="color: #d32f2f;" title="Delete">'
        '<span class="material-symbols-outlined" style="vertical-align: middle;">delete</span>'
        '</a>',
        url
    )


# Inline items! These show up within the classes they're imported in.

class VoteInline(TabularInline):
    model = Vote
    extra = 0
    readonly_fields = ('voted_at',)


class PollItemInline(TabularInline):
    model = PollItem
    extra = 1
    fields = ('content', 'username', 'approval_status')
    show_change_link = True


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('posted_date',)


class PollInline(TabularInline):
    model = Poll
    extra = 0
    max_num = 1
    show_change_link = True


# Admin restructure using classes.

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('picture_preview', 'username', 'email', 'full_name', 'type', 'is_staff', 'delete_button')
    list_filter = ('type',)
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-join_date',)

    fieldsets = (
        ("Profile", {'fields': ('picture', 'full_name', 'username', 'email', 'date_of_birth')}),
        ("Security and permissions", {'fields': ('type', 'password', 'password_hint')}),
        ("General", {'fields': ('join_date',)}),
    )
    readonly_fields = ('join_date',)

    def delete_button(self, obj):
        return get_delete_button(obj)

    delete_button.short_description = ""

    def picture_preview(self, obj):
        if obj.picture:
            return format_html('<img src="{}" class="w-12 h-12 rounded-full object-cover"/>', obj.picture.url)
        return ""

    picture_preview.short_description = "Picture"


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('type_label', 'user_who_sent', 'linked_post', 'is_read')
    list_filter = ('notification_type',)
    list_editable = ('is_read',)
    search_fields = ('username__username', 'question_id__title')

    @admin.display(description="Type")
    def type_label(self, obj):
        return obj.get_notification_type_display()

    def user_who_sent(self, obj): return obj.username.username

    def linked_post(self, obj): return obj.question_id.title

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('username', 'question_id')


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ('title', 'category', 'username', 'date_posted', 'likes', 'delete_button')
    list_filter = ('category_id', 'date_posted')
    search_fields = ('title', 'description', 'username__username')
    inlines = [PollInline, CommentInline]

    @admin.display(description="Category")
    def category(self, obj):
        return obj.category_id

    @admin.display(description="Likes")
    def likes(self, obj):
        return obj.total_likes

    def delete_button(self, obj):
        return get_delete_button(obj)

    delete_button.short_description = ""

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category_id', 'username')


@admin.register(Poll)
class PollAdmin(ModelAdmin):
    list_display = ('title', 'question_title', 'votes', 'delete_button')
    inlines = [PollItemInline]

    def question_title(self, obj): return obj.question_id.title

    def votes(self, obj): return obj.get_total_votes()

    def delete_button(self, obj):
        return get_delete_button(obj)

    delete_button.short_description = ""


@admin.register(PollItem)
class PollItemAdmin(ModelAdmin):
    list_display = ('content', 'question_title', 'username', 'approval_status', 'delete_button')
    list_editable = ('approval_status',)
    inlines = [VoteInline]

    def question_title(self, obj): return obj.poll_id.question_id.title

    def delete_button(self, obj):
        return get_delete_button(obj)

    delete_button.short_description = ""


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('username', 'text', 'question_title', 'posted_date', 'delete_button')

    @admin.display(description="Question title")
    def question_title(self, obj):
        return obj.question_id

    def text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    def delete_button(self, obj):
        return get_delete_button(obj)

    delete_button.short_description = ""


@admin.register(Vote)
class VoteAdmin(ModelAdmin):
    list_display = ('username', 'get_poll_item', 'voted_at')

    def get_poll_item(self, obj):
        return obj.pollitem_id.content
