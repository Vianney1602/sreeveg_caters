/**
 * Security Utilities for Frontend
 * Provides helper functions for data sanitization and security validation
 */

/**
 * Sanitize user input to prevent XSS attacks
 * @param {string} input - User input string
 * @returns {string} - Sanitized string
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} - True if valid email
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate phone number (Indian format)
 * @param {string} phone - Phone number
 * @returns {boolean} - True if valid phone
 */
export const isValidPhone = (phone) => {
  const phoneRegex = /^[6-9]\d{9}$/;
  return phoneRegex.test(phone.replace(/\s+/g, ''));
};

/**
 * Sanitize object data for storage
 * Removes sensitive fields before storing in sessionStorage
 * @param {Object} data - Data object
 * @param {Array} sensitiveFields - Array of field names to remove
 * @returns {Object} - Sanitized object
 */
export const sanitizeForStorage = (data, sensitiveFields = ['password', 'token', 'secret']) => {
  if (typeof data !== 'object' || data === null) return data;
  
  const sanitized = { ...data };
  sensitiveFields.forEach(field => {
    delete sanitized[field];
  });
  
  return sanitized;
};

/**
 * Clear all sensitive data from browser storage
 */
export const clearSensitiveData = () => {
  // Clear sessionStorage items
  const sensitiveKeys = [
    '_userToken',
    '_st',
    '_au',
    '_user',
    '_cart',
    '_bulkCart',
    '_orderCompleted',
    '_orderedItems',
    '_bulkOrderedItems',
    '_currentPage',
    '_showWelcome',
    '_bulkGuestCount'
  ];
  
  sensitiveKeys.forEach(key => {
    try {
      sessionStorage.removeItem(key);
    } catch (e) {
      // Silent fail
    }
  });
  
  // Clear browser history state
  try {
    window.history.replaceState(null, '', '/');
  } catch (e) {
    // Silent fail
  }
};

/**
 * Validate URL path to prevent injection
 * @param {string} path - URL path
 * @returns {boolean} - True if valid path
 */
export const isValidPath = (path) => {
  const validPaths = [
    '/',
    '/menu',
    '/cart',
    '/bulk-menu',
    '/bulk-cart',
    '/admin-login',
    '/admin',
    '/signup',
    '/signin',
    '/order-history',
    '/account'
  ];
  
  return validPaths.includes(path);
};

/**
 * Disable console in production to prevent data leaks
 */
export const disableConsoleInProduction = () => {
  if (process.env.NODE_ENV === 'production') {
    console.log = () => {};
    console.debug = () => {};
    console.info = () => {};
    // Keep console.error and console.warn for critical issues
  }
};

/**
 * Generate a secure random token (for CSRF protection)
 * @returns {string} - Random token
 */
export const generateSecureToken = () => {
  const array = new Uint8Array(32);
  window.crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

/**
 * Check if the user's session is still valid
 * @param {number} maxAge - Maximum session age in milliseconds
 * @returns {boolean} - True if session is valid
 */
export const isSessionValid = (maxAge = 24 * 60 * 60 * 1000) => {
  try {
    const sessionStart = sessionStorage.getItem('_sessionStart');
    if (!sessionStart) return false;
    
    const now = Date.now();
    const elapsed = now - parseInt(sessionStart);
    
    return elapsed < maxAge;
  } catch (e) {
    return false;
  }
};

/**
 * Set session start time
 */
export const setSessionStart = () => {
  try {
    sessionStorage.setItem('_sessionStart', Date.now().toString());
  } catch (e) {
    // Silent fail
  }
};

const security = {
  sanitizeInput,
  isValidEmail,
  isValidPhone,
  sanitizeForStorage,
  clearSensitiveData,
  isValidPath,
  disableConsoleInProduction,
  generateSecureToken,
  isSessionValid,
  setSessionStart
};

export default security;
