# Generated by Django 5.1.2 on 2024-12-03 13:20

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Task Type",
                "verbose_name_plural": "Task Types",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="A descriptive title for the task", max_length=255
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Detailed description of the task",
                        null=True,
                    ),
                ),
                (
                    "budget",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Budget allocated for the task",
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Open", "Open"),
                            ("In Progress", "In Progress"),
                            ("Completed", "Completed"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Open",
                        max_length=20,
                    ),
                ),
                (
                    "is_urgent",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        help_text="Location of the task, if applicable",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("slug", models.SlugField(blank=True, max_length=300, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "elder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tasks",
                        to="eldertasks.tasktype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Task",
                "verbose_name_plural": "Tasks",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, "Rating must be at least 1"
                            ),
                            django.core.validators.MaxValueValidator(
                                5, "Rating must be at most 5"
                            ),
                        ]
                    ),
                ),
                ("comment", models.TextField(blank=True, max_length=1000, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "elder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="given_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "helper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="eldertasks.task",
                    ),
                ),
            ],
            options={
                "verbose_name": "Review",
                "verbose_name_plural": "Reviews",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["helper", "rating"],
                        name="eldertasks__helper__fe0459_idx",
                    ),
                    models.Index(
                        fields=["task", "rating"], name="eldertasks__task_id_49bf15_idx"
                    ),
                ],
                "unique_together": {("task", "elder", "helper")},
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("message", models.TextField(max_length=1000)),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("task_application", "Task Application"),
                            ("task_status", "Task Status Update"),
                            ("review", "Review Received"),
                            ("message", "Message"),
                            ("system", "System Notification"),
                        ],
                        max_length=50,
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "related_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "related_task",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="eldertasks.task",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "is_read"],
                        name="eldertasks__user_id_a5133b_idx",
                    ),
                    models.Index(
                        fields=["notification_type"],
                        name="eldertasks__notific_556579_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="TaskApplication",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Accepted", "Accepted"),
                            ("Rejected", "Rejected"),
                            ("Withdrawn", "Withdrawn"),
                        ],
                        default="Pending",
                        max_length=20,
                    ),
                ),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "application_message",
                    models.TextField(blank=True, max_length=500, null=True),
                ),
                (
                    "helper_previous_tasks_count",
                    models.PositiveIntegerField(
                        default=0, help_text="Number of previously completed tasks"
                    ),
                ),
                (
                    "helper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applied_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="eldertasks.task",
                    ),
                ),
            ],
            options={
                "verbose_name": "Task Application",
                "verbose_name_plural": "Task Applications",
                "ordering": ["-applied_at"],
                "indexes": [
                    models.Index(
                        fields=["task", "status"], name="eldertasks__task_id_176c57_idx"
                    ),
                    models.Index(
                        fields=["helper", "status"],
                        name="eldertasks__helper__d2d7bb_idx",
                    ),
                ],
                "unique_together": {("task", "helper")},
            },
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["elder", "status"], name="eldertasks__elder_i_f7d393_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["task_type", "status"], name="eldertasks__task_ty_83ed2e_idx"
            ),
        ),
    ]
