const jwt = require('jsonwebtoken');
const config = require('../config');
// const redis = require('redis');
const { promisify } = require('util');
const crypto = require('crypto');
const uuidv4 = () => crypto.randomUUID();

// Create Redis client (temporarily disabled)
let redisClient = null;

/**
 * Middleware to verify JWT token
 */
const verifyToken = async (req, res, next) => {
  // Get auth header
  const authHeader = req.headers.authorization;

  // Log only in development environment
  if (process.env.NODE_ENV !== 'production') {
    console.log('Verifying token, auth header:', authHeader ? 'present' : 'missing');
  }

  if (!authHeader) {
    return res.status(401).json({
      status: 'error',
      message: 'Authentication required. Please provide a valid token.'
    });
  }

  // Check if auth header has Bearer token
  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') {
    if (process.env.NODE_ENV !== 'production') {
      console.log('Invalid auth header format:', authHeader);
    }
    return res.status(401).json({
      status: 'error',
      message: 'Invalid authentication format. Use Bearer <token>.'
    });
  }

  const token = parts[1];

  // Don't log sensitive information in production
  if (process.env.NODE_ENV !== 'production') {
    console.log('Token to verify:', token.substring(0, 10) + '...');
    console.log('JWT Secret length:', config.jwtSecret.length);
  }

  try {
    // Verify token with options
    const decoded = jwt.verify(token, config.jwtSecret, {
      algorithms: ['HS256'], // Only allow HS256 algorithm
      maxAge: '1d' // Token expires after 1 day as an additional check
    });

    // Check if token has JTI (JWT ID)
    const tokenJti = decoded.jti;

    // Token blacklist check temporarily disabled
    // Redis functionality is disabled

    // Check if token is about to expire (less than 30 minutes remaining)
    const tokenExp = decoded.exp * 1000; // Convert to milliseconds
    const currentTime = Date.now();
    const timeRemaining = tokenExp - currentTime;

    if (timeRemaining < 30 * 60 * 1000) { // Less than 30 minutes
      // Add a header to indicate token is about to expire
      res.set('X-Token-Expiring-Soon', 'true');

      // Add token JTI to header for refresh middleware
      if (tokenJti) {
        res.set('X-Token-JTI', tokenJti);
      }
    }

    if (process.env.NODE_ENV !== 'production') {
      console.log('Token verified successfully');
    }

    // Store user info in request object
    req.user = decoded;

    // Add user info to headers for downstream services
    req.headers['X-User-ID'] = decoded.user_id || decoded.id;
    req.headers['X-User-Role'] = decoded.role;
    req.headers['X-User-Email'] = decoded.email || '';
    req.headers['X-User-First-Name'] = decoded.first_name || '';
    req.headers['X-User-Last-Name'] = decoded.last_name || '';

    // Add token JTI to headers for token validation in services
    if (tokenJti) {
      req.headers['X-Token-JTI'] = tokenJti;
    }

    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        status: 'error',
        message: 'Token has expired. Please login again.',
        code: 'TOKEN_EXPIRED'
      });
    } else if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        status: 'error',
        message: 'Invalid token. Please login again.',
        code: 'INVALID_TOKEN'
      });
    }

    console.error('Token verification failed:', error.message);
    return res.status(401).json({
      status: 'error',
      message: 'Authentication failed. Please login again.'
    });
  }
};

/**
 * Middleware to check if user has required role
 */
const hasRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        status: 'error',
        message: 'Authentication required. Please login to access this resource.'
      });
    }

    // Convert to array if single role is provided
    const requiredRoles = Array.isArray(roles) ? roles : [roles];

    if (requiredRoles.includes(req.user.role)) {
      next();
    } else {
      // Log unauthorized access attempts in all environments
      console.warn(`Access denied: User ${req.user.user_id} with role ${req.user.role} attempted to access resource requiring ${requiredRoles.join(', ')}`);

      return res.status(403).json({
        status: 'error',
        message: 'Access denied: You do not have permission to access this resource.',
        code: 'INSUFFICIENT_PERMISSIONS'
      });
    }
  };
};

/**
 * Middleware to check if user has access to a specific resource
 * This is more granular than role-based access control
 */
const hasResourceAccess = (resourceType) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        status: 'error',
        message: 'Authentication required. Please login to access this resource.'
      });
    }

    const userId = req.user.user_id;
    const userRole = req.user.role;
    const resourceId = req.params.id || req.query.id;

    // Admin always has access
    if (userRole === 'ADMIN') {
      return next();
    }

    // Resource-specific access control logic
    switch (resourceType) {
      case 'MEDICAL_RECORD':
        // Patients can only access their own records
        if (userRole === 'PATIENT') {
          // Check if the record belongs to the patient
          // This would typically involve a database query or service call
          // For now, we'll use a simple check based on the request parameters
          const patientId = req.params.patient_id || req.query.patient_id;
          if (patientId && patientId === userId) {
            return next();
          }
          return res.status(403).json({
            status: 'error',
            message: 'Access denied: You can only access your own medical records.',
            code: 'RESOURCE_ACCESS_DENIED'
          });
        }
        // Doctors and nurses have access to all records
        else if (['DOCTOR', 'NURSE'].includes(userRole)) {
          return next();
        }
        break;

      // Add more resource types as needed

      default:
        // Default to role-based access control
        return next();
    }

    // If we get here, access is denied
    return res.status(403).json({
      status: 'error',
      message: 'Access denied: You do not have permission to access this resource.',
      code: 'RESOURCE_ACCESS_DENIED'
    });
  };
};

module.exports = {
  verifyToken,
  hasRole,
  hasResourceAccess
};
