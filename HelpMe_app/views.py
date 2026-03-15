from http.client import HTTPResponse

from django.shortcuts import render, redirect, resolve_url
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout

from HelpMe_app.forms import *
from HelpMe_app.models import *
from HelpMe_app.utils import auth_success_response


def home(request):
    categories = Category.objects.prefetch_related('question_set').all()
    return render(request, 'home.html', {'categories': categories})


def post_overview(request, question_id):
    question = get_object_or_404(Question, questionID=question_id)
    return render(request, 'post_overview.html', {'question': question})


def about(request):
    return render(request, 'about_us.html')


def sign_up(request):
    if request.method == 'POST':
        # File upload for the picture
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.type = 'STANDARD'
            user.save()
            django_login(request, user, backend='HelpMe_app.custom_login_backend.UseEmailOrUsername')
            return auth_success_response(request, "Creating your account and logging in...")
        else:
            print(form.errors)
    else:
        form = RegistrationForm()

    return render(request, 'authentication/sign_up.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            django_login(request, user)
            return auth_success_response(request, f"Welcome back, {user.username}")
    else:
        form = AuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})


def logout(request):
    if request.method == 'POST':
        current_user = request.user  # Save the user information for the transition animation.
        django_logout(request)
        request.user = current_user
        return auth_success_response(request, "Signing you out...")

    return redirect('home')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # This keeps the user logged in :)
            update_session_auth_hash(request, user)

            return auth_success_response(request, "Updating your password...", changePassword=True)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'authentication/change_password.html', {'form': form})


def my_account(request):
    return render(request, 'authentication/my_account.html')


def test_everything(request):
    context = {
        'users': User.objects.all(),
        'categories': Category.objects.all(),
        'questions': Question.objects.all(),
        'comments': Comment.objects.all(),
        'notifications': Notification.objects.all(),
        'polls': Poll.objects.all(),
        'poll_items': PollItem.objects.all(),
    }
    return render(request, 'testing_only/test_everything.html', context)
