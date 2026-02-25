import axios from 'axios';

// Force local backend for anything other than the primary production domain to simplify local development/testing
if (window.location.hostname !== 'info.hotelshanmugabhavaan.com' && window.location.hostname !== 'hotelshanmugabhavaan.com') {
  axios.defaults.baseURL = 'http://127.0.0.1:8000';
  console.log("%c[DEBUG] LOCAL DEVELOPER MODE: Backend forced to " + axios.defaults.baseURL, "color: white; background: red; font-size: 16px; font-weight: bold;");
} else if (!axios.defaults.baseURL) {
  axios.defaults.baseURL = process.env.REACT_APP_API_BASE_URL;
  console.log("[DEBUG] Production mode: Backend set from env:", axios.defaults.baseURL);
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
      const response = await axios.post('/api/users/login', {
        email: username, // api/users/login expects 'email' key
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
      // Skip redirect for login/auth endpoints — let the component show the error
      const requestUrl = error.config?.url || '';
      const isAuthRequest = requestUrl.includes('/login') ||
        requestUrl.includes('/forgot-password') ||
        requestUrl.includes('/reset-password') ||
        requestUrl.includes('/verify-otp') ||
        requestUrl.includes('/google-login');

      if (!isAuthRequest) {
        // Token expired or invalid - auto logout
        authService.logout();
        window.location.href = '/'; // Redirect to home
      }
    }
    return Promise.reject(error);
  }
);

export default authService;
