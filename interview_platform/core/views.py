from django.shortcuts import render

def home_view(request):
    return render(request, 'core/home.html')

def room_view(request, id):
    return render(request, 'core/room.html')
