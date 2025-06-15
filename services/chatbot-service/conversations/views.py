from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Conversation, ConversationParticipant, ConversationSummary, ConversationTemplate
from .serializers import (
    ConversationSerializer, ConversationCreateSerializer, ConversationListSerializer,
    ConversationParticipantSerializer, ConversationSummarySerializer,
    ConversationTemplateSerializer
)
from .services import ConversationService

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['conversation_type', 'status', 'priority']
    search_fields = ['title', 'metadata']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Return conversations where user is a participant"""
        return Conversation.objects.filter(
            participants__user=self.request.user,
            participants__is_active=True
        ).select_related('created_by').prefetch_related('participants__user')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'participant')
        
        try:
            user = User.objects.get(id=user_id)
            participant, created = ConversationParticipant.objects.get_or_create(
                conversation=conversation,
                user=user,
                defaults={'role': role}
            )
            
            if not created and not participant.is_active:
                participant.is_active = True
                participant.left_at = None
                participant.save()
            
            serializer = ConversationParticipantSerializer(participant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            participant = ConversationParticipant.objects.get(
                conversation=conversation,
                user_id=user_id,
                is_active=True
            )
            participant.is_active = False
            participant.left_at = timezone.now()
            participant.save()
            
            return Response({'message': 'Participant removed successfully'})
        
        except ConversationParticipant.DoesNotExist:
            return Response(
                {'error': 'Participant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive the conversation"""
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.archived_at = timezone.now()
        conversation.status = 'archived'
        conversation.save()
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive the conversation"""
        conversation = self.get_object()
        conversation.is_archived = False
        conversation.archived_at = None
        conversation.status = 'active'
        conversation.save()
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get all participants of the conversation"""
        conversation = self.get_object()
        participants = conversation.participants.filter(is_active=True)
        serializer = ConversationParticipantSerializer(participants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """Generate a summary of the conversation"""
        conversation = self.get_object()
        summary_type = request.data.get('summary_type', 'general')
        
        try:
            service = ConversationService()
            summary = service.generate_summary(conversation, summary_type, request.user)
            serializer = ConversationSummarySerializer(summary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing conversation participants
    """
    serializer_class = ConversationParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        queryset = ConversationParticipant.objects.select_related('user', 'conversation')
        
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        # Only return participants from conversations the user is part of
        return queryset.filter(
            conversation__participants__user=self.request.user,
            conversation__participants__is_active=True
        )


class ConversationSummaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversation summaries
    """
    serializer_class = ConversationSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['summary_type', 'conversation']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ConversationSummary.objects.filter(
            conversation__participants__user=self.request.user,
            conversation__participants__is_active=True
        ).select_related('conversation', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ConversationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversation templates
    """
    serializer_class = ConversationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        # Users can see public templates and their own templates
        return ConversationTemplate.objects.filter(
            Q(is_active=True) | Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a new conversation from this template"""
        template = self.get_object()
        title = request.data.get('title', f"Conversation from {template.name}")
        participant_ids = request.data.get('participant_ids', [])
        
        # Create conversation with template metadata
        conversation_data = {
            'title': title,
            'conversation_type': template.template_type,
            'metadata': {
                'template_id': template.id,
                'template_name': template.name,
                **template.metadata
            },
            'participant_ids': participant_ids
        }
        
        serializer = ConversationCreateSerializer(
            data=conversation_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            conversation = serializer.save()
            
            # Create initial message if template has one
            if template.initial_message:
                from conversations.models import Message
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=template.initial_message,
                    message_type='text'
                )
            
            response_serializer = ConversationSerializer(conversation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
