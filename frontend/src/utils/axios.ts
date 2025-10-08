import axios from 'axios';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: '/',
});

// Request interceptor to add token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        const hasToken = !!localStorage.getItem('token');
        const requestUrl: string = error.config?.url || '';
        // Only act if we actually had a token; otherwise just reject silently
        if (hasToken) {
          localStorage.removeItem('token');
          // Avoid redirect loops on auth pages or during login call itself
          const onAuthPage = currentPath.includes('/login') || currentPath.includes('/register');
          const isLoginCall = requestUrl.includes('/api/v1/auth/login');
          if (!onAuthPage && !isLoginCall) {
            setTimeout(() => {
              window.location.href = '/login';
            }, 100);
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;

