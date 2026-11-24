from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import TaskForm
from .models import Task


def home(request):
    return HttpResponse(
        '<h1>Hello, World!</h1><p>Welcome to my app!</p><p><a href="/tasks/">View tasks</a></p>'
    )

def about(request):
    return HttpResponse("<h1>About</h1><p>This is the about page of my app!</p>")


def task_list(request):
    tasks = Task.objects.select_related("category").all()
    return render(request, "myapp/task_list.html", {"tasks": tasks})


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task-list")
    else:
        form = TaskForm()

    return render(request, "myapp/task_form.html", {"form": form})