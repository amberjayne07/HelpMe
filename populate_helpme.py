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
    """Helper function to create or get a comment"""
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
    """Helper function to create or get a poll item"""
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
        'Python': 'python',
        'Django': 'django',
        'Web Development': 'web-development'
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
            'category': 'Python',
            'username': 'user1',
            'title': 'How to learn Python?',
            'description': 'I am new to programming and want to learn Python. Any suggestions?',
            'users_liked': ['user2']
        },
        {
            'category': 'Django',
            'username': 'user2',
            'title': 'Django vs Flask?',
            'description': 'Which framework is better for web development, Django or Flask?',
            'users_liked': ['user1', 'admin']
        },
        {
            'category': 'Web Development',
            'username': 'limited_user',
            'title': 'Best practices for HTML?',
            'description': 'What are some best practices for writing clean HTML code?',
            'users_liked': ['admin']
        }
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

    # Create comments
    comments = []
    comment_data = [
        (0, 'user2', 'I recommend starting with the official Python tutorial.'),
        (1, 'user1', 'Django has more built-in features, Flask is more flexible.'),
        (2, 'admin', 'Use semantic HTML and validate your code.')
    ]
    for question_id, username, text in comment_data:
        comment, created = add_comment(questions[question_id], users[username], text)
        comments.append(comment)
    print(f'- Created {len(comments)} comments')

    # Create polls and poll items
    poll1, _ = add_poll(questions[0], 'Best way to learn Python?')
    poll2, _ = add_poll(questions[1], 'Preferred framework?')

    suggestion_comment1, _ = add_comment(questions[0], users['user1'], 'I think online courses are the way to go.')
    suggestion_comment2, _ = add_comment(questions[1], users['limited_user'], 'Flask is just so much lighter.')

    add_poll_item(poll1, users['admin'], 'Official Python Tutorial', comment=comments[0], approval_status='APPROVED')
    add_poll_item(poll1, users['user1'], 'Online courses like Coursera', comment=suggestion_comment1, approval_status='NEUTRAL')
    add_poll_item(poll2, users['user2'], 'Django', comment=comments[1], approval_status='APPROVED')
    add_poll_item(poll2, users['limited_user'], 'Flask', comment=suggestion_comment2, approval_status='DECLINED')
    print('- Created 2 polls with 4 poll items')

    item_tutorial = PollItem.objects.get(content='Official Python Tutorial')
    item_django = PollItem.objects.get(content='Django')

    add_vote(users['user2'], item_tutorial)
    add_vote(users['limited_user'], item_tutorial, session_key='guest_session_123')
    add_vote(users['limited_user'], item_django, session_key='guest_session_456')
    add_vote(users['admin'], item_django)
    add_vote(users['user1'], item_django)
    print('- Added 5 votes')

    # Create notifications
    notifications = []
    notification_data = [
        (questions[0], users['user2'], 'COMMENT', comments[0], True),
        (questions[1], users['user1'], 'LIKE', None, False),
        (questions[2], users['admin'], 'SUGGESTION', suggestion_comment2, False)
    ]
    for question, user, notif_type, comment, is_read in notification_data:
        notif, created = add_notification(question, user, notif_type, comment, is_read)
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