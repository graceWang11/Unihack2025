# This allows real-time text updates in the shared editor!
# websocket logic

import json
from src.server import server
from channels.generic.websocket import AsyncWebsocketConsumer

user_channels = {}

class WSConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		# await self.channel_layer.group_add("users", self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		for user in user_channels:
			if user_channels[user] == self.channel_name:
				del user_channels[user]
		# await self.channel_layer.group_discard("users", self.channel_name)

	async def receive(self, text_data):
		data = json.loads(text_data)
		if "type" in data:
			# Text/Whiteboard sync
			if data["type"] == "txt_update":
				room = server.get_room_from_user(data['id'])
				
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
