# Joseph Beattie - Context processors...
from django.conf import settings
from HelpMe_app.models import Notification, Category, Question


# Get pages listed in settings to apply glow effect / animation to.
def glow_settings(request):
    return {
        'GLOW_PAGES': getattr(settings, 'GLOW_PAGES', []),
    }


def background_notifications(request):
    if request.user.is_authenticated:
        # Check if user is logged in...
        base_query = Notification.objects.filter(
            question_id__username=request.user
        ).exclude(username=request.user).select_related('question_id', 'username', 'comment_id')

        return {
            'unread_notifications': base_query.filter(is_read=False).distinct(),
            'read_notifications': base_query.filter(is_read=True).distinct()[:20]
        }
    return {
        'unread_notifications': [],
        'read_notifications': []
    }

def global_categories(request):
    # Makes categories available to all templates globally.
    return {
        'categories': Category.objects.all()
    }