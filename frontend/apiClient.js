import { generateUUID } from './utils.js';

export const API_BASE_URL = window.location.origin;

// Simple token handling for optional dev auth flow
let memoryToken = null;
export function getAuthToken() {
  if (memoryToken) return memoryToken;
  try {
    const stored = localStorage.getItem('immoassist_token');
    if (stored) memoryToken = stored;
  } catch {}
  return memoryToken;
}
export function setAuthToken(token) {
  memoryToken = token;
  try { localStorage.setItem('immoassist_token', token); } catch {}
}

function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra };
  const token = getAuthToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

/**
 * Создаёт сессию на сервере.
 * @returns {Promise<{userId:string, id:string, appName:string}>}
 */
export async function createSession(appName = 'app', userId = 'u_999') {
  const generatedSessionId = generateUUID();
  const response = await fetch(
    `${API_BASE_URL}/apps/${appName}/users/${userId}/sessions/${generatedSessionId}`,
    {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify({}),
    },
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Возвращает список сессий пользователя
 */
export async function listUserSessions(appName = 'app', userId = 'u_999') {
  const resp = await fetch(`${API_BASE_URL}/apps/${appName}/users/${userId}/sessions`, {
    method: 'GET',
    headers: buildHeaders(),
  });
  if (!resp.ok) throw new Error(`Failed to list sessions: ${resp.status}`);
  return resp.json();
}

/**
 * Возвращает детали сессии (включая events)
 */
export async function getSessionDetails(appName = 'app', userId = 'u_999', sessionId) {
  const resp = await fetch(`${API_BASE_URL}/apps/${appName}/users/${userId}/sessions/${sessionId}`, {
    method: 'GET',
    headers: buildHeaders(),
  });
  if (!resp.ok) throw new Error(`Failed to get session: ${resp.status}`);
  return resp.json();
}

/**
 * Удаляет сессию пользователя
 */
export async function deleteSession(appName = 'app', userId = 'u_999', sessionId) {
  const resp = await fetch(`${API_BASE_URL}/apps/${appName}/users/${userId}/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: buildHeaders(),
  });
  if (!resp.ok && resp.status !== 404) throw new Error(`Failed to delete session: ${resp.status}`);
  return true;
}

// Dev-only auth helpers (optional; not required by local server)
export async function devSendCode(email = 'default.posts@klarvest.io') {
  const resp = await fetch('https://dev.immoassist.io/api/v1/auth/send-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!resp.ok) throw new Error(`send-code failed: ${resp.status}`);
  return resp.json();
}

export async function devVerifyCode(email = 'default.posts@klarvest.io', code = '1111') {
  const resp = await fetch('https://dev.immoassist.io/api/v1/auth/verify-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code }),
  });
  if (!resp.ok) throw new Error(`verify-code failed: ${resp.status}`);
  const data = await resp.json();
  if (data?.token) setAuthToken(data.token);
  return data;
}