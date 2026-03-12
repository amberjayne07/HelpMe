from django.contrib import admin
from .models import User, Category, Question, Notification, Poll, Comment, PollItem

# Register models so they appear in the admin site
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Notification)
admin.site.register(Poll)
admin.site.register(Comment)
admin.site.register(PollItem)
