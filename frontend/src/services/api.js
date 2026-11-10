/**
 * AudienceFlow — Axios API Service
 *
 * All backend communication lives here.
 * Base URL is read from VITE_API_BASE_URL (defaults to http://localhost:8000).
 */

import axios from 'axios';

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// ---------------------------------------------------------------------------
// Request interceptor — attach auth token when available (future milestone)
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response interceptor — centralised error logging
// ---------------------------------------------------------------------------

apiClient.interceptors.response.use(
  (response) => {
    console.debug(
      `[AudienceFlow API] ${response.config.method?.toUpperCase()} ${response.config.url} → ${response.status}`
    );
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(
        `[AudienceFlow API] Error ${error.response.status} on ${error.config?.url}:`,
        error.response.data
      );
    } else if (error.request) {
      console.error('[AudienceFlow API] No response — is the backend running?', error.message);
    } else {
      console.error('[AudienceFlow API] Request setup error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------

/**
 * GET /health
 * Returns { status, service, version, database }
 */
export async function checkHealth() {
  const response = await apiClient.get('/health');
  return response.data;
}

// ---------------------------------------------------------------------------
// Auth — Roles
// ---------------------------------------------------------------------------

/**
 * GET /auth/roles
 * Returns array of { id, name, description } objects.
 * Admin is excluded from the list by the backend.
 */
export async function getRoles() {
  const response = await apiClient.get('/auth/roles');
  return response.data; // [{ id, name, description }, ...]
}

// ---------------------------------------------------------------------------
// Auth — Register
// ---------------------------------------------------------------------------

/**
 * POST /auth/register
 */
export async function registerUser(payload) {
  const response = await apiClient.post('/auth/register', payload);
  return response.data; // { message, user }
}

// ---------------------------------------------------------------------------
// Auth — Login
// ---------------------------------------------------------------------------

/**
 * POST /auth/login
 * @param {{ email: string, password: string }} payload
 * @returns {{ message: string, user: object }} on 200
 * @throws AxiosError:
 *   401 → invalid credentials
 *   422 → validation error
 *   503 → database unavailable
 */
export async function loginUser(payload) {
  const response = await apiClient.post('/auth/login', payload);
  return response.data; // { message, user }
}

// ---------------------------------------------------------------------------
// Auth — Me (protected)
// ---------------------------------------------------------------------------

/**
 * GET /auth/me
 * Returns the current user's profile using the stored JWT.
 * Requires the access_token to be stored in localStorage.
 */
export async function getMe() {
  const response = await apiClient.get('/auth/me');
  return response.data;
}

/**
 * Log out — clear the stored access token.
 */
export function logout() {
  localStorage.removeItem('access_token');
}

// ---------------------------------------------------------------------------
// Dashboard (protected — requires JWT)
// ---------------------------------------------------------------------------

/**
 * GET /dashboard/stats
 * Returns real counts: campaigns by status, audience members, recent campaigns.
 */
export async function getDashboardStats() {
  const r = await apiClient.get('/dashboard/stats');
  return r.data;
}

// ---------------------------------------------------------------------------
// Campaigns (protected — requires JWT)
// ---------------------------------------------------------------------------

export async function getCampaigns(skip = 0, limit = 50) {
  const r = await apiClient.get(`/campaigns?skip=${skip}&limit=${limit}`);
  return r.data;
}

export async function createCampaign(payload) {
  const r = await apiClient.post('/campaigns', payload);
  return r.data;
}

export async function getCampaign(id) {
  const r = await apiClient.get(`/campaigns/${id}`);
  return r.data;
}

export async function updateCampaign(id, payload) {
  const r = await apiClient.put(`/campaigns/${id}`, payload);
  return r.data;
}

export async function deleteCampaign(id) {
  await apiClient.delete(`/campaigns/${id}`);
}

// ---------------------------------------------------------------------------
// Named export of the raw client (for future endpoint modules)
// ---------------------------------------------------------------------------

export default apiClient;
