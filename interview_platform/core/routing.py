#websocket routes
from django.urls import re_path
from core import consumers  # WebSocket consumers

websocket_urlpatterns = [
    re_path(r'ws/editor/$', consumers.EditorConsumer.as_asgi()),
    #ws/editor/ → WebSocket URL for the real-time text editor.
    re_path(r'ws/whiteboard/$', consumers.WhiteboardConsumer.as_asgi()),
    #ws/whiteboard/ → WebSocket URL for the real-time whiteboard.
]
