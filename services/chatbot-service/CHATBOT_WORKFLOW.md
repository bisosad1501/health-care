# Chatbot Workflow Documentation
# Tài liệu mô tả luồng hoạt động của Healthcare Chatbot

## 1. MESSAGE PROCESSING FLOW (Luồng xử lý tin nhắn)

### Step 1: Message Reception
- User sends message via WebSocket or REST API
- Message is stored in database with metadata
- Real-time notification sent to other participants

### Step 2: Intent Detection
```python
# In messages/services.py - detect_message_intent()
def detect_message_intent(content):
    # Phân tích nội dung tin nhắn
    if "pain" or "hurt" in content:
        return "health_concern"
    elif "appointment" in content:
        return "appointment"
    elif "emergency" in content:
        return "emergency"
    # ... more intents
```

### Step 3: AI Processing
```python
# In ai/services.py - process_user_input()
def process_user_input(user_input, intent):
    # 1. Tìm kiếm trong knowledge base
    knowledge_results = search_knowledge(user_input)
    
    # 2. Xây dựng context cho AI
    context = build_medical_context(user_input, knowledge_results)
    
    # 3. Gọi OpenAI API
    ai_response = call_openai_api(context, intent)
    
    # 4. Trả về phản hồi có cấu trúc
    return format_response(ai_response)
```

## 2. REAL-TIME COMMUNICATION (Giao tiếp thời gian thực)

### WebSocket Consumers
```python
# websockets/consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        # 1. Parse message
        data = json.loads(text_data)
        
        # 2. Process with AI if needed
        if data['type'] == 'user_message':
            ai_response = await self.get_ai_response(data['message'])
            
        # 3. Broadcast to conversation participants
        await self.channel_layer.group_send(
            f"conversation_{self.conversation_id}",
            {
                'type': 'chat_message',
                'message': ai_response
            }
        )
```

## 3. MEDICAL KNOWLEDGE INTEGRATION (Tích hợp kiến thức y tế)

### Knowledge Search Process
```python
# knowledge/services.py
class KnowledgeSearchService:
    def search_medical_info(self, query):
        # 1. Tách entities y tế từ query
        entities = self.extract_medical_entities(query)
        
        # 2. Tìm kiếm trong database
        results = []
        if entities['symptoms']:
            results.extend(self.search_symptoms(entities['symptoms']))
        if entities['diseases']:
            results.extend(self.search_diseases(entities['diseases']))
            
        # 3. Rank results by relevance
        return self.rank_results(results, query)
```

## 4. AI HEALTH ANALYSIS (Phân tích sức khỏe bằng AI)

### Symptom Analysis Workflow
```python
# ai/views.py - analyze_symptoms endpoint
def analyze_symptoms(request):
    symptoms = request.data['symptoms']
    
    # 1. Validate input
    if not symptoms:
        return error_response("No symptoms provided")
    
    # 2. Build medical context
    context = {
        'symptoms': symptoms,
        'duration': request.data.get('duration'),
        'severity': request.data.get('severity'),
        'medical_history': request.data.get('medical_history', [])
    }
    
    # 3. Generate AI analysis
    analysis = ai_service.analyze_health_symptoms(**context)
    
    # 4. Return structured response
    return {
        'possible_conditions': analysis['conditions'],
        'recommendations': analysis['recommendations'],
        'urgency_level': analysis['urgency'],
        'disclaimer': 'This is not medical advice...'
    }
```

## 5. CONVERSATION MANAGEMENT (Quản lý hội thoại)

### Conversation Context Tracking
- Each conversation maintains context across messages
- AI remembers previous symptoms and conditions mentioned
- Conversation summaries generated periodically
- Medical history tracked throughout conversation

## 6. EMERGENCY DETECTION (Phát hiện trường hợp khẩn cấp)

### Emergency Keywords Detection
```python
EMERGENCY_KEYWORDS = [
    'chest pain', 'difficulty breathing', 'severe bleeding',
    'unconscious', 'severe allergic reaction', 'stroke symptoms'
]

def detect_emergency(message_content):
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_content.lower():
            return True, "EMERGENCY_DETECTED"
    return False, None
```

### Emergency Response
- Immediate alert to healthcare providers
- Instructions to call emergency services
- No AI processing delay for emergency cases
- Escalation to human medical staff

## 7. PERSONALIZATION (Cá nhân hóa)

### User Context Building
```python
def build_user_context(user_id):
    context = {
        'medical_history': get_user_medical_history(user_id),
        'current_medications': get_user_medications(user_id),
        'previous_conversations': get_recent_conversations(user_id),
        'preferences': get_user_preferences(user_id)
    }
    return context
```

## 8. QUALITY ASSURANCE (Đảm bảo chất lượng)

### Response Validation
- Medical information fact-checking against knowledge base
- Confidence scoring for AI responses
- Fallback to pre-approved responses for critical topics
- Human review queue for uncertain cases

### Feedback Loop
- User feedback collection after each interaction
- Response quality tracking
- Continuous improvement of AI prompts
- Medical expert review of responses

## 🤖 OPENAI INTEGRATION (Tích hợp OpenAI)

### Cấu hình OpenAI API
```python
# In settings.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Cần API key từ OpenAI
OPENAI_MODEL = 'gpt-3.5-turbo'  # Hoặc 'gpt-4' cho tính năng mạnh hơn
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.7  # Độ sáng tạo (0.0 = deterministic, 1.0 = creative)
```

### OpenAI API Call Process
```python
# In ai/services.py - HealthcareAIService
import openai

class HealthcareAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def call_openai_api(self, prompt, context=None):
        """
        Gọi OpenAI API với prompt được tối ưu cho healthcare
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý AI chuyên về y tế. Luôn nhấn mạnh rằng thông tin chỉ mang tính tham khảo và không thay thế tư vấn y tế chuyên nghiệp."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Gọi OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Lấy response từ OpenAI
            ai_response = response.choices[0].message.content
            
            # Log usage để theo dõi chi phí
            self.log_api_usage(response.usage)
            
            return {
                'response': ai_response,
                'tokens_used': response.usage.total_tokens,
                'model_used': self.model,
                'success': True
            }
            
        except openai.error.RateLimitError:
            return {'error': 'Rate limit exceeded', 'success': False}
        except openai.error.APIError as e:
            return {'error': f'OpenAI API error: {str(e)}', 'success': False}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}', 'success': False}
```

### Healthcare-Specific Prompts
```python
def build_healthcare_prompt(self, user_input, intent, context):
    """
    Xây dựng prompt chuyên biệt cho từng loại câu hỏi y tế
    """
    
    if intent == 'symptom_analysis':
        prompt = f"""
        PHÂN TÍCH TRIỆU CHỨNG Y TẾ:
        
        Bệnh nhân báo cáo: "{user_input}"
        
        Thông tin bổ sung:
        - Thời gian: {context.get('duration', 'Không rõ')}
        - Mức độ: {context.get('severity', 'Không rõ')}
        - Tiền sử bệnh: {context.get('medical_history', 'Không có')}
        
        Hãy phân tích và cung cấp:
        1. CÁC NGUYÊN NHÂN CÓ THỂ (3-5 nguyên nhân phổ biến nhất)
        2. KHUYẾN NGHỊ HÀNH ĐỘNG (theo thứ tự ưu tiên)
        3. DẤU HIỆU CẢNH BÁO (khi nào cần gặp bác sĩ gấp)
        4. CHĂM SÓC TẠI NHÀ (nếu phù hợp)
        
        LƯU Ý QUAN TRỌNG:
        - Luôn nhấn mạnh đây chỉ là thông tin tham khảo
        - Khuyến khích tham khảo ý kiến bác sĩ
        - Không đưa ra chẩn đoán chính xác
        - Ưu tiên an toàn của bệnh nhân
        
        Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
        """
    
    elif intent == 'medication_inquiry':
        prompt = f"""
        THÔNG TIN THUỐC Y TẾ:
        
        Câu hỏi về thuốc: "{user_input}"
        
        Hãy cung cấp thông tin về:
        1. CÔNG DỤNG CHÍNH của thuốc
        2. CÁCH DÙNG CƠ BẢN (liều lượng thông thường)
        3. TÁC DỤNG PHỤ THƯỜNG GẶP
        4. TƯƠNG TÁC THUỐC CẦN LƯU Ý
        5. KHUYẾN CÁO ĐỘC BIỆT
        
        LƯU Ý QUAN TRỌNG:
        - Luôn nhấn mạnh phải tuân theo chỉ định của bác sĩ
        - Không tự ý thay đổi liều lượng
        - Báo cáo tác dụng phụ cho bác sĩ
        - Kiểm tra tương tác với thuốc khác đang dùng
        
        Trả lời bằng tiếng Việt, chính xác và an toàn.
        """
    
    elif intent == 'emergency':
        prompt = f"""
        TÌNH HUỐNG KHẨN CẤP Y TẾ:
        
        Triệu chứng báo cáo: "{user_input}"
        
        🚨 CẢNH BÁO KHẨN CẤP 🚨
        
        Dựa trên triệu chứng được mô tả, đây có thể là tình huống cần can thiệp y tế gấp.
        
        HÀNH ĐỘNG NGAY LẬP TỨC:
        1. GỌI 115 (Cấp cứu) hoặc đến bệnh viện gần nhất
        2. KHÔNG TỰ Ý XỬ LÝ tại nhà
        3. KHÔNG TRỄ NÃNG việc tìm kiếm chăm sóc y tế
        
        Trong khi chờ cấp cứu:
        - Giữ bình tĩnh
        - Theo dõi tình trạng
        - Chuẩn bị thông tin y tế cần thiết
        
        ⚠️ KHUYẾN CÁO: Thông tin này không thay thế việc gọi cấp cứu ngay lập tức!
        """
    
    else:  # general inquiry
        prompt = f"""
        THÔNG TIN Y TẾ TỔNG QUÁT:
        
        Câu hỏi: "{user_input}"
        
        Hãy cung cấp thông tin y tế chính xác, dễ hiểu về vấn đề được hỏi.
        
        Cấu trúc trả lời:
        1. GIẢI THÍCH vấn đề/khái niệm
        2. THÔNG TIN CHI TIẾT liên quan
        3. KHUYẾN NGHỊ thực tế (nếu có)
        4. KHI NÀO CẦN GẶP BÁC SĨ
        
        LƯU Ý:
        - Thông tin chỉ mang tính tham khảo
        - Khuyến khích tham khảo chuyên gia y tế
        - Ưu tiên sự an toàn của người hỏi
        
        Trả lời bằng tiếng Việt, khoa học và dễ hiểu.
        """
    
    return prompt
```

### Cost Tracking & Usage Monitoring
```python
def log_api_usage(self, usage_data):
    """
    Theo dõi usage và chi phí OpenAI API
    """
    # Tính toán chi phí dựa trên model
    cost_per_token = {
        'gpt-3.5-turbo': 0.0015,  # $0.0015 per 1K tokens
        'gpt-4': 0.03,            # $0.03 per 1K tokens
    }
    
    tokens_used = usage_data.total_tokens
    cost = (tokens_used / 1000) * cost_per_token.get(self.model, 0.002)
    
    # Lưu vào database
    AIUsageLog.objects.create(
        user=self.current_user,
        ai_model=self.get_ai_model_instance(),
        operation_type='chat_completion',
        tokens_used=tokens_used,
        cost=cost,
        success=True
    )
```

### Error Handling & Fallbacks
```python
def handle_openai_errors(self, user_input):
    """
    Xử lý lỗi OpenAI và fallback responses
    """
    try:
        return self.call_openai_api(user_input)
    
    except openai.error.RateLimitError:
        # Rate limit exceeded - sử dụng pre-built responses
        return self.get_fallback_response(user_input)
    
    except openai.error.InvalidRequestError:
        # Invalid request - refine prompt
        simplified_prompt = self.simplify_prompt(user_input)
        return self.call_openai_api(simplified_prompt)
    
    except openai.error.APIError:
        # API error - fallback to knowledge base
        return self.search_knowledge_base_only(user_input)
    
    except Exception as e:
        # Unknown error - safe fallback
        return {
            'response': 'Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau hoặc liên hệ với đội ngũ y tế.',
            'success': False,
            'error': str(e)
        }

def get_fallback_response(self, user_input):
    """
    Fallback khi không thể gọi OpenAI
    """
    # Tìm kiếm trong pre-built responses
    intent = self.detect_intent(user_input)
    
    fallback_responses = {
        'greeting': 'Xin chào! Tôi là trợ lý y tế AI. Tôi có thể giúp bạn tìm hiểu về các vấn đề sức khỏe.',
        'symptom_inquiry': 'Tôi hiểu bạn đang quan tâm về triệu chứng. Để được hỗ trợ tốt nhất, vui lòng mô tả chi tiết triệu chứng và tham khảo ý kiến bác sĩ.',
        'medication': 'Về thông tin thuốc, tôi khuyến khích bạn tham khảo ý kiến dược sĩ hoặc bác sĩ để được tư vấn chính xác.',
        'emergency': '🚨 Nếu đây là tình huống khẩn cấp, vui lòng gọi 115 hoặc đến cấp cứu ngay lập tức!'
    }
    
    return {
        'response': fallback_responses.get(intent, 'Xin lỗi, vui lòng thử đặt câu hỏi khác hoặc liên hệ với đội ngũ y tế.'),
        'success': False,
        'fallback': True
    }
```

## 🏥 MICROSERVICES INTEGRATION (Liên kết giữa các Services)

### Healthcare System Architecture
```
                    ┌─────────────────┐
                    │   API Gateway   │
                    └─────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   User      │   │ Appointment │   │  Chatbot    │
    │  Service    │   │   Service   │   │  Service    │
    └─────────────┘   └─────────────┘   └─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
          │                  │                  │
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   Medical   │   │   Billing   │   │Notification │
    │   Records   │   │   Service   │   │  Service    │
    └─────────────┘   └─────────────┘   └─────────────┘
```

### 1. APPOINTMENT SERVICE INTEGRATIONS

#### A. Với User Service
```python
# Chatbot gọi User Service để lấy thông tin user
class AppointmentIntegration:
    def get_user_info(self, user_id):
        """Lấy thông tin user từ User Service"""
        response = requests.get(
            f"{USER_SERVICE_URL}/api/users/{user_id}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
    def check_user_permissions(self, user_id, action):
        """Kiểm tra quyền của user"""
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/{user_id}/check-permissions/",
            json={"action": action},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()["has_permission"]
```

#### B. Với Appointment Service
```python
class AppointmentServiceClient:
    def __init__(self):
        self.appointment_service_url = settings.APPOINTMENT_SERVICE_URL
        self.api_key = settings.APPOINTMENT_SERVICE_API_KEY
    
    def search_available_slots(self, doctor_id, date_range):
        """Tìm lịch trống của bác sĩ"""
        response = requests.get(
            f"{self.appointment_service_url}/api/appointments/available-slots/",
            params={
                "doctor_id": doctor_id,
                "start_date": date_range["start"],
                "end_date": date_range["end"]
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def book_appointment(self, patient_id, doctor_id, slot_time, reason):
        """Đặt lịch hẹn"""
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_datetime": slot_time,
            "reason": reason,
            "status": "scheduled",
            "source": "chatbot"
        }
        
        response = requests.post(
            f"{self.appointment_service_url}/api/appointments/",
            json=appointment_data,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def get_patient_appointments(self, patient_id):
        """Lấy danh sách lịch hẹn của bệnh nhân"""
        response = requests.get(
            f"{self.appointment_service_url}/api/appointments/",
            params={"patient_id": patient_id},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def cancel_appointment(self, appointment_id, reason):
        """Hủy lịch hẹn"""
        response = requests.patch(
            f"{self.appointment_service_url}/api/appointments/{appointment_id}/",
            json={
                "status": "cancelled",
                "cancellation_reason": reason,
                "cancelled_at": timezone.now().isoformat()
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
```

#### C. Với Medical Records Service
```python
class MedicalRecordsClient:
    def get_patient_history(self, patient_id):
        """Lấy lịch sử bệnh án"""
        response = requests.get(
            f"{MEDICAL_RECORDS_URL}/api/records/{patient_id}/history/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
    def get_recent_visits(self, patient_id, limit=5):
        """Lấy các lần khám gần đây"""
        response = requests.get(
            f"{MEDICAL_RECORDS_URL}/api/records/{patient_id}/visits/",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

#### D. Với Notification Service
```python
class NotificationClient:
    def send_appointment_confirmation(self, appointment_id, patient_id):
        """Gửi thông báo xác nhận lịch hẹn"""
        notification_data = {
            "recipient_id": patient_id,
            "type": "appointment_confirmation",
            "title": "Xác nhận lịch hẹn",
            "message": f"Lịch hẹn #{appointment_id} đã được xác nhận",
            "data": {"appointment_id": appointment_id},
            "channels": ["email", "sms", "push"]
        }
        
        response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/api/notifications/send/",
            json=notification_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    
    def send_appointment_reminder(self, appointment_id, patient_id, reminder_time):
        """Gửi nhắc nhở lịch hẹn"""
        reminder_data = {
            "recipient_id": patient_id,
            "type": "appointment_reminder",
            "title": "Nhắc nhở lịch hẹn",
            "message": "Bạn có lịch hẹn trong 24 giờ tới",
            "scheduled_time": reminder_time,
            "data": {"appointment_id": appointment_id}
        }
        
        response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/api/notifications/schedule/",
            json=reminder_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### 2. CHATBOT APPOINTMENT WORKFLOWS

#### A. Đặt lịch hẹn qua Chatbot
```python
class ChatbotAppointmentService:
    def __init__(self):
        self.appointment_client = AppointmentServiceClient()
        self.user_client = UserServiceClient()
        self.notification_client = NotificationClient()
    
    async def handle_appointment_booking(self, user_input, user_id, conversation_id):
        """Xử lý yêu cầu đặt lịch hẹn từ chatbot"""
        
        # 1. Phân tích intent và extract thông tin
        intent_data = self.extract_appointment_intent(user_input)
        
        if intent_data["type"] == "book_appointment":
            return await self.process_booking_request(intent_data, user_id, conversation_id)
        elif intent_data["type"] == "check_appointments":
            return await self.get_user_appointments(user_id)
        elif intent_data["type"] == "cancel_appointment":
            return await self.cancel_appointment_request(intent_data, user_id)
    
    async def process_booking_request(self, intent_data, user_id, conversation_id):
        """Xử lý yêu cầu đặt lịch"""
        
        # 1. Lấy thông tin user
        user_info = self.user_client.get_user_info(user_id)
        
        # 2. Tìm bác sĩ phù hợp
        specialty = intent_data.get("specialty")
        doctors = self.appointment_client.search_doctors(specialty=specialty)
        
        if not doctors:
            return {
                "response": f"Xin lỗi, hiện tại chưa có bác sĩ {specialty} trống lịch.",
                "quick_replies": ["Chọn chuyên khoa khác", "Xem lịch tuần sau"]
            }
        
        # 3. Tìm lịch trống
        preferred_date = intent_data.get("preferred_date")
        available_slots = []
        
        for doctor in doctors:
            slots = self.appointment_client.search_available_slots(
                doctor_id=doctor["id"],
                date_range={
                    "start": preferred_date,
                    "end": preferred_date + timedelta(days=7)
                }
            )
            available_slots.extend(slots)
        
        if not available_slots:
            return {
                "response": "Không tìm thấy lịch trống trong thời gian bạn yêu cầu.",
                "suggested_actions": ["Chọn thời gian khác", "Xem lịch bác sĩ khác"],
                "available_dates": self.get_next_available_dates(doctors)
            }
        
        # 4. Hiển thị lựa chọn cho user thông qua conversation
        return await self.show_appointment_options(
            available_slots, user_id, conversation_id
        )
    
    async def confirm_appointment_booking(self, slot_data, user_id, reason):
        """Xác nhận đặt lịch"""
        
        # 1. Đặt lịch hẹn
        appointment = self.appointment_client.book_appointment(
            patient_id=user_id,
            doctor_id=slot_data["doctor_id"],
            slot_time=slot_data["datetime"],
            reason=reason
        )
        
        if appointment["success"]:
            # 2. Gửi thông báo xác nhận
            self.notification_client.send_appointment_confirmation(
                appointment["id"], user_id
            )
            
            # 3. Lên lịch nhắc nhở
            reminder_time = appointment["datetime"] - timedelta(hours=24)
            self.notification_client.send_appointment_reminder(
                appointment["id"], user_id, reminder_time
            )
            
            # 4. Cập nhật medical records
            self.update_medical_records(user_id, appointment["id"])
            
            return {
                "response": f"✅ Đã đặt lịch hẹn thành công!\n\n"
                           f"📅 Thời gian: {appointment['datetime']}\n"
                           f"👨‍⚕️ Bác sĩ: {appointment['doctor_name']}\n"
                           f"📍 Địa điểm: {appointment['location']}\n"
                           f"🆔 Mã lịch hẹn: {appointment['id']}",
                "appointment_data": appointment,
                "quick_replies": ["Xem chi tiết", "Thêm vào lịch", "Đặt lịch khác"]
            }
        else:
            return {
                "response": "❌ Không thể đặt lịch hẹn. Vui lòng thử lại.",
                "error": appointment.get("error"),
                "suggested_actions": ["Chọn thời gian khác", "Liên hệ tổng đài"]
            }
```

#### B. Kiểm tra lịch hẹn
```python
async def get_user_appointments(self, user_id):
    """Lấy danh sách lịch hẹn của user"""
    
    appointments = self.appointment_client.get_patient_appointments(user_id)
    
    if not appointments:
        return {
            "response": "Bạn chưa có lịch hẹn nào.",
            "quick_replies": ["Đặt lịch hẹn mới", "Xem lịch bác sĩ"]
        }
    
    # Format response
    upcoming_appointments = [
        apt for apt in appointments 
        if apt["datetime"] > timezone.now() and apt["status"] == "scheduled"
    ]
    
    response_text = "📅 Lịch hẹn sắp tới của bạn:\n\n"
    
    for apt in upcoming_appointments[:3]:  # Show max 3
        response_text += f"• {apt['datetime'].strftime('%d/%m/%Y %H:%M')}\n"
        response_text += f"  👨‍⚕️ {apt['doctor_name']}\n"
        response_text += f"  🏥 {apt['location']}\n"
        response_text += f"  📋 {apt['reason']}\n\n"
    
    return {
        "response": response_text,
        "appointments": upcoming_appointments,
        "quick_replies": ["Hủy lịch hẹn", "Đổi lịch hẹn", "Xem tất cả"]
    }
```

### 3. EVENT-DRIVEN COMMUNICATION

#### A. Webhook Events
```python
# Appointment Service gửi events khi có thay đổi
APPOINTMENT_EVENTS = {
    "appointment.created": "Lịch hẹn mới được tạo",
    "appointment.confirmed": "Lịch hẹn được xác nhận",
    "appointment.cancelled": "Lịch hẹn bị hủy",
    "appointment.completed": "Lịch hẹn hoàn thành",
    "appointment.no_show": "Bệnh nhân không đến"
}

@api_view(['POST'])
def handle_appointment_webhook(request):
    """Xử lý webhook từ Appointment Service"""
    
    event_type = request.data.get("event_type")
    appointment_data = request.data.get("data")
    
    if event_type == "appointment.created":
        # Gửi thông báo xác nhận
        send_confirmation_message(appointment_data)
        
    elif event_type == "appointment.cancelled":
        # Thông báo hủy lịch
        send_cancellation_message(appointment_data)
        
    elif event_type == "appointment.reminder":
        # Gửi nhắc nhở
        send_reminder_message(appointment_data)
    
    return Response({"status": "processed"})
```

#### B. Message Queue Integration
```python
# Sử dụng Redis/RabbitMQ cho async processing
import celery

@celery.task
def process_appointment_booking(appointment_data):
    """Background task xử lý đặt lịch"""
    
    # 1. Validate appointment
    if not validate_appointment_data(appointment_data):
        return {"error": "Invalid appointment data"}
    
    # 2. Call Appointment Service
    result = appointment_client.book_appointment(appointment_data)
    
    # 3. Send notifications
    if result["success"]:
        notification_client.send_confirmation(result["appointment_id"])
    
    # 4. Update chatbot conversation
    update_conversation_with_appointment(
        appointment_data["conversation_id"], 
        result
    )
    
    return result
```

### 4. API GATEWAY ROUTING

```yaml
# API Gateway configuration
routes:
# Chatbot routes
- path: /api/chatbot/*
  service: chatbot-service
  
# Appointment routes  
- path: /api/appointments/*
  service: appointment-service
  
# User routes
- path: /api/users/*
  service: user-service
  
# Cross-service routes
- path: /api/integrations/appointments/book
  service: chatbot-service
  method: POST
  downstream: appointment-service
```

Kiến trúc này cho phép **Chatbot Service** tương tác liền mạch với **Appointment Service** và các service khác, tạo ra trải nghiệm người dùng thống nhất! 🏥🤖
