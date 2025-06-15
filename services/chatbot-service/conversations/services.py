from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Conversation, ConversationSummary, ConversationParticipant
from .models import Message


class ConversationService:
    """
    Service class for conversation-related business logic
    """
    
    def __init__(self):
        # Simplified - no AI service for now
        pass
    
    def create_conversation(self, created_by, title, conversation_type='general', 
                          participant_ids=None, metadata=None):
        """
        Create a new conversation with participants
        """
        conversation = Conversation.objects.create(
            title=title,
            conversation_type=conversation_type,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        # Add creator as owner
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=created_by,
            role='owner'
        )
        
        # Add other participants
        if participant_ids:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
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
    
    def get_user_conversations(self, user, status=None, conversation_type=None):
        """
        Get conversations for a specific user
        """
        queryset = Conversation.objects.filter(
            participants__user=user,
            participants__is_active=True
        ).distinct()
        
        if status:
            queryset = queryset.filter(status=status)
        
        if conversation_type:
            queryset = queryset.filter(conversation_type=conversation_type)
        
        return queryset.order_by('-updated_at')
    
    def get_conversation_statistics(self, user=None, days=30):
        """
        Get conversation statistics
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        base_query = Conversation.objects.filter(created_at__gte=cutoff_date)
        
        if user:
            base_query = base_query.filter(
                participants__user=user,
                participants__is_active=True
            )
        
        stats = {
            'total_conversations': base_query.count(),
            'active_conversations': base_query.filter(status='active').count(),
            'archived_conversations': base_query.filter(is_archived=True).count(),
            'by_type': base_query.values('conversation_type').annotate(
                count=Count('id')
            ),
            'by_status': base_query.values('status').annotate(
                count=Count('id')
            ),
            'average_participants': base_query.annotate(
                participant_count=Count('participants')
            ).aggregate(
                avg_participants=Count('participants')
            )['avg_participants'] or 0
        }
        
        return stats
    
    def generate_summary(self, conversation, summary_type='general', created_by=None):
        """
        Generate a summary of the conversation using AI
        """
        # Get all messages in the conversation
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('created_at').select_related('sender')
        
        if not messages.exists():
            raise ValueError("Cannot generate summary for empty conversation")
        
        # Prepare conversation context
        conversation_text = self._format_conversation_for_summary(messages)
        
        # Generate summary using AI service
        summary_data = self._generate_ai_summary(conversation_text, summary_type)
        
        # Create summary record
        summary = ConversationSummary.objects.create(
            conversation=conversation,
            summary_type=summary_type,
            summary_text=summary_data['summary'],
            key_points=summary_data.get('key_points', []),
            action_items=summary_data.get('action_items', []),
            participants_summary=summary_data.get('participants_summary', {}),
            created_by=created_by
        )
        
        return summary
    
    def _format_conversation_for_summary(self, messages):
        """
        Format conversation messages for AI summary generation
        """
        formatted_messages = []
        
        for message in messages:
            sender_name = message.sender.username if message.sender else "System"
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M")
            
            formatted_messages.append(
                f"[{timestamp}] {sender_name}: {message.content}"
            )
        
        return "\n".join(formatted_messages)
    
    def _generate_ai_summary(self, conversation_text, summary_type):
        """
        Generate AI summary based on conversation type
        """
        if summary_type == 'medical':
            prompt = f"""
            Analyze the following medical conversation and provide a comprehensive summary:
            
            {conversation_text}
            
            Please provide:
            1. A brief summary of the conversation
            2. Key medical points discussed
            3. Any symptoms or conditions mentioned
            4. Recommended actions or follow-ups
            5. Summary of each participant's contributions
            
            Format the response as JSON with keys: summary, key_points, action_items, participants_summary
            """
        elif summary_type == 'consultation':
            prompt = f"""
            Analyze the following consultation conversation and provide a summary:
            
            {conversation_text}
            
            Please provide:
            1. Main consultation topics
            2. Questions asked and answers provided
            3. Decisions made or recommendations given
            4. Next steps or follow-up actions
            5. Participant roles and contributions
            
            Format the response as JSON with keys: summary, key_points, action_items, participants_summary
            """
        else:  # general
            prompt = f"""
            Summarize the following conversation:
            
            {conversation_text}
            
            Please provide:
            1. A concise summary of the main discussion points
            2. Key decisions or outcomes
            3. Action items or next steps
            4. Overview of participant contributions
            
            Format the response as JSON with keys: summary, key_points, action_items, participants_summary
            """
        
        try:
            # Use AI service to generate summary
            ai_response = self.ai_service.generate_response(
                prompt=prompt,
                context={
                    'type': 'conversation_summary',
                    'summary_type': summary_type
                }
            )
            
            # Parse JSON response
            summary_data = json.loads(ai_response)
            
            return {
                'summary': summary_data.get('summary', ''),
                'key_points': summary_data.get('key_points', []),
                'action_items': summary_data.get('action_items', []),
                'participants_summary': summary_data.get('participants_summary', {})
            }
            
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to basic summary if AI fails
            newline_count = len(conversation_text.split('\n'))
            return {
                'summary': f"Summary generated from conversation with {newline_count} messages",
                'key_points': [],
                'action_items': [],
                'participants_summary': {}
            }
    
    def archive_old_conversations(self, days=365):
        """
        Archive conversations older than specified days
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_conversations = Conversation.objects.filter(
            updated_at__lt=cutoff_date,
            status='active',
            is_archived=False
        )
        
        archived_count = old_conversations.update(
            is_archived=True,
            archived_at=timezone.now(),
            status='archived'
        )
        
        return archived_count
    
    def get_conversation_health_metrics(self, conversation):
        """
        Get health-related metrics for a conversation
        """
        messages = Message.objects.filter(conversation=conversation)
        
        # Count different types of health-related content
        symptom_mentions = messages.filter(
            content__icontains='symptom'
        ).count()
        
        medication_mentions = messages.filter(
            Q(content__icontains='medication') | 
            Q(content__icontains='medicine') |
            Q(content__icontains='drug')
        ).count()
        
        appointment_mentions = messages.filter(
            Q(content__icontains='appointment') |
            Q(content__icontains='visit') |
            Q(content__icontains='schedule')
        ).count()
        
        return {
            'total_messages': messages.count(),
            'symptom_mentions': symptom_mentions,
            'medication_mentions': medication_mentions,
            'appointment_mentions': appointment_mentions,
            'health_score': self._calculate_health_conversation_score(
                symptom_mentions, medication_mentions, appointment_mentions
            )
        }
    
    def _calculate_health_conversation_score(self, symptoms, medications, appointments):
        """
        Calculate a health conversation relevance score
        """
        # Simple scoring algorithm
        score = (symptoms * 3) + (medications * 2) + (appointments * 1)
        return min(score, 100)  # Cap at 100
