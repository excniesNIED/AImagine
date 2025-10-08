import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from '../utils/axios';

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// Helper to safely access localStorage (SSR-safe)
const getStoredToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

const setStoredToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
};

const removeStoredToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
};

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(getStoredToken());
  const isLoading = ref(false);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  
  const login = async (credentials: { username: string; password: string }) => {
    try {
      // OAuth2 expects form data, not JSON
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      const { access_token, user: userData } = response.data;
      
      token.value = access_token;
      user.value = userData;
      setStoredToken(access_token);
      // Don't call fetchProfile here - we already have user data from login response
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };
  
  const register = async (userData: {
    username: string;
    email: string;
    password: string;
  }) => {
    try {
      await axios.post('/api/v1/auth/register', userData);
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };
  
  const logout = () => {
    token.value = null;
    user.value = null;
    removeStoredToken();
    if (typeof window !== 'undefined') {
      // Stay on the current page; do not force reload to avoid loops
    }
  };
  
  const fetchProfile = async () => {
    if (!token.value) return;

    isLoading.value = true;

    try {
      const response = await axios.get('/api/v1/users/me');
      user.value = response.data;
      return true;
    } catch (error) {
      // Suppress console noise on unauthenticated state
      if ((error as any)?.response?.status !== 401) {
        console.error('Failed to fetch profile:', error);
      }
      // Clear token and user, but don't remove from localStorage yet
      // The interceptor will handle that
      token.value = null;
      user.value = null;
      return false;
    } finally {
      isLoading.value = false;
    }
  };
  
  // Initialize (only on client side)
  // Fetch profile in the background to sync user data, don't block
  if (typeof window !== 'undefined' && token.value && !user.value) {
    // Delay slightly to let the page render first
    setTimeout(() => {
      fetchProfile();
    }, 150);
  }
  
  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchProfile,
  };
});