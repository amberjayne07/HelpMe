from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from HelpMe_app.forms import *
from HelpMe_app.models import *
from HelpMe_app.utils import auth_success_response
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import slugify
from django.db.models import Q
def home(request):
    categories = Category.objects.prefetch_related('question_set').all()
    return render(request, 'home.html', {'categories': categories})


def post_overview(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    user_vote = None

    if hasattr(question, 'poll'):
        session_key = request.session.session_key

        if request.user.is_authenticated:
            user_vote = Vote.objects.filter(
                username=request.user,
                pollitem_id__poll_id=question.poll
            ).first()
        elif session_key:
            user_vote = Vote.objects.filter(
                session_key=session_key,
                pollitem_id__poll_id=question.poll
            ).first()

    return render(request, 'post_overview.html', {
        'question': question,
        'user_vote': user_vote
    })

def about(request):
    return render(request, 'about_us.html')

def account_upsell(request):
    return render(request, 'account_upsell.html')


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
    password_hint = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            django_login(request, user)
            return auth_success_response(request, f"Welcome back, {user.username}")
        else:
            login_data = request.POST.get('username', '').strip()

            if login_data:
                user = User.objects.filter(
                    Q(username__iexact=login_data) | Q(email__iexact=login_data)
                ).first()

                if user:
                    password_hint = user.password_hint
    else:
        form = AuthenticationForm()

    return render(request, 'authentication/login.html', {
        'form': form,
        'password_hint': password_hint
    })


@login_required
def logout(request):
    if request.method == 'POST':
        current_user = request.user
        django_logout(request)
        request.user = current_user
        return auth_success_response(request, "Signing you out...")

    return redirect('HelpMe_app:home')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # This keeps the user logged in :)
            update_session_auth_hash(request, user)

            return auth_success_response(request, "Updating your password...", change_password=True)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'authentication/change_password.html', {'form': form})


@login_required
def my_account(request):
    user_posts = Question.objects.filter(username=request.user).order_by('-date_posted')[:5]
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
    if request.method == 'POST':
        question = get_object_or_404(Question, question_id=question_id)

        if request.user in question.liked_by.all():
            question.liked_by.remove(request.user)
            liked = False
        else:
            question.liked_by.add(request.user)
            liked = True

            # Trigger Like Notification (Only if not liking your own post)
            if request.user != question.username:
                Notification.objects.get_or_create(
                    notification_id=uuid.uuid4(),
                    question_id=question,
                    username=request.user,  # The person who liked it
                    notification_type='LIKE'
                )

        return JsonResponse({
            'liked': liked,
            'count': question.liked_by.count()
        })


@login_required
def create_comment(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)

    if request.method == 'POST':
        comment_text = request.POST.get('text')
        new_poll_item_text = request.POST.get('new_poll_item', '').strip()
        current_user = request.user

        new_comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            question_id=question,
            username=current_user,
            text=comment_text
        )

        poll_item_added = False
        if new_poll_item_text:
            poll = Poll.objects.filter(question_id=question).first()
            if poll:
                PollItem.objects.create(
                    pollitem_id=uuid.uuid4(),
                    poll_id=poll,
                    username=current_user,
                    content=new_poll_item_text,
                    comment_id=new_comment,
                    approval_status='NEUTRAL'
                )
                poll_item_added = True

        if current_user != question.username:
            n_type = 'SUGGESTION' if poll_item_added else 'COMMENT'

            Notification.objects.create(
                notification_id=uuid.uuid4(),
                question_id=question,
                username=current_user,
                comment_id=new_comment,
                notification_type=n_type
            )

        return redirect('HelpMe_app:post_overview', question_id=question_id)


@login_required
@require_POST
def respond_to_suggestion(request, item_id):
    poll_item = get_object_or_404(PollItem, pollitem_id=item_id)

    if poll_item.poll_id.question_id.username != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to moderate this suggestion.'
        }, status=403)

    action = request.POST.get('action')

    if action == 'approve':
        poll_item.approval_status = 'APPROVED'
        message = "Suggestion approved and added to the poll."
    elif action == 'decline':
        poll_item.approval_status = 'DECLINED'
        message = "Suggestion has been declined."
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid action provided.'
        }, status=400)

    poll_item.save()
    return JsonResponse({
        'status': 'success',
        'message': message,
        'new_status': poll_item.get_approval_status_display()
    })


@require_POST
def vote_on_poll(request, item_id):
    poll_item = get_object_or_404(PollItem, pollitem_id=item_id)
    poll = poll_item.poll_id

    if request.user.is_authenticated:
        voter_user = request.user
        s_key = None
    else:
        voter_user = User.objects.filter(type='LIMITED').first()
        if not voter_user:
            voter_user = User.objects.create(
                username='guest_system_user',
                full_name='Guest',
                email='guest@guest.com',
                date_of_birth='2000-01-01',
                type='LIMITED'
            )
            voter_user.set_unusable_password()
            voter_user.save()

        if not request.session.session_key:
            request.session.create()
        s_key = request.session.session_key
    already_voted = Vote.objects.filter(
        username=voter_user,
        session_key=s_key,
        pollitem_id__poll_id=poll
    ).exists()

    if not already_voted:
        Vote.objects.create(
            vote_id=uuid.uuid4(),
            username=voter_user,
            session_key=s_key,
            pollitem_id=poll_item
        )

    return redirect('HelpMe_app:post_overview', question_id=poll.question_id.question_id)
def go_back(request):
    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)

# USER CREATION / EDITING TOOLS
@require_POST
def create_question(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    category_id = request.POST.get('category_id')

    if not title or not description or not category_id:
        return redirect('HelpMe_app:home')

    if request.user.is_authenticated:
        author = request.user
    else:
        author = User.objects.filter(type='LIMITED').first()

        if not author:
            author = User.objects.create(
                username='guest_system_user',
                full_name='Guest',
                email='guest@guest.com',
                date_of_birth='2000-01-01',
                type='LIMITED',
                is_active=True
            )
            author.set_unusable_password()
            author.save()

    category = get_object_or_404(Category, category_id=category_id)

    # CREATE THE QUESTION
    new_question = Question.objects.create(
        question_id=uuid.uuid4(),
        username=author,
        category_id=category,
        title=title,
        description=description
    )

    # POLL LOGIC
    include_poll = request.POST.get('include_poll') == 'on'

    if include_poll:
        use_custom = request.POST.get('use_custom_poll_title') == 'on'
        custom_text = request.POST.get('poll_title_custom', '').strip()
        final_poll_title = custom_text if (use_custom and custom_text) else title

        poll_options = []
        for key in request.POST:
            if key.startswith('poll_option_'):
                option_value = request.POST.get(key).strip()
                if option_value:
                    poll_options.append(option_value)

        if len(poll_options) >= 2:
            new_poll = Poll.objects.create(
                poll_id=uuid.uuid4(),
                question_id=new_question,
                title=final_poll_title
            )

            for option_text in poll_options:
                PollItem.objects.create(
                    pollitem_id=uuid.uuid4(),
                    poll_id=new_poll,
                    username=author,
                    content=option_text,
                    approval_status='CREATOR'
                )

    return redirect('HelpMe_app:post_overview', question_id=new_question.question_id)


@login_required
@require_POST
def edit_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)

    if request.method == 'POST':
        question.title = request.POST.get('title')
        question.description = request.POST.get('description')
        question.save()

        include_poll = request.POST.get('include_poll') == 'on'

        if include_poll:
            poll, created = Poll.objects.get_or_create(
                question_id=question,
                defaults={'poll_id': uuid.uuid4(), 'title': question.title}
            )
            poll.pollitem_set.all().delete()
            poll_options = [request.POST.get(k).strip() for k in request.POST
                            if k.startswith('poll_option_') and request.POST.get(k).strip()]

            if len(poll_options) >= 2:
                for option_text in poll_options:
                    PollItem.objects.create(
                        pollitem_id=uuid.uuid4(),
                        poll_id=poll,
                        username=request.user,
                        content=option_text,
                        approval_status='CREATOR'
                    )
            else:
                poll.delete()
        else:
            Poll.objects.filter(question_id=question).delete()

        return redirect('HelpMe_app:post_overview', question_id=question.question_id)



@login_required
@require_POST
def delete_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    if question.username.type == 'LIMITED' or question.username != request.user:
        return redirect('HelpMe_app:post_overview', question_id=question_id)

    question.delete()

    return redirect('HelpMe_app:home')

# NOTIFICATIONS LOGIC
@require_POST
@login_required
def clear_notification_history(request):
    # Permanently deletes all notifications already marked as read.
    Notification.objects.filter(
        question_id__username=request.user,
        is_read=True
    ).delete()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        notification_id=notification_id,
        question_id__username=request.user
    )
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def mark_all_notifications_read(request):
    # Marks every unread notification for the user as read.
    Notification.objects.filter(
        question_id__username=request.user,
        is_read=False
    ).exclude(username=request.user).update(is_read=True)
    return JsonResponse({'status': 'success'})

# ADMIN ONLY.
@staff_member_required
@require_POST
def create_category(request):
    name = request.POST.get('name')
    if name:
        new_slug = slugify(name)

        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'slug': new_slug}
        )

    return redirect('HelpMe_app:home')

def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        results = Question.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category_id__name__icontains=query) |
            Q(username__username__icontains=query)
        ).distinct().order_by('-date_posted')

    return render(request, "search_results.html", {
        "results": results,
        "query": query,
    })
    