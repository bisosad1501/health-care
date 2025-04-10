import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class UserService:
    """
    Service để giao tiếp với User Service thông qua API Gateway.
    """
    
    @staticmethod
    def get_user_info(user_id):
        """
        Lấy thông tin người dùng từ User Service thông qua API Gateway.
        
        Args:
            user_id (int): ID của người dùng
            
        Returns:
            dict: Thông tin người dùng hoặc None nếu có lỗi
        """
        try:
            response = requests.get(f"{settings.API_GATEWAY_URL}/api/users/{user_id}/")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch user info: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return None
    
    @staticmethod
    def get_doctor_info(doctor_id):
        """
        Lấy thông tin bác sĩ từ User Service thông qua API Gateway.
        
        Args:
            doctor_id (int): ID của bác sĩ
            
        Returns:
            dict: Thông tin bác sĩ hoặc None nếu có lỗi
        """
        try:
            response = requests.get(f"{settings.API_GATEWAY_URL}/api/users/doctors/{doctor_id}/")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch doctor info: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching doctor info: {str(e)}")
            return None
    
    @staticmethod
    def get_patient_info(patient_id):
        """
        Lấy thông tin bệnh nhân từ User Service thông qua API Gateway.
        
        Args:
            patient_id (int): ID của bệnh nhân
            
        Returns:
            dict: Thông tin bệnh nhân hoặc None nếu có lỗi
        """
        try:
            response = requests.get(f"{settings.API_GATEWAY_URL}/api/users/patients/{patient_id}/")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch patient info: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching patient info: {str(e)}")
            return None
    
    @staticmethod
    def validate_user_token(token):
        """
        Xác thực token người dùng thông qua API Gateway.
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Thông tin người dùng đã xác thực hoặc None nếu token không hợp lệ
        """
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{settings.API_GATEWAY_URL}/api/auth/validate-token/", headers=headers)
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to validate token: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
