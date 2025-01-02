from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Max, Count, Prefetch
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
    
    