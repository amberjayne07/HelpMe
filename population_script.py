import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpme_project.settings')
import django
django.setup()

import uuid
from HelpMe_app.models import User, Category, Question, Notification, Poll, Comment, PollItem, Vote


def add_user(username, password, user_type, full_name, email, date_of_birth, picture, password_hint):
    """Helper function to create or get a user"""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'password': password,
            'type': user_type,
            'full_name': full_name,
            'email': email,
            'date_of_birth': date_of_birth,
            'picture': picture,
            'password_hint': password_hint,
            'is_active': True,
        }
    )
    if created:
        user.set_password(password)
        user.save()
    return user, created


def add_category(name, slug):
    """Helper function to create or get a category"""
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={'slug': slug}
    )
    if not created and cat.slug != slug:
        cat.slug = slug
        cat.save()
    return cat, created


def add_question(category, username, title, description):
    """Helper function to create or get a question"""
    q, created = Question.objects.get_or_create(
        category_id=category,
        username=username,
        title=title,
        defaults={
            'question_id': uuid.uuid4(),
            'description': description,
        }
    )
    return q, created


def add_comment(question, username, text):
    """
    Helper function to create or get a comment

    Rules enforced here:
      - The question owner cannot comment on their own question.
      - LIMITED users cannot comment at all (they can only create posts and vote).
    """
    # Disallow limited users from commenting
    if getattr(username, 'type', None) == 'LIMITED':
        print(f"  ! Skipped comment (LIMITED user) by '{username.username}' on '{question.title}'")
        return None, False

    # Disallow self-comments by question owner
    try:
        is_owner = (question.username == username)
    except Exception:
        # Fallback if comparison behavior differs in model setup
        is_owner = getattr(question.username, 'username', None) == getattr(username, 'username', None)

    if is_owner:
        print(f"  ! Skipped self-comment by '{username.username}' on their own question '{question.title}'")
        return None, False

    comment, created = Comment.objects.get_or_create(
        question_id=question,
        username=username,
        text=text,
        defaults={'comment_id': uuid.uuid4()}
    )
    return comment, created


def add_notification(question, username, notification_type, comment=None, is_read=False):
    """Helper function to create or get a notification"""
    if notification_type in ['COMMENT', 'SUGGESTION'] and not comment:
        # Invalid notification (requires a comment)
        return None, False

    notif, created = Notification.objects.get_or_create(
        question_id=question,
        username=username,
        notification_type=notification_type,
        comment_id=comment,
        defaults={'notification_id': uuid.uuid4(), 'is_read': is_read}
    )
    return notif, created


def add_poll(question, title):
    """Helper function to create or get a poll"""
    poll, created = Poll.objects.get_or_create(
        question_id=question,
        defaults={'poll_id': uuid.uuid4(), 'title': title}
    )
    return poll, created


def add_poll_item(poll, username, content, comment, approval_status='NEUTRAL'):
    """
    Helper function to create or get a poll item

    Guards:
      - Requires a linked comment.
      - Ensures the comment belongs to the same question as the poll's question.
    """
    if comment is None:
        print(f"  ! Skipped poll item '{content}' (no linked comment).")
        return None, False

    # Ensure comment.question == poll.question
    if getattr(comment, 'question_id', None) != getattr(poll, 'question_id', None):
        print(f"  ! Skipped poll item '{content}' (comment not on same question as the poll).")
        return None, False

    item, created = PollItem.objects.get_or_create(
        poll_id=poll,
        username=username,
        content=content,
        comment_id=comment,
        defaults={
            'pollitem_id': uuid.uuid4(),
            'approval_status': approval_status
        }
    )
    return item, created


def add_vote(username, poll_item, session_key=None):
    """Helper function to create a vote if it doesn't exist"""
    vote, created = Vote.objects.get_or_create(
        username=username,
        pollitem_id=poll_item,
        session_key=session_key,
        defaults={'vote_id': uuid.uuid4()}
    )
    return vote, created


def populate():
    # User data
    users_data = {
        'user1': {
            'password': 'password1',
            'type': 'STANDARD',
            'full_name': 'User One',
            'email': 'user1@example.com',
            'date_of_birth': '1990-01-01',
            'picture': 'profilepics/default.png',
            'password_hint': 'My first pet'
        },
        'user2': {
            'password': 'password2',
            'type': 'STANDARD',
            'full_name': 'User Two',
            'email': 'user2@example.com',
            'date_of_birth': '1990-02-02',
            'picture': 'profilepics/default.png',
            'password_hint': 'My favorite color'
        },
        'admin': {
            'password': 'adminpass',
            'type': 'ADMIN',
            'full_name': 'Admin User',
            'email': 'admin@example.com',
            'date_of_birth': '1985-05-05',
            'picture': 'profilepics/default.png',
            'password_hint': 'Admin hint'
        },
        'limited_user': {
            'password': 'limitedpass',
            'type': 'LIMITED',
            'full_name': 'Limited User',
            'email': 'limited@example.com',
            'date_of_birth': '1995-03-03',
            'picture': 'profilepics/default.png',
            'password_hint': 'Limited access'
        }
    }

    # Create users
    users = {}
    for username, user_data in users_data.items():
        user, created = add_user(
            username=username,
            password=user_data['password'],
            user_type=user_data['type'],
            full_name=user_data['full_name'],
            email=user_data['email'],
            date_of_birth=user_data['date_of_birth'],
            picture=user_data['picture'],
            password_hint=user_data['password_hint']
        )
        users[username] = user
        status = 'created' if created else 'already exists'
        print(f'- User: {username} ({status})')

    # Category data
    categories_data = {
        'Social': 'social',
        'School': 'school',
        'Health': 'health',
        'Money': 'money',
    }

    # Create categories
    categories = {}
    for name, slug in categories_data.items():
        cat, created = add_category(name, slug)
        categories[name] = cat
        status = 'created' if created else 'already exists'
        print(f'- Category: {name} ({status})')

    # Question data
    questions_data = [
        {
            'category': 'Social',
            'username': 'user1',
            'title': 'How to make friends in a new city?',
            'description': 'I just moved to a new city and I am finding it hard to make friends. Any tips?',
            'users_liked': ['user2']
        },
        {
            'category': 'Social',
            'username': 'user2',
            'title': 'How to build confidence in social situations?',
            'description': 'I struggle with social anxiety and feel nervous around new people. What are some ways to build confidence?',
            'users_liked': ['admin']
        },
        {
            'category': 'School',
            'username': 'user2',
            'title': 'What study techniques work best for memorization?',
            'description': 'I have trouble memorizing information for exams. What study methods have worked for others?',
            'users_liked': ['user1', 'admin']
        },
        {
            'category': 'School',
            'username': 'limited_user',
            'title': 'How to manage time between multiple courses?',
            'description': 'Balancing multiple courses is overwhelming. How do you prioritize and manage your time effectively?',
            'users_liked': ['user1']
        },
        {
            'category': 'Health',
            'username': 'limited_user',
            'title': 'Best way to get better sleep?',
            'description': 'I have been struggling with sleep lately. What are some effective ways to improve sleep quality?',
            'users_liked': ['admin']
        },
        {
            'category': 'Health',
            'username': 'user1',
            'title': 'How to start a regular exercise routine?',
            'description': 'I want to exercise more regularly but keep losing motivation. How do you stay committed to fitness?',
            'users_liked': ['user2', 'admin']
        },
        {
            'category': 'Money',
            'username': 'user1',
            'title': 'How to save money on a tight budget?',
            'description': 'I am trying to save money but I have a very tight budget. What are some practical tips for saving money in this situation?',
            'users_liked': ['user2', 'admin']
        },
        {
            'category': 'Money',
            'username': 'admin',
            'title': 'Best investment options for beginners?',
            'description': 'I have some money saved and want to invest it, but I am new to investing. What are good starting points?',
            'users_liked': ['user1', 'user2']
        },
    ]

    # Create questions
    questions = []
    for q_data in questions_data:
        question, created = add_question(
            category=categories[q_data['category']],
            username=users[q_data['username']],
            title=q_data['title'],
            description=q_data['description'],
        )

        for username_of_who_liked in q_data.get('users_liked', []):
            question.liked_by.add(users[username_of_who_liked])
        questions.append(question)
        print(f'- Question: {q_data["title"]}')

    # ---------------------------
    # Create comments
    # ---------------------------
    comments = {}
    # Q0 (Social, user1)
    comments['q0_clubs'], _ = add_comment(questions[0], users['user2'],
        'I think joining local clubs or meetup groups can help you meet new people.')

    # Q1 (Social, user2)
    comments['q1_small_groups'], _ = add_comment(questions[1], users['admin'],
        'Start with small group settings where the pressure is lower.')

    # Q2 (School, user2) – study techniques
    comments['q2_active_recall'], _ = add_comment(questions[2], users['user1'],
        'Active recall and spaced repetition really helped me remember information longer.')
    comments['q2_pomodoro'], _ = add_comment(questions[2], users['admin'],
        'I use the Pomodoro technique to break my study sessions into focused blocks.')

    # Q3 (School, limited_user)
    comments['q3_todo'], _ = add_comment(questions[3], users['user1'],
        'Create a prioritized to-do list to keep track of what matters most.')

    # Q4 (Health, limited_user)
    comments['q4_bedtime'], _ = add_comment(questions[4], users['admin'],
        'Establishing a consistent bedtime routine can help improve sleep quality.')

    # Q5 (Health, user1)
    comments['q5_20min'], _ = add_comment(questions[5], users['user2'],
        'I started with just 20 minutes of exercise a day - consistency matters more than duration.')

    # Q6 (Money, user1)
    comments['q6_budget'], _ = add_comment(questions[6], users['user2'],
        'Creating a budget and tracking your expenses can help you identify areas where you can cut back.')

    # Q7 (Money, admin)
    comments['q7_index'], _ = add_comment(questions[7], users['user1'],
        'Starting with index funds or ETFs is a good low-risk beginner option.')

    created_comments_count = sum(1 for c in comments.values() if c is not None)
    print(f'- Created {created_comments_count} comments')

    # ---------------------------
    # Create polls
    # ---------------------------
    poll1, _ = add_poll(questions[0], 'Best way to make friends?')
    poll2, _ = add_poll(questions[1], 'How to build social confidence?')
    poll3, _ = add_poll(questions[2], 'Best study technique?')
    poll4, _ = add_poll(questions[3], 'How to manage multiple courses?')
    poll5, _ = add_poll(questions[4], 'Best sleep improvement method?')
    poll6, _ = add_poll(questions[5], 'How to stay motivated with exercise?')
    poll7, _ = add_poll(questions[6], 'Best money-saving tip?')
    poll8, _ = add_poll(questions[7], 'Best investment for beginners?')

    suggestion = {}
    suggestion['q0_online'], _ = add_comment(questions[0], users['admin'],
        'Online communities and hobby groups are great too.')
    suggestion['q1_therapy'], _ = add_comment(questions[1], users['user1'],
        'Therapy or counseling can really help build confidence.')
    suggestion['q2_mindmap'], _ = add_comment(questions[2], users['user1'],
        'Mind mapping helps me organize and remember information visually.')
    suggestion['q3_calendar'], _ = add_comment(questions[3], users['admin'],
        'Use a shared calendar and block off study times in advance.')
    suggestion['q4_limit_screen'], _ = add_comment(questions[4], users['user1'],
        'Limiting screen time before bed also helps a lot.')
    suggestion['q5_accountability'], _ = add_comment(questions[5], users['user2'],
        'Finding an accountability partner or workout buddy keeps me on track.')
    suggestion['q6_automate'], _ = add_comment(questions[6], users['admin'],
        'Automate your savings so money goes to a savings account first.')
    suggestion['q7_diversify'], _ = add_comment(questions[7], users['user2'],
        'Diversify your portfolio even as a beginner.')

    # ---------------------------
    # Poll items for each poll - 2+ options each
    # Ensure linked comments belong to the same question as the poll
    # ---------------------------
    add_poll_item(poll1, users['admin'], 'Join local clubs and meetup groups',
                  comment=comments['q0_clubs'], approval_status='APPROVED')
    add_poll_item(poll1, users['user1'], 'Online communities and hobby groups',
                  comment=suggestion['q0_online'], approval_status='APPROVED')

    add_poll_item(poll2, users['user2'], 'Start with small group settings',
                  comment=comments['q1_small_groups'], approval_status='APPROVED')
    add_poll_item(poll2, users['admin'], 'Therapy or counseling',
                  comment=suggestion['q1_therapy'], approval_status='APPROVED')

    add_poll_item(poll3, users['user1'], 'Active recall and spaced repetition',
                  comment=comments['q2_active_recall'], approval_status='APPROVED')
    add_poll_item(poll3, users['admin'], 'Pomodoro technique with focused blocks',
                  comment=comments['q2_pomodoro'], approval_status='APPROVED')
    add_poll_item(poll3, users['user1'], 'Mind mapping for visual organization',
                  comment=suggestion['q2_mindmap'], approval_status='NEUTRAL')

    add_poll_item(poll4, users['admin'], 'Use shared calendar for scheduling',
                  comment=suggestion['q3_calendar'], approval_status='APPROVED')
    add_poll_item(poll4, users['user1'], 'Create a prioritized to-do list',
                  comment=comments['q3_todo'], approval_status='APPROVED')

    add_poll_item(poll5, users['admin'], 'Consistent bedtime routine',
                  comment=comments['q4_bedtime'], approval_status='APPROVED')
    add_poll_item(poll5, users['user1'], 'Limit screen time before bed',
                  comment=suggestion['q4_limit_screen'], approval_status='APPROVED')

    add_poll_item(poll6, users['user2'], 'Start small with 20-minute sessions',
                  comment=comments['q5_20min'], approval_status='APPROVED')
    add_poll_item(poll6, users['user2'], 'Find an accountability partner',
                  comment=suggestion['q5_accountability'], approval_status='APPROVED')

    add_poll_item(poll7, users['admin'], 'Track expenses and cut back on discretionary spending',
                  comment=comments['q6_budget'], approval_status='APPROVED')
    add_poll_item(poll7, users['admin'], 'Automate savings first',
                  comment=suggestion['q6_automate'], approval_status='APPROVED')

    add_poll_item(poll8, users['user1'], 'Index funds or ETFs',
                  comment=comments['q7_index'], approval_status='APPROVED')
    add_poll_item(poll8, users['user2'], 'Diversify your portfolio early',
                  comment=suggestion['q7_diversify'], approval_status='APPROVED')

    # ---------------------------
    # Votes
    # ---------------------------
    # Get poll items by content
    item_join_clubs = PollItem.objects.get(content='Join local clubs and meetup groups')
    item_online_communities = PollItem.objects.get(content='Online communities and hobby groups')
    item_small_groups = PollItem.objects.get(content='Start with small group settings')
    item_therapy = PollItem.objects.get(content='Therapy or counseling')
    item_active_recall = PollItem.objects.get(content='Active recall and spaced repetition')
    item_pomodoro = PollItem.objects.get(content='Pomodoro technique with focused blocks')
    item_shared_calendar = PollItem.objects.get(content='Use shared calendar for scheduling')
    item_bedtime = PollItem.objects.get(content='Consistent bedtime routine')
    item_no_screen = PollItem.objects.get(content='Limit screen time before bed')
    item_20min = PollItem.objects.get(content='Start small with 20-minute sessions')
    item_accountability = PollItem.objects.get(content='Find an accountability partner')
    item_track_expenses = PollItem.objects.get(content='Track expenses and cut back on discretionary spending')
    item_automate = PollItem.objects.get(content='Automate savings first')
    item_index_funds = PollItem.objects.get(content='Index funds or ETFs')
    item_diversify = PollItem.objects.get(content='Diversify your portfolio early')

    # Add votes
    add_vote(users['user2'], item_join_clubs)
    add_vote(users['limited_user'], item_join_clubs, session_key='guest_session_123')
    add_vote(users['admin'], item_online_communities)
    add_vote(users['user1'], item_online_communities)

    add_vote(users['user1'], item_small_groups)
    add_vote(users['user2'], item_small_groups)
    add_vote(users['limited_user'], item_therapy, session_key='guest_session_124')

    add_vote(users['admin'], item_active_recall)
    add_vote(users['user2'], item_active_recall)
    add_vote(users['user1'], item_pomodoro)
    add_vote(users['limited_user'], item_pomodoro)

    add_vote(users['user1'], item_shared_calendar)
    add_vote(users['admin'], item_shared_calendar)

    add_vote(users['user2'], item_bedtime)
    add_vote(users['admin'], item_bedtime)
    add_vote(users['user1'], item_no_screen)
    add_vote(users['limited_user'], item_no_screen, session_key='guest_session_125')

    add_vote(users['user1'], item_20min)
    add_vote(users['user2'], item_20min)
    add_vote(users['admin'], item_accountability)
    add_vote(users['limited_user'], item_accountability, session_key='guest_session_126')

    add_vote(users['user2'], item_track_expenses)
    add_vote(users['limited_user'], item_track_expenses)
    add_vote(users['admin'], item_automate)
    add_vote(users['user1'], item_automate)

    add_vote(users['user1'], item_index_funds)
    add_vote(users['admin'], item_index_funds)
    add_vote(users['user2'], item_diversify)
    add_vote(users['limited_user'], item_diversify, session_key='guest_session_127')

    # ---------------------------
    # Notifications
    # ---------------------------
    notifications = []
    notification_data = [
        (questions[0], users['user2'], 'COMMENT', comments['q0_clubs'], True),
        (questions[1], users['admin'], 'LIKE', None, False),
        (questions[2], users['user1'], 'COMMENT', comments['q2_active_recall'], False),
        (questions[3], users['user2'], 'SUGGESTION', suggestion['q3_calendar'], False),
        (questions[4], users['admin'], 'COMMENT', comments['q4_bedtime'], True),
        (questions[5], users['user1'], 'LIKE', None, False),
        (questions[6], users['user1'], 'COMMENT', comments['q6_budget'], False),
        (questions[7], users['user2'], 'SUGGESTION', suggestion['q7_diversify'], False),
    ]
    for question, user, notif_type, comment, is_read in notification_data:
        notif, created = add_notification(question, user, notif_type, comment, is_read)
        if notif:
            notifications.append(notif)
    print(f'- Created {len(notifications)} notifications')


def print_summary():
    """Print a summary of all created data"""
    print('\n=== Database Summary ===')
    print(f'Users: {User.objects.count()}')
    print(f'Categories: {Category.objects.count()}')
    print(f'Questions: {Question.objects.count()}')
    print(f'Comments: {Comment.objects.count()}')
    print(f'Notifications: {Notification.objects.count()}')
    print(f'Polls: {Poll.objects.count()}')
    print(f'Poll Items: {PollItem.objects.count()}')
    print(f'Votes: {Vote.objects.count()}')


if __name__ == '__main__':
    print("Starting HelpMe population script...")
    populate()
    print_summary()
    print("\nHelpMe population complete!")