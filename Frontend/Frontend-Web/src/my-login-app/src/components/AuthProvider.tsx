import React, { createContext, useContext, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  token: string | null;
  role: string | null;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState<string | null>(localStorage.getItem('username'));
  const [role, setRole] = useState<string | null>(localStorage.getItem('role'));

  const isAuthenticated = !!token;

  const login = useCallback(async (user: string, password: string): Promise<{ success: boolean; error?: string }> => {
    if (!user || !password) {
      return { success: false, error: 'Usuario y contraseña son requeridos' };
    }

    try {
      const formData = new URLSearchParams();
      formData.append('username', user.trim());
      formData.append('password', password);

      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      if (!response.ok) {
        if (response.status === 401) {
          return { success: false, error: 'Credenciales incorrectas' };
        }
        return { success: false, error: 'Error del servidor. Intenta luego.' };
      }

      const data = await response.json();
      const accessToken = data.access_token;
      
      // Decode JWT to get role
      let extractedRole = 'USER';
      try {
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        extractedRole = payload.role || 'USER';
      } catch (e) {
        console.error("Error decoding token:", e);
      }
      
      setToken(accessToken);
      setUsername(user.trim());
      setRole(extractedRole);
      
      localStorage.setItem('token', accessToken);
      localStorage.setItem('username', user.trim());
      localStorage.setItem('role', extractedRole);

      return { success: true };
    } catch (err) {
      return { success: false, error: 'Error de conexión' };
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUsername(null);
    setRole(null);
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout, token, role } as any}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};