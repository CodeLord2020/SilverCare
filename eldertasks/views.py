from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Task, TaskApplication, Review
from .forms import TaskForm, TaskApplicationForm, ReviewForm

# Task List View (Elder View - Only their tasks)
class TaskListView(ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.filter(elder=self.request.user).order_by("-created_at")


# Task Detail View (Includes Applications)
class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["applications"] = self.object.applications.all()
        context["review_form"] = ReviewForm()  # If the task is completed, elder can leave a review
        return context


# Task Create View (Elder Creates Task)
class TaskCreateView(CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.elder = self.request.user
        return super().form_valid(form)


# Task Update View
class TaskUpdateView(UpdateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm

    def get_queryset(self):
        # Ensure only task owners can edit
        return Task.objects.filter(elder=self.request.user)


# Task Delete View
class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task_list")

    def get_queryset(self):
        # Ensure only task owners can delete
        return Task.objects.filter(elder=self.request.user)


# Apply for a Task (Helper Applies)
class TaskApplicationCreateView(CreateView):
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
class ReviewCreateView(View):
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
