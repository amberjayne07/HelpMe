import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'helpme_project.settings')
import django
django.setup()

import uuid
from HelpMe_app.models import User, Category, Question, Notification, Poll, Comment, PollItem

def add_user(username, password, user_type, full_name, email, date_of_birth, picture, password_hint):
    """Helper function to create or get a user"""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'password': password,
            'type': user_type,
            'full_name': full_name,
            'email': email,
            'dateOfBirth': date_of_birth,
            'picture': picture,
            'passwordHint': password_hint
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

def add_question(category, username, title, description, likes=0):
    """Helper function to create or get a question"""
    q, created = Question.objects.get_or_create(
        categoryID=category,
        username=username,
        title=title,
        defaults={
            'questionID': uuid.uuid4(),
            'description': description,
            'likes': likes
        }
    )
    return q, created

def add_comment(username, text):
    """Helper function to create or get a comment"""
    comment, created = Comment.objects.get_or_create(
        username=username,
        text=text,
        defaults={'commentID': uuid.uuid4()}
    )
    return comment, created

def add_notification(question, username, notification_type, is_read=False):
    """Helper function to create or get a notification"""
    notif, created = Notification.objects.get_or_create(
        questionID=question,
        username=username,
        notificationType=notification_type,
        defaults={'notificationID': uuid.uuid4(), 'isRead': is_read}
    )
    return notif, created

def add_poll(question, title):
    """Helper function to create or get a poll"""
    poll, created = Poll.objects.get_or_create(
        questionID=question,
        defaults={'pollID': uuid.uuid4(), 'title': title}
    )
    return poll, created

def add_poll_item(poll, username, content, comment=None, approval_status='NEUTRAL'):
    """Helper function to create or get a poll item"""
    item, created = PollItem.objects.get_or_create(
        pollID=poll,
        content=content,
        defaults={
            'pollItemID': uuid.uuid4(),
            'username': username,
            'commentID': comment,
            'approvalStatus': approval_status
        }
    )
    return item, created

def populate():
    # User data
    users_data = {
        'user1': {
            'password': 'password1',
            'type': 'STANDARD',
            'full_name': 'User One',
            'email': 'user1@example.com',
            'date_of_birth': '1990-01-01',
            'picture': 'default.png',
            'password_hint': 'My first pet'
        },
        'user2': {
            'password': 'password2',
            'type': 'STANDARD',
            'full_name': 'User Two',
            'email': 'user2@example.com',
            'date_of_birth': '1990-02-02',
            'picture': 'default.png',
            'password_hint': 'My favorite color'
        },
        'admin': {
            'password': 'adminpass',
            'type': 'ADMIN',
            'full_name': 'Admin User',
            'email': 'admin@example.com',
            'date_of_birth': '1985-05-05',
            'picture': 'default.png',
            'password_hint': 'Admin hint'
        },
        'limited_user': {
            'password': 'limitedpass',
            'type': 'LIMITED',
            'full_name': 'Limited User',
            'email': 'limited@example.com',
            'date_of_birth': '1995-03-03',
            'picture': 'default.png',
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
            'likes': 5
        },
        {
            'category': 'Django',
            'username': 'user2',
            'title': 'Django vs Flask?',
            'description': 'Which framework is better for web development, Django or Flask?',
            'likes': 3
        },
        {
            'category': 'Web Development',
            'username': 'limited_user',
            'title': 'Best practices for HTML?',
            'description': 'What are some best practices for writing clean HTML code?',
            'likes': 1
        }
    ]

    # Create questions
    questions = []
    for q_data in questions_data:
        question, created = add_question(
            category=categories[q_data['category']],
            username=q_data['username'],
            title=q_data['title'],
            description=q_data['description'],
            likes=q_data['likes']
        )
        questions.append(question)
        print(f'- Question: {q_data["title"]}')

    # Create comments
    comments = []
    comment_data = [
        ('user2', 'I recommend starting with the official Python tutorial.'),
        ('user1', 'Django has more built-in features, Flask is more flexible.'),
        ('admin', 'Use semantic HTML and validate your code.')
    ]
    for username, text in comment_data:
        comment, created = add_comment(username, text)
        comments.append(comment)
    print(f'- Created {len(comments)} comments')

    # Create polls and poll items
    poll1, _ = add_poll(questions[0], 'Best way to learn Python?')
    poll2, _ = add_poll(questions[1], 'Preferred framework?')
    
    add_poll_item(poll1, 'admin', 'Official Python Tutorial', comment=comments[0], approval_status='APPROVED')
    add_poll_item(poll1, 'user1', 'Online courses like Coursera', approval_status='NEUTRAL')
    add_poll_item(poll2, 'user2', 'Django', comment=comments[1], approval_status='APPROVED')
    add_poll_item(poll2, 'limited_user', 'Flask', approval_status='DECLINED')
    print('- Created 2 polls with 4 poll items')

    # Create notifications
    notifications = []
    notification_data = [
        (questions[0], 'user2', 'COMMENT', True),
        (questions[1], 'user1', 'LIKE', False),
        (questions[2], 'admin', 'SUGGESTION', False)
    ]
    for question, username, notif_type, is_read in notification_data:
        notif, created = add_notification(question, username, notif_type, is_read)
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

if __name__ == '__main__':
    print("Starting HelpMe population script...")
    populate()
    print_summary()
    print("\nHelpMe population complete!")