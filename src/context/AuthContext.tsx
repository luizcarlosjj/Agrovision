/**
 * Auth Context
 * Manages user authentication state and backend integration
 */

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { analysisService } from '@services';
import { logger } from '@utils/logger';

/**
 * User state
 */
interface User {
  id: string;
  email: string;
  name: string;
  token: string;
}

/**
 * Auth context type
 */
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  register: (email: string, password: string, name: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

/**
 * Create context
 */
const AuthContextInternal = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth Provider Component
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Register new user
   */
  const register = useCallback(async (email: string, password: string, name: string) => {
    try {
      setIsLoading(true);
      setError(null);

      logger.log('[AuthContext] Registering user:', email);

      const userData = await analysisService.registerUser(email, password, name);

      setUser({
        id: userData.id,
        email: userData.email,
        name: userData.name,
        token: userData.token,
      });

      logger.success('[AuthContext] User registered:', email);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMsg);
      logger.error('[AuthContext] Registration error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Login user
   */
  const login = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);

      logger.log('[AuthContext] Logging in user:', email);

      const userData = await analysisService.loginUser(email, password);

      setUser({
        id: userData.id,
        email: userData.email,
        name: userData.name,
        token: userData.token,
      });

      logger.success('[AuthContext] User logged in:', email);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed';
      setError(errorMsg);
      logger.error('[AuthContext] Login error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    logger.log('[AuthContext] Logging out');
    setUser(null);
    setError(null);
  }, []);

  return (
    <AuthContextInternal.Provider
      value={{
        user,
        isLoading,
        error,
        register,
        login,
        logout,
      }}
    >
      {children}
    </AuthContextInternal.Provider>
  );
}

/**
 * Use auth context hook
 */
export function useAuth() {
  const context = useContext(AuthContextInternal);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
