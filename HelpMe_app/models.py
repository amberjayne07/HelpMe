from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.password_validation import validate_password
import uuid


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        if password:
            validate_password(password)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # hashes password
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=128)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    dateOfBirth = models.DateField()
    picture = models.ImageField(upload_to='profilepics/',default='profilepics/default.png')
    joinDate = models.DateField(auto_now_add=True)
    passwordHint = models.CharField(max_length=100)

    STANDARD = 'STANDARD'
    LIMITED = 'LIMITED'
    ADMIN = 'ADMIN'
    USER_TYPES = [
        (STANDARD, 'Standard'),
        (LIMITED, 'Limited'),
        (ADMIN, 'Admin'),
    ]
    type = models.CharField(max_length=10, choices=USER_TYPES)

    # REQUIRED for Django admin + authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username
    


class Category(models.Model):
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Question(models.Model):
    questionID = models.UUIDField(primary_key=True)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=240)
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    datePosted = models.DateTimeField(auto_now_add=True)
    lastUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    commentID = models.UUIDField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    postedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.commentID)

class Notification(models.Model):
    notificationID = models.UUIDField(primary_key=True)
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    
    LIKE = 'LIKE'
    COMMENT = 'COMMENT'
    SUGGESTION = 'SUGGESTION'
    NOTIFICATION_TYPES = [
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (SUGGESTION, 'Suggestion'),
    ]
    notificationType = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    isRead = models.BooleanField(default=False)
    commentID = models.OneToOneField(Comment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.notificationID)


class Poll(models.Model):
    pollID = models.UUIDField(primary_key=True)
    questionID = models.OneToOneField(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title


class PollItem(models.Model):
    pollItemID = models.UUIDField(primary_key=True)
    pollID = models.ForeignKey(Poll, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    commentID = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
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
    approvalStatus = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default=NEUTRAL)

    def __str__(self):
        return str(self.pollItemID)
