import { generateUUID } from './utils.js';

export const API_BASE_URL = window.location.origin;

/**
 * Создаёт сессию на сервере.
 * @returns {Promise<{userId:string, id:string, appName:string}>}
 */
export async function createSession() {
  const generatedSessionId = generateUUID();
  const response = await fetch(
    `${API_BASE_URL}/apps/app/users/u_999/sessions/${generatedSessionId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    },
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
} 