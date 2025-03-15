import uuid
from src.editor import Editor
from src.whiteboard import Whiteboard
from src.user import User

class Room:
	def __init__(self, room_id=None):
		self.id = room_id if room_id else str(uuid.uuid4())[:8]
		self.users = []
		self.editor = Editor()
		self.whiteboard = Whiteboard()

	def remove_user(self, id):
		for user in self.users:
			if user.id == id:
				self.users.remove(user)