from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Tạo router
router = DefaultRouter()
router.register(r'categories', views.KnowledgeCategoryViewSet)
router.register(r'entries', views.KnowledgeEntryViewSet)
router.register(r'tags', views.KnowledgeTagViewSet)
router.register(r'terms', views.MedicalTermViewSet)
router.register(r'diseases', views.DiseaseInformationViewSet)
router.register(r'symptoms', views.SymptomInformationViewSet)
router.register(r'responses', views.ChatbotResponseViewSet)
router.register(r'search', views.KnowledgeSearchViewSet, basename='knowledge-search')
router.register(r'symptom-check', views.SymptomCheckViewSet, basename='symptom-check')
router.register(r'recommendations', views.KnowledgeRecommendationViewSet, basename='knowledge-recommendations')
router.register(r'stats', views.KnowledgeStatsViewSet, basename='knowledge-stats')
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
