from django.contrib import admin
from .models import AIInteraction


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'confidence_score', 'response_time')
    list_filter = ('created_at', 'confidence_score')
    search_fields = ('user_query', 'ai_response', 'session_id')
    readonly_fields = ('created_at', 'response_time')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'session_id', 'created_at')
        }),
        ('Interaction Data', {
            'fields': ('user_query', 'ai_response')
        }),
        ('Metrics', {
            'fields': ('confidence_score', 'response_time')
        }),
    )
