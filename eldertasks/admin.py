from django.contrib import admin
from .models import TaskType, Task, TaskMedia, TaskApplication, Review, Notification


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ['name']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TaskMedia)
class TaskMediaAdmin(admin.ModelAdmin):
    list_display = ('task', 'media')
    list_filter =  ('task', 'media', 'task__elder')
    readonly_fields = ('created_at', 'updated_at')



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_type', 'status', 'elder', 'budget', 'is_urgent', 'created_at')
    list_filter = ('status', 'is_urgent', 'created_at', 'task_type')
    search_fields = ('title', 'description', 'elder__first_name', 'elder__last_name', 'task_type__name')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at', 'slug')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'task_type', 'elder', 'budget', 'status', 'is_urgent', 'location')
        }),
        ('Slug and Timestamps', {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskApplication)
class TaskApplicationAdmin(admin.ModelAdmin):
    list_display = ('task', 'helper', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('task__title', 'helper__first_name', 'helper__last_name', 'application_message')
    ordering = ['-applied_at']
    readonly_fields = ('applied_at', 'updated_at', 'helper_previous_tasks_count')
    fieldsets = (
        (None, {
            'fields': ('task', 'helper', 'status', 'application_message')
        }),
        ('Statistics', {
            'fields': ('helper_previous_tasks_count', 'applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('task', 'elder', 'helper', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('task__title', 'elder__first_name', 'elder__last_name', 'helper__first_name', 'helper__last_name', 'comment')
    ordering = ['-created_at']
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('task', 'elder', 'helper', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'message', 'related_task__title', 'related_user__first_name')
    ordering = ['-created_at']
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'notification_type', 'is_read')
        }),
        ('Related Objects', {
            'fields': ('related_task', 'related_user'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
