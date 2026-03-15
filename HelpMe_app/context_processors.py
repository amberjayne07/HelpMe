# Joseph Beattie - Context processors...
from django.conf import settings
from .models import Notification


# Get pages listed in settings to apply glow effect / animation to.
def glow_settings(request):
    return {
        'GLOW_PAGES': getattr(settings, 'GLOW_PAGES', []),
    }


def background_notifications(request):
    if request.user.is_authenticated:
        # Check if user is logged in...
        base_query = Notification.objects.filter(
            questionID__username=request.user
        ).exclude(username=request.user).select_related('questionID', 'username', 'commentID')

        return {
            'unread_notifications': base_query.filter(isRead=False).order_by('-notificationID'),
            'read_notifications': base_query.filter(isRead=True).order_by('-notificationID')[:20]
        }
    return {
        'unread_notifications': [],
        'read_notifications': []
    }
