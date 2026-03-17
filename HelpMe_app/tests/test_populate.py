import uuid
from django.test import TestCase
from io import StringIO
from django.core.management import call_command
import sys
import os

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpme_project.settings')

import django
django.setup()

from HelpMe_app.models import User, Category, Question, Notification, Poll, Comment, PollItem

# Import populate functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from populate_helpme import (
    add_user, add_category, add_question, add_comment,
    add_notification, add_poll, add_poll_item, populate, print_summary
)


class AddUserFunctionTest(TestCase):
    """Test cases for the add_user helper function"""

    def test_add_user_creation(self):
        """Test creating a new user"""
        user, created = add_user(
            username='newuser',
            password='StrongPass123!?',
            user_type=User.STANDARD,
            full_name='New User',
            email='newuser@example.com',
            date_of_birth='1990-01-01',
            picture='pic.jpg',
            password_hint='hint'
        )
        self.assertTrue(created)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.full_name, 'New User')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_add_user_get_existing(self):
        """Test getting existing user"""
        # Create user first
        user1, created1 = add_user(
            username='existinguser',
            password='StrongPass123!?',
            user_type=User.STANDARD,
            full_name='Existing User',
            email='existing@example.com',
            date_of_birth='1990-01-01',
            picture='pic.jpg',
            password_hint='hint'
        )
        self.assertTrue(created1)

        # Try to get the same user
        user2, created2 = add_user(
            username='existinguser',
            password='DifferentPass123!?',
            user_type=User.ADMIN,
            full_name='Different Name',
            email='different@example.com',
            date_of_birth='1995-01-01',
            picture='different.jpg',
            password_hint='different hint'
        )
        self.assertFalse(created2)
        self.assertEqual(user1.id, user2.id)
        self.assertEqual(user2.full_name, 'Existing User')  # Original data preserved

    def test_add_user_password_hashing(self):
        """Test that password is hashed"""
        user, _ = add_user(
            username='hashuser',
            password='PlainPassword123!?',
            user_type=User.STANDARD,
            full_name='Hash User',
            email='hash@example.com',
            date_of_birth='1990-01-01',
            picture='pic.jpg',
            password_hint='hint'
        )
        self.assertNotEqual(user.password, 'PlainPassword123!?')


class AddCategoryFunctionTest(TestCase):
    """Test cases for the add_category helper function"""

    def test_add_category_creation(self):
        """Test creating a new category"""
        cat, created = add_category('Python', 'python')
        self.assertTrue(created)
        self.assertEqual(cat.name, 'Python')
        self.assertEqual(cat.slug, 'python')

    def test_add_category_get_existing(self):
        """Test getting existing category and potentially updating slug"""
        cat1, created1 = add_category('Django', 'django')
        self.assertTrue(created1)

        # When we try to add with same name but different slug, slug is updated
        cat2, created2 = add_category('Django', 'django-framework')
        self.assertFalse(created2)
        self.assertEqual(cat1.category_id, cat2.category_id)
        # After refresh, slug should be updated
        cat2.refresh_from_db()
        self.assertEqual(cat2.slug, 'django-framework')

    def test_add_category_update_slug(self):
        """Test updating slug of existing category"""
        cat1, _ = add_category('Web Dev', 'web-dev')
        cat2, _ = add_category('Web Dev', 'webdev')
        # Slug should be updated to the new value
        cat2.refresh_from_db()
        self.assertEqual(cat2.slug, 'webdev')
        cat2.refresh_from_db()
        self.assertEqual(cat2.slug, 'webdev')


class AddQuestionFunctionTest(TestCase):
    """Test cases for the add_question helper function"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='questioner',
            email='question@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='Question User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')

    def test_add_question_creation(self):
        """Test creating a new question"""
        q, created = add_question(
            category=self.category,
            username=self.user,
            title='Test Question?',
            description='This is a test question'
        )
        self.assertTrue(created)
        self.assertEqual(q.title, 'Test Question?')
        self.assertEqual(q.username, self.user)

    def test_add_question_default_likes(self):
        """Test that likes default to 0"""
        q, _ = add_question(
            category=self.category,
            username=self.user,
            title='Another Question?',
            description='Description'
        )
        self.assertEqual(q.total_likes, 0)

    def test_add_question_get_existing(self):
        """Test getting existing question"""
        q1, created1 = add_question(
            category=self.category,
            username=self.user,
            title='Existing Question?',
            description='First description'
        )
        self.assertTrue(created1)

        q2, created2 = add_question(
            category=self.category,
            username=self.user,
            title='Existing Question?',
            description='Different description'
        )
        self.assertFalse(created2)
        self.assertEqual(q1.question_id, q2.question_id)


class AddCommentFunctionTest(TestCase):
    """Test cases for the add_comment helper function"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            date_of_birth='1990-01-01',
            password='Str0ng_P@ssw0rd!?',
            full_name='Test User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test',
            description='Test'
        )

    def test_add_comment_creation(self):
        """Test creating a new comment"""
        comment, created = add_comment(self.question, self.user, 'This is helpful')
        self.assertTrue(created)
        self.assertEqual(comment.username, self.user)
        self.assertEqual(comment.text, 'This is helpful')

    def test_add_comment_get_existing(self):
        """Test getting existing comment"""
        c1, created1 = add_comment(self.question, self.user, 'Existing comment')
        self.assertTrue(created1)

        c2, created2 = add_comment(self.question, self.user, 'Existing comment')
        self.assertFalse(created2)
        self.assertEqual(c1.comment_id, c2.comment_id)


class AddNotificationFunctionTest(TestCase):
    """Test cases for the add_notification helper function"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='notifuser',
            email='notif@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='Notif User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test',
            description='Test'
        )

    def test_add_notification_creation(self):
        """Test creating a LIKE notification (doesn't require comment)"""
        reviewer = User.objects.create_user(
            username='reviewer2',
            email='reviewer2@example.com',
            date_of_birth='1992-01-01',
            password='TestPass123!',
            full_name='Reviewer 2',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        notif, created = add_notification(
            self.question,
            reviewer,
            Notification.LIKE,
            comment=None,
            is_read=False
        )
        self.assertTrue(created)
        self.assertEqual(notif.notification_type, Notification.LIKE)
        self.assertFalse(notif.is_read)

    def test_add_notification_types(self):
        """Test creating LIKE notification"""
        reviewer = User.objects.create_user(
            username='reviewer3',
            email='reviewer3@example.com',
            date_of_birth='1992-01-01',
            password='TestPass123!',
            full_name='Reviewer 3',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        notif, _ = add_notification(
            self.question,
            reviewer,
            Notification.LIKE,
            comment=None
        )
        self.assertEqual(notif.notification_type, Notification.LIKE)


class AddPollFunctionTest(TestCase):
    """Test cases for the add_poll helper function"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='polluser',
            email='poll@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='Poll User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test',
            description='Test'
        )
        self.question2 = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test 2',
            description='Test 2'
        )

    def test_add_poll_creation(self):
        """Test creating a new poll"""
        poll, created = add_poll(self.question, 'Test Poll')
        self.assertTrue(created)
        self.assertEqual(poll.title, 'Test Poll')
        self.assertEqual(poll.question_id, self.question)

    def test_add_poll_get_existing(self):
        """Test getting existing poll"""
        p1, created1 = add_poll(self.question, 'Poll Title')
        self.assertTrue(created1)

        p2, created2 = add_poll(self.question2, 'Poll Title')
        # created2 should be True since we're using different question
        self.assertTrue(created2)
        # But when using same question, should get same poll
        p3, created3 = add_poll(self.question, 'Poll Title')
        self.assertFalse(created3)
        self.assertEqual(str(p1.poll_id), str(p3.poll_id))


class AddPollItemFunctionTest(TestCase):
    """Test cases for the add_poll_item helper function"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='pollitemuser',
            email='pollitem@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='PollItem User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.user2 = User.objects.create_user(
            username='commentuser',
            email='commentuser@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='Comment User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test',
            description='Test'
        )
        self.poll = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question,
            title='Test Poll'
        )
        self.comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user,
            question_id=self.question,
            text='Test comment'
        )

    def test_add_poll_item_creation(self):
        """Test creating a new poll item"""
        item, created = add_poll_item(
            self.poll,
            self.user,
            'Option 1',
            self.comment,
            approval_status=PollItem.APPROVED
        )
        self.assertTrue(created)
        self.assertEqual(item.content, 'Option 1')
        self.assertEqual(item.approval_status, PollItem.APPROVED)
        self.assertEqual(item.comment_id, self.comment)
        self.assertTrue(created)
        self.assertEqual(item.content, 'Option 1')
        self.assertEqual(item.approval_status, PollItem.APPROVED)
        self.assertEqual(item.comment_id, self.comment)

    def test_add_poll_item_with_comment(self):
        """Test creating poll item with comment"""
        item, created = add_poll_item(
            self.poll,
            self.user,
            'Option with comment',
            self.comment,
            approval_status=PollItem.APPROVED
        )
        self.assertTrue(created)
        self.assertEqual(item.comment_id, self.comment)

    def test_add_poll_item_default_status(self):
        """Test default approval status"""
        item, _ = add_poll_item(
            self.poll,
            self.user,
            'Default option',
            self.comment
        )
        self.assertEqual(item.approval_status, PollItem.NEUTRAL)


class PopulateFunctionTest(TestCase):
    """Test cases for the main populate function"""

    def test_populate_creates_users(self):
        """Test that populate creates the correct number of users"""
        initial_count = User.objects.count()
        populate()
        final_count = User.objects.count()
        # Should create 4 users: user1, user2, admin, limited_user
        self.assertGreaterEqual(final_count - initial_count, 4)

    def test_populate_creates_categories(self):
        """Test that populate creates categories"""
        Category.objects.all().delete()
        Question.objects.all().delete()
        populate()
        categories = Category.objects.all()
        self.assertGreaterEqual(categories.count(), 3)
        category_names = [cat.name for cat in categories]
        self.assertIn('Python', category_names)
        self.assertIn('Django', category_names)
        self.assertIn('Web Development', category_names)

    def test_populate_creates_questions(self):
        """Test that populate creates questions"""
        initial_count = Question.objects.count()
        populate()
        final_count = Question.objects.count()
        # Should create at least 3 questions
        self.assertGreaterEqual(final_count - initial_count, 3)

    def test_populate_creates_comments(self):
        """Test that populate creates comments"""
        initial_count = Comment.objects.count()
        populate()
        final_count = Comment.objects.count()
        # Should create at least 3 comments
        self.assertGreaterEqual(final_count - initial_count, 3)

    def test_populate_creates_polls(self):
        """Test that populate creates polls"""
        initial_count = Poll.objects.count()
        populate()
        final_count = Poll.objects.count()
        # Should create at least 2 polls
        self.assertGreaterEqual(final_count - initial_count, 2)

    def test_populate_creates_poll_items(self):
        """Test that populate creates poll items"""
        initial_count = PollItem.objects.count()
        populate()
        final_count = PollItem.objects.count()
        # Should create at least 4 poll items
        self.assertGreaterEqual(final_count - initial_count, 4)

    def test_populate_creates_notifications(self):
        """Test that populate creates notifications"""
        initial_count = Notification.objects.count()
        populate()
        final_count = Notification.objects.count()
        # Should create at least 3 notifications
        self.assertGreaterEqual(final_count - initial_count, 3)

    def test_populate_idempotent(self):
        """Test that running populate twice doesn't duplicate data"""
        Question.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
        
        populate()
        count_after_first = User.objects.count()
        
        populate()
        count_after_second = User.objects.count()
        
        # Counts should be the same if get_or_create works properly
        self.assertEqual(count_after_first, count_after_second)

    def test_populate_data_integrity(self):
        """Test that populate creates valid relationships"""
        Question.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
        
        populate()
        
        # Check that questions have proper category relationships
        questions = Question.objects.all()
        for question in questions:
            self.assertIsNotNone(question.category_id)
            self.assertIn(question.category_id.name, 
                         ['Python', 'Django', 'Web Development'])
        
        # Check that polls have proper question relationships
        polls = Poll.objects.all()
        for poll in polls:
            self.assertIsNotNone(poll.question_id)
        
        # Check that poll items have proper poll relationships
        poll_items = PollItem.objects.all()
        for item in poll_items:
            self.assertIsNotNone(item.poll_id)

    def test_populate_user_types(self):
        """Test that populate creates users of different types"""
        User.objects.filter(username__in=['admin', 'limited_user']).delete()
        populate()
        
        admin_users = User.objects.filter(type=User.ADMIN)
        self.assertGreater(admin_users.count(), 0)
        
        limited_users = User.objects.filter(type=User.LIMITED)
        self.assertGreater(limited_users.count(), 0)

    def test_populate_all_models_have_data(self):
        """Test that all models have data after populate"""
        User.objects.all().delete()
        Category.objects.all().delete()
        Question.objects.all().delete()
        Comment.objects.all().delete()
        Poll.objects.all().delete()
        PollItem.objects.all().delete()
        Notification.objects.all().delete()
        
        populate()
        
        self.assertGreater(User.objects.count(), 0)
        self.assertGreater(Category.objects.count(), 0)
        self.assertGreater(Question.objects.count(), 0)
        self.assertGreater(Comment.objects.count(), 0)
        self.assertGreater(Poll.objects.count(), 0)
        self.assertGreater(PollItem.objects.count(), 0)
        self.assertGreater(Notification.objects.count(), 0)


class DataConsistencyTest(TestCase):
    """Test cases for data consistency across models"""

    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test', slug='test')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            date_of_birth='1990-01-01',
            password='StrongPass123!?',
            full_name='Test',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test',
            description='Test'
        )

    def test_foreign_key_relationships(self):
        """Test foreign key relationships are properly maintained"""
        questions = Question.objects.filter(category_id=self.category)
        self.assertGreater(questions.count(), 0)
        for question in questions:
            self.assertEqual(question.category_id.category_id, self.category.category_id)

    def test_cascade_delete_question_to_poll(self):
        """Test that deleting question deletes related polls"""
        poll = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question,
            title='Test'
        )
        poll_id = poll.poll_id
        self.question.delete()
        self.assertFalse(Poll.objects.filter(poll_id=poll_id).exists())

    def test_cascade_delete_question_to_notification(self):
        """Test that deleting question deletes related notifications"""
        notif = Notification.objects.create(
            notification_id=uuid.uuid4(),
            question_id=self.question,
            username=self.user,
            notification_type=Notification.LIKE
        )
        notif_id = notif.notification_id
        self.question.delete()
        self.assertFalse(Notification.objects.filter(notification_id=notif_id).exists())
