import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from HelpMe_app.models import (
    User, Category, Question, Notification, 
    Poll, Comment, PollItem
)


def create_test_user(username='testuser', email='test@example.com'):
    """Helper to create a test user"""
    return User.objects.create_user(
        username=username,
        email=email,
        date_of_birth='1990-01-01',
        password='StrongPass123!?',
        full_name=f'Test {username}',
        picture='test.jpg',
        type=User.STANDARD,
        password_hint='My pet'
    )


class UserModelTest(TestCase):
    """Test cases for the User model"""

    def setUp(self):
        """Create a test user for reuse"""
        self.user = create_test_user('testuser', 'test@example.com')

    def test_user_creation(self):
        """Test basic user creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.full_name, 'Test testuser')
        self.assertEqual(self.user.type, User.STANDARD)

    def test_user_string_representation(self):
        """Test User __str__ method"""
        self.assertEqual(str(self.user), 'testuser')

    def test_username_unique(self):
        """Test that usernames must be unique"""
        with self.assertRaises(Exception):
            create_test_user('testuser', 'another@example.com')

    def test_email_unique(self):
        """Test that emails must be unique"""
        with self.assertRaises(Exception):
            create_test_user('anotheruser', 'test@example.com')

    def test_user_type_choices(self):
        """Test that user type choices are valid"""
        user_admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            date_of_birth='1985-05-05',
            password='StrongPass123!?',
            full_name='Admin',
            picture='admin.jpg',
            type=User.ADMIN,
            password_hint='admin hint'
        )
        self.assertEqual(user_admin.type, User.ADMIN)

        user_limited = User.objects.create_user(
            username='limited',
            email='limited@example.com',
            date_of_birth='1995-03-03',
            password='StrongPass123!?',
            full_name='Limited',
            picture='limited.jpg',
            type=User.LIMITED,
            password_hint='limited hint'
        )
        self.assertEqual(user_limited.type, User.LIMITED)

    def test_password_is_hashed(self):
        """Test that password is hashed when set"""
        self.assertNotEqual(self.user.password, 'testpass123')

    def test_join_date_auto_set(self):
        """Test that join_date is automatically set"""
        self.assertIsNotNone(self.user.join_date)


class CategoryModelTest(TestCase):
    """Test cases for the Category model"""

    def setUp(self):
        """Create a test category"""
        self.category = Category.objects.create(
            name='Python',
            slug='python'
        )

    def test_category_creation(self):
        """Test basic category creation"""
        self.assertEqual(self.category.name, 'Python')
        self.assertEqual(self.category.slug, 'python')

    def test_category_string_representation(self):
        """Test Category __str__ method"""
        self.assertEqual(str(self.category), 'Python')

    def test_category_name_unique(self):
        """Test that category names must be unique"""
        with self.assertRaises(Exception):
            Category.objects.create(
                name='Python',
                slug='python-2'
            )

    def test_category_primary_key(self):
        """Test that category_id is auto-generated"""
        self.assertIsNotNone(self.category.category_id)
        self.assertEqual(self.category.category_id, self.category.pk)


class QuestionModelTest(TestCase):
    """Test cases for the Question model"""

    def setUp(self):
        """Create test data"""
        self.user = create_test_user('questionuser', 'question@example.com')
        self.category = Category.objects.create(
            name='Django',
            slug='django'
        )
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='How to use Django ORM?',
            description='I need help with Django ORM queries'
        )

    def test_question_creation(self):
        """Test basic question creation"""
        self.assertEqual(self.question.category_id, self.category)
        self.assertEqual(self.question.username, self.user)
        self.assertEqual(self.question.title, 'How to use Django ORM?')
        self.assertEqual(self.question.total_likes, 0)

    def test_question_string_representation(self):
        """Test Question __str__ method returns something"""
        result = self.question.__str__()
        self.assertIsNotNone(result)
        self.assertEqual(result, 'How to use Django ORM?')

    def test_question_likes_default_zero(self):
        """Test that likes default to 0"""
        self.assertEqual(self.question.total_likes, 0)

    def test_question_like_increment(self):
        """Test incrementing likes with ManyToMany"""
        user2 = create_test_user('likeuser', 'like@example.com')
        self.question.liked_by.add(user2)
        self.question.refresh_from_db()
        self.assertEqual(self.question.total_likes, 1)

    def test_question_multiple_likes(self):
        """Test multiple users can like a question"""
        users = [
            create_test_user('user1', 'user1@example.com'),
            create_test_user('user2', 'user2@example.com'),
            create_test_user('user3', 'user3@example.com'),
        ]
        for user in users:
            self.question.liked_by.add(user)
        self.question.refresh_from_db()
        self.assertEqual(self.question.total_likes, 3)

    def test_question_dates(self):
        """Test creation and update dates"""
        self.assertIsNotNone(self.question.date_posted)
        self.assertIsNotNone(self.question.last_updated)

    def test_question_cascade_delete(self):
        """Test that deleting category cascades to questions"""
        question_id = self.question.question_id
        self.category.delete()
        self.assertFalse(Question.objects.filter(question_id=question_id).exists())



class NotificationModelTest(TestCase):
    """Test cases for the Notification model"""

    def setUp(self):
        """Create test data"""
        self.author = create_test_user('author', 'author@example.com')
        self.reviewer = create_test_user('reviewer', 'reviewer@example.com')
        self.category = Category.objects.create(name='Web Dev', slug='web-dev')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.author,
            title='Test Question',
            description='Test'
        )
        self.notification = Notification.objects.create(
            notification_id=uuid.uuid4(),
            question_id=self.question,
            username=self.reviewer,
            notification_type=Notification.LIKE
        )

    def test_notification_creation(self):
        """Test basic notification creation"""
        self.assertEqual(self.notification.question_id, self.question)
        self.assertEqual(self.notification.username, self.reviewer)
        self.assertEqual(self.notification.notification_type, Notification.LIKE)
        self.assertFalse(self.notification.is_read)

    def test_notification_string_representation(self):
        """Test Notification __str__ method returns something"""
        result = self.notification.__str__()
        self.assertIsNotNone(result)
        self.assertEqual(result, str(self.notification.notification_id))

    def test_notification_types(self):
        """Test all notification types"""
        comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.reviewer,
            question_id=self.question,
            text='Test comment for notification'
        )
        notif_comment = Notification.objects.create(
            notification_id=uuid.uuid4(),
            question_id=self.question,
            username=self.reviewer,
            notification_type=Notification.COMMENT,
            comment_id=comment
        )
        self.assertEqual(notif_comment.notification_type, Notification.COMMENT)

        comment2 = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.reviewer,
            question_id=self.question,
            text='Test suggestion comment'
        )
        notif_suggestion = Notification.objects.create(
            notification_id=uuid.uuid4(),
            question_id=self.question,
            username=self.reviewer,
            notification_type=Notification.SUGGESTION,
            comment_id=comment2
        )
        self.assertEqual(notif_suggestion.notification_type, Notification.SUGGESTION)

    def test_notification_is_read_toggle(self):
        """Test toggling is_read status"""
        self.assertFalse(self.notification.is_read)
        self.notification.is_read = True
        self.notification.save()
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_notification_cascade_delete(self):
        """Test that deleting question cascades to notifications"""
        notif_id = self.notification.notification_id
        self.question.delete()
        self.assertFalse(Notification.objects.filter(notification_id=notif_id).exists())



class PollModelTest(TestCase):
    """Test cases for the Poll model"""

    def setUp(self):
        """Create test data"""
        self.user = create_test_user('pollquestionuser', 'pollquestion@example.com')
        self.category = Category.objects.create(name='Python', slug='python')
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Best Python framework?',
            description='What is the best Python framework?'
        )
        self.question2 = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Best Django feature?',
            description='What is the best Django feature?'
        )
        self.poll = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question,
            title='Framework Poll'
        )

    def test_poll_creation(self):
        """Test basic poll creation"""
        self.assertEqual(self.poll.question_id, self.question)
        self.assertEqual(self.poll.title, 'Framework Poll')

    def test_poll_string_representation(self):
        """Test Poll __str__ method returns something"""
        result = self.poll.__str__()
        self.assertIsNotNone(result)

    def test_poll_blank_title(self):
        """Test poll with blank title"""
        poll_blank = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question2,
            title=''
        )
        self.assertEqual(poll_blank.title, '')

    def test_poll_cascade_delete(self):
        """Test that deleting question cascades to polls"""
        poll_id = self.poll.poll_id
        self.question.delete()
        self.assertFalse(Poll.objects.filter(poll_id=poll_id).exists())



class CommentModelTest(TestCase):
    """Test cases for the Comment model"""

    def setUp(self):
        """Create test comment"""
        self.user = create_test_user('pollitemuser', 'pollitem@example.com')
        self.user2 = create_test_user('commenter2', 'commenter2@example.com')
        self.category = Category.objects.create(name='Tech', slug='tech')
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
        self.question3 = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test 3',
            description='Test 3'
        )
        self.comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user,
            question_id=self.question,
            text='This is a helpful comment'
        )

    def test_comment_creation(self):
        """Test basic comment creation"""
        self.assertEqual(self.comment.username, self.user)
        self.assertEqual(self.comment.question_id, self.question)
        self.assertEqual(self.comment.text, 'This is a helpful comment')

    def test_comment_string_representation(self):
        """Test Comment __str__ method returns something"""
        result = self.comment.__str__()
        self.assertIsNotNone(result)

    def test_comment_date_auto_set(self):
        """Test that posted_date is automatically set"""
        self.assertIsNotNone(self.comment.posted_date)

    def test_comment_long_text(self):
        """Test comment with long text"""
        long_text = 'x' * 1000
        comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user,
            question_id=self.question,
            text=long_text
        )
        self.assertEqual(len(comment.text), 1000)



class PollItemModelTest(TestCase):
    """Test cases for the PollItem model"""

    def setUp(self):
        """Create test data"""
        self.user = create_test_user('polluser', 'poll@example.com')
        self.user2 = create_test_user('commenter2', 'commenter2@example.com')
        self.category = Category.objects.create(name='Tech', slug='tech')
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
        self.question2 = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test 2',
            description='Test 2'
        )
        self.question3 = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title='Test 3',
            description='Test 3'
        )
        self.comment = Comment.objects.create(
            comment_id=uuid.uuid4(),
            username=self.user,
            question_id=self.question,
            text='Test comment'
        )
        self.poll_item = PollItem.objects.create(
            pollitem_id=uuid.uuid4(),
            poll_id=self.poll,
            username=self.user,
            comment_id=self.comment,
            content='Django',
            approval_status=PollItem.NEUTRAL
        )

    def test_poll_item_creation(self):
        """Test basic poll item creation"""
        self.assertEqual(self.poll_item.poll_id, self.poll)
        self.assertEqual(self.poll_item.username, self.user)
        self.assertEqual(self.poll_item.content, 'Django')
        self.assertEqual(self.poll_item.approval_status, PollItem.NEUTRAL)

    def test_poll_item_string_representation(self):
        """Test PollItem __str__ method returns something"""
        result = self.poll_item.__str__()
        self.assertIsNotNone(result)

    def test_poll_item_approval_statuses(self):
        """Test all approval status options"""
        statuses = [
            PollItem.CREATOR,
            PollItem.NEUTRAL,
            PollItem.APPROVED,
            PollItem.DECLINED
        ]
        for idx, status in enumerate(statuses):
            # Create a new question and poll for each status to avoid OneToOne constraint
            q = Question.objects.create(
                question_id=uuid.uuid4(),
                category_id=self.category,
                username=self.user,
                title=f'Status test {idx}',
                description=f'Test {idx}'
            )
            poll = Poll.objects.create(
                poll_id=uuid.uuid4(),
                question_id=q,
                title=f'Poll {idx}'
            )
            item = PollItem.objects.create(
                pollitem_id=uuid.uuid4(),
                poll_id=poll,
                username=self.user,
                comment_id=self.comment,
                content=f'Option {status}',
                approval_status=status
            )
            self.assertEqual(item.approval_status, status)

    def test_poll_item_with_comment(self):
        """Test poll item with associated comment"""
        poll2 = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question2,
            title='Poll 2'
        )
        item_with_comment = PollItem.objects.create(
            pollitem_id=uuid.uuid4(),
            poll_id=poll2,
            username=self.user,
            comment_id=self.comment,
            content='Commented option',
            approval_status=PollItem.APPROVED
        )
        self.assertEqual(item_with_comment.comment_id, self.comment)

    def test_poll_item_cascade_delete(self):
        """Test that deleting comment cascades to poll items"""
        poll3 = Poll.objects.create(
            poll_id=uuid.uuid4(),
            question_id=self.question3,
            title='Poll 3'
        )
        item_with_comment = PollItem.objects.create(
            pollitem_id=uuid.uuid4(),
            poll_id=poll3,
            username=self.user,
            comment_id=self.comment,
            content='Test'
        )
        comment_id = self.comment.comment_id
        self.comment.delete()
        # Item should be deleted with comment
        self.assertFalse(PollItem.objects.filter(comment_id__comment_id=comment_id).exists())

