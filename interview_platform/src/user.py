import nanoid

class User:
	def __init__(self):
		self.id = nanoid.generate(size=5)