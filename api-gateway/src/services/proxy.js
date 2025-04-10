const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../config');

/**
 * Create proxy middleware for a service
 * @param {string} serviceName - Name of the service
 * @param {string} serviceUrl - URL of the service
 * @param {Object} options - Additional options for the proxy
 * @returns {Function} Proxy middleware
 */
const createServiceProxy = (serviceName, serviceUrl, options = {}) => {
  return createProxyMiddleware({
    target: serviceUrl,
    changeOrigin: true,
    pathRewrite: options.pathRewrite || null,
    // Increase timeout
    timeout: 30000,
    proxyTimeout: 30000,
    // Handle request body
    onProxyReq: (proxyReq, req, res) => {
      // Log the request
      console.log(`[${serviceName.toUpperCase()}] ${req.method} ${req.originalUrl}`);
      // Log the target URL
      console.log(`[${serviceName.toUpperCase()}] Target URL: ${serviceUrl}${req.url}`);
      // Log headers
      console.log(`[${serviceName.toUpperCase()}] Headers: ${JSON.stringify(req.headers)}`);

      // Chuyển tiếp thông tin người dùng từ token
      if (req.user) {
        // Lấy thông tin người dùng từ User Service
        const axios = require('axios');
        const config = require('../config');

        // Thêm user_id vào header
        if (req.user.user_id) {
          proxyReq.setHeader('X-User-ID', req.user.user_id.toString());
        } else if (req.user.id) {
          proxyReq.setHeader('X-User-ID', req.user.id.toString());
        }

        // Thêm email vào header nếu có
        if (req.user.email) {
          proxyReq.setHeader('X-User-Email', req.user.email);
        }

        // Thêm first_name và last_name vào header nếu có
        if (req.user.first_name) {
          proxyReq.setHeader('X-User-First-Name', req.user.first_name);
        }

        if (req.user.last_name) {
          proxyReq.setHeader('X-User-Last-Name', req.user.last_name);
        }

        // Thêm token gốc vào header
        if (req.headers.authorization) {
          proxyReq.setHeader('X-Original-Authorization', req.headers.authorization);

          // Thêm thông tin role dựa vào user_id
          // Lấy role từ thông tin user đã được xác thực
          if (req.user.role) {
            proxyReq.setHeader('X-User-Role', req.user.role);
            console.log(`[${serviceName.toUpperCase()}] Setting role ${req.user.role} for user_id ${req.user.id || req.user.user_id}`);
          }
        }

        // Log thông tin người dùng
        console.log(`[${serviceName.toUpperCase()}] User info:`, req.user);
      }

      // Handle request body
      if (req.body && Object.keys(req.body).length > 0) {
        const bodyData = JSON.stringify(req.body);
        proxyReq.setHeader('Content-Type', 'application/json');
        proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
        // Write body data to the proxy request
        proxyReq.write(bodyData);
      }
    },
    onError: (err, req, res) => {
      // Handle proxy error
      console.error(`[${serviceName.toUpperCase()}] Proxy Error:`, err);
      res.status(500).json({
        status: 'error',
        message: `Service ${serviceName} is unavailable`,
        error: err.message
      });
    }
  });
};

// Create proxies for all services
const userServiceProxy = createServiceProxy('users', config.services.user);

// Direct proxy for auth service
const authServiceProxy = createProxyMiddleware({
  target: config.services.user,
  changeOrigin: true,
  // Don't rewrite path for auth service
  pathRewrite: null,
  // Increase timeout
  timeout: 60000,
  proxyTimeout: 60000,
  // Log everything
  logLevel: 'debug',
  // Handle request body
  onProxyReq: (proxyReq, req, res) => {
    // Log the request
    console.log(`[AUTH] ${req.method} ${req.originalUrl}`);
    // Log the target URL
    console.log(`[AUTH] Target URL: ${config.services.user}${req.url}`);

    // Handle request body
    if (req.body && Object.keys(req.body).length > 0) {
      const bodyData = JSON.stringify(req.body);
      proxyReq.setHeader('Content-Type', 'application/json');
      proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
      // Write body data to the proxy request
      proxyReq.write(bodyData);
    }
  },
  onError: (err, req, res) => {
    // Handle proxy error
    console.error(`[AUTH] Proxy Error:`, err);
    res.status(500).json({
      status: 'error',
      message: `Auth service is unavailable`,
      error: err.message
    });
  }
});

const appointmentServiceProxy = createServiceProxy('appointments', config.services.appointment);
const medicalRecordServiceProxy = createServiceProxy('medical-records', config.services.medicalRecord);
const billingServiceProxy = createServiceProxy('billing', config.services.billing, {
  pathRewrite: {
    '^/api/billing': '/api'
  }
});
const pharmacyServiceProxy = createServiceProxy('pharmacy', config.services.pharmacy);
const labServiceProxy = createServiceProxy('lab', config.services.lab, {
  pathRewrite: {
    '^/api/laboratory': '/api'
  }
});
const notificationServiceProxy = createServiceProxy('notifications', config.services.notification, {
  pathRewrite: {
    '^/api/notifications': '/api'
  }
});

module.exports = {
  userServiceProxy,
  authServiceProxy,
  appointmentServiceProxy,
  medicalRecordServiceProxy,
  billingServiceProxy,
  pharmacyServiceProxy,
  labServiceProxy,
  notificationServiceProxy
};
