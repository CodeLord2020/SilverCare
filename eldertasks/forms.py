from django import forms
from .models import Task, TaskApplication, Review

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "budget", "task_type", "location"]

class TaskApplicationForm(forms.ModelForm):
    class Meta:
        model = TaskApplication
        fields = []  # No extra fields needed; user/task will be set automatically.

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
