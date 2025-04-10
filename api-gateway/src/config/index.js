require('dotenv').config();

module.exports = {
  port: process.env.PORT || 4000,
  jwtSecret: process.env.JWT_SECRET || 'your_secret_key', // IMPORTANT: Always use environment variable in production
  services: {
    user: process.env.USER_SERVICE_URL || 'http://user-service:8000',
    appointment: process.env.APPOINTMENT_SERVICE_URL || 'http://appointment-service:8002',
    medicalRecord: process.env.MEDICAL_RECORD_SERVICE_URL || 'http://medical-record-service:8001',
    billing: process.env.BILLING_SERVICE_URL || 'http://billing-service:8003',
    pharmacy: process.env.PHARMACY_SERVICE_URL || 'http://pharmacy-service:8004',
    lab: process.env.LAB_SERVICE_URL || 'http://laboratory-service:8005',
    notification: process.env.NOTIFICATION_SERVICE_URL || 'http://notification-service:8006'
  }
};
