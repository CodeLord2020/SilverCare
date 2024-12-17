from django.shortcuts import render
# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Task, TaskApplication, Review, TaskMedia, TaskType
from .forms import TaskForm, TaskApplicationForm, ReviewForm, TaskMediaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Task List View (Elder View - Only their tasks)
# class TaskListView(LoginRequiredMixin, ListView):
#     model = Task
#     template_name = "tasks/task_list.html"
#     context_object_name = "tasks"
#     paginate_by = 10

#     def get_queryset(self):
#         return Task.objects.filter(elder=self.request.user).order_by("-created_at")

from django.db.models import Q

class TaskListView(ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.all().order_by("-created_at")
        
        # Filter by task type if provided
        task_type = self.request.GET.get('task_type')
        if task_type:
            queryset = queryset.filter(task_type__id=task_type)
        
        # Filter by owner if requested
        show_my_tasks = self.request.GET.get('my_tasks') == 'true'
        if show_my_tasks:
            queryset = queryset.filter(elder=self.request.user)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(location__icontains=search_query) 
            )
        
        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add task types for filtering
        context['task_types'] = TaskType.objects.filter(is_active=True)
        
        # Preserve filter parameters
        context['current_task_type'] = self.request.GET.get('task_type', '')
        context['show_my_tasks'] = self.request.GET.get('my_tasks') == 'true'
        context['search_query'] = self.request.GET.get('search', '')
        context['page_topic'] = "Task Explorer"
        
        return context
    


# Task Detail View (Includes Applications)
class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasktype = self.object.task_type.name
        
        # Filter applications based on status and user permissions
        if self.request.user.is_superuser:
            # Admin sees all applications
            applications = self.object.applications.all()
        else:
            # Regular users don't see withdrawn applications
            applications = self.object.applications.exclude(status='Withdrawn')
        
        context["applications"] = applications
        context["review_form"] = ReviewForm()  # If the task is completed, elder can leave a review
        context["medias"] = [media for media in self.object.taskmedia.all()]
        context['page_topic'] = f"CATEGORY: {tasktype}"
        return context



class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    success_url = reverse_lazy('tasks:task_list')  # Adjust to your desired redirect

    def form_valid(self, form):
        form.instance.elder = self.request.user
        
        # Save the task first
        self.object = form.save()
        
        # Handle media upload
        if 'media' in self.request.FILES:
            media_files = self.request.FILES.getlist('media')
            for media_file in media_files:
                TaskMedia.objects.create(
                    task=self.object,
                    media=media_file
                )
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_form'] = TaskMediaForm()  # Add media upload form to context
        context['page_topic'] = "CREATE TASK"
        return context
    

# class TaskCreateView(LoginRequiredMixin, CreateView):
#     model = Task
#     template_name = "tasks/task_form.html"
#     form_class = TaskForm

#     def form_valid(self, form):
#         form.instance.elder = self.request.user
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         # This allows for media upload after task creation
#         return reverse('tasks:task_media_upload_create')
    

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "tasks/taskupdate_form.html"
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy("tasks:task_detail", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        # Ensure only the owner can edit
        return Task.objects.filter(elder=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["media_form"] = TaskMediaForm()
        return context

# class TaskMediaUploadView(LoginRequiredMixin, View):
#     def post(self, request, pk, *args, **kwargs):
#         # Fetch the task instance
#         task = Task.objects.filter(id=pk, elder=request.user).first()
#         if not task:
#             return JsonResponse({"error": "Task not found or unauthorized."}, status=403)

#         # Handle the uploaded files
#         media_files = request.FILES.getlist("media")
#         if not media_files:
#             return JsonResponse({"error": "No files uploaded."}, status=400)

#         # Validate media count
#         if len(media_files) + task.taskmedia.count() > 3:
#             return JsonResponse({"error": "You can upload a maximum of 3 media files."}, status=400)

#         # Save each file as a new TaskMedia instance
#         for file in media_files:
#             TaskMedia.objects.create(task=task, media=file)

#         return redirect('tasks:task_edit', pk=pk)

        # return JsonResponse({"success": "Media uploaded successfully!"})

class TaskMediaUploadCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Get the most recently created task by the current user
        task = Task.objects.filter(elder=request.user).order_by('-created_at').first()
        
        if task and 'media' in request.FILES:
            media_files = request.FILES.getlist('media')
            for media_file in media_files:
                TaskMedia.objects.create(
                    task=task,
                    media=media_file
                )
        
        return redirect('tasks:task_detail', pk=task.pk)


class TaskMediaUploadView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        # Fetch the task instance
        task = Task.objects.filter(id=pk, elder=request.user).first()
        if not task:
            messages.error(request, "Task not found or you are not authorized to edit this task.")
            return redirect('tasks:task_edit', pk=pk)

        # Handle the uploaded files
        media_files = request.FILES.getlist("media")
        if not media_files:
            messages.error(request, "No files were uploaded. Please upload valid media files.")
            return redirect('tasks:task_edit', pk=pk)

        # Validate media count
        if len(media_files) + task.taskmedia.count() > 3:
            messages.error(request, "You can upload a maximum of 3 media files per task.")
            return redirect('tasks:task_edit', pk=pk)

        # Save each file as a new TaskMedia instance
        for file in media_files:
            TaskMedia.objects.create(task=task, media=file)

        messages.success(request, "Media files uploaded successfully.")
        return redirect('tasks:task_edit', pk=pk)

# class TaskMediaUploadView(LoginRequiredMixin, View):
#     def post(self, request, pk, *args, **kwargs):
#         print("task pk got here: ",pk)
#         task = Task.objects.filter(id=pk, elder=request.user).first()
#         print("task instance got here: ", task.elder.first_name)
#         if not task:
#             return JsonResponse({"error": "Task not found or unauthorized."}, status=403)

#         media_form = TaskMediaForm(request.POST, request.FILES, task=task)
#         if media_form.is_valid():
#             print("media form valid got here: ",pk)
#             if task.taskmedia.count() >= 3:
#                 count = task.taskmedia.count()
#                 print("task media count got here: ", count)
#                 return JsonResponse({"error": "You can upload a maximum of 3 media files."}, status=400)
#             # Handle multiple files if needed
#             media_files = request.FILES.getlist("media")
#             for file in media_files:
#                 media_form.instance = TaskMedia(task=task, media=file)
#                 media_form.save()

#             # for file in media_files:
#             #     TaskMedia.objects.create(task=task, media=file)
#             return JsonResponse({"success": "Media uploaded successfully!"})

#         return JsonResponse({"error": media_form.errors}, status=400)



# Task Delete View
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task_list")

    def get_queryset(self):
        # Ensure only task owners can delete
        return Task.objects.filter(elder=self.request.user)


def task_media_delete(request, pk):
    media = get_object_or_404(TaskMedia, pk=pk)
    task = media.task
    media.delete()
    return redirect('tasks:task_edit', pk=task.pk)


# Apply for a Task (Helper Applies)
class TaskApplicationCreateView(LoginRequiredMixin, CreateView):
    model = TaskApplication
    form_class = TaskApplicationForm

    def form_valid(self, form):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        form.instance.task = task
        form.instance.helper = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:task_detail", kwargs={"pk": self.kwargs["task_id"]})


# Review Submission View
class ReviewCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs["task_id"])
        if task.status == "Completed" and task.elder == request.user:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.task = task
                review.elder = request.user
                review.helper = task.applications.filter(status="Accepted").first().helper
                review.save()
                return redirect("tasks:task_detail", pk=task.id)
        return redirect("tasks:task_detail", pk=task.id)




@login_required
def accept_application(request, application_id):
    application = get_object_or_404(TaskApplication, id=application_id)
    
    if request.user != application.task.elder:
        messages.error(request, "You are not authorized to accept this application.")
        return redirect('task_detail', task_id=application.task.id)
    
    try:
        application.accept()
        messages.success(request, "Application accepted successfully.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('task_detail', task_id=application.task.id)


@login_required
def reject_application(request, application_id):
    application = get_object_or_404(TaskApplication, id=application_id)
    
    if request.user != application.task.elder:
        messages.error(request, "You are not authorized to reject this application.")
        return redirect('task_detail', task_id=application.task.id)
    
    try:
        application.reject()
        messages.success(request, "Application rejected successfully.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('task_detail', task_id=application.task.id)


@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(TaskApplication, id=application_id)
    
    if request.user != application.helper:
        messages.error(request, "You are not authorized to withdraw this application.")
        return redirect('task_detail', task_id=application.task.id)
    
    try:
        application.withdraw()
        messages.success(request, "Application withdrawn successfully.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('task_detail', task_id=application.task.id)


@login_required
def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user != task.elder:
        messages.error(request, "You are not authorized to mark this task as complete.")
        return redirect('task_detail', task_id=task.id)
    
    try:
        task.mark_as_completed(request.user)
        messages.success(request, "Task marked as completed.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('task_detail', task_id=task.id)