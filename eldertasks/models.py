from django.db import models
import uuid
# Create your models here.
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from cloudinary.models import CloudinaryField

class TaskType(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task Type"
        verbose_name_plural = "Task Types"
        ordering = ['name']

    def __str__(self):
        return self.name
    



class Task(models.Model):
    
    class Status(models.TextChoices):
        OPEN = 'Open', 'Open'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'Cancelled', 'Cancelled'

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    elder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )

    task_type = models.ForeignKey(
        TaskType, 
        on_delete=models.PROTECT, 
        related_name='tasks'
    )

    title = models.CharField(
        max_length=255,
        help_text="A descriptive title for the task"
    )

    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Detailed description of the task"
    )

    budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],  
        help_text="Budget allocated for the task"
    )

    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN
    )

    is_urgent = models.BooleanField(
        null=True,
        blank=True,
        default=False)

    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Location of the task, if applicable"
    )

    slug = models.SlugField(
        unique=True, 
        max_length=300, 
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['elder', 'status']),
            models.Index(fields=['task_type', 'status'])
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug
        """
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            
            # Ensure slug uniqueness
            while Task.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = unique_slug

        super().save(*args, **kwargs)
        

    def mark_as_completed(self, user):
        """
        Mark the task as completed, allowed only by the elder.
        """
        if user != self.elder:
            raise PermissionError("Only the elder who created the task can mark it as completed.")
        
        if self.status != self.Status.IN_PROGRESS:
            raise ValueError("Only tasks in progress can be marked as completed.")

        self.status = self.Status.COMPLETED
        self.save()

    # @property
    # def is_urgent(self):
    #     return self.is_urgent
        # return self.status in [self.Status.OPEN, self.Status.IN_PROGRESS]


class TaskMedia(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='taskmedia')
    media = CloudinaryField(
        'image', 
        blank=True, 
        null=True,
        help_text="Task picture (Max 5MB, recommended 500x500px)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.task and self.task.taskmedia.count() >= 3:
        # if TaskMedia.objects.filter(task = self.task).count() >= 3:
            raise ValidationError(message="Limit media reached for this Task")
        
    def save(self, *args, **kwargs):
        # if self.task.taskmedia.count() >= 3:
        #     raise ValidationError("A task cannot have more than 3 media resources.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.task.title} media resource"
    


class TaskApplication(models.Model):
    """
    Enhanced Task Application model with more robust status management
    """
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACCEPTED = 'Accepted', 'Accepted'
        REJECTED = 'Rejected', 'Rejected'
        WITHDRAWN = 'Withdrawn', 'Withdrawn'

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )

    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='applied_tasks'
    )

    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    application_message = models.TextField(
        blank=True, 
        null=True, 
        max_length=500
    )

    helper_previous_tasks_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of previously completed tasks"
    )

    class Meta:
        verbose_name = "Task Application"
        verbose_name_plural = "Task Applications"
        unique_together = ('task', 'helper')
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['helper', 'status'])
        ]

    def __str__(self):
        return f"Application for {self.task.title} by {self.helper}"

    def save(self, *args, **kwargs):
        """
        Override save method to update helper's task count
        """
        if not self.pk:
            # Only update on first save
            self.helper_previous_tasks_count = TaskApplication.objects.filter(
                helper=self.helper, 
                status=self.Status.ACCEPTED
            ).count()
        
        super().save(*args, **kwargs)

    def accept(self):
        """
        Method to accept the application with additional checks
        """
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending applications can be accepted")
        
        # Update task status
        self.task.status = self.task.Status.IN_PROGRESS
        self.task.save()

        self.status = self.Status.ACCEPTED
        self.save()

        self.task.status = self.task.Status.IN_PROGRESS
        self.task.save()


    def withdraw(self):
        """
        Withdraw the application and update the task status if needed.
        """
        if self.status != self.Status.ACCEPTED:
            raise ValueError("Only accepted applications can be withdrawn.")

        self.status = self.Status.WITHDRAWN
        self.save()

        # If there are no accepted applications, set task status to OPEN
        if not self.task.applications.filter(status=self.Status.ACCEPTED).exists():
            self.task.status = self.task.Status.OPEN
            self.task.save()


    def reject(self, reason=None):
        """
        Method to reject the application with optional reason
        """
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending applications can be rejected")
        
        self.status = self.Status.REJECTED
        self.save()
        



class Review(models.Model):
    """
    Enhanced Review model with comprehensive validation
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    task = models.ForeignKey(
        'Task', 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )

    elder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_reviews'
    )

    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_reviews'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, "Rating must be at least 1"),
            MaxValueValidator(5, "Rating must be at most 5")
        ]
    )

    comment = models.TextField(
        blank=True, 
        null=True, 
        max_length=1000
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # helpfulness_rating = models.DecimalField(
    #     max_digits=3, 
    #     decimal_places=2, 
    #     null=True, 
    #     blank=True
    # )


    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        unique_together = ('task', 'elder', 'helper')
        indexes = [
            models.Index(fields=['helper', 'rating']),
            models.Index(fields=['task', 'rating'])
        ]

    def __str__(self):
        return f"Review for {self.helper} - {self.rating} Stars"
    

    # def save(self, *args, **kwargs):
    #     """
    #     Custom save method to calculate helpfulness rating
    #     """
    #     if self.rating:
    #         # Simple helpfulness calculation (can be made more complex)
    #         self.helpfulness_rating = self.rating / 5.0 * 10
        
    #     super().save(*args, **kwargs)





class Notification(models.Model):
    """
    Advanced Notification model with more robust management
    """
    class NotificationType(models.TextChoices):
        TASK_APPLICATION = 'task_application', 'Task Application'
        TASK_STATUS_UPDATE = 'task_status', 'Task Status Update'
        REVIEW_RECEIVED = 'review', 'Review Received'
        MESSAGE = 'message', 'Message'
        SYSTEM = 'system', 'System Notification'

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )

    message = models.TextField(max_length=1000)

    notification_type = models.CharField(
        max_length=50, 
        choices=NotificationType.choices
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    related_task = models.ForeignKey(
        Task, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='generated_notifications'
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type'])
        ]

    def __str__(self):
        return f"Notification for {self.user}"
    

    def mark_as_read(self):
        """
        Mark notification as read with timestamp
        """
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        """
        Mark notification as unread
        """
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read'])

    @classmethod
    def create_notification(
        cls, 
        user, 
        message, 
        notification_type=NotificationType.MESSAGE,
        related_task=None,
        related_user=None
    ):
        """
        Class method to create notifications easily
        """
        return cls.objects.create(
            user=user,
            message=message,
            notification_type=notification_type,
            related_task=related_task,
            related_user=related_user
        )

