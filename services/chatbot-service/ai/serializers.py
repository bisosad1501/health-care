from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AIInteraction, AIModel, AIPromptTemplate, AIUsageLog, AIFeedback

User = get_user_model()


class AIModelSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'provider', 'model_version', 'capabilities',
            'max_tokens', 'cost_per_token', 'is_active', 'configuration',
            'created_at', 'updated_at', 'usage_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_usage_count(self, obj):
        return obj.interactions.count()


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIPromptTemplate
        fields = [
            'id', 'name', 'description', 'template_text', 'category',
            'variables', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'usage_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_usage_count(self, obj):
        return AIInteraction.objects.filter(
            metadata__template_id=obj.id
        ).count()


class AIInteractionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    model_name = serializers.CharField(source='ai_model.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AIInteraction
        fields = [
            'id', 'user', 'user_name', 'ai_model', 'model_name',
            'conversation', 'intent', 'user_input', 'ai_response',
            'confidence_score', 'tokens_used', 'response_time',
            'duration_seconds', 'status', 'error_message',
            'metadata', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'response_time', 'tokens_used',
            'confidence_score', 'status', 'error_message'
        ]
    
    def get_duration_seconds(self, obj):
        if obj.response_time:
            return round(obj.response_time / 1000, 2)  # Convert ms to seconds
        return None


class AIInteractionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInteraction
        fields = [
            'conversation', 'user_input', 'intent', 'metadata'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        return AIInteraction.objects.create(
            user=request.user,
            **validated_data
        )


class AIUsageLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    model_name = serializers.CharField(source='ai_model.name', read_only=True)
    cost_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AIUsageLog
        fields = [
            'id', 'user', 'user_name', 'ai_model', 'model_name',
            'operation_type', 'tokens_used', 'cost', 'cost_display',
            'success', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_cost_display(self, obj):
        if obj.cost:
            return f"${obj.cost:.4f}"
        return "$0.0000"


class AIFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AIFeedback
        fields = [
            'id', 'interaction', 'user', 'user_name', 'rating',
            'feedback_text', 'is_helpful', 'improvement_suggestions',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']


class AIHealthAnalysisSerializer(serializers.Serializer):
    """
    Serializer for health analysis requests
    """
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text="List of symptoms described by the user"
    )
    duration = serializers.CharField(
        max_length=50,
        required=False,
        help_text="How long the symptoms have been present"
    )
    severity = serializers.ChoiceField(
        choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')],
        required=False,
        help_text="Severity level of symptoms"
    )
    medical_history = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Relevant medical history"
    )
    current_medications = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        help_text="Current medications"
    )
    age = serializers.IntegerField(
        required=False,
        min_value=0,
        max_value=150,
        help_text="Patient age"
    )
    gender = serializers.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        required=False,
        help_text="Patient gender"
    )


class AIHealthAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for health analysis responses
    """
    analysis = serializers.CharField(help_text="AI analysis of the symptoms")
    possible_conditions = serializers.ListField(
        child=serializers.CharField(),
        help_text="Possible medical conditions"
    )
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        help_text="Recommended actions"
    )
    severity_assessment = serializers.CharField(
        help_text="Assessment of symptom severity"
    )
    urgency_level = serializers.ChoiceField(
        choices=[
            ('low', 'Low - Monitor symptoms'),
            ('medium', 'Medium - Consider seeing a doctor'),
            ('high', 'High - Seek medical attention soon'),
            ('emergency', 'Emergency - Seek immediate medical care')
        ],
        help_text="Urgency level for seeking medical care"
    )
    disclaimer = serializers.CharField(
        help_text="Medical disclaimer",
        default="This analysis is for informational purposes only and should not replace professional medical advice."
    )
    confidence_score = serializers.FloatField(
        help_text="AI confidence in the analysis (0-1)"
    )


class AIChatRequestSerializer(serializers.Serializer):
    """
    Serializer for chat requests to AI
    """
    message = serializers.CharField(
        max_length=2000,
        help_text="User message to the AI"
    )
    conversation_id = serializers.IntegerField(
        required=False,
        help_text="ID of the conversation (for context)"
    )
    context = serializers.DictField(
        required=False,
        help_text="Additional context for the AI"
    )
    intent = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Detected or specified intent"
    )


class AIChatResponseSerializer(serializers.Serializer):
    """
    Serializer for chat responses from AI
    """
    response = serializers.CharField(help_text="AI response message")
    intent = serializers.CharField(help_text="Detected intent")
    confidence = serializers.FloatField(help_text="Response confidence")
    suggested_actions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Suggested follow-up actions"
    )
    quick_replies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Suggested quick reply options"
    )
    needs_human_intervention = serializers.BooleanField(
        help_text="Whether human intervention is recommended"
    )


class AIStatisticsSerializer(serializers.Serializer):
    """
    Serializer for AI usage statistics
    """
    total_interactions = serializers.IntegerField()
    successful_interactions = serializers.IntegerField()
    failed_interactions = serializers.IntegerField()
    average_response_time = serializers.FloatField()
    total_tokens_used = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=4)
    interactions_by_intent = serializers.DictField()
    interactions_by_day = serializers.DictField()
    average_confidence_score = serializers.FloatField()
    user_satisfaction_rating = serializers.FloatField()
