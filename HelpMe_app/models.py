from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.password_validation import validate_password
import uuid


class UserManager(BaseUserManager):
    def create_user(self, username, email, full_name, date_of_birth, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        if not full_name:
            raise ValueError("Full name is required")
        if not date_of_birth:
            raise ValueError("Date of birth is required")

        email = self.normalize_email(email)

        if password:
            validate_password(password)

        user = self.model(username=username, email=email, full_name=full_name, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(password)  # hashes password
        user.save()
        return user

    def create_superuser(self, username, email, full_name, date_of_birth, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("type", "ADMIN")
        return self.create_user(username, email, full_name, date_of_birth, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=128)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField("Email address", unique=True)
    date_of_birth = models.DateField("Date of birth (YYYY-MM-DD)")
    picture = models.ImageField("User picture", upload_to='profilepics/', default='profilepics/default.png')
    join_date = models.DateField("Join date", auto_now_add=True)
    password_hint = models.CharField("Password hint", max_length=100)

    STANDARD = 'STANDARD'
    LIMITED = 'LIMITED'
    ADMIN = 'ADMIN'
    USER_TYPES = [
        (STANDARD, 'Standard'),
        (LIMITED, 'Limited'),
        (ADMIN, 'Admin'),
    ]
    type = models.CharField(max_length=10, choices=USER_TYPES, default=STANDARD)

    # REQUIRED for Django admin + authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'date_of_birth']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.type == self.ADMIN:
            self.is_staff = True
            self.is_superuser = True

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Question(models.Model):
    question_id = models.UUIDField(primary_key=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=240)
    description = models.TextField()
    liked_by = models.ManyToManyField(User, related_name='liked_questions', blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.liked_by.count()


class Comment(models.Model):
    comment_id = models.UUIDField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.comment_id)


class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    LIKE = 'LIKE'
    COMMENT = 'COMMENT'
    SUGGESTION = 'SUGGESTION'
    NOTIFICATION_TYPES = [
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (SUGGESTION, 'Suggestion'),
    ]
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    comment_id = models.OneToOneField(Comment, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.notification_type in [self.COMMENT, self.SUGGESTION] and not self.comment_id:
            raise ValueError(f"Notification type {self.notification_type} requires a comment ID to be set.")

        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.notification_id)


class Poll(models.Model):
    poll_id = models.UUIDField(primary_key=True)
    question_id = models.OneToOneField(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)

    def get_total_votes(self):
        return Vote.objects.filter(pollitem_id__poll_id=self).count() or 1

    def __str__(self):
        return self.title


class PollItem(models.Model):
    pollitem_id = models.UUIDField(primary_key=True)
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    content = models.CharField(max_length=50)

    CREATOR = 'CREATOR'
    NEUTRAL = 'NEUTRAL'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    APPROVAL_CHOICES = [
        (CREATOR, 'Creator'),
        (NEUTRAL, 'Neutral'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default=NEUTRAL)

    def __str__(self):
        return str(self.pollitem_id)


class Vote(models.Model):
    vote_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    pollitem_id = models.ForeignKey(PollItem, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('username', 'session_key', 'pollitem_id')