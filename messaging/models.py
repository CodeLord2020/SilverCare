from django.db import models
from eldertasks.models import Task
# Create your models here.
import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _




class Conversation(models.Model):

    id = models.UUIDField(
        primary_key = True,
        default=uuid.uuid4,
        editable=False
    )

    task = models.OneToOneField(Task,
                                on_delete=models.CASCADE,
                                related_name="conversation")
    
    elder = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='elder_conversation')
    
    helper = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='helpr_conversation')
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['elder', 'is_active']),
            models.Index(fields=['helper', 'is_active']),
            models.Index(fields=['task', 'is_active'])
        ]

    def __str__(self):
        return f"Chat: {self.task.title} ({self.elder.name} - {self.helper.name})"
    

class Message(models.Model):
    id = models.UUIDField(

        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    conversation = models.ForeignKey(Conversation,
                                     on_delete=models.CASCADE,
                                     related_name="messages")
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='sent_messages')
    
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'is_read'])
        ]

    def __str__(self):
        return f"Message from {self.sender.name} at {self.created_at}"
    


class UnreadMessageCounter(models.Model):
    """
    Keeps track of unread messages for each user in each conversation
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='unread_counters'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='unread_counters'
    )
    count = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'conversation']
        indexes = [
            models.Index(fields=['user', 'count'])
        ]