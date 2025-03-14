#This allows real-time text updates in the shared editor!
#websocket logic
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EditorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("editor_room", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("editor_room", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "editor_room",
            {
                "type": "editor_update",
                "content": data["content"]
            }
        )

    async def editor_update(self, event):
        await self.send(text_data=json.dumps({
            "content": event["content"]
        }))
        
class WhiteboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("whiteboard_room", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("whiteboard_room", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "whiteboard_room",
            {
                "type": "whiteboard_update",
                "draw_data": data["draw_data"]
            }
        )

    async def whiteboard_update(self, event):
        await self.send(text_data=json.dumps({
            "draw_data": event["draw_data"]
        }))
