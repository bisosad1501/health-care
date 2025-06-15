from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='ai_chat'),
    path('health/', views.health_info, name='health_info'),
    path('health-chat/', views.HealthChatView.as_view(), name='health_chat'),
]
