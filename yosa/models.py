from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username

class Event(models.Model):
    EVENT_TYPES = [
        ('party', 'Party'),
        ('meetup', 'Meetup'),
        ('game', 'Game Night'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_attendees = models.IntegerField()
    current_attendees = models.IntegerField(default=0)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def is_upcoming(self):
        return self.date > timezone.now()
    
    def seats_left(self):
        return self.max_attendees - self.current_attendees

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='confirmed')
    special_requests = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'event']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_feedback = models.BooleanField(default=False)  # If it's feedback to admin
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.subject} - {self.sender.username}"

class Trending(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.event.title} - {self.views} views"
