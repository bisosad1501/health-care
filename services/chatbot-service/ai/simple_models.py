# Simplified AI models to avoid field errors
from django.db import models
from django.utils import timezone
import uuid


class SimpleAIModel(models.Model):
    """Simplified AI Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, default='chat')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ai_simple_model'
        
    def __str__(self):
        return self.name


class SimpleAIInteraction(models.Model):
    """Simplified AI Interaction"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ai_simple_interaction'
        
    def __str__(self):
        return f"Interaction {self.created_at}"
