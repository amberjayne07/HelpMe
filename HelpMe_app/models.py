from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    full_name = models.CharField(max_length=128)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=16)
    email = models.EmailField(unique=True)
    dateOfBirth = models.DateField()
    picture = models.ImageField(upload_to='user_pics/')
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

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Category(models.Model):
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.categoryID


class Question(models.Model):
    questionID = models.UUIDField(primary_key=True)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    title = models.CharField(max_length=240)
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    datePosted = models.DateTimeField(auto_now_add=True)
    lastUpdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.questionID


class Notification(models.Model):
    notificationID = models.UUIDField(primary_key=True)
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    
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

    def __str__(self):
        return self.notificationID


class Poll(models.Model):
    pollID = models.UUIDField(primary_key=True)
    questionID = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.pollID


class Comment(models.Model):
    commentID = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=30)
    text = models.TextField()
    postedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.commentID


class PollItem(models.Model):
    pollItemID = models.UUIDField(primary_key=True)
    pollID = models.ForeignKey(Poll, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
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
        return self.pollItemID
