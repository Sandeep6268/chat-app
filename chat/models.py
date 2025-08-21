from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(User, related_name='chatrooms')
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    read_timestamp = models.DateTimeField(null=True, blank=True)  # Add this field

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f'{self.sender.username}: {self.content}'
    

# Add this new model to track unread messages
class UserMessageStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_statuses')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='user_statuses')
    is_read = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'message')