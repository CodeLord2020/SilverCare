from django.urls import path
from . import views
from .views import (
    TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskMediaUploadView,
    TaskApplicationCreateView, ReviewCreateView, task_media_delete, TaskMediaUploadCreateView
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("<uuid:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<uuid:pk>/edit/", TaskUpdateView.as_view(), name="task_edit"),
    path('media/upload/create/', TaskMediaUploadCreateView.as_view(), name='task_media_upload_create'),
    path("<uuid:pk>/upload-media/", TaskMediaUploadView.as_view(), name="task_media_upload"),
    path("<uuid:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("<uuid:task_id>/apply/", TaskApplicationCreateView.as_view(), name="task_apply"),
    path("<uuid:task_id>/review/", ReviewCreateView.as_view(), name="task_review"),
    path("media/<int:pk>/delete/", task_media_delete, name="task_media_delete"),

    path('applications/<uuid:application_id>/accept/', views.accept_application, name='accept_application'),
    path('applications/<uuid:application_id>/reject/', views.reject_application, name='reject_application'),
    path('applications/<uuid:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('<uuid:task_id>/complete/', views.mark_task_complete, name='mark_task_complete'),
    
]
