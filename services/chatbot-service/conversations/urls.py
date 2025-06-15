from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('conversations', views.ConversationViewSet, basename='conversation')
router.register('participants', views.ConversationParticipantViewSet, basename='participant')
router.register('summaries', views.ConversationSummaryViewSet, basename='summary')
router.register('templates', views.ConversationTemplateViewSet, basename='template')

app_name = 'conversations'

urlpatterns = [
    path('', include(router.urls)),
]
