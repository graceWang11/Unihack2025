import nanoid
from src.editor import Editor
from src.whiteboard import Whiteboard
from src.user import User

class Room:
	def __init__(self):
		self.id = nanoid.generate(size=5)
		self.users = []
		self.editor = Editor()
		self.whiteboard = Whiteboard()

	def remove_user(self, id):
		for user in self.users:
			if user.id == id:
				self.users.remove(user)