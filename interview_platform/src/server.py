from src.room import Room
from src.user import User

class Server:
	def __init__(self):
		self.rooms = []
		self.user_rooms = {}
	
	def new_user(self, room):
		user = User()
		self.get_room(room).users.append(user)
		self.user_rooms[user.id] = room
		return user.id
	
	def remove_user(self, id):
		self.get_room(self.user_rooms[id]).remove_user(id)
		self.user_rooms.pop(id, None)
	
	def new_room(self):
		room = Room()
		self.rooms.append(room)
		return room.id

	def get_room(self, id):
		for room in self.rooms:
			if room.id == id:
				return room
	
	def get_room_from_user(self, id):
		return self.get_room(self.user_rooms[id])

server = Server()