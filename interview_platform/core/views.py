from django.shortcuts import render

# Create your views here.
def editor_view(request):
    return render(request, 'core/editor.html')

def whiteboard_view(request):
    return render(request, 'core/whiteboard.html')