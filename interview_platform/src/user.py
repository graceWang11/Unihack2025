import uuid

class User:
	def __init__(self):
		self.id = str(uuid.uuid4())[:5]