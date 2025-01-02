from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from .models import Message, UnreadMessageCounter, Conversation
from eldertasks.models import TaskApplication



@receiver(post_save, sender = TaskApplication)
def create_conversation_on_application_accepted(sender, instance, created, **kwargs):
    if instance.status ==TaskApplication.Status.ACCEPTED:
        conversation, created = Conversation.objects.get_or_create(
            task = instance.task,
            defaults={
                'elder': instance.task.elder,
                'helper': instance.helper,
            }
        )

        if created:
            UnreadMessageCounter.objects.bulk_create([
                UnreadMessageCounter(user = instance.task.elder, conversation =conversation),
                UnreadMessageCounter(user = instance.helper, conversation = conversation)
            ])


@receiver(post_save, sender = Message)
def update_conversation_and_counter(sender, instance, created, **kwargs):
    if created:
         # Update conversation last message time
        instance.conversation.last_message_at = instance.created_at
        instance.conversation.save(update_fields=['last_message_at'])
        
        # Update unread counter for the recipient
        UnreadMessageCounter.objects.filter(
            conversation=instance.conversation
        ).exclude(
            user=instance.sender
        ).update(
            count=models.F('count') + 1
        )
