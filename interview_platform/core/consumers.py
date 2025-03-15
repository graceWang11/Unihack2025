# This allows real-time text updates in the shared editor!
# websocket logic

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WSConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.channel_layer.group_add("room", self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard("room", self.channel_name)

	async def receive(self, text_data):
		data = json.loads(text_data)
		await self.channel_layer.group_send(
			"room",
			{
				"type": data["type"], # forward updates to text or whiteboard based on received info
				"data": data["data"]
			}
		)

	async def txt_update(self, event):
		await self.send(text_data=json.dumps({
			"type": "txt_update",
			"data": event["data"]
		}))
	
	async def wb_buffer(self, event):
		await self.send(text_data=json.dumps({
			"type": "wb_buffer",
			"data": event["data"]
		}))
