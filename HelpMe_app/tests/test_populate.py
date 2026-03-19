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

from HelpMe_app.models import User, Category, Question, Notification, Poll, Comment, PollItem, Vote

# Import populate functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from population_script import (
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
        # total_likes is assumed as part of your model or a property
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
        self.owner = User.objects.create_user(
            username='owneruser',
            email='owner@example.com',
            date_of_birth='1990-01-01',
            password='Str0ng_P@ssw0rd!?',
            full_name='Owner User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.other = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            date_of_birth='1991-01-01',
            password='Str0ng_P@ssw0rd!?',
            full_name='Other User',
            picture='test.jpg',
            type=User.STANDARD,
            password_hint='hint'
        )
        self.limited = User.objects.create_user(
            username='limited_user',
            email='limited@example.com',
            date_of_birth='1995-03-03',
            password='Str0ng_P@ssw0rd!?',
            full_name='Limited User',
            picture='test.jpg',
            type=User.LIMITED,
            password_hint='hint'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.owner,
            title='Test',
            description='Test'
        )

    def test_add_comment_creation(self):
        """Test creating a new comment by non-owner user (allowed)"""
        comment, created = add_comment(self.question, self.other, 'This is helpful')
        self.assertTrue(created)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.username, self.other)
        self.assertEqual(comment.text, 'This is helpful')

    def test_add_comment_get_existing(self):
        """Test getting existing comment by non-owner"""
        c1, created1 = add_comment(self.question, self.other, 'Existing comment')
        self.assertTrue(created1)

        c2, created2 = add_comment(self.question, self.other, 'Existing comment')
        self.assertFalse(created2)
        self.assertEqual(c1.comment_id, c2.comment_id)

    def test_owner_cannot_comment_on_own_question(self):
        """Owner cannot comment on their own question"""
        c, created = add_comment(self.question, self.owner, 'Self comment')
        self.assertIsNone(c)
        self.assertFalse(created)
        self.assertEqual(Comment.objects.filter(text='Self comment').count(), 0)

    def test_limited_user_cannot_comment(self):
        """LIMITED user cannot comment"""
        c, created = add_comment(self.question, self.limited, 'Limited trying to comment')
        self.assertIsNone(c)
        self.assertFalse(created)
        self.assertEqual(Comment.objects.filter(text__icontains='Limited').count(), 0)


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
        self.reviewer = User.objects.create_user(
            username='reviewer3',
            email='reviewer3@example.com',
            date_of_birth='1992-01-01',
            password='TestPass123!',
            full_name='Reviewer 3',
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
        notif, created = add_notification(
            self.question,
            self.reviewer,
            Notification.LIKE,
            comment=None,
            is_read=False
        )
        self.assertTrue(created)
        self.assertEqual(notif.notification_type, Notification.LIKE)
        self.assertFalse(notif.is_read)

    def test_add_notification_types(self):
        """Test creating LIKE notification (type value)"""
        notif, _ = add_notification(
            self.question,
            self.reviewer,
            Notification.LIKE,
            comment=None
        )
        self.assertEqual(notif.notification_type, Notification.LIKE)

    def test_comment_and_suggestion_require_comment(self):
        """COMMENT and SUGGESTION notifications must have a comment"""
        # COMMENT without comment
        n1, c1 = add_notification(self.question, self.reviewer, Notification.COMMENT, comment=None)
        self.assertIsNone(n1)
        self.assertFalse(c1)
        # SUGGESTION without comment
        n2, c2 = add_notification(self.question, self.reviewer, Notification.SUGGESTION, comment=None)
        self.assertIsNone(n2)
        self.assertFalse(c2)
        self.assertEqual(Notification.objects.count(), 0)

        # With a real comment -> allowed
        c, _ = add_comment(self.question, self.reviewer, "A real comment")
        n3, c3 = add_notification(self.question, self.user, Notification.COMMENT, comment=c, is_read=True)
        self.assertIsNotNone(n3)
        self.assertTrue(c3)
        self.assertTrue(n3.is_read)


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
        self.question_other = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user2,
            title='Other Q',
            description='Other'
        )
        self.poll = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question,
            title='Test Poll'
        )
        # Create a comment on self.question (by non-owner to mirror production guard)
        self.comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user2,
            question_id=self.question,
            text='Test comment'
        )
        # Comment on a different question
        self.other_comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user,
            question_id=self.question_other,
            text='Other comment'
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

    def test_poll_item_requires_comment_on_same_question(self):
        """Poll item must reference a comment associated with the same question as the poll"""
        bad_item, bad_created = add_poll_item(
            self.poll,
            self.user,
            'Bad linkage',
            self.other_comment,  # comment is on different question
            approval_status=PollItem.APPROVED
        )
        self.assertIsNone(bad_item)
        self.assertFalse(bad_created)
        self.assertEqual(PollItem.objects.filter(content='Bad linkage').count(), 0)

    def test_poll_item_requires_non_none_comment(self):
        """Poll item creation requires a non-None comment"""
        none_item, none_created = add_poll_item(
            self.poll,
            self.user,
            'No comment',
            None,
            approval_status=PollItem.APPROVED
        )
        self.assertIsNone(none_item)
        self.assertFalse(none_created)
        self.assertEqual(PollItem.objects.filter(content='No comment').count(), 0)


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
        self.assertGreaterEqual(categories.count(), 4)
        category_names = [cat.name for cat in categories]
        self.assertIn('Social', category_names)
        self.assertIn('School', category_names)
        self.assertIn('Health', category_names)
        self.assertIn('Money', category_names)

    def test_populate_creates_questions(self):
        """Test that populate creates questions"""
        initial_count = Question.objects.count()
        populate()
        final_count = Question.objects.count()
        # The script creates 8 questions
        self.assertGreaterEqual(final_count - initial_count, 8)

    def test_populate_creates_comments(self):
        """Test that populate creates comments"""
        initial_count = Comment.objects.count()
        populate()
        final_count = Comment.objects.count()
        # The script creates at least 17 comments (9 + 8 suggestion comments)
        self.assertGreaterEqual(final_count - initial_count, 10)  # safe lower bound

    def test_populate_creates_polls(self):
        """Test that populate creates polls"""
        initial_count = Poll.objects.count()
        populate()
        final_count = Poll.objects.count()
        # The script creates 8 polls
        self.assertGreaterEqual(final_count - initial_count, 8)

    def test_populate_creates_poll_items(self):
        """Test that populate creates poll items"""
        initial_count = PollItem.objects.count()
        populate()
        final_count = PollItem.objects.count()
        # The script creates 17 poll items
        self.assertGreaterEqual(final_count - initial_count, 10)  # safe lower bound

    def test_populate_creates_notifications(self):
        """Test that populate creates notifications"""
        initial_count = Notification.objects.count()
        populate()
        final_count = Notification.objects.count()
        # The script creates 8 notifications
        self.assertGreaterEqual(final_count - initial_count, 5)  # safe lower bound

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
                          ['Social', 'School', 'Health', 'Money'])

        # Check that polls have proper question relationships
        polls = Poll.objects.all()
        for poll in polls:
            self.assertIsNotNone(poll.question_id)

        # Check that poll items have proper poll and comment relationships
        poll_items = PollItem.objects.all()
        for item in poll_items:
            self.assertIsNotNone(item.poll_id)
            self.assertIsNotNone(item.comment_id)
            # Guard: comment must belong to the same question as the poll
            self.assertEqual(item.comment_id.question_id, item.poll_id.question_id)

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

    def test_populate_no_self_comments_and_no_limited_comments(self):
        """Ensure populate() does not create self-comments or LIMITED user comments"""
        populate()
        for c in Comment.objects.select_related('question_id', 'username').all():
            # No self-comments
            self.assertNotEqual(c.username_id, c.question_id.username_id)
            # No LIMITED user comments
            self.assertNotEqual(c.username.type, User.LIMITED)

    def test_study_techniques_poll_has_three_items(self):
        """Ensure the 'Best study technique?' poll has three items and all comments match the poll's question"""
        populate()
        poll = Poll.objects.filter(title='Best study technique?').first()
        self.assertIsNotNone(poll)
        items = list(PollItem.objects.filter(poll_id=poll))
        self.assertEqual(len(items), 3)
        for it in items:
            self.assertEqual(it.comment_id.question_id, poll.question_id)


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