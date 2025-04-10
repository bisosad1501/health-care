const express = require('express');
const { verifyToken } = require('../middleware/auth');
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
  // If verifyToken middleware passes, the token is valid
  // Return user information from the token
  res.status(200).json({
    id: req.user.id,
    email: req.user.email,
    role: req.user.role,
    first_name: req.user.first_name,
    last_name: req.user.last_name
  });
});

// Protected routes (authentication required)
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
router.use('/api/patient-profile', userServiceProxy);
router.use('/api/doctor-profile', userServiceProxy);
router.use('/api/nurse-profile', userServiceProxy);
router.use('/api/addresses', userServiceProxy);
router.use('/api/contact-info', userServiceProxy);
router.use('/api/documents', userServiceProxy);
router.use('/api/admin', userServiceProxy);
router.use('/api/insurance-information', userServiceProxy);
router.use('/api/insurance-providers', verifyToken, userServiceProxy);

// Appointment Service routes
router.use('/api/appointments', verifyToken, appointmentServiceProxy);
router.use('/api/doctor-availabilities', verifyToken, appointmentServiceProxy);
router.use('/api/time-slots', verifyToken, appointmentServiceProxy);
router.use('/api/appointment-reminders', verifyToken, appointmentServiceProxy);

// Medical Record Service routes
router.use('/api/medical-records', verifyToken, medicalRecordServiceProxy);
router.use('/api/diagnoses', verifyToken, medicalRecordServiceProxy);
router.use('/api/treatments', verifyToken, medicalRecordServiceProxy);
router.use('/api/allergies', verifyToken, medicalRecordServiceProxy);
router.use('/api/immunizations', verifyToken, medicalRecordServiceProxy);
router.use('/api/medical-histories', verifyToken, medicalRecordServiceProxy);
router.use('/api/medications', verifyToken, medicalRecordServiceProxy);
router.use('/api/vital-signs', verifyToken, medicalRecordServiceProxy);
router.use('/api/lab-tests', verifyToken, medicalRecordServiceProxy);
router.use('/api/lab-results', verifyToken, medicalRecordServiceProxy);

// Pharmacy Service routes
router.use('/api/pharmacy', verifyToken, (req, res, next) => {
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
router.use('/api/billing', verifyToken, (req, res, next) => {
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

// Insurance claims routes (part of Billing Service)
router.use('/api/insurance-claims', verifyToken, (req, res, next) => {
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
router.use('/api/laboratory', verifyToken, (req, res, next) => {
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

// Notification Service routes
router.use('/api/notifications', verifyToken, (req, res, next) => {
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
router.post('/api/notifications/events', verifyToken, (req, res, next) => {
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

// Health check endpoint
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'API Gateway is running'
  });
});

module.exports = router;
