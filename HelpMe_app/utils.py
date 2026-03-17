from django.shortcuts import render, resolve_url
from django.conf import settings


def auth_success_response(request, text="User auth issue, redirecting...", change_password=False):
    # Helper function to redirect the user to the login redirect URL with a transition.
    if not change_password:
        redirect_to = resolve_url(settings.AUTH_REDIRECT_URL)
    else:
        redirect_to = resolve_url(settings.MY_ACCOUNT_URL)
    return render(request, 'authentication/auth_transition.html', {
        'redirect_url': redirect_to,
        'text_to_user': text
    })
