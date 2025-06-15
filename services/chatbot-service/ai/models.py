from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AIInteraction(models.Model):
    """Model to track AI interactions for health consultations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    user_query = models.TextField()
    ai_response = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"AI Interaction {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
