# Ví dụ cụ thể: User đặt lịch hẹn qua Chatbot
# Example: Appointment booking workflow through Chatbot

from integrations import (
    appointment_service, user_service, medical_records_service, 
    notification_service, billing_service
)
from ai.services import HealthcareAIService
from conversations.models import Conversation
from conversations.models import Message

class ChatbotAppointmentWorkflow:
    """
    Workflow xử lý đặt lịch hẹn hoàn chỉnh qua Chatbot
    """
    
    def __init__(self):
        self.ai_service = HealthcareAIService()
    
    async def handle_appointment_request(self, user_message: str, user_id: int, conversation_id: int):
        """
        Xử lý yêu cầu đặt lịch hẹn từ user
        
        Ví dụ input: "Tôi muốn đặt lịch khám tim vào tuần sau"
        """
        
        # BƯỚC 1: Phân tích intent và extract thông tin
        intent_analysis = await self._analyze_appointment_intent(user_message)
        
        if intent_analysis['intent'] != 'book_appointment':
            return await self._handle_non_appointment_intent(intent_analysis, user_id)
        
        # BƯỚC 2: Lấy thông tin user từ User Service
        try:
            user_profile = await user_service.get_user_profile(user_id)
            user_medical_info = await user_service.get_user_medical_info(user_id)
        except Exception as e:
            return {
                "response": "Xin lỗi, không thể lấy thông tin tài khoản. Vui lòng thử lại.",
                "error": str(e)
            }
        
        # BƯỚC 3: Tìm bác sĩ phù hợp
        specialty = intent_analysis.get('specialty', 'general')
        location = user_profile.get('preferred_location')
        
        try:
            available_doctors = await appointment_service.search_doctors(
                specialty=specialty,
                location=location
            )
        except Exception as e:
            return {
                "response": f"Không thể tìm kiếm bác sĩ {specialty}. Vui lòng thử lại sau.",
                "error": str(e)
            }
        
        if not available_doctors:
            return await self._handle_no_doctors_available(specialty, user_id, conversation_id)
        
        # BƯỚC 4: Lấy lịch sử y tế để đưa ra gợi ý tốt hơn
        try:
            medical_history = await medical_records_service.get_patient_history(user_id)
            recent_diagnoses = await medical_records_service.get_recent_diagnoses(user_id, limit=3)
        except Exception as e:
            # Không bắt buộc phải có medical history
            medical_history = []
            recent_diagnoses = []
        
        # BƯỚC 5: Tìm lịch trống
        preferred_date = intent_analysis.get('preferred_date')
        if not preferred_date:
            # Mặc định tìm trong 2 tuần tới
            preferred_date = datetime.now() + timedelta(days=1)
        
        available_slots = []
        for doctor in available_doctors[:3]:  # Chỉ check 3 bác sĩ đầu tiên
            try:
                slots = await appointment_service.get_available_slots(
                    doctor_id=doctor['id'],
                    date=preferred_date
                )
                for slot in slots:
                    slot['doctor_info'] = doctor
                available_slots.extend(slots)
            except Exception as e:
                continue  # Skip doctor nếu có lỗi
        
        if not available_slots:
            return await self._handle_no_slots_available(
                available_doctors, user_id, conversation_id
            )
        
        # BƯỚC 6: Hiển thị options cho user
        return await self._present_appointment_options(
            available_slots, intent_analysis, user_id, conversation_id
        )
    
    async def _analyze_appointment_intent(self, user_message: str) -> dict:
        """Phân tích intent của user message"""
        
        # Sử dụng AI để phân tích
        ai_prompt = f"""
        Phân tích tin nhắn sau để xác định intent đặt lịch hẹn:
        "{user_message}"
        
        Trả về JSON với:
        - intent: book_appointment/check_appointment/cancel_appointment/general
        - specialty: chuyên khoa (tim, da liễu, nhi, v.v.)
        - preferred_date: ngày mong muốn (nếu có)
        - urgency: urgent/normal/flexible
        - symptoms: triệu chứng được mô tả (nếu có)
        """
        
        ai_response = await self.ai_service.call_openai_api(ai_prompt)
        
        try:
            import json
            return json.loads(ai_response['response'])
        except:
            # Fallback parsing
            return self._fallback_intent_parsing(user_message)
    
    async def _present_appointment_options(self, available_slots: list, 
                                         intent_analysis: dict, user_id: int, 
                                         conversation_id: int) -> dict:
        """Hiển thị các lựa chọn lịch hẹn cho user"""
        
        # Sắp xếp slots theo thời gian
        sorted_slots = sorted(available_slots, key=lambda x: x['datetime'])
        top_slots = sorted_slots[:5]  # Hiển thị 5 lựa chọn đầu tiên
        
        response_text = "🏥 Tôi tìm thấy các lịch hẹn sau:\n\n"
        
        quick_replies = []
        for i, slot in enumerate(top_slots, 1):
            doctor = slot['doctor_info']
            datetime_str = datetime.fromisoformat(slot['datetime']).strftime('%d/%m/%Y %H:%M')
            
            response_text += f"{i}. 👨‍⚕️ BS. {doctor['name']}\n"
            response_text += f"   📅 {datetime_str}\n"
            response_text += f"   🏥 {doctor['hospital']}\n"
            response_text += f"   💰 {slot.get('cost', 'Miễn phí')}\n\n"
            
            quick_replies.append(f"Chọn lịch {i}")
        
        quick_replies.extend(["Xem thêm lựa chọn", "Thay đổi thời gian", "Chọn bác sĩ khác"])
        
        # Lưu context để xử lý lựa chọn sau này
        await self._save_appointment_context(
            conversation_id, user_id, top_slots, intent_analysis
        )
        
        return {
            "response": response_text,
            "quick_replies": quick_replies,
            "appointment_options": top_slots,
            "next_action": "await_slot_selection"
        }
    
    async def confirm_appointment_selection(self, slot_index: int, user_id: int, 
                                          conversation_id: int, additional_info: dict = None):
        """Xác nhận lựa chọn lịch hẹn của user"""
        
        # Lấy context đã lưu
        context = await self._get_appointment_context(conversation_id, user_id)
        if not context or slot_index >= len(context['slots']):
            return {
                "response": "Không tìm thấy thông tin lịch hẹn. Vui lòng bắt đầu lại.",
                "error": "Invalid slot selection"
            }
        
        selected_slot = context['slots'][slot_index]
        
        # BƯỚC 1: Đặt lịch hẹn qua Appointment Service
        appointment_data = {
            'patient_id': user_id,
            'doctor_id': selected_slot['doctor_info']['id'],
            'appointment_datetime': selected_slot['datetime'],
            'reason': context['intent_analysis'].get('symptoms', 'Tư vấn sức khỏe'),
            'source': 'chatbot',
            'notes': additional_info.get('notes', ''),
            'contact_preference': additional_info.get('contact_preference', 'phone')
        }
        
        try:
            appointment = await appointment_service.book_appointment(appointment_data)
        except Exception as e:
            return {
                "response": "❌ Không thể đặt lịch hẹn. Vui lòng thử lại hoặc liên hệ tổng đài.",
                "error": str(e),
                "suggested_actions": ["Chọn lịch khác", "Liên hệ tổng đài: 1900-xxx"]
            }
        
        if not appointment.get('success'):
            return {
                "response": f"❌ Đặt lịch thất bại: {appointment.get('error', 'Lỗi không xác định')}",
                "suggested_actions": ["Chọn lịch khác", "Thử lại sau"]
            }
        
        appointment_id = appointment['appointment']['id']
        
        # BƯỚC 2: Gửi notifications
        try:
            await notification_service.send_appointment_confirmation(
                user_id, appointment['appointment']
            )
            await notification_service.schedule_appointment_reminder(
                user_id, appointment['appointment']
            )
        except Exception as e:
            # Không chặn flow nếu notification fail
            print(f"Notification error: {e}")
        
        # BƯỚC 3: Tạo consultation record
        try:
            consultation_data = {
                'appointment_id': appointment_id,
                'consultation_method': 'chatbot_booking',
                'symptoms_reported': context['intent_analysis'].get('symptoms', []),
                'ai_analysis': context.get('ai_analysis', {}),
                'booking_context': context
            }
            await medical_records_service.create_consultation_record(
                user_id, consultation_data
            )
        except Exception as e:
            print(f"Medical record creation error: {e}")
        
        # BƯỚC 4: Xử lý billing (nếu có phí)
        if selected_slot.get('cost', 0) > 0:
            try:
                billing_data = {
                    'appointment_id': appointment_id,
                    'consultation_fee': selected_slot['cost'],
                    'service_type': 'appointment_booking'
                }
                await billing_service.create_consultation_charge(user_id, billing_data)
            except Exception as e:
                print(f"Billing error: {e}")
        
        # BƯỚC 5: Tạo response thành công
        doctor = selected_slot['doctor_info']
        appointment_datetime = datetime.fromisoformat(appointment['appointment']['datetime'])
        
        success_response = f"""
✅ **Đặt lịch hẹn thành công!**

📋 **Thông tin lịch hẹn:**
🆔 Mã: {appointment['appointment']['code']}
👨‍⚕️ Bác sĩ: BS. {doctor['name']}
🏥 Bệnh viện: {doctor['hospital']}
📅 Thời gian: {appointment_datetime.strftime('%d/%m/%Y lúc %H:%M')}
📍 Phòng: {appointment['appointment'].get('room', 'Sẽ thông báo sau')}
💰 Chi phí: {selected_slot.get('cost', 'Miễn phí')}

📱 **Thông báo:**
- Bạn sẽ nhận được SMS xác nhận trong vài phút
- Nhắc nhở sẽ được gửi trước 24h
- Vui lòng đến sớm 15 phút

❓ **Cần hỗ trợ thêm?**
        """
        
        quick_replies = [
            "Xem chi tiết lịch hẹn",
            "Thêm vào lịch điện thoại", 
            "Đặt lịch hẹn khác",
            "Hướng dẫn đến bệnh viện",
            "Liên hệ bác sĩ"
        ]
        
        # BƯỚC 6: Cập nhật conversation
        await self._update_conversation_with_appointment(
            conversation_id, appointment['appointment']
        )
        
        return {
            "response": success_response,
            "quick_replies": quick_replies,
            "appointment_data": appointment['appointment'],
            "success": True,
            "next_actions": {
                "add_to_calendar": {
                    "title": f"Khám bệnh - BS. {doctor['name']}",
                    "datetime": appointment['appointment']['datetime'],
                    "location": doctor['hospital'],
                    "description": f"Lịch hẹn #{appointment['appointment']['code']}"
                },
                "contact_doctor": {
                    "phone": doctor.get('phone'),
                    "email": doctor.get('email')
                }
            }
        }
    
    async def _save_appointment_context(self, conversation_id: int, user_id: int, 
                                      slots: list, intent_analysis: dict):
        """Lưu context để sử dụng sau"""
        # Có thể lưu vào Redis hoặc database
        # Ở đây chỉ là example
        pass
    
    async def _get_appointment_context(self, conversation_id: int, user_id: int) -> dict:
        """Lấy context đã lưu"""
        # Retrieve from storage
        # Example return
        return {
            'slots': [],
            'intent_analysis': {},
            'timestamp': datetime.now()
        }
    
    async def _update_conversation_with_appointment(self, conversation_id: int, 
                                                  appointment_data: dict):
        """Cập nhật conversation với thông tin appointment"""
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Tạo system message
            system_message = f"""
🏥 Lịch hẹn đã được tạo thành công

📋 Mã lịch hẹn: {appointment_data['code']}
📅 Thời gian: {appointment_data['datetime']}
👨‍⚕️ Bác sĩ: {appointment_data['doctor_name']}
            """
            
            Message.objects.create(
                conversation=conversation,
                content=system_message,
                message_type='system',
                is_system_message=True,
                metadata={
                    'appointment_id': appointment_data['id'],
                    'message_type': 'appointment_confirmation'
                }
            )
            
            # Cập nhật conversation metadata
            if not conversation.metadata:
                conversation.metadata = {}
            
            conversation.metadata['last_appointment_id'] = appointment_data['id']
            conversation.metadata['appointment_count'] = conversation.metadata.get('appointment_count', 0) + 1
            conversation.save()
            
        except Exception as e:
            print(f"Error updating conversation: {e}")

# Example usage:
"""
workflow = ChatbotAppointmentWorkflow()

# User gửi tin nhắn
user_message = "Tôi muốn đặt lịch khám tim vào tuần sau"
user_id = 123
conversation_id = 456

# Xử lý request
result = await workflow.handle_appointment_request(user_message, user_id, conversation_id)

# User chọn lịch hẹn số 2
confirmation = await workflow.confirm_appointment_selection(
    slot_index=1,  # Index 1 = lựa chọn số 2
    user_id=user_id,
    conversation_id=conversation_id,
    additional_info={
        'notes': 'Có triệu chứng đau ngực nhẹ',
        'contact_preference': 'phone'
    }
)
"""
