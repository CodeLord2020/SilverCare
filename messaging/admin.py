from django.contrib import admin
from .models import Conversation, Message, UnreadMessageCounter

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'elder', 'helper', 'is_active', 'last_message_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('task__title', 'elder__name', 'helper__name')
    ordering = ('-last_message_at',)
    readonly_fields = ('id', 'last_message_at')
    fieldsets = (
        ("Basic Info", {
            'fields': ('id', 'task', 'elder', 'helper')
        }),
        ("Status", {
            'fields': ('is_active', 'last_message_at', 'created_at')
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('conversation__task__title', 'sender__name', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ("Message Details", {
            'fields': ('id', 'conversation', 'sender', 'content', 'created_at')
        }),
        ("Status", {
            'fields': ('is_read', 'read_at')
        }),
    )

@admin.register(UnreadMessageCounter)
class UnreadMessageCounterAdmin(admin.ModelAdmin):
    list_display = ('user', 'conversation', 'count', 'last_read_at')
    list_filter = ('count',)
    search_fields = ('user__name', 'conversation__task__title')
    ordering = ('-count',)
    readonly_fields = ('count', 'last_read_at')
    fieldsets = (
        ("User Info", {
            'fields': ('user', 'conversation')
        }),
        ("Message Stats", {
            'fields': ('count', 'last_read_at')
        }),
    )
