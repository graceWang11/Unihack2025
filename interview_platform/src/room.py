import nanoid
from editor import Editor
from whiteboard import Whiteboard

class Room:
	def __init__(self):
		self.id = nanoid.generate(size=5)
		self.users = []
		self.editor = Editor()
		self.whiteboard = Whiteboard()
