from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:conversation_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notifications/<int:user_id>/', consumers.NotificationConsumer.as_asgi()),
    path('ws/health-monitor/<int:user_id>/', consumers.HealthMonitorConsumer.as_asgi()),
]
