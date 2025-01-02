from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Max, Count, Prefetch, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Conversation, Message, UnreadMessageCounter



class InboxView(LoginRequiredMixin, ListView):
    template_name = 'messaging/inbox.html'
    context_object_name = 'conversations'
    paginate_by = 20

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(elder=self.request.user) | Q(helper=self.request.user),
            is_active=True
        ).select_related(
            'elder', 
            'helper', 
            'task'
        ).prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-created_at')[:1],
                to_attr='latest_message'
            ),
            Prefetch(
                'unread_counters',
                queryset=UnreadMessageCounter.objects.filter(user=self.request.user),
                to_attr='user_unread'
            )
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__is_read=False,
                    messages__sender__is_not=self.request.user
                )
            )
        ).order_by('-last_message_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_unread'] = UnreadMessageCounter.objects.filter(
            user=self.request.user
        ).aggregate(total=Sum('count'))['total'] or 0
        return context
    




class ConversationView(LoginRequiredMixin, DetailView):
    template_name = 'messaging/conversation.html'
    context_object_name = 'conversation'

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(elder=self.request.user) | Q(helper=self.request.user),
            is_active=True
        ).select_related('elder', 'helper', 'task')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get messages with pagination
        messages = self.object.messages.select_related('sender').order_by('-created_at')
        paginator = Paginator(messages, 50)
        page = self.request.GET.get('page', 1)
        context['messages'] = paginator.get_page(page)
        
        # Mark messages as read
        if self.request.user != self.object.messages.last().sender:
            self.mark_messages_as_read()
        
        # Add other participants for UI
        context['other_participant'] = (
            self.object.helper if self.request.user == self.object.elder 
            else self.object.elder
        )
        
        return context

    def mark_messages_as_read(self):
        unread_messages = self.object.messages.filter(
            is_read=False
        ).exclude(
            sender=self.request.user
        )
        
        unread_messages.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        UnreadMessageCounter.objects.filter(
            conversation=self.object,
            user=self.request.user
        ).update(
            count=0,
            last_read_at=timezone.now()
        )

