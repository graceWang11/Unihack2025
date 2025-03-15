#websocket routes
from django.urls import re_path
from core import consumers  # WebSocket consumers

websocket_urlpatterns = [
    #ws/ → WebSocket URL for the real-time editor and whiteboard.
    re_path(r'ws/$', consumers.WSConsumer.as_asgi()),
]
