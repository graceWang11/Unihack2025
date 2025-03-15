# This allows real-time text updates in the shared editor!
# websocket logic

import json
from src.server import server
from channels.generic.websocket import AsyncWebsocketConsumer

user_channels = {}

class WSConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		print("WebSocket connection established")
		await self.accept()

	async def disconnect(self, close_code):
		print(f"WebSocket disconnected with code: {close_code}")
		# Get the user ID from the scope
		u = self.scope.get('user_id')
		
		# Only try to delete if user_id exists
		if u is not None and u in user_channels:
			del user_channels[u]
		
		# Only try to remove user if it exists
		try:
			server.remove_user(u)
		except Exception as e:
			print(f"Error removing user: {str(e)}")
		# await self.channel_layer.group_discard("users", self.channel_name)

	async def receive(self, text_data):
		data = json.loads(text_data)
		if "type" in data:
			# Text/Whiteboard sync
			if data["type"] == "txt_update":
				room = server.get_room_from_user(data['id'])
				
				room.editor.set_text(data["data"])
				
				# Broadcast new text
				for user in room.users:
					await self.channel_layer.send(
						user_channels[user.id],
						{
							"type": "txt_update",
							"data": data["data"]
						}
					)
			elif data["type"] == "wb_buffer":
				room = server.get_room_from_user(data['id'])
				# Update whiteboard state
				room.whiteboard.set_state(data["data"])

				# Broadcast new state
				for user in room.users:
					await self.channel_layer.send(
						user_channels[user.id],
						{
							"type": "wb_buffer",
							"data": data["data"]
						}
					)
		elif "join" in data:
			# Add user to room
			room = server.get_room(data["join"])
			# No room found
			if room == None:
				await self.send(text_data=json.dumps({
					"exit": 1,
				}))
				return
			
			# Create new user
			uid = server.new_user(data["join"])
			user_channels[uid] = self.channel_name
			
			# Send user ID and initial room state
			await self.send(text_data=json.dumps({
				"join": uid,
			}))
			await self.send(text_data=json.dumps({
				"type": "txt_update",
				"data": room.editor.get_text()
			}))
			await self.send(text_data=json.dumps({
				"type": "wb_buffer",
				"data": room.whiteboard.get_state()
			}))

	# Broadcast text update
	async def txt_update(self, event):
		await self.send(text_data=json.dumps({
			"type": "txt_update",
			"data": event["data"]
		}))
	
	# Broadcast whiteboard update
	async def wb_buffer(self, event):
		await self.send(text_data=json.dumps({
			"type": "wb_buffer",
			"data": event["data"]
		}))
