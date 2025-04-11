require('dotenv').config();

// Sử dụng cùng một JWT_SECRET với Django settings.SECRET_KEY
const COMMON_JWT_SECRET = 'django-insecure-key'; 

module.exports = {
  port: process.env.PORT || 4000,
  jwtSecret: process.env.JWT_SECRET || COMMON_JWT_SECRET, // Đảm bảo đồng bộ với các service khác
  services: {
    user: process.env.USER_SERVICE_URL || 'http://localhost:8000',
    appointment: process.env.APPOINTMENT_SERVICE_URL || 'http://localhost:8002',
    medicalRecord: process.env.MEDICAL_RECORD_SERVICE_URL || 'http://localhost:8001',
    billing: process.env.BILLING_SERVICE_URL || 'http://localhost:8003',
    pharmacy: process.env.PHARMACY_SERVICE_URL || 'http://localhost:8004',
    lab: process.env.LAB_SERVICE_URL || 'http://localhost:8005',
    notification: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:8006'
  }
};
