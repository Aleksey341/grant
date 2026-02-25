import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null; token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void; isLoading: boolean;
}
const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem('access_token');
    const u = localStorage.getItem('user');
    if (t && u) { try { setToken(t); setUser(JSON.parse(u)); } catch {} }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    const { access_token, user: u } = res.data;
    localStorage.setItem('access_token', access_token); localStorage.setItem('user', JSON.stringify(u));
    setToken(access_token); setUser(u);
  };
  const register = async (email: string, password: string, fullName?: string) => {
    const res = await authApi.register(email, password, fullName);
    const { access_token, user: u } = res.data;
    localStorage.setItem('access_token', access_token); localStorage.setItem('user', JSON.stringify(u));
    setToken(access_token); setUser(u);
  };
  const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('user'); setToken(null); setUser(null); };

  return <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>{children}</AuthContext.Provider>;
}
export function useAuth() { const c = useContext(AuthContext); if (!c) throw new Error('useAuth must be inside AuthProvider'); return c; }
