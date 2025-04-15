import requests
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# Lấy URL các service từ biến môi trường hoặc settings
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:8000')
MEDICAL_RECORD_SERVICE_URL = os.environ.get('MEDICAL_RECORD_SERVICE_URL', 'http://medical-record-service:8001')
PHARMACY_SERVICE_URL = os.environ.get('PHARMACY_SERVICE_URL', 'http://pharmacy-service:8004')
LAB_SERVICE_URL = os.environ.get('LAB_SERVICE_URL', 'http://laboratory-service:8005')
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://notification-service:8006')


def get_auth_headers(token=None):
    """Tạo headers xác thực cho các request đến service khác"""
    headers = {
        'Content-Type': 'application/json',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


# Tích hợp với User Service
def get_user_info(user_id, token=None):
    """Lấy thông tin người dùng từ User Service"""
    try:
        url = f"{USER_SERVICE_URL}/api/users/{user_id}/"
        response = requests.get(url, headers=get_auth_headers(token))
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error fetching user info: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching user info: {str(e)}")
        return None


def get_doctor_info(doctor_id, token=None):
    """Lấy thông tin bác sĩ từ User Service"""
    try:
        url = f"{USER_SERVICE_URL}/api/doctors/{doctor_id}/"
        response = requests.get(url, headers=get_auth_headers(token))
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error fetching doctor info: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching doctor info: {str(e)}")
        return None


# Tích hợp với Medical Record Service
def get_patient_medical_record(patient_id, token=None):
    """Lấy thông tin hồ sơ y tế của bệnh nhân"""
    try:
        url = f"{MEDICAL_RECORD_SERVICE_URL}/api/medical-records/?patient_id={patient_id}"
        response = requests.get(url, headers=get_auth_headers(token))
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error fetching medical record: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching medical record: {str(e)}")
        return None


def update_medical_record(medical_record_id, data, token=None):
    """Cập nhật hồ sơ y tế"""
    try:
        url = f"{MEDICAL_RECORD_SERVICE_URL}/api/medical-records/{medical_record_id}/"
        response = requests.patch(url, json=data, headers=get_auth_headers(token))
        if response.status_code in [200, 201]:
            return response.json()
        logger.error(f"Error updating medical record: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception updating medical record: {str(e)}")
        return None


# Tích hợp với Laboratory Service
def create_lab_request(appointment_id, doctor_id, patient_id, tests, token=None):
    """Tạo yêu cầu xét nghiệm"""
    try:
        url = f"{LAB_SERVICE_URL}/api/lab-requests/"
        data = {
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "tests": tests
        }
        response = requests.post(url, json=data, headers=get_auth_headers(token))
        if response.status_code in [200, 201]:
            return response.json()
        logger.error(f"Error creating lab request: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception creating lab request: {str(e)}")
        return None


def get_lab_results(appointment_id, token=None):
    """Lấy kết quả xét nghiệm cho lịch hẹn"""
    try:
        url = f"{LAB_SERVICE_URL}/api/lab-results/?appointment_id={appointment_id}"
        response = requests.get(url, headers=get_auth_headers(token))
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error fetching lab results: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching lab results: {str(e)}")
        return None


# Tích hợp với Pharmacy Service
def create_prescription(appointment_id, doctor_id, patient_id, medications, token=None):
    """Tạo đơn thuốc"""
    try:
        url = f"{PHARMACY_SERVICE_URL}/api/prescriptions/"
        data = {
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "medications": medications
        }
        response = requests.post(url, json=data, headers=get_auth_headers(token))
        if response.status_code in [200, 201]:
            return response.json()
        logger.error(f"Error creating prescription: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception creating prescription: {str(e)}")
        return None


def get_prescription(prescription_id, token=None):
    """Lấy thông tin đơn thuốc"""
    try:
        url = f"{PHARMACY_SERVICE_URL}/api/prescriptions/{prescription_id}/"
        response = requests.get(url, headers=get_auth_headers(token))
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error fetching prescription: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching prescription: {str(e)}")
        return None


# Tích hợp với Notification Service
def send_notification(user_id, notification_type, message, token=None):
    """Gửi thông báo cho người dùng"""
    try:
        url = f"{NOTIFICATION_SERVICE_URL}/api/notifications/"
        data = {
            "user_id": user_id,
            "type": notification_type,
            "message": message
        }
        response = requests.post(url, json=data, headers=get_auth_headers(token))
        if response.status_code in [200, 201]:
            return response.json()
        logger.error(f"Error sending notification: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logger.error(f"Exception sending notification: {str(e)}")
        return None
