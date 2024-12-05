from django.urls import path
from .views import (
    TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskMediaUploadView,
    TaskApplicationCreateView, ReviewCreateView, task_media_delete
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("<uuid:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<uuid:pk>/edit/", TaskUpdateView.as_view(), name="task_edit"),
    path("<uuid:pk>/upload-media/", TaskMediaUploadView.as_view(), name="task_media_upload"),
    path("<uuid:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("<uuid:task_id>/apply/", TaskApplicationCreateView.as_view(), name="task_apply"),
    path("<uuid:task_id>/review/", ReviewCreateView.as_view(), name="task_review"),
    path("media/<int:pk>/delete/", task_media_delete, name="task_media_delete"),
    
]
