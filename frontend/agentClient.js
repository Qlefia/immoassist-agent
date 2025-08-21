import { API_BASE_URL } from './apiClient.js';

/**
 * Send a user text message to backend and stream the response.
 * @param {{appName:string,userId:string,sessionId:string,message:string,preferredAgent?:string}} params
 * @param {(chunk:any,isFirst:boolean)=>void} onEventData - invoked for each SSE event JSON chunk.
 * @returns {Promise<void>} resolves when stream ends.
 */
export async function sendTextMessage({ appName, userId, sessionId, message, preferredAgent }, onEventData) {
  const requestBody = {
    appName,
    userId,
    sessionId,
    newMessage: {
      parts: [{ text: message }],
      role: 'user',
    },
    streaming: false,
  };

  // Add preferred agent if provided
  if (preferredAgent) {
    requestBody.preferredAgent = preferredAgent;
  }

  const response = await fetch(`${API_BASE_URL}/agent/run_sse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) return;
  const decoder = new TextDecoder();
  let lineBuffer = '';
  let eventDataBuffer = '';
  let isFirst = true;

  while (true) {
    const { done, value } = await reader.read();
    if (value) lineBuffer += decoder.decode(value, { stream: true });

    let eolIndex;
    while ((eolIndex = lineBuffer.indexOf('\n')) >= 0 || (done && lineBuffer.length > 0)) {
      let line;
      if (eolIndex >= 0) {
        line = lineBuffer.substring(0, eolIndex);
        lineBuffer = lineBuffer.substring(eolIndex + 1);
      } else {
        line = lineBuffer;
        lineBuffer = '';
      }

      if (line.trim() === '') {
        if (eventDataBuffer.length > 0) {
          const jsonData = eventDataBuffer.endsWith('\n')
            ? eventDataBuffer.slice(0, -1)
            : eventDataBuffer;
          onEventData(jsonData, isFirst);
          isFirst = false;
          eventDataBuffer = '';
        }
      } else if (line.startsWith('data:')) {
        eventDataBuffer += line.substring(5).trimStart() + '\n';
      }
    }

    if (done) {
      if (eventDataBuffer.length > 0) {
        onEventData(eventDataBuffer, isFirst);
      }
      break;
    }
  }
}
