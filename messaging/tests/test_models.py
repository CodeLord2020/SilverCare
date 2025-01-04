
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Conversation, Message, UnreadMessageCounter
from eldertasks.models import Task, TaskApplication
import uuid

User = get_user_model()

class MessageModelTests(TestCase):
    def setUp(self):
        # Create users
        self.elder = User.objects.create_user(
            email='elder@test.com',
            password='testpass123',
            first_name='Elder',
            last_name='Test',
            is_verified = True
        )
        self.helper = User.objects.create_user(
            email='helper@test.com',
            password='testpass123',
            first_name='Helper',
            last_name='Test',
            is_verified = True
        )
        
        # Create task
        self.task = Task.objects.create(
            elder=self.elder,
            title='Test Task',
            budget=100.00
        )
        
        # Create conversation
        self.conversation = Conversation.objects.create(
            task=self.task,
            elder=self.elder,
            helper=self.helper
        )

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.elder,
            content="Test message"
        )
        self.assertEqual(message.content, "Test message")
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)

    def test_unread_counter_update(self):
        # Create message from elder to helper
        Message.objects.create(
            conversation=self.conversation,
            sender=self.elder,
            content="Test message"
        )
        
        counter = UnreadMessageCounter.objects.get(
            conversation=self.conversation,
            user=self.helper
        )
        self.assertEqual(counter.count, 1)

    def test_conversation_last_message_update(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.elder,
            content="Test message"
        )
        self.conversation.refresh_from_db()
        self.assertEqual(
            self.conversation.last_message_at.timestamp(),
            message.created_at.timestamp()
        )