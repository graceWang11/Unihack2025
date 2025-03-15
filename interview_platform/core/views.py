from django.shortcuts import render

def home_view(request):
    return render(request, 'core/home.html')

def editor_view(request):
    return render(request, 'core/editor.html')

def whiteboard_view(request):
    return render(request, 'core/whiteboard.html')

def home_view(request):
    return render(request, 'core/home.html')