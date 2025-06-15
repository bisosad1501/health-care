from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .services import AIHealthChatService
from .models import AIInteraction

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class HealthChatView(View):
    """API endpoint for health chat interactions"""
    
    def __init__(self):
        super().__init__()
        self.chat_service = AIHealthChatService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            query = data.get('message', '').strip()
            
            if not query:
                return JsonResponse({
                    'error': 'Message is required'
                }, status=400)
            
            # Get user info if available
            user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            session_id = data.get('session_id')
            
            # Process the health query
            result = self.chat_service.process_health_query(
                query=query,
                user_id=user_id,
                session_id=session_id
            )
            
            # Save interaction to database
            try:
                AIInteraction.objects.create(
                    user_id=user_id,
                    session_id=session_id,
                    user_query=query,
                    ai_response=result['response'],
                    confidence_score=result['confidence'],
                    response_time=result['response_time']
                )
            except Exception as e:
                logger.warning(f"Failed to save AI interaction: {e}")
            
            return JsonResponse({
                'response': result['response'],
                'confidence': result['confidence'],
                'response_time': result['response_time']
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in health chat: {e}")
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def health_info(request):
    """Get general health information"""
    try:
        chat_service = AIHealthChatService()
        advice = chat_service.knowledge_service.get_general_advice()
        
        return JsonResponse({
            'advice': advice,
            'disclaimer': 'This information is for educational purposes only. Consult healthcare professionals for medical advice.'
        })
        
    except Exception as e:
        logger.error(f"Error getting health info: {e}")
        return JsonResponse({
            'error': 'Unable to retrieve health information'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    """Simple chat endpoint for compatibility"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'error': 'Message is required'
            }, status=400)
        
        # Use health chat service for all queries
        chat_service = AIHealthChatService()
        result = chat_service.process_health_query(
            query=message,
            user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
            session_id=data.get('session_id')
        )
        
        return JsonResponse({
            'response': result['response']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)
