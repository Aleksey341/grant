import axios from 'axios';
const API_BASE = (import.meta as any).env?.VITE_API_URL || '';
const api = axios.create({ baseURL: API_BASE, timeout: 30000 });
api.interceptors.request.use(c => { const t = localStorage.getItem('access_token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c; });
api.interceptors.response.use(r => r, e => { if (e.response?.status === 401) { localStorage.removeItem('access_token'); localStorage.removeItem('user'); window.location.href = '/'; } return Promise.reject(e); });
export const authApi = {
  register: (email: string, password: string, full_name?: string) => api.post('/api/auth/register', { email, password, full_name }),
  login: (email: string, password: string) => api.post('/api/auth/login', { email, password }),
  me: () => api.get('/api/auth/me'),
  updateMe: (data: any) => api.put('/api/auth/me', data),
};
export const grantsApi = {
  list: (params?: any) => api.get('/api/grants', { params }),
  get: (id: number) => api.get(`/api/grants/${id}`),
  upcoming: (days?: number) => api.get('/api/grants/upcoming', { params: { days } }),
  subscribe: (id: number) => api.post(`/api/grants/${id}/subscribe`),
  unsubscribe: (id: number) => api.delete(`/api/grants/${id}/subscribe`),
};
export const applicationsApi = {
  list: () => api.get('/api/applications'),
  create: (grant_id: number) => api.post('/api/applications', { grant_id }),
  get: (id: number) => api.get(`/api/applications/${id}`),
  update: (id: number, data: any) => api.put(`/api/applications/${id}`, data),
  delete: (id: number) => api.delete(`/api/applications/${id}`),
};
export const aiApi = {
  hint: (data: any) => api.post('/api/ai/hint', data),
  checkText: (text: string, context?: string) => api.post('/api/ai/check-text', { text, context }),
  generateSection: (data: any) => api.post('/api/ai/generate-section', data),
};
export const documentsApi = {
  generatePdf: (app_id: number) => api.post(`/api/documents/pdf/${app_id}`),
  generateDocx: (app_id: number) => api.post(`/api/documents/docx/${app_id}`),
  downloadUrl: (app_id: number, type: string) => `${API_BASE}/api/documents/download/${app_id}/${type}`,
};
export const notificationsApi = {
  subscribePush: (data: any) => api.post('/api/notifications/push/subscribe', data),
  getTelegramCode: () => api.get('/api/notifications/telegram/link-code'),
  getVapidKey: () => api.get('/api/notifications/vapid-public-key'),
};
export const adminApi = {
  stats: () => api.get('/api/admin/stats'),
  users: () => api.get('/api/admin/users'),
  runScrape: () => api.post('/api/scrape/run'),
  scrapeStatus: () => api.get('/api/scrape/status'),
};
export default api;
