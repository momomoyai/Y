from django.db import models
from django.utils import timezone
from datetime import datetime, date

class Person(models.Model):
    name = models.CharField(default="Jane Doe", max_length=100)
    username = models.CharField(default="user123", max_length=100, unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    joined_date = models.DateField(default=date.today)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

class Tweet(models.Model):
    parent_tweet = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comments'
    )

    content = models.TextField(max_length=280)
    liked_by = models.ManyToManyField(Person, related_name='liked_tweets', blank=True)
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(Person, on_delete = models.CASCADE)