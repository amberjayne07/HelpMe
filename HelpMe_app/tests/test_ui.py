import uuid

from django.test import TestCase, Client
from django.urls import reverse

from HelpMe_app.models import Category, Question, User, Poll, PollItem, Vote, Comment

class HomePageUITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category_a = Category.objects.create(name="General", slug="general")
        self.category_b = Category.objects.create(name="Help", slug="help")

    def test_anonymous_homepage_shows_welcome_message(self):
        resp = self.client.get(reverse("HelpMe_app:home"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "home.html")
        self.assertContains(resp, "What can we <b>help</b> you with?")

    def test_authenticated_homepage_shows_username(self):
        user = User.objects.create_user(
            username="uiuser",
            email="ui@example.com",
            date_of_birth="2000-01-01",
            password="Password123!",
            full_name="UI User",
            picture="test.jpg",
            type=User.STANDARD,
            password_hint="hint",
        )
        self.client.force_login(user)

        resp = self.client.get(reverse("HelpMe_app:home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "What can we <b>help</b> you with, uiuser?")
        self.assertContains(resp, "General")
        self.assertContains(resp, "Help")


class PostOverviewUITest(TestCase):
    def setUp(self):
        self.client = Client()

        self.category = Category.objects.create(name="Test", slug="test")
        self.user = User.objects.create_user(
            username="poster",
            email="poster@example.com",
            date_of_birth="1990-01-01",
            password="Password123!",
            full_name="Poster User",
            picture="test.jpg",
            type=User.STANDARD,
            password_hint="hint",
        )

        # Create a question and its poll
        self.question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=self.user,
            title="Test Question",
            description="This is a test question.",
        )

    def test_post_overview_shows_anonymous_for_limited_user(self):
        limited_user = User.objects.create_user(
            username="limited",
            email="limited@example.com",
            date_of_birth="1995-01-01",
            password="Password123!",
            full_name="Limited User",
            picture="test.jpg",
            type=User.LIMITED,
            password_hint="hint",
        )

        question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=limited_user,
            title="Anonymous post",
            description="Should be anonymous",
        )

        resp = self.client.get(reverse("HelpMe_app:post_overview", args=[question.question_id]))
        self.assertContains(resp, "Post shared anonymously")

    def test_poll_vote_form_shown_when_not_voted(self):
        poll = Poll.objects.create(poll_id=uuid.uuid4(), question_id=self.question, title="Poll")
        option = PollItem.objects.create(
            pollitem_id=uuid.uuid4(),
            poll_id=poll,
            username=self.user,
            content="Option 1",
            approval_status=PollItem.CREATOR,
        )

        resp = self.client.get(reverse("HelpMe_app:post_overview", args=[self.question.question_id]))
        self.assertContains(resp, "Select to vote")
        self.assertContains(resp, reverse("HelpMe_app:vote_on_poll", args=[option.pollitem_id]))

    def test_poll_results_shown_when_voted(self):
        self.client.force_login(self.user)

        poll = Poll.objects.create(poll_id=uuid.uuid4(), question_id=self.question, title="Poll")
        option = PollItem.objects.create(
            pollitem_id=uuid.uuid4(),
            poll_id=poll,
            username=self.user,
            content="Option 1",
            approval_status=PollItem.CREATOR,
        )

        Vote.objects.create(
            vote_id=uuid.uuid4(),
            username=self.user,
            session_key=None,
            pollitem_id=option,
        )

        resp = self.client.get(reverse("HelpMe_app:post_overview", args=[self.question.question_id]))
        self.assertContains(resp, "Results")
        self.assertContains(resp, "vote(s) counted")

    def test_post_overview_shows_comments_when_exist(self):
        commenter = User.objects.create_user(
            username="commenter",
            email="commenter@example.com",
            date_of_birth="1995-01-01",
            password="Password123!",
            full_name="Commenter User",
            picture="test.jpg",
            type=User.STANDARD,
            password_hint="hint",
        )

        Comment.objects.create(
            comment_id=uuid.uuid4(),
            question_id=self.question,
            username=commenter,
            text="This is a test comment.",
        )

        resp = self.client.get(reverse("HelpMe_app:post_overview", args=[self.question.question_id]))
        self.assertContains(resp, "This is a test comment.")
        self.assertNotContains(resp, "No comments yet.")


class AuthPagesUITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            date_of_birth="1990-01-01",
            password="Password123!",
            full_name="Test User",
            picture="test.jpg",
            type=User.STANDARD,
            password_hint="My hint",
        )

    def test_sign_up_page_renders_form(self):
        resp = self.client.get(reverse("HelpMe_app:sign_up"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "authentication/sign_up.html")
        self.assertContains(resp, "name=\"username\"")
        self.assertContains(resp, "name=\"email\"")
        self.assertContains(resp, "name=\"password1\"")

    def test_login_page_renders_form(self):
        resp = self.client.get(reverse("HelpMe_app:login"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "authentication/login.html")
        self.assertContains(resp, "name=\"username\"")
        self.assertContains(resp, "name=\"password\"")

    def test_login_page_shows_password_hint_on_invalid_login(self):
        resp = self.client.post(reverse("HelpMe_app:login"), {
            "username": "testuser",
            "password": "wrongpassword"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "My hint")

    def test_change_password_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("HelpMe_app:change_password"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "authentication/change_password.html")
        self.assertContains(resp, "name=\"old_password\"")
        self.assertContains(resp, "name=\"new_password1\"")

    def test_my_account_page_shows_user_posts(self):
        self.client.force_login(self.user)
        # Create a post for the user
        question = Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=Category.objects.create(name="Cat", slug="cat"),
            username=self.user,
            title="My Post",
            description="Description",
        )
        resp = self.client.get(reverse("HelpMe_app:my_account"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "authentication/my_account.html")
        self.assertContains(resp, "My Post")


class StaticPagesUITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_us_page_renders(self):
        resp = self.client.get(reverse("HelpMe_app:about_us"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "about_us.html")

    def test_account_upsell_page_renders(self):
        resp = self.client.get(reverse("HelpMe_app:account_upsell"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "account_upsell.html")


class SearchUITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="SearchCat", slug="searchcat")
        Question.objects.create(
            question_id=uuid.uuid4(),
            category_id=self.category,
            username=User.objects.create_user(
                username="searchuser",
                email="search@example.com",
                date_of_birth="1990-01-01",
                password="Password123!",
                full_name="Search User",
                picture="test.jpg",
                type=User.STANDARD,
                password_hint="hint",
            ),
            title="Searchable Question",
            description="This should be found.",
        )
 