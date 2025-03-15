from src.server import server
from django.shortcuts import render, redirect

def home_view(request):
	return render(request, 'core/home.html')

def room_view(request, id):
	return render(request, 'core/room.html', context={"room": id})

def create_room_view(request):
	room = server.new_room()
	
	return redirect('/room/' + room)