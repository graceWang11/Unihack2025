# This allows real-time text updates in the shared editor!
# websocket logic

import json
import asyncio
from src.server import server
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime, timedelta
from django.utils import timezone
from core.models import InterviewSession

user_channels = {}

class WSConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope["user"].id if self.scope["user"].is_authenticated else "anon"
		self.room_name = None
		await self.accept()
		
		# Start background task to broadcast global time
		asyncio.create_task(self.broadcast_time())

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
		try:
			data = json.loads(text_data)
			
			# Handle join request
			if 'join' in data:
				self.room_name = f"room_{data['join']}"
				
				# Join room group
				await self.channel_layer.group_add(
					self.room_name,
					self.channel_name
				)
				
				# Send back join confirmation
				await self.send(text_data=json.dumps({
					'join': self.user_id
				}))
			
			# Handle timer start request
			elif data.get('type') == 'start_timer':
				room_id = data.get('room')
				duration = data.get('duration', 900)  # Default 15 minutes
				
				if room_id:
					# Update session end time in database using sync_to_async
					try:
						end_time = await self.update_session_end_time(room_id, duration)
						
						# Broadcast timer update to room
						if end_time:
							await self.channel_layer.group_send(
								f"room_{room_id}",
								{
									'type': 'timer_update',
									'end_time': end_time.isoformat()
								}
							)
					except Exception as e:
						print(f"Error updating database session end time: {e}")
			
			# Handle get_timer request
			elif data.get('type') == 'get_timer':
				if self.room_name:
					room_id = self.room_name.replace('room_', '')
					try:
						end_time = await self.get_session_end_time(room_id)
						if end_time:
							await self.send(text_data=json.dumps({
								'type': 'timer_update',
								'end_time': end_time.isoformat()
							}))
					except Exception as e:
						print(f"Error getting session end time: {e}")
			
			# Handle other message types (text update, whiteboard update, etc.)
			elif 'type' in data:
				# Broadcast to room group
				if self.room_name:
					await self.channel_layer.group_send(
						self.room_name,
						{
							'type': data['type'],
							'data': data.get('data', '')
						}
					)
		
		except json.JSONDecodeError:
			print("Received invalid JSON")
		except Exception as e:
			print(f"Error processing message: {e}")

	# Handlers for different message types
	async def txt_update(self, event):
		await self.send(text_data=json.dumps({
			'type': 'txt_update',
			'data': event['data']
		}))
	
	async def wb_buffer(self, event):
		await self.send(text_data=json.dumps({
			'type': 'wb_buffer',
			'data': event['data']
		}))
	
	async def timer_update(self, event):
		await self.send(text_data=json.dumps({
			'type': 'timer_update',
			'end_time': event['end_time']
		}))

	# Database access methods using sync_to_async
	@database_sync_to_async
	def update_session_end_time(self, room_id, duration):
		try:
			session = InterviewSession.objects.get(id=room_id)
			end_time = timezone.now() + timedelta(seconds=duration)
			session.end_time = end_time
			session.save()
			return end_time
		except InterviewSession.DoesNotExist:
			print(f"InterviewSession with ID {room_id} not found")
			return None
		except Exception as e:
			print(f"Error updating session end time: {e}")
			return None
	
	@database_sync_to_async
	def get_session_end_time(self, room_id):
		try:
			session = InterviewSession.objects.get(id=room_id)
			return session.end_time
		except InterviewSession.DoesNotExist:
			print(f"InterviewSession with ID {room_id} not found")
			return None
		except Exception as e:
			print(f"Error getting session end time: {e}")
			return None

	async def broadcast_time(self):
		"""Broadcast global time to all clients periodically."""
		while True:
			if self.room_name:
				# Send the current time to all clients in the room
				await self.channel_layer.group_send(
					self.room_name,
					{
						'type': 'global_time',
						'timestamp': int(timezone.now().timestamp()),
					}
				)
			await asyncio.sleep(5)  # Update every 5 seconds

	async def global_time(self, event):
		"""Send global time to the client"""
		await self.send(text_data=json.dumps({
			'type': 'global_time',
			'timestamp': event['timestamp'],
		}))
