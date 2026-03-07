import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

export interface User {
  id: number;
  uuid: string;
  email?: string;
  phone?: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_verified: boolean;
  role: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (emailOrPhone: string, password: string) => Promise<void>;
  loginWithPhoneOTP: (phone: string) => Promise<void>;
  verifyPhoneOTP: (phone: string, otp: string) => Promise<void>;
  loginWithDigilocker: () => void;
  loginWithGoogle: () => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getAccessToken = (): string | null => {
    return localStorage.getItem('access_token');
  };

  const getRefreshToken = (): string | null => {
    return localStorage.getItem('refresh_token');
  };

  const setTokens = (authResponse: AuthResponse): void => {
    localStorage.setItem('access_token', authResponse.access_token);
    localStorage.setItem('refresh_token', authResponse.refresh_token);
    localStorage.setItem('token_type', authResponse.token_type);
    localStorage.setItem('token_expires_in', authResponse.expires_in.toString());
  };

  const clearTokens = (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('token_expires_in');
  };

  const getAuthHeaders = (): HeadersInit => {
    const token = getAccessToken();
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  };

  const getCurrentUser = useCallback(async (): Promise<void> => {
    const token = getAccessToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        clearTokens();
        setUser(null);
      }
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshToken = useCallback(async (): Promise<void> => {
    const refresh = getRefreshToken();
    if (!refresh) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data: AuthResponse = await response.json();
      setTokens(data);
      setUser(data.user);
    } catch {
      clearTokens();
      setUser(null);
      throw new Error('Token refresh failed');
    }
  }, []);

  const login = async (emailOrPhone: string, password: string): Promise<void> => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email_or_phone: emailOrPhone, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    setTokens(data);
    setUser(data.user);
  };

  const loginWithPhoneOTP = async (phone: string): Promise<void> => {
    const response = await fetch(`${API_URL}/auth/login/phone/request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send OTP');
    }
  };

  const verifyPhoneOTP = async (phone: string, otp: string): Promise<void> => {
    const response = await fetch(`${API_URL}/auth/login/phone/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone, otp }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'OTP verification failed');
    }

    const data: AuthResponse = await response.json();
    setTokens(data);
    setUser(data.user);
  };

  const loginWithDigilocker = (): void => {
    window.location.href = `${API_URL}/auth/digilocker`;
  };

  const loginWithGoogle = (): void => {
    window.location.href = `${API_URL}/auth/google`;
  };

  const logout = (): void => {
    clearTokens();
    setUser(null);
    window.location.href = '/login';
  };

  useEffect(() => {
    getCurrentUser();
  }, [getCurrentUser]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      return;
    }

    const expiresIn = localStorage.getItem('token_expires_in');
    if (expiresIn) {
      const expiryTime = parseInt(expiresIn, 10) * 1000;
      const refreshTime = expiryTime - 5 * 60 * 1000;

      const timer = setTimeout(() => {
        refreshToken();
      }, refreshTime);

      return () => clearTimeout(timer);
    }
  }, [refreshToken]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    loginWithPhoneOTP,
    verifyPhoneOTP,
    loginWithDigilocker,
    loginWithGoogle,
    logout,
    refreshToken,
    getCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
