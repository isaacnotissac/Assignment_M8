from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def home(request):
    return HttpResponse("<h1>Hello, World!</h1><p>Welcome to my app!</p>")

def about(request):
    return HttpResponse("<h1>About</h1><p>This is the about page of my app!</p>")