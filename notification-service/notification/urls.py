"""
URL configuration for notification app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, NotificationTemplateViewSet, 
    NotificationScheduleViewSet, InAppNotificationViewSet, 
    process_event
)

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')
router.register(r'templates', NotificationTemplateViewSet)
router.register(r'schedules', NotificationScheduleViewSet)
router.register(r'in-app', InAppNotificationViewSet, basename='in-app-notification')

urlpatterns = [
    path('', include(router.urls)),
    path('events', process_event, name='process-event'),
]
