import axios from 'axios';
import { DEMO_USER, MOCK_GRANTS, MOCK_APPLICATION } from './mockData';

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';
const api = axios.create({ baseURL: API_BASE, timeout: 30000 });
api.interceptors.request.use(c => { const t = localStorage.getItem('access_token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c; });
api.interceptors.response.use(r => r, e => { if (e.response?.status === 401) { localStorage.removeItem('access_token'); localStorage.removeItem('user'); window.location.href = '/'; } return Promise.reject(e); });

// Demo mode: active on GitHub Pages or when VITE_DEMO_MODE=true
export const isDemoMode = typeof window !== 'undefined' && (
  window.location.hostname.includes('github.io') ||
  (import.meta as any).env?.VITE_DEMO_MODE === 'true'
);

const ok = (data: any) => Promise.resolve({ data, status: 200, statusText: 'OK', headers: {}, config: {} as any });

export const authApi = {
  register: (email: string, password: string, full_name?: string) => {
    if (isDemoMode) {
      const u = { ...DEMO_USER, email, full_name: full_name || email.split('@')[0] };
      return ok({ access_token: 'demo-token', user: u });
    }
    return api.post('/api/auth/register', { email, password, full_name });
  },
  login: (email: string, password: string) => {
    if (isDemoMode) {
      const u = { ...DEMO_USER, email };
      return ok({ access_token: 'demo-token', user: u });
    }
    return api.post('/api/auth/login', { email, password });
  },
  me: () => isDemoMode ? ok(DEMO_USER) : api.get('/api/auth/me'),
  updateMe: (data: any) => isDemoMode ? ok({ ...DEMO_USER, ...data }) : api.put('/api/auth/me', data),
};

export const grantsApi = {
  list: (params?: any) => {
    if (isDemoMode) {
      let grants = [...MOCK_GRANTS];
      if (params?.category) grants = grants.filter(g => g.category === params.category);
      if (params?.search) grants = grants.filter(g => g.source_name.toLowerCase().includes(params.search.toLowerCase()));
      return ok(grants);
    }
    return api.get('/api/grants', { params });
  },
  get: (id: number) => {
    if (isDemoMode) {
      const g = MOCK_GRANTS.find(g => g.id === id);
      return g ? ok(g) : Promise.reject(new Error('Not found'));
    }
    return api.get(`/api/grants/${id}`);
  },
  upcoming: (days?: number) => {
    if (isDemoMode) {
      const cutoff = new Date(); cutoff.setDate(cutoff.getDate() + (days || 30));
      const grants = MOCK_GRANTS.filter(g => g.nearest_deadline && new Date(g.nearest_deadline) <= cutoff);
      return ok(grants);
    }
    return api.get('/api/grants/upcoming', { params: { days } });
  },
  subscribe: (id: number) => isDemoMode ? ok({ subscribed: true }) : api.post(`/api/grants/${id}/subscribe`),
  unsubscribe: (id: number) => isDemoMode ? ok({ subscribed: false }) : api.delete(`/api/grants/${id}/subscribe`),
};

export const applicationsApi = {
  list: () => isDemoMode ? ok([]) : api.get('/api/applications'),
  create: (grant_id: number) => {
    if (isDemoMode) return ok({ ...MOCK_APPLICATION, grant_id, id: Date.now() });
    return api.post('/api/applications', { grant_id });
  },
  get: (id: number) => isDemoMode ? ok({ ...MOCK_APPLICATION, id }) : api.get(`/api/applications/${id}`),
  update: (id: number, data: any) => isDemoMode ? ok({ ...MOCK_APPLICATION, id, ...data }) : api.put(`/api/applications/${id}`, data),
  delete: (id: number) => isDemoMode ? ok({}) : api.delete(`/api/applications/${id}`),
};

export const aiApi = {
  hint: (data: any) => isDemoMode
    ? ok({ hints: ['Опишите конкретные измеримые результаты', 'Укажите целевую аудиторию и её численность', 'Добавьте сроки реализации каждого этапа', 'Подчеркните уникальность вашего подхода'] })
    : api.post('/api/ai/hint', data),
  checkText: (text: string, context?: string) => isDemoMode
    ? ok({ improved_text: text + ' (улучшено AI)', changes: ['Улучшена структура предложения', 'Добавлена конкретика'] })
    : api.post('/api/ai/check-text', { text, context }),
  generateSection: (data: any) => isDemoMode
    ? ok({ text: 'В демо-режиме генерация AI-разделов недоступна. Запустите backend для полного функционала.' })
    : api.post('/api/ai/generate-section', data),
};

export const documentsApi = {
  generatePdf: (app_id: number) => isDemoMode ? ok({ message: 'Демо: PDF генерируется только при запущенном backend' }) : api.post(`/api/documents/pdf/${app_id}`),
  generateDocx: (app_id: number) => isDemoMode ? ok({ message: 'Демо: DOCX генерируется только при запущенном backend' }) : api.post(`/api/documents/docx/${app_id}`),
  downloadUrl: (app_id: number, type: string) => `${API_BASE}/api/documents/download/${app_id}/${type}`,
};

export const notificationsApi = {
  subscribePush: (data: any) => isDemoMode ? ok({}) : api.post('/api/notifications/push/subscribe', data),
  getTelegramCode: () => isDemoMode ? ok({ code: 'DEMO-1234', expires_in: 600 }) : api.get('/api/notifications/telegram/link-code'),
  getVapidKey: () => isDemoMode ? ok({ key: '' }) : api.get('/api/notifications/vapid-public-key'),
};

export const adminApi = {
  stats: () => isDemoMode ? ok({ users: 1, grants: 10, applications: 0, notifications_sent: 0 }) : api.get('/api/admin/stats'),
  users: () => isDemoMode ? ok([DEMO_USER]) : api.get('/api/admin/users'),
  runScrape: () => isDemoMode ? ok({ message: 'Демо: парсинг недоступен без backend' }) : api.post('/api/scrape/run'),
  scrapeStatus: () => isDemoMode ? ok({ status: 'idle' }) : api.get('/api/scrape/status'),
};

export default api;
