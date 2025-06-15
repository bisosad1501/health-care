import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from conversations.models import Conversation, ConversationParticipant
from conversations.models import Message
from ai.services import HealthcareAIService

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer cho chat real-time"""
    
    async def connect(self):
        """Kết nối WebSocket"""
        # Lấy conversation_id từ URL
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Lấy user từ scope (được xác thực bởi middleware)
        self.user = self.scope.get('user')
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Kiểm tra quyền truy cập conversation
        has_access = await self.check_conversation_access()
        if not has_access:
            await self.close()
            return
        
        # Tham gia group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Chấp nhận kết nối
        await self.accept()
        
        # Đánh dấu user online
        await self.mark_user_online()
        
        # Gửi thông báo user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'message': {
                    'type': 'user_joined',
                    'user_id': str(self.user.id) if hasattr(self.user, 'id') else 'anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
    
    async def disconnect(self, close_code):
        """Ngắt kết nối WebSocket"""
        # Đánh dấu user offline
        await self.mark_user_offline()
        
        # Gửi thông báo user left
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'message': {
                        'type': 'user_left',
                        'user_id': str(self.user.id) if hasattr(self.user, 'id') else 'anonymous',
                        'timestamp': timezone.now().isoformat()
                    }
                }
            )
            
            # Rời khỏi group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Nhận tin nhắn từ WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(text_data_json)
            elif message_type == 'message_read':
                await self.handle_message_read(text_data_json)
            elif message_type == 'ai_request':
                await self.handle_ai_request(text_data_json)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    async def handle_chat_message(self, data):
        """Xử lý tin nhắn chat"""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Tạo message trong database
        message = await self.create_message(content)
        if not message:
            return
        
        # Gửi tin nhắn đến tất cả thành viên trong group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'content': message.content,
                    'sender_type': message.sender_type,
                    'sender_id': message.sender_id,
                    'sender_name': message.sender_name,
                    'created_at': message.created_at.isoformat(),
                    'message_type': message.message_type,
                }
            }
        )
        
        # Nếu là tin nhắn từ user và conversation là AI assistant, tự động tạo phản hồi AI
        conversation = await self.get_conversation()
        if (message.sender_type == 'USER' and 
            conversation and 
            conversation.conversation_type == 'HEALTH_ASSISTANT'):
            
            # Tạo phản hồi AI bất đồng bộ
            asyncio.create_task(self.generate_ai_response(content))
    
    async def handle_typing_indicator(self, data):
        """Xử lý chỉ báo đang gõ"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'message': {
                    'user_id': str(self.user.id) if hasattr(self.user, 'id') else 'anonymous',
                    'is_typing': is_typing,
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
    
    async def handle_message_read(self, data):
        """Xử lý đánh dấu tin nhắn đã đọc"""
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)
    
    async def handle_ai_request(self, data):
        """Xử lý yêu cầu AI trực tiếp"""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Gửi thông báo AI đang xử lý
        await self.send(text_data=json.dumps({
            'type': 'ai_processing',
            'message': {
                'status': 'processing',
                'timestamp': timezone.now().isoformat()
            }
        }))
        
        # Tạo phản hồi AI
        await self.generate_ai_response(content)
    
    # Event handlers cho group messages
    async def chat_message(self, event):
        """Gửi tin nhắn chat"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        """Gửi chỉ báo đang gõ"""
        # Không gửi lại cho chính user đang gõ
        if event['message']['user_id'] != str(getattr(self.user, 'id', 'anonymous')):
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'message': event['message']
            }))
    
    async def user_status(self, event):
        """Gửi thông báo trạng thái user"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'message': event['message']
        }))
    
    async def ai_response(self, event):
        """Gửi phản hồi AI"""
        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'message': event['message']
        }))
    
    # Database operations
    @database_sync_to_async
    def check_conversation_access(self):
        """Kiểm tra quyền truy cập conversation"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            # Kiểm tra nếu user là participant
            user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
            
            # Check direct user_id
            if conversation.user_id == user_id:
                return True
            
            # Check doctor/patient IDs
            if (conversation.doctor_id == user_id or 
                conversation.patient_id == user_id):
                return True
            
            # Check participants
            participant_exists = ConversationParticipant.objects.filter(
                conversation=conversation,
                user_id=user_id,
                is_active=True
            ).exists()
            
            return participant_exists
            
        except Conversation.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking conversation access: {str(e)}")
            return False
    
    @database_sync_to_async
    def get_conversation(self):
        """Lấy conversation"""
        try:
            return Conversation.objects.get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_message(self, content):
        """Tạo message trong database"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
            user_name = getattr(self.user, 'name', '') or getattr(self.user, 'username', '')
            
            message = Message.objects.create(
                conversation=conversation,
                content=content,
                sender_type='USER',
                sender_id=user_id,
                sender_name=user_name,
                message_type='TEXT'
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return None
    
    @database_sync_to_async
    def mark_user_online(self):
        """Đánh dấu user online"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
            
            participant, created = ConversationParticipant.objects.get_or_create(
                conversation=conversation,
                user_id=user_id,
                defaults={
                    'user_name': getattr(self.user, 'name', '') or getattr(self.user, 'username', ''),
                    'role': 'USER',
                    'is_active': True
                }
            )
            
            participant.mark_as_online()
            
        except Exception as e:
            logger.error(f"Error marking user online: {str(e)}")
    
    @database_sync_to_async
    def mark_user_offline(self):
        """Đánh dấu user offline"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
            
            participant = ConversationParticipant.objects.filter(
                conversation=conversation,
                user_id=user_id
            ).first()
            
            if participant:
                participant.mark_as_offline()
                
        except Exception as e:
            logger.error(f"Error marking user offline: {str(e)}")
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Đánh dấu tin nhắn đã đọc"""
        try:
            message = Message.objects.get(id=message_id)
            user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
            message.mark_as_read(user_id)
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
    
    async def generate_ai_response(self, user_message):
        """Tạo phản hồi AI"""
        try:
            # Tạo AI service
            ai_service = HealthcareAIService()
            
            # Context cho AI
            context = {
                'user_id': str(self.user.id) if hasattr(self.user, 'id') else 'anonymous',
                'user_name': getattr(self.user, 'name', '') or getattr(self.user, 'username', ''),
                'conversation_id': self.conversation_id
            }
            
            # Gọi AI service bất đồng bộ
            result = await database_sync_to_async(ai_service.process_user_message)(
                self.conversation_id, user_message, context['user_id'], context
            )
            
            if result.get('success'):
                # Gửi phản hồi AI đến group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'ai_response',
                        'message': {
                            'content': result['message'],
                            'interaction_id': result.get('interaction_id'),
                            'tokens_used': result.get('tokens_used'),
                            'processing_time': result.get('processing_time'),
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
            else:
                # Gửi thông báo lỗi
                await self.send(text_data=json.dumps({
                    'type': 'ai_error',
                    'message': {
                        'error': result.get('error', 'Unknown error'),
                        'message': result.get('message', 'Xin lỗi, đã có lỗi xảy ra.'),
                        'timestamp': timezone.now().isoformat()
                    }
                }))
                
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'ai_error',
                'message': {
                    'error': str(e),
                    'message': 'Xin lỗi, tôi không thể tạo phản hồi lúc này.',
                    'timestamp': timezone.now().isoformat()
                }
            }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer cho thông báo real-time"""
    
    async def connect(self):
        """Kết nối WebSocket cho thông báo"""
        self.user = self.scope.get('user')
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Tham gia group thông báo của user
        self.user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
        self.notification_group_name = f'notifications_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Ngắt kết nối WebSocket thông báo"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Nhận tin nhắn (có thể để mark as read)"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_notification_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_read(notification_id)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in notification consumer")
    
    # Event handlers
    async def send_notification(self, event):
        """Gửi thông báo"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))
    
    async def new_message_notification(self, event):
        """Gửi thông báo tin nhắn mới"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def appointment_notification(self, event):
        """Gửi thông báo lịch hẹn"""
        await self.send(text_data=json.dumps({
            'type': 'appointment',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Đánh dấu thông báo đã đọc"""
        try:
            # Implement notification reading logic here
            # This would depend on your notification model
            pass
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")


class HealthMonitorConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer cho theo dõi sức khỏe real-time"""
    
    async def connect(self):
        """Kết nối WebSocket cho theo dõi sức khỏe"""
        self.user = self.scope.get('user')
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Tham gia group theo dõi sức khỏe
        self.user_id = str(self.user.id) if hasattr(self.user, 'id') else 'anonymous'
        self.health_group_name = f'health_monitor_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.health_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Ngắt kết nối WebSocket theo dõi sức khỏe"""
        if hasattr(self, 'health_group_name'):
            await self.channel_layer.group_discard(
                self.health_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Nhận dữ liệu sức khỏe"""
        try:
            text_data_json = json.loads(text_data)
            data_type = text_data_json.get('type')
            
            if data_type == 'vital_signs':
                await self.handle_vital_signs(text_data_json.get('data', {}))
            elif data_type == 'symptom_update':
                await self.handle_symptom_update(text_data_json.get('data', {}))
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in health monitor consumer")
    
    async def handle_vital_signs(self, data):
        """Xử lý dữ liệu sinh hiệu"""
        # Log vital signs data
        await database_sync_to_async(self.log_vital_signs)(data)
        
        # Check for alerts
        alerts = await database_sync_to_async(self.check_vital_signs_alerts)(data)
        
        if alerts:
            # Send alerts to user
            await self.send(text_data=json.dumps({
                'type': 'health_alert',
                'alerts': alerts,
                'timestamp': timezone.now().isoformat()
            }))
    
    async def handle_symptom_update(self, data):
        """Xử lý cập nhật triệu chứng"""
        # Process symptom data
        await database_sync_to_async(self.process_symptom_data)(data)
    
    # Event handlers
    async def health_alert(self, event):
        """Gửi cảnh báo sức khỏe"""
        await self.send(text_data=json.dumps({
            'type': 'health_alert',
            'message': event['message']
        }))
    
    async def medication_reminder(self, event):
        """Gửi nhắc nhở uống thuốc"""
        await self.send(text_data=json.dumps({
            'type': 'medication_reminder',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def log_vital_signs(self, data):
        """Log dữ liệu sinh hiệu"""
        try:
            # Implement vital signs logging
            logger.info(f"Vital signs received for user {self.user_id}: {data}")
        except Exception as e:
            logger.error(f"Error logging vital signs: {str(e)}")
    
    @database_sync_to_async
    def check_vital_signs_alerts(self, data):
        """Kiểm tra cảnh báo sinh hiệu"""
        alerts = []
        
        # Check blood pressure
        if 'blood_pressure' in data:
            systolic = data['blood_pressure'].get('systolic', 0)
            diastolic = data['blood_pressure'].get('diastolic', 0)
            
            if systolic > 140 or diastolic > 90:
                alerts.append({
                    'type': 'high_blood_pressure',
                    'message': 'Huyết áp cao được phát hiện. Vui lòng liên hệ bác sĩ.',
                    'severity': 'medium'
                })
        
        # Check heart rate
        if 'heart_rate' in data:
            heart_rate = data['heart_rate']
            if heart_rate > 100 or heart_rate < 60:
                alerts.append({
                    'type': 'abnormal_heart_rate',
                    'message': f'Nhịp tim bất thường: {heart_rate} bpm. Vui lòng theo dõi.',
                    'severity': 'medium' if 50 < heart_rate < 110 else 'high'
                })
        
        return alerts
    
    @database_sync_to_async
    def process_symptom_data(self, data):
        """Xử lý dữ liệu triệu chứng"""
        try:
            # Implement symptom data processing
            logger.info(f"Symptom data received for user {self.user_id}: {data}")
        except Exception as e:
            logger.error(f"Error processing symptom data: {str(e)}")
