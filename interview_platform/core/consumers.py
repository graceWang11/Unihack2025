# This allows real-time text updates in the shared editor!
# websocket logic

import json
import datetime
from src.server import server
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

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
			elif data["type"] == "start_timer":
				# Start a timer for the room
				room_id = data.get("room")
				duration = data.get("duration", 15 * 60)  # Default 15 minutes
				
				print(f"Received start_timer request for room {room_id}, duration {duration} seconds")
				
				room = server.get_room(room_id)
				if room:
					# Only set the end time if it's not already set
					if not room.end_time:
						end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
						room.end_time = end_time
						print(f"Setting timer for room {room_id} to end at {end_time}")
						
						# Also update the database session end time
						try:
							from core.models import InterviewSession
							session = InterviewSession.objects.get(id=room_id)
							session.end_time = end_time
							session.save()
							print(f"Updated database session {room_id} end time to {end_time}")
						except Exception as e:
							print(f"Error updating database session end time: {str(e)}")
					else:
						end_time = room.end_time
						print(f"Timer for room {room_id} already set to end at {end_time}")
					
					# Broadcast the timer to all users in the room
					print(f"Broadcasting timer to {len(room.users)} users in room {room_id}")
					for user in room.users:
						try:
							if user.id in user_channels:
								await self.channel_layer.send(
									user_channels[user.id],
									{
										"type": "timer_update",
										"end_time": end_time.isoformat()
									}
								)
								print(f"Sent timer update to user {user.id}")
							else:
								print(f"User {user.id} not found in user_channels")
						except Exception as e:
							print(f"Error sending timer to user {user.id}: {str(e)}")
			elif data["type"] == "get_timer":
				# Client is requesting the current timer state
				u = self.scope.get('user_id')
				if u:
					try:
						room = server.get_room_from_user(u)
						if room and hasattr(room, 'end_time') and room.end_time is not None:
							await self.send(text_data=json.dumps({
								"type": "timer_update",
								"end_time": room.end_time.isoformat()
							}))
					except Exception as e:
						print(f"Error getting timer: {str(e)}")
			elif data["type"] == "expire_session":
				# Mark the session as expired
				room_id = data.get("room")
				print(f"Marking session {room_id} as expired")
				
				try:
					# Use database_sync_to_async to update the database
					await self.mark_session_expired(room_id)
				except Exception as e:
					print(f"Error marking session as expired: {str(e)}")
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
			self.scope['user_id'] = uid  # Store user ID in scope
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
			
			# Send timer state if it exists
			try:
				if hasattr(room, 'end_time') and room.end_time is not None:
					await self.send(text_data=json.dumps({
						"type": "timer_update",
						"end_time": room.end_time.isoformat()
					}))
			except Exception as e:
				print(f"Error sending timer state: {str(e)}")

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

	# Broadcast timer update
	async def timer_update(self, event):
		await self.send(text_data=json.dumps({
			"type": "timer_update",
			"end_time": event["end_time"]
		}))

	@database_sync_to_async
	def mark_session_expired(self, room_id):
		"""Mark a session as expired in the database."""
		from core.models import InterviewSession
		try:
			session = InterviewSession.objects.get(id=room_id)
			session.is_active = False
			session.save()
			print(f"Successfully marked session {room_id} as inactive")
		except Exception as e:
			print(f"Database error marking session as expired: {str(e)}")
