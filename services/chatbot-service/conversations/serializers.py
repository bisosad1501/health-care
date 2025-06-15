from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, ConversationParticipant, ConversationSummary, ConversationTemplate

User = get_user_model()


class ConversationParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = [
            'id', 'user', 'user_name', 'user_email', 'role', 
            'joined_at', 'left_at', 'is_active', 'permissions'
        ]
        read_only_fields = ['id', 'joined_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    message_count = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'status', 'priority',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'participants', 'metadata', 'is_archived', 'archived_at',
            'message_count', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_activity(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else obj.updated_at


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = [
            'title', 'conversation_type', 'priority', 'metadata', 'participant_ids'
        ]
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        request = self.context.get('request')
        
        conversation = Conversation.objects.create(
            created_by=request.user,
            **validated_data
        )
        
        # Add creator as participant
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=request.user,
            role='owner'
        )
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                ConversationParticipant.objects.create(
                    conversation=conversation,
                    user=user,
                    role='participant'
                )
            except User.DoesNotExist:
                continue
        
        return conversation


class ConversationSummarySerializer(serializers.ModelSerializer):
    conversation_title = serializers.CharField(source='conversation.title', read_only=True)
    
    class Meta:
        model = ConversationSummary
        fields = [
            'id', 'conversation', 'conversation_title', 'summary_type',
            'summary_text', 'key_points', 'action_items', 'participants_summary',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ConversationTemplateSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'category',
            'initial_message', 'suggested_responses', 'metadata',
            'is_active', 'created_by', 'created_at', 'updated_at',
            'usage_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_usage_count(self, obj):
        # Count conversations that used this template
        return Conversation.objects.filter(
            metadata__template_id=obj.id
        ).count()


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for conversation lists"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    participant_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'status', 'priority',
            'created_by_name', 'created_at', 'updated_at',
            'participant_count', 'unread_count', 'last_message_preview'
        ]
    
    def get_participant_count(self, obj):
        return obj.participants.filter(is_active=True).count()
    
    def get_unread_count(self, obj):
        # This would require message read receipts
        return 0  # Placeholder
    
    def get_last_message_preview(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            preview = last_message.content[:100]
            return preview + "..." if len(last_message.content) > 100 else preview
        return None
