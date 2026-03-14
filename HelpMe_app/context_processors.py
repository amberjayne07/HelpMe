# Joseph Beattie - Context processor to get pages from settings to apply glow effect background / animation to.
from django.conf import settings

def glow_settings(request):
    return {
        'GLOW_PAGES': getattr(settings, 'GLOW_PAGES', []),
    }
