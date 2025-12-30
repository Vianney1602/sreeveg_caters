import axios from 'axios';

// Ensure axios has a baseURL set for API calls
// In production (Render), use the backend URL from environment or current origin
// In development, use localhost:5000
if (!axios.defaults.baseURL) {
  // Check if we're on Render deployment
  const isProduction = window.location.hostname.includes('render.com') || 
                      window.location.hostname.includes('sreevegcaters.com');
  
  if (isProduction) {
    // Use the backend URL from environment or construct from current host
    axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'https://sreeveg-caters.onrender.com';
  } else {
    // Development: use local backend
    axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
  }
}

// In-memory storage for sensitive tokens (cleared on browser close)
let inMemoryToken = null;
let inMemoryAdmin = null;

// Auth Service - Centralized authentication logic
const authService = {
  // Token management - use sessionStorage (cleared on browser close) instead of localStorage
  getToken() {
    // Try in-memory first (most secure), then fall back to sessionStorage
    return inMemoryToken || sessionStorage.getItem('_st');
  },

  setToken(token) { 
    inMemoryToken = token;
    // Also store in sessionStorage as backup (cleared when tab closes)
    sessionStorage.setItem('_st', token);
  },

  removeToken() {
    inMemoryToken = null;
    inMemoryAdmin = null;
    sessionStorage.removeItem('_st');
    sessionStorage.removeItem('_au');
  },

  // Admin info - in-memory storage (not exposed in dev tools)
  getAdminInfo() {
    if (inMemoryAdmin) return inMemoryAdmin;
    const userStr = sessionStorage.getItem('_au');
    return userStr ? JSON.parse(userStr) : null;
  },

  setAdminInfo(adminData) {
    inMemoryAdmin = adminData;
    // Minimal storage in sessionStorage
    sessionStorage.setItem('_au', JSON.stringify({ username: adminData.username }));
  },

  // Check authentication status
  isAuthenticated() {
    return !!this.getToken();
  },

  // Login
  async login(username, password) {
    try {
      const response = await axios.post('/api/admin/login', {
        username,
        password,
      });

      const { access_token, admin } = response.data;
      
      this.setToken(access_token);
      this.setAdminInfo(admin);

      return { success: true, admin };
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed. Please check your credentials.';
      return { success: false, error: message };
    }
  },

  // Logout
  logout() {
    this.removeToken();
  },

  // Verify token
  async verifyToken() {
    try {
      const token = this.getToken();
      if (!token) return false;

      const response = await axios.get('/api/admin/verify', {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      this.logout();
      return false;
    }
  },

  // Refresh token
  async refreshToken() {
    try {
      const token = this.getToken();
      if (!token) return { success: false };

      const response = await axios.post('/api/admin/refresh', {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const { access_token, admin } = response.data;
      this.setToken(access_token);
      this.setAdminInfo(admin);

      return { success: true, admin };
    } catch (error) {
      this.logout();
      return { success: false };
    }
  },
};

// Setup axios interceptor to automatically attach Authorization header
axios.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Setup response interceptor to handle 401 (unauthorized) globally
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - auto logout
      authService.logout();
      window.location.href = '/'; // Redirect to home
    }
    return Promise.reject(error);
  }
);

export default authService;
