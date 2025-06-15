from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
from datetime import datetime

from conversations.models import Conversation, Message
from knowledge.services import KnowledgeService


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_api(request):
    """Simple chat API endpoint"""
    try:
        data = request.data
        message_content = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_content:
            return Response({
                'error': 'Message content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                conversation = Conversation.objects.create(
                    title=f"Health Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    conversation_type='HEALTH_ASSISTANT'
                )
        else:
            conversation = Conversation.objects.create(
                title=f"Health Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                conversation_type='HEALTH_ASSISTANT'
            )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender_type='USER',
            content=message_content,
            content_type='TEXT'
        )
        
        # Generate AI response using knowledge base
        ai_response = generate_health_response(message_content)
        
        # Save AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            sender_type='ASSISTANT',
            content=ai_response,
            content_type='TEXT',
            metadata={
                'source': 'knowledge_base',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return Response({
            'response': ai_response,
            'conversation_id': str(conversation.id),
            'type': 'text',
            'metadata': {
                'knowledge_used': True,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_conversation(request):
    """Create new conversation"""
    try:
        data = request.data
        title = data.get('title', f"Health Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        conversation = Conversation.objects.create(
            title=title,
            conversation_type='HEALTH_ASSISTANT'
        )
        
        return Response({
            'conversation_id': str(conversation.id),
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': f'Internal server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'ok',
        'service': 'chatbot-service',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


def generate_health_response(user_message):
    """Generate health response based on user message"""
    message = user_message.lower()
    
    # Emergency keywords detection
    emergency_keywords = ['cấp cứu', 'khẩn cấp', 'nguy hiểm', 'khó thở', 'ngất xỉu', 'đau ngực']
    if any(keyword in message for keyword in emergency_keywords):
        return """🚨 **CẢNH BÁO KHẨN CẤP** 🚨

Tôi phát hiện câu hỏi của bạn có thể liên quan đến tình huống khẩn cấp.

**HÀNH ĐỘNG NGAY:**
• **Gọi 115** (Cấp cứu) hoặc đến bệnh viện gần nhất
• **Gọi 114** (Thông tin y tế) để được hướng dẫn

⚠️ **LỜI KHUYÊN:** Trong tình huống khẩn cấp, đừng chờ đợi. Hãy tìm kiếm sự giúp đỡ y tế ngay lập tức!"""
    
    # Common health topics
    if 'đau đầu' in message or 'sốt' in message:
        return """Dựa trên triệu chứng bạn mô tả (đau đầu và sốt), đây có thể là dấu hiệu của:

**Các nguyên nhân có thể:**
• Cảm cúm hoặc nhiễm trùng virus
• Nhiễm trùng đường hô hấp
• Căng thẳng, mệt mỏi
• Thiếu nước

**Khuyến nghị:**
• Nghỉ ngơi đầy đủ
• Uống nhiều nước
• Có thể dùng paracetamol giảm đau
• Nếu sốt >39°C hoặc kéo dài >3 ngày, hãy đến khám bác sĩ

⚠️ **Lưu ý:** Đây chỉ là thông tin tham khảo, không thay thế việc khám bác sĩ."""
    
    if 'cảm cúm' in message or 'phòng ngừa' in message:
        return """**Cách phòng ngừa cảm cúm hiệu quả:**

🛡️ **Phòng ngừa cơ bản:**
• Rửa tay thường xuyên với xà phòng
• Đeo khẩu trang nơi đông người
• Tránh tiếp xúc gần với người bệnh
• Không chạm tay vào mặt

💉 **Tiêm vaccine:**
• Tiêm vaccine cúm hàng năm
• Đặc biệt quan trọng với người cao tuổi, trẻ em

🏋️ **Tăng cường sức đề kháng:**
• Ăn đủ chất dinh dưỡng
• Tập thể dục đều đặn
• Ngủ đủ giấc (7-8 tiếng/đêm)
• Giảm stress"""
    
    if 'paracetamol' in message or 'thuốc' in message:
        return """**Thông tin về Paracetamol:**

💊 **Công dụng:**
• Giảm đau, hạ sốt
• An toàn cho hầu hết mọi người

⚠️ **Tác dụng phụ:**
• Hiếm gặp khi dùng đúng liều
• Tổn thương gan nếu quá liều
• Dị ứng (hiếm)

📋 **Liều dùng:**
• Người lớn: 500-1000mg/lần, tối đa 4g/ngày
• Trẻ em: theo cân nặng (10-15mg/kg/lần)

❌ **Chống chỉ định:**
• Suy gan nặng
• Dị ứng với paracetamol
• Uống nhiều rượu bia"""
    
    # Default response
    return """Cảm ơn bạn đã đặt câu hỏi về sức khỏe! 

🏥 **Tôi có thể hỗ trợ bạn về:**
• Triệu chứng và bệnh lý thường gặp
• Thông tin về thuốc và liều dùng
• Cách phòng ngừa bệnh tật
• Chế độ dinh dưỡng và lối sống lành mạnh
• Hướng dẫn sơ cứu cơ bản

💡 **Gợi ý:** Hãy mô tả cụ thể triệu chứng hoặc vấn đề sức khỏe mà bạn quan tâm để tôi có thể tư vấn chính xác hơn.

⚠️ **Lưu ý:** Thông tin tôi cung cấp chỉ mang tính chất tham khảo. Trong trường hợp cần thiết, hãy tham khảo ý kiến bác sĩ chuyên khoa."""
