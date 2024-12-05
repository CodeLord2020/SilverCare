from django import forms
from .models import Task, TaskApplication, Review, TaskMedia
from django.core.exceptions import ValidationError


class TaskApplicationForm(forms.ModelForm):
    class Meta:
        model = TaskApplication
        fields = []  # No extra fields needed; user/task will be set automatically.



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "budget", "task_type", "location"]


# class TaskMediaForm(forms.ModelForm):
#     class Meta:
#         model = TaskMedia
#         fields = ['media']
#         widgets = {
#             'media': forms.ClearableFileInput(attrs={
#                 'allow_multiple_selected': True,
#                 'class': 'form-control shadow-sm rounded-3',
#             }),
#         }

    # def __init__(self, *args, task=None, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.task = task

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     instance.task = self.task
    #     if commit:
    #         instance.save()
    #     return instance

    # def __init__(self, *args, **kwargs):
    #     self.task = kwargs.pop('task', None)
    #     super().__init__(*args, **kwargs)
        

    # def clean(self):
    #     cleaned_data = super().clean()
    #     media = cleaned_data.get('media')

    #     if self.task and media:
    #         if isinstance(media, list):
    #             if len(media) + self.task.taskmedia.count() > 3:
    #                 raise forms.ValidationError("Maximum of 3 media files per task allowed.")
    #         else:
    #             if self.task.taskmedia.count() >= 3:
    #                 raise forms.ValidationError("Maximum of 3 media files per task allowed.")

    #     return cleaned_data


# class TaskMediaForm(forms.ModelForm):
#     class Meta:
#         model = TaskMedia
#         fields = ['media']
#         widgets = {
#             'media': forms.ClearableFileInput(attrs={
#                 'allow_multiple_selected': True,
#                 # 'multiple': True,
#                 'class': 'form-control shadow-sm rounded-3',
#             }),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         media = cleaned_data.get('media')

#         if media:
#             if isinstance(media, list):
#                 if len(media) + self.instance.task.taskmedia.count() > 3:
#                     raise forms.ValidationError("Maximum of 3 media files per task allowed.")
#             else:
#                 if self.instance.task.taskmedia.count() >= 3:
#                     raise forms.ValidationError("Maximum of 3 media files per task allowed.")

#         return cleaned_data


class TaskMediaForm(forms.ModelForm):
    class Meta:
        model = TaskMedia
        fields = ['media']
        widgets = {
            'media': forms.ClearableFileInput(attrs={
                'allow_multiple_selected': True,
                'class': 'form-control shadow-sm rounded-3',
            }),
        }

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.task:
            instance.task = self.task
        if commit:
            instance.save()
        return instance