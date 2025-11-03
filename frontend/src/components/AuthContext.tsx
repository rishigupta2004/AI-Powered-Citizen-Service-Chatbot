import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from 'sonner';

interface User {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  aadhaar?: string;
  loginMethod: 'phone' | 'aadhaar' | 'google';
  avatar?: string;
  verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastActivity, setLastActivity] = useState(Date.now());

  // ============= SECURITY SETTINGS =============
  const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutes
  const MAX_SESSION_LIFETIME = 60 * 60 * 1000; // 1 hour
  // =============================================

  // STEP 1: Load user from sessionStorage on mount
  useEffect(() => {
    const storedData = sessionStorage.getItem('seva_sindhu_user');
    if (storedData) {
      try {
        const parsed = JSON.parse(storedData);
        
        // Check if session has expired by max lifetime
        const loginTime = parsed.loginTime || Date.now();
        const sessionAge = Date.now() - loginTime;
        
        if (sessionAge > MAX_SESSION_LIFETIME) {
          sessionStorage.removeItem('seva_sindhu_user');
          toast.error('Session expired. Please login again for security.');
        } else {
          setUser(parsed.user);
          setLastActivity(parsed.lastActivity || Date.now());
        }
      } catch (error) {
        console.error('Error parsing stored user:', error);
        sessionStorage.removeItem('seva_sindhu_user');
      }
    }
    setIsLoading(false);
  }, []);

  // STEP 2: Inactivity timeout checker
  useEffect(() => {
    if (!user) return;

    const checkInactivity = setInterval(() => {
      const inactiveTime = Date.now() - lastActivity;
      
      if (inactiveTime > INACTIVITY_TIMEOUT) {
        logout();
        toast.error('Session expired due to inactivity. Please login again.', {
          duration: 5000,
        });
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkInactivity);
  }, [user, lastActivity]);

  // STEP 3: Track user activity
  useEffect(() => {
    if (!user) return;

    const updateActivity = () => {
      const now = Date.now();
      setLastActivity(now);
      
      // Update sessionStorage with new activity time
      const storedData = sessionStorage.getItem('seva_sindhu_user');
      if (storedData) {
        const parsed = JSON.parse(storedData);
        sessionStorage.setItem('seva_sindhu_user', JSON.stringify({
          ...parsed,
          lastActivity: now,
        }));
      }
    };

    // Listen to user interactions
    window.addEventListener('mousemove', updateActivity);
    window.addEventListener('keypress', updateActivity);
    window.addEventListener('click', updateActivity);
    window.addEventListener('scroll', updateActivity);

    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('keypress', updateActivity);
      window.removeEventListener('click', updateActivity);
      window.removeEventListener('scroll', updateActivity);
    };
  }, [user]);

  const login = (userData: User) => {
    const sessionData = {
      user: userData,
      loginTime: Date.now(),
      lastActivity: Date.now(),
    };
    
    setUser(userData);
    setLastActivity(Date.now());
    sessionStorage.setItem('seva_sindhu_user', JSON.stringify(sessionData));
  };

  const logout = () => {
    setUser(null);
    sessionStorage.removeItem('seva_sindhu_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
