server = Server()

class Server:
	rooms = []

	def get_room(id):
		for room in rooms:
			if room.id == id:
				return room