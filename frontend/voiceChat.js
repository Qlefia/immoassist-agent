import { API_BASE_URL } from './apiClient.js';
import { addMessage, showTypingIndicator } from './chatUI.js';
import { sendTextMessage } from './agentClient.js';

// Voice chat state - will be managed externally
let isVoiceChatActive = false;
let currentAudio = null;
let lastTTS = '';

/**
 * Update the visual state of the voice-chat button.
 * @param {HTMLButtonElement} button
 * @param {'inactive'|'active'|'listening'} state
 */
export function updateVoiceChatButtonState(button, state) {
  const textSpan = button.querySelector('.voice-chat-text');
  if (!textSpan) return;
  button.classList.remove('voice-chat-inactive', 'voice-chat-active', 'voice-chat-listening');

  switch (state) {
    case 'inactive':
      button.classList.add('voice-chat-inactive');
      textSpan.textContent = 'SPRACH-CHAT';
      button.title = 'Sprach-Chat aktivieren';
      break;
    case 'active':
      button.classList.add('voice-chat-active');
      textSpan.textContent = 'CHAT BEENDEN';
      button.title = 'Sprach-Chat beenden';
      break;
    case 'listening':
      button.classList.add('voice-chat-active', 'voice-chat-listening');
      textSpan.textContent = 'HÖRE ZU...';
      button.title = 'Ich höre Ihnen zu...';
      break;
    default:
      break;
  }
}

/**
 * Calculate Levenshtein similarity ratio between two strings (0-1).
 * @param {string} a
 * @param {string} b
 * @returns {number}
 */
export function similarityRatio(a, b) {
  if (!a || !b) return 0;
  a = a.trim().toLowerCase();
  b = b.trim().toLowerCase();
  if (a === b) return 1;
  if (a.includes(b) || b.includes(a)) {
    return Math.min(a.length, b.length) / Math.max(a.length, b.length);
  }
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1, // insertion
          matrix[i - 1][j] + 1, // deletion
        );
      }
    }
  }
  const levDist = matrix[b.length][a.length];
  const maxLen = Math.max(a.length, b.length);
  return maxLen === 0 ? 1 : 1 - levDist / maxLen;
}

/**
 * Stop any currently playing audio.
 */
export function stopCurrentAudio() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
}

/**
 * Generate TTS audio from text and play it via streaming.
 * @param {string} text
 * @returns {Promise<void>}
 */
export async function generateAndPlayVoiceChatTTS(text) {
  if (!text || !isVoiceChatActive) return;
  lastTTS = text.trim().toLowerCase();

  try {
    console.log('Generating TTS for text length:', text.length, 'characters');
    const startTime = performance.now();

    const response = await fetch(`${API_BASE_URL}/agent/tts-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        voice_id: 'pNInz6obpgDQGcFmaJgB', // Adam - multilingual voice
        model_id: 'eleven_flash_v2_5', // Flash model for minimal latency
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    stopCurrentAudio();

    console.log('Collecting audio data via streaming...');
    const audioChunks = [];
    const reader = response.body.getReader();
    let firstChunkTime = null;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('All chunks received');
          break;
        }
        if (value) {
          audioChunks.push(value);
          if (!firstChunkTime) {
            firstChunkTime = performance.now();
            const firstChunkLatency = Math.round(firstChunkTime - startTime);
            console.log(`First chunk received in ${firstChunkLatency}ms`);
          }
        }
      }

      if (audioChunks.length > 0) {
        const loadTime = Math.round(performance.now() - startTime);
        console.log(`All audio data collected in ${loadTime}ms, creating audio file`);

        const audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' });
        const audioUrl = URL.createObjectURL(audioBlob);

        currentAudio = new Audio(audioUrl);
        currentAudio.preload = 'auto';

        currentAudio.onplay = () => {
          const totalLatency = Math.round(performance.now() - startTime);
          console.log(`Audio playback started, total latency: ${totalLatency}ms`);
        };

        currentAudio.onended = () => {
          console.log('Audio playback completed');
          URL.revokeObjectURL(audioUrl);
          finalizeVoiceChat();
        };

        currentAudio.onerror = (error) => {
          console.error('Audio playback error:', error);
          URL.revokeObjectURL(audioUrl);
          finalizeVoiceChat();
        };

        await currentAudio.play();
      } else {
        console.log('No audio chunks received');
        finalizeVoiceChat();
      }
    } catch (readerError) {
      console.error('Error reading streaming data:', readerError);
      finalizeVoiceChat();
    }
  } catch (error) {
    console.error('TTS generation error:', error);
    finalizeVoiceChat();
  }
}

/**
 * Finalize voice chat session after TTS completes.
 */
export function finalizeVoiceChat() {
  if (isVoiceChatActive) {
    setTimeout(() => {
      // Import speechManager dynamically to avoid circular dependency
      import('./speechManager.js').then(({ default: speechManager }) => {
        speechManager.finalizeVoiceChat();
      });
    }, 500);
  }
}

/**
 * Process voice chat input by sending to agent and playing response.
 * @param {string} transcript
 * @param {{appName:string,userId:string,sessionId:string}} sessionInfo
 * @param {(jsonData:string, isFirst:boolean, element:HTMLElement)=>void} processEventData
 * @param {(sources:any[], element:HTMLElement)=>void} displayRagSources
 * @returns {Promise<void>}
 */
export async function processVoiceChatInput(
  transcript,
  sessionInfo,
  // processEventData and displayRagSources are now available on window
) {
  if (!transcript || !isVoiceChatActive) return;

  addMessage(transcript, 'user-message');
  stopCurrentAudio();

  try {
    const aiMessageElement = addMessage('', 'bot-message');
    showTypingIndicator(aiMessageElement);

    let responseText = '';

    await sendTextMessage(
      { ...sessionInfo, message: transcript },
      (jsonData, isFirst) => {
        window.processEventData(jsonData, aiMessageElement, isFirst);
        const rawContent = aiMessageElement.getAttribute('data-raw-content') || '';
        if (rawContent) responseText = rawContent;
      },
    );

    if (aiMessageElement.pendingSources?.length) {
      window.displayRagSources(aiMessageElement.pendingSources, aiMessageElement);
    }

    if (isVoiceChatActive && responseText.trim()) {
      await generateAndPlayVoiceChatTTS(responseText.trim());
    }
  } catch (error) {
    console.error('Voice chat input processing error:', error);
    addMessage('Es ist ein Fehler bei der Verarbeitung der Anfrage aufgetreten.', 'bot-message');
  }
}

/**
 * Set voice chat active state.
 * @param {boolean} active
 */
export function setVoiceChatActive(active) {
  isVoiceChatActive = active;
}

/**
 * Get current voice chat active state.
 * @returns {boolean}
 */
export function getVoiceChatActive() {
  return isVoiceChatActive;
}

/**
 * Get last TTS text for echo filtering.
 * @returns {string}
 */
export function getLastTTS() {
  return lastTTS;
}
