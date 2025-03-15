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
		# Only try to remove if the user exists
		if id is not None and id in self.user_rooms:
			self.get_room(self.user_rooms[id]).remove_user(id)
			del self.user_rooms[id]
	
	def new_room(self, room_id=None):
		"""Create a new room with an optional specific ID."""
		room = Room(room_id)
		self.rooms.append(room)
		print(f"Created new room with ID: {room.id}")
		return room.id

	def get_room(self, id):
		print(f"Looking for room with ID: {id}")
		for room in self.rooms:
			if room.id == id:
				print(f"Found room with ID: {id}")
				return room
		print(f"Room with ID {id} not found")
		return None
	
	def get_room_from_user(self, id):
		return self.get_room(self.user_rooms[id])

server = Server()