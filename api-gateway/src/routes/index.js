const express = require('express');
const { verifyToken } = require('../middleware/auth'); // Bạn có thể xóa dòng import này nếu không dùng nữa
const config = require('../config');
const {
  userServiceProxy,
  authServiceProxy,
  appointmentServiceProxy,
  medicalRecordServiceProxy,
  billingServiceProxy,
  pharmacyServiceProxy,
  labServiceProxy,
  notificationServiceProxy
} = require('../services/proxy');

const router = express.Router();

// Public routes (no authentication required)
// Direct pass-through to auth service for login and register
router.use('/api/auth/login', authServiceProxy);
router.use('/api/auth/register', authServiceProxy);

// Use local auth routes for token refresh, logout, and sessions
router.use('/api/auth/token/refresh', require('./auth'));
router.use('/api/auth/logout', require('./auth'));
router.use('/api/auth/sessions', require('./auth'));

// Token validation endpoint for microservices
router.get('/api/auth/validate-token', (req, res) => {
  // Nếu không có verifyToken, req.user có thể undefined
  // Bạn có thể điều chỉnh logic ở đây nếu cần thiết
  res.status(200).json({
    id: req.user ? req.user.id : null,
    email: req.user ? req.user.email : null,
    role: req.user ? req.user.role : null,
    first_name: req.user ? req.user.first_name : null,
    last_name: req.user ? req.user.last_name : null
  });
});

// Protected routes (authentication not enforced at gateway level)
// Special route for /api/users/me/
router.get('/api/users/me/', (req, res) => {
  console.log('User info request received:', req.method, req.url);
  console.log('Request headers:', req.headers);
  console.log('User from token:', req.user);

  // Forward request directly to User Service
  const userServiceUrl = config.services.user;
  const targetUrl = `${userServiceUrl}/api/users/me/`;
  console.log('Forwarding to:', targetUrl);

  // Use axios to forward the request
  const axios = require('axios');
  axios.get(targetUrl, {
    headers: {
      'Authorization': req.headers.authorization
    }
  })
  .then(response => {
    res.status(response.status).json(response.data);
  })
  .catch(error => {
    console.error('Error forwarding request:', error.message);
    res.status(error.response?.status || 500).json({
      message: error.message,
      details: error.response?.data
    });
  });
});

// Other user routes
router.use('/api/users', userServiceProxy);
router.use('/api/doctors/available', appointmentServiceProxy); // Chuyển hướng đến appointment-service
router.use('/api/doctors', userServiceProxy);
router.use('/api/specialties', userServiceProxy);
router.use('/api/departments', appointmentServiceProxy); // Chuyển hướng đến appointment-service
router.use('/api/patient-profile', userServiceProxy);
router.use('/api/doctor-profile', userServiceProxy);
router.use('/api/nurse-profile', userServiceProxy);
router.use('/api/addresses', userServiceProxy);
router.use('/api/contact-info', userServiceProxy);
router.use('/api/documents', userServiceProxy);
router.use('/api/admin', userServiceProxy);
router.use('/api/insurance-information', userServiceProxy);
router.use('/api/insurance-providers', userServiceProxy);

// Direct test endpoint for debugging
router.get('/api/appointments/test', (req, res, next) => {
  console.log('[DEBUG] Forwarding to test endpoint');
  console.log('User from token:', req.user);

  // Forward directly to Appointment Service
  const axios = require('axios');
  const appointmentServiceUrl = config.services.appointment;

  // Add headers from token
  const headers = {
    'Authorization': req.headers.authorization,
    'X-User-ID': req.user ? (req.user.user_id || req.user.id) : '',
    'X-User-Role': req.user ? req.user.role : '',
    'X-User-Email': req.user ? req.user.email : ''
  };

  // Call the service directly
  axios.get(`${appointmentServiceUrl}/api/test/`, { headers })
    .then(response => {
      res.status(200).json(response.data);
    })
    .catch(error => {
      console.error('Error calling test endpoint:', error.message);
      res.status(error.response?.status || 500).json({
        error: error.message,
        details: error.response?.data
      });
    });
});

// Direct access to patient-appointments endpoint
router.get('/api/direct/patient-appointments', (req, res) => {
  console.log('[DEBUG] Direct access to patient-appointments');
  console.log('User from token:', req.user);

  // Forward directly to Appointment Service
  const axios = require('axios');
  const appointmentServiceUrl = config.services.appointment;

  // Add headers from token
  const headers = {
    'Authorization': req.headers.authorization,
    'X-User-ID': req.user ? (req.user.user_id || req.user.id) : '',
    'X-User-Role': req.user ? req.user.role : '',
    'X-User-Email': req.user ? req.user.email : '',
    'X-User-First-Name': req.user ? req.user.first_name || '' : '',
    'X-User-Last-Name': req.user ? req.user.last_name || '' : ''
  };

  console.log('Sending request to:', `${appointmentServiceUrl}/api/appointments/patient-appointments/`);
  console.log('With headers:', headers);

  // Call the service directly
  axios.get(`${appointmentServiceUrl}/api/appointments/patient-appointments/`, { headers })
    .then(response => {
      console.log('Response received:', response.status);
      res.status(200).json(response.data);
    })
    .catch(error => {
      console.error('Error calling patient-appointments endpoint:', error.message);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
      }
      res.status(error.response?.status || 500).json({
        error: error.message,
        details: error.response?.data
      });
    });
});

// Appointment Service routes
router.use('/api/appointments', appointmentServiceProxy);
router.use('/api/doctor-availabilities', appointmentServiceProxy);
router.use('/api/time-slots', appointmentServiceProxy);
router.use('/api/appointment-reminders', appointmentServiceProxy);

// Medical Record Service routes
router.use('/api/medical-records', medicalRecordServiceProxy);
router.use('/api/encounters', medicalRecordServiceProxy);
router.use('/api/diagnoses', medicalRecordServiceProxy);
router.use('/api/treatments', medicalRecordServiceProxy);
router.use('/api/allergies', medicalRecordServiceProxy);
router.use('/api/immunizations', medicalRecordServiceProxy);
router.use('/api/medical-histories', medicalRecordServiceProxy);
router.use('/api/medications', medicalRecordServiceProxy);
router.use('/api/vital-signs', medicalRecordServiceProxy);
router.use('/api/lab-tests', medicalRecordServiceProxy);
router.use('/api/lab-results', medicalRecordServiceProxy);
// Special route for creating encounters from appointments
router.post('/api/appointments/:appointment_id/create-encounter', (req, res, next) => {
  console.log('[MEDICAL_RECORD] Creating encounter from appointment');
  medicalRecordServiceProxy(req, res, next);
});

// Pharmacy Service routes
router.use('/api/prescriptions', pharmacyServiceProxy);
router.use('/api/medications', pharmacyServiceProxy);
router.use('/api/pharmacy', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    console.log(`[PHARMACY] Setting role ${req.user.role} for user_id ${req.user.user_id}`);
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  console.log(`[PHARMACY] User info: ${JSON.stringify(req.user)}`);

  // Forward the request to the pharmacy service
  // Không cần thay đổi URL vì Pharmacy Service đã hỗ trợ cả hai đường dẫn
  pharmacyServiceProxy(req, res, next);
});

// Billing Service routes
router.use('/api/invoices', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    console.log(`[BILLING] Setting role ${req.user.role} for user_id ${req.user.user_id}`);
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Email'] = req.user.email;
    req.headers['X-User-First-Name'] = req.user.first_name || '';
    req.headers['X-User-Last-Name'] = req.user.last_name || '';
    console.log(`[BILLING] User info: ${JSON.stringify(req.user)}`);
  }

  // Forward the request to the billing service
  billingServiceProxy(req, res, next);
});

// Special routes for creating invoices from other services
router.use('/api/create-from-lab-test', (req, res, next) => {
  console.log('[BILLING] Creating invoice from lab test');
  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Role'] = req.user.role;
    req.headers['X-User-Email'] = req.user.email;
  }
  // Rewrite path to match billing service endpoint
  req.url = req.url.replace('/api/create-from-lab-test', '/api/create-from-lab-test');
  billingServiceProxy(req, res, next);
});

router.use('/api/create-from-prescription', (req, res, next) => {
  console.log('[BILLING] Creating invoice from prescription');
  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Role'] = req.user.role;
    req.headers['X-User-Email'] = req.user.email;
  }
  // Rewrite path to match billing service endpoint
  req.url = req.url.replace('/api/create-from-prescription', '/api/create-from-prescription');
  billingServiceProxy(req, res, next);
});

router.use('/api/create-from-medical-record', (req, res, next) => {
  console.log('[BILLING] Creating invoice from medical record');
  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Role'] = req.user.role;
    req.headers['X-User-Email'] = req.user.email;
  }
  // Rewrite path to match billing service endpoint
  req.url = req.url.replace('/api/create-from-medical-record', '/api/create-from-medical-record');
  billingServiceProxy(req, res, next);
});

router.use('/api/create-from-appointment', (req, res, next) => {
  console.log('[BILLING] Creating invoice from appointment');
  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Role'] = req.user.role;
    req.headers['X-User-Email'] = req.user.email;
  }
  // Rewrite path to match billing service endpoint
  req.url = req.url.replace('/api/create-from-appointment', '/api/create-from-appointment');
  billingServiceProxy(req, res, next);
});

// Invoice Items routes (part of Billing Service)
router.use('/api/invoice-items', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Email'] = req.user.email;
    req.headers['X-User-First-Name'] = req.user.first_name || '';
    req.headers['X-User-Last-Name'] = req.user.last_name || '';
  }

  // Forward the request to the billing service
  billingServiceProxy(req, res, next);
});

// Payments routes (part of Billing Service)
router.use('/api/payments', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Email'] = req.user.email;
    req.headers['X-User-First-Name'] = req.user.first_name || '';
    req.headers['X-User-Last-Name'] = req.user.last_name || '';
  }

  // Forward the request to the billing service
  billingServiceProxy(req, res, next);
});

// Insurance claims routes (part of Billing Service)
router.use('/api/insurance-claims', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    console.log(`[BILLING] Setting role ${req.user.role} for user_id ${req.user.user_id}`);
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Email'] = req.user.email;
    req.headers['X-User-First-Name'] = req.user.first_name || '';
    req.headers['X-User-Last-Name'] = req.user.last_name || '';
    console.log(`[BILLING] Insurance claim request from: ${JSON.stringify(req.user)}`);
  }

  // Rewrite path to match billing service endpoint
  req.url = req.url.replace('/api/insurance-claims', '/api/insurance-claims');
  console.log(`[BILLING] Insurance claim request URL: ${req.url}`);

  // Forward the request to the billing service
  billingServiceProxy(req, res, next);
});
// Laboratory Service routes
router.use('/api/laboratory', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    console.log(`[LABORATORY] Setting role ${req.user.role} for user_id ${req.user.user_id}`);
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  console.log(`[LABORATORY] User info: ${JSON.stringify(req.user)}`);

  // Forward the request to the laboratory service
  labServiceProxy(req, res, next);
});

// Laboratory Test Types routes
router.use('/api/test-types', labServiceProxy);

// Laboratory Test Results routes
router.use('/api/test-results', labServiceProxy);

// Laboratory Sample Collections routes
router.use('/api/sample-collections', labServiceProxy);

// Notification Service routes
router.use('/api/notifications', (req, res, next) => {
  // Add user role to headers
  if (req.user && req.user.role) {
    console.log(`[NOTIFICATION] Setting role ${req.user.role} for user_id ${req.user.user_id}`);
    req.headers['X-User-Role'] = req.user.role;
  }

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Email'] = req.user.email;
    req.headers['X-User-First-Name'] = req.user.first_name || '';
    req.headers['X-User-Last-Name'] = req.user.last_name || '';
    console.log(`[NOTIFICATION] User info: ${JSON.stringify(req.user)}`);
  }

  // Forward the request to the notification service
  notificationServiceProxy(req, res, next);
});

// Special route for service-to-service event notifications
router.post('/api/notifications/events', (req, res, next) => {
  console.log('[NOTIFICATION] Received event notification');

  // Add service info to headers
  req.headers['X-Service-Name'] = req.body.service || 'UNKNOWN';

  // Add user info to headers
  if (req.user) {
    req.headers['X-User-ID'] = req.user.user_id;
    req.headers['X-User-Role'] = req.user.role;
    req.headers['X-User-Email'] = req.user.email;
  }

  // Forward the request to the notification service events endpoint
  // Manually set the URL to match the endpoint in the notification service
  req.url = '/api/events';
  console.log(`[NOTIFICATIONS] Target URL: http://notification-service:8006${req.url}`);
  console.log(`[NOTIFICATIONS] Headers: ${JSON.stringify(req.headers)}`);
  notificationServiceProxy(req, res, next);
});

// Health check endpoints
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'API Gateway is running'
  });
});

// Đường dẫn health check đơn giản hóa
router.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'api-gateway'
  });
});

// Health check cho các service - đường dẫn đơn giản hóa
router.use('/api/laboratory/health', (req, res, next) => {
  req.url = '/health/';
  labServiceProxy(req, res, next);
});

router.use('/api/pharmacy/health', (req, res, next) => {
  req.url = '/health/';
  pharmacyServiceProxy(req, res, next);
});

// Trả về trực tiếp từ API Gateway cho Medical Record Service
router.get('/api/medical-records/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'medical-record-service'
  });
});

router.get('/api/medical-records/health/', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'medical-record-service'
  });
});

// Chuyển đổi đường dẫn cũ cho Medical Record Service
router.get('/api/medical-records/api/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'medical-record-service'
  });
});

router.get('/api/medical-records/api/health/', (req, res) => {
  res.status(200).json({
    status: 'UP',
    service: 'medical-record-service'
  });
});

router.use('/api/billing/health', (req, res, next) => {
  req.url = '/health/';
  billingServiceProxy(req, res, next);
});

router.use('/api/users/health', (req, res, next) => {
  req.url = '/health/';
  userServiceProxy(req, res, next);
});

router.use('/api/appointments/health', (req, res, next) => {
  req.url = '/health/';
  appointmentServiceProxy(req, res, next);
});

router.use('/api/notifications/health', (req, res, next) => {
  req.url = '/health/';
  notificationServiceProxy(req, res, next);
});

// Giữ lại đường dẫn cũ để đảm bảo tương thích ngược
router.use('/api/laboratory/api/health', labServiceProxy);
router.use('/api/pharmacy/api/health', pharmacyServiceProxy);
router.use('/api/medical-records/api/health', medicalRecordServiceProxy);
router.use('/api/billing/api/health', billingServiceProxy);
router.use('/api/users/api/health', userServiceProxy);
router.use('/api/appointments/api/health', appointmentServiceProxy);
router.use('/api/notifications/api/health', notificationServiceProxy);

module.exports = router;