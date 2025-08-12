import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, endpoints } from '@/lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  is_admin?: boolean;
  is_superuser?: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  checkAdminStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = (token: string, userData: User) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_data', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setUser(null);
  };

  const checkAdminStatus = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    try {
      const response = await api.get(endpoints.admin.check);
      if (response.data) {
        const userData = localStorage.getItem('user_data');
        if (userData) {
          const parsedUser = JSON.parse(userData);
          const updatedUser = {
            ...parsedUser,
            is_admin: response.data.is_admin,
            is_superuser: response.data.is_superuser,
          } as User;
          setUser(updatedUser);
          localStorage.setItem('user_data', JSON.stringify(updatedUser));
        }
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('user_data');
      
      if (token && userData) {
        try {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
          // Check admin status if user is logged in
          try {
            const response = await api.get(endpoints.admin.check);
            if (response.data) {
              const updatedUser = {
                ...parsedUser,
                is_admin: response.data.is_admin,
                is_superuser: response.data.is_superuser,
              } as User;
              setUser(updatedUser);
              localStorage.setItem('user_data', JSON.stringify(updatedUser));
            }
          } catch (error) {
            console.error('Error checking admin status:', error);
            // Continue with the parsed user even if admin check fails
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || user?.is_superuser || false,
    checkAdminStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
