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
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from HelpMe_app.forms import *
from HelpMe_app.models import *
from HelpMe_app.utils import auth_success_response
from django.http import JsonResponse


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


@login_required
def logout(request):
    if request.method == 'POST':
        current_user = request.user  # Save the user information for the transition animation.
        django_logout(request)
        request.user = current_user
        return auth_success_response(request, "Signing you out...")

    return redirect('home')


@login_required
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


@login_required
def my_account(request):
    user_posts = Question.objects.filter(username=request.user).order_by('-datePosted')[:5]
    return render(request, 'authentication/my_account.html', {
        'user_posts': user_posts,
    })


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


# RESPONDING TO POSTS
@login_required
def like_question(request, question_id):
    # Use your exact model field 'questionID'
    question = get_object_or_404(Question, questionID=question_id)

    # Increment the like counter
    question.likes += 1
    question.save()

    # Create the notification for the question owner
    # Only create if the person liking isn't the owner themselves
    if question.username != request.user:
        Notification.objects.create(
            notificationID=uuid.uuid4(),
            questionID=question,
            username=request.user,  # The 'Actor' who liked it
            notificationType='LIKE',
            isRead=False
        )

    # Redirect back to the post page
    return redirect('HelpMe_app:post_overview', question_id=question_id)


# NOTIFICATIONS LOGIC
@require_POST
@login_required
def clear_notification_history(request):
    # Permanently deletes all notifications already marked as read.
    Notification.objects.filter(
        questionID__username=request.user,
        isRead=True
    ).delete()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            notificationID=notification_id,
            questionID__username=request.user
        )
        notification.isRead = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)


@login_required
@require_POST
def mark_all_notifications_read(request):
    # Marks every unread notification for the user as read.
    Notification.objects.filter(
        questionID__username=request.user,
        isRead=False
    ).exclude(username=request.user).update(isRead=True)
    return JsonResponse({'status': 'success'})
