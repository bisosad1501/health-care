# Healthcare Microservices Integration
# Cấu hình tích hợp giữa các services trong hệ thống

from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
import asyncio
from datetime import datetime, timedelta

@dataclass
class ServiceConfig:
    """Cấu hình cho từng service"""
    name: str
    url: str
    api_key: str
    timeout: int = 30
    retry_attempts: int = 3

class HealthcareServiceRegistry:
    """Registry quản lý tất cả services trong hệ thống"""
    
    def __init__(self):
        self.services = {
            'user': ServiceConfig(
                name='user-service',
                url='http://user-service:8000',
                api_key='user-service-key'
            ),
            'appointment': ServiceConfig(
                name='appointment-service', 
                url='http://appointment-service:8000',
                api_key='appointment-service-key'
            ),
            'medical_records': ServiceConfig(
                name='medical-record-service',
                url='http://medical-record-service:8000', 
                api_key='medical-records-key'
            ),
            'billing': ServiceConfig(
                name='billing-service',
                url='http://billing-service:8000',
                api_key='billing-service-key'
            ),
            'notification': ServiceConfig(
                name='notification-service',
                url='http://notification-service:8000',
                api_key='notification-service-key'
            ),
            'pharmacy': ServiceConfig(
                name='pharmacy-service',
                url='http://pharmacy-service:8000',
                api_key='pharmacy-service-key'
            ),
            'laboratory': ServiceConfig(
                name='laboratory-service',
                url='http://laboratory-service:8000',
                api_key='laboratory-service-key'
            )
        }

class CrossServiceCommunication:
    """Lớp quản lý giao tiếp giữa các services"""
    
    def __init__(self, service_registry: HealthcareServiceRegistry):
        self.registry = service_registry
        
    async def call_service(self, service_name: str, endpoint: str, 
                          method: str = 'GET', data: dict = None) -> dict:
        """Gọi API của service khác"""
        
        service = self.registry.services.get(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found")
        
        url = f"{service.url}/api/{endpoint}"
        headers = {
            'Authorization': f'Bearer {service.api_key}',
            'Content-Type': 'application/json',
            'X-Service-Source': 'chatbot-service'
        }
        
        for attempt in range(service.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, timeout=service.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, json=data, headers=headers, timeout=service.timeout)
                elif method.upper() == 'PUT':
                    response = requests.put(url, json=data, headers=headers, timeout=service.timeout)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=headers, timeout=service.timeout)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == service.retry_attempts - 1:
                    raise Exception(f"Failed to call {service_name} after {service.retry_attempts} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

class AppointmentServiceIntegration:
    """Tích hợp với Appointment Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
    
    async def search_doctors(self, specialty: str = None, location: str = None) -> List[dict]:
        """Tìm kiếm bác sĩ"""
        params = {}
        if specialty:
            params['specialty'] = specialty
        if location:
            params['location'] = location
            
        endpoint = f"doctors/?{self._build_query_string(params)}"
        return await self.comm.call_service('appointment', endpoint)
    
    async def get_available_slots(self, doctor_id: int, date: datetime) -> List[dict]:
        """Lấy lịch trống của bác sĩ"""
        endpoint = f"doctors/{doctor_id}/available-slots/?date={date.strftime('%Y-%m-%d')}"
        return await self.comm.call_service('appointment', endpoint)
    
    async def book_appointment(self, appointment_data: dict) -> dict:
        """Đặt lịch hẹn"""
        return await self.comm.call_service('appointment', 'appointments/', 'POST', appointment_data)
    
    async def get_patient_appointments(self, patient_id: int) -> List[dict]:
        """Lấy lịch hẹn của bệnh nhân"""
        endpoint = f"appointments/?patient_id={patient_id}"
        return await self.comm.call_service('appointment', endpoint)
    
    async def cancel_appointment(self, appointment_id: int, reason: str) -> dict:
        """Hủy lịch hẹn"""
        data = {'status': 'cancelled', 'cancellation_reason': reason}
        return await self.comm.call_service('appointment', f'appointments/{appointment_id}/', 'PUT', data)
    
    def _build_query_string(self, params: dict) -> str:
        return '&'.join([f"{k}={v}" for k, v in params.items()])

class UserServiceIntegration:
    """Tích hợp với User Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def get_user_profile(self, user_id: int) -> dict:
        """Lấy thông tin profile user"""
        return await self.comm.call_service('user', f'users/{user_id}/')
    
    async def get_user_medical_info(self, user_id: int) -> dict:
        """Lấy thông tin y tế cơ bản của user"""
        return await self.comm.call_service('user', f'users/{user_id}/medical-info/')
    
    async def update_user_preferences(self, user_id: int, preferences: dict) -> dict:
        """Cập nhật preferences của user"""
        return await self.comm.call_service('user', f'users/{user_id}/preferences/', 'PUT', preferences)

class MedicalRecordsIntegration:
    """Tích hợp với Medical Records Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def get_patient_history(self, patient_id: int) -> List[dict]:
        """Lấy lịch sử khám bệnh"""
        return await self.comm.call_service('medical_records', f'records/{patient_id}/history/')
    
    async def get_recent_diagnoses(self, patient_id: int, limit: int = 5) -> List[dict]:
        """Lấy chẩn đoán gần đây"""
        endpoint = f'records/{patient_id}/diagnoses/?limit={limit}'
        return await self.comm.call_service('medical_records', endpoint)
    
    async def get_medications(self, patient_id: int) -> List[dict]:
        """Lấy danh sách thuốc đang dùng"""
        return await self.comm.call_service('medical_records', f'records/{patient_id}/medications/')
    
    async def create_consultation_record(self, patient_id: int, consultation_data: dict) -> dict:
        """Tạo bản ghi tư vấn từ chatbot"""
        data = {
            'patient_id': patient_id,
            'consultation_type': 'chatbot',
            'consultation_data': consultation_data,
            'created_by': 'chatbot-service'
        }
        return await self.comm.call_service('medical_records', 'consultations/', 'POST', data)

class NotificationIntegration:
    """Tích hợp với Notification Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def send_appointment_confirmation(self, user_id: int, appointment_data: dict) -> dict:
        """Gửi xác nhận lịch hẹn"""
        notification_data = {
            'recipient_id': user_id,
            'type': 'appointment_confirmation',
            'title': 'Xác nhận lịch hẹn',
            'message': f"Lịch hẹn vào {appointment_data['datetime']} đã được xác nhận",
            'data': appointment_data,
            'channels': ['email', 'sms', 'push_notification']
        }
        return await self.comm.call_service('notification', 'notifications/', 'POST', notification_data)
    
    async def schedule_appointment_reminder(self, user_id: int, appointment_data: dict) -> dict:
        """Lên lịch nhắc nhở"""
        reminder_time = datetime.fromisoformat(appointment_data['datetime']) - timedelta(hours=24)
        
        reminder_data = {
            'recipient_id': user_id,
            'type': 'appointment_reminder', 
            'title': 'Nhắc nhở lịch hẹn',
            'message': 'Bạn có lịch hẹn vào ngày mai',
            'scheduled_time': reminder_time.isoformat(),
            'data': appointment_data,
            'channels': ['push_notification', 'sms']
        }
        return await self.comm.call_service('notification', 'notifications/schedule/', 'POST', reminder_data)
    
    async def send_health_alert(self, user_id: int, alert_data: dict) -> dict:
        """Gửi cảnh báo sức khỏe"""
        alert_notification = {
            'recipient_id': user_id,
            'type': 'health_alert',
            'priority': 'high',
            'title': 'Cảnh báo sức khỏe',
            'message': alert_data['message'],
            'data': alert_data,
            'channels': ['push_notification', 'email']
        }
        return await self.comm.call_service('notification', 'notifications/', 'POST', alert_notification)

class BillingIntegration:
    """Tích hợp với Billing Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def create_consultation_charge(self, patient_id: int, consultation_data: dict) -> dict:
        """Tạo phí tư vấn chatbot"""
        billing_data = {
            'patient_id': patient_id,
            'service_type': 'chatbot_consultation',
            'amount': consultation_data.get('consultation_fee', 0),
            'description': 'Tư vấn sức khỏe qua chatbot',
            'consultation_data': consultation_data
        }
        return await self.comm.call_service('billing', 'charges/', 'POST', billing_data)
    
    async def get_patient_bills(self, patient_id: int) -> List[dict]:
        """Lấy hóa đơn của bệnh nhân"""
        return await self.comm.call_service('billing', f'bills/?patient_id={patient_id}')

class PharmacyIntegration:
    """Tích hợp với Pharmacy Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def search_medications(self, medication_name: str) -> List[dict]:
        """Tìm kiếm thuốc"""
        endpoint = f'medications/search/?q={medication_name}'
        return await self.comm.call_service('pharmacy', endpoint)
    
    async def get_medication_info(self, medication_id: int) -> dict:
        """Lấy thông tin chi tiết thuốc"""
        return await self.comm.call_service('pharmacy', f'medications/{medication_id}/')
    
    async def check_drug_interactions(self, medication_ids: List[int]) -> dict:
        """Kiểm tra tương tác thuốc"""
        data = {'medication_ids': medication_ids}
        return await self.comm.call_service('pharmacy', 'medications/check-interactions/', 'POST', data)

class LaboratoryIntegration:
    """Tích hợp với Laboratory Service"""
    
    def __init__(self, comm: CrossServiceCommunication):
        self.comm = comm
        
    async def get_patient_lab_results(self, patient_id: int, limit: int = 10) -> List[dict]:
        """Lấy kết quả xét nghiệm"""
        endpoint = f'results/?patient_id={patient_id}&limit={limit}'
        return await self.comm.call_service('laboratory', endpoint)
    
    async def interpret_lab_results(self, lab_result_id: int) -> dict:
        """Giải thích kết quả xét nghiệm"""
        return await self.comm.call_service('laboratory', f'results/{lab_result_id}/interpret/')

# Khởi tạo tất cả integrations
service_registry = HealthcareServiceRegistry()
comm = CrossServiceCommunication(service_registry)

# Các integration clients
appointment_service = AppointmentServiceIntegration(comm)
user_service = UserServiceIntegration(comm)
medical_records_service = MedicalRecordsIntegration(comm)
notification_service = NotificationIntegration(comm)
billing_service = BillingIntegration(comm)
pharmacy_service = PharmacyIntegration(comm)
laboratory_service = LaboratoryIntegration(comm)
