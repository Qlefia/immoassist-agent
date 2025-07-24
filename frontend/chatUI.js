import { supportedLanguages } from './constants.js';
import { convertMarkdownToHtml, renderMathFormulas } from './dom.js';
import { elements } from './domCache.js';

function getChatContainer() {
  return elements.chatMessages;
}

/**
 * Append a new chat bubble to the conversation and return the DOM element.
 * @param {string} text - The message text. Pass empty string for placeholder.
 * @param {('user-message'|'bot-message')} className - CSS class determining bubble style.
 * @returns {HTMLElement}
 */
export function addMessage(text, className) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', className);

  if (text) {
    if (className === 'bot-message') {
      // Preserve raw text for later processing (RAG sources, streaming updates etc.)
      messageElement.setAttribute('data-raw-content', text);
      messageElement.innerHTML = convertMarkdownToHtml(text);
      renderMathFormulas(messageElement);
    } else {
      messageElement.textContent = text;
    }
  }

  const container = getChatContainer();
  container.appendChild(messageElement);
  container.scrollTop = container.scrollHeight;
  return messageElement;
}

/**
 * Replace element content with a typing indicator (3 animated dots).
 * @param {HTMLElement} messageElement
 */
export function showTypingIndicator(messageElement) {
  messageElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
}

/**
 * Create a temporary recognition bubble for microphone or voice-chat input.
 * @param {boolean} isVoiceChat - true for voice chat, false for single mic press.
 * @param {boolean} isAutoLanguage - whether language is set to AUTO.
 * @param {number} currentLangIndex - index in supportedLanguages (0 = AUTO).
 * @returns {HTMLElement}
 */
export function createRecognitionBubble(
  isVoiceChat = false,
  isAutoLanguage = true,
  currentLangIndex = 0,
) {
  const bubbleElement = document.createElement('div');
  bubbleElement.classList.add('message', 'user-message', 'recognition-bubble');
  if (isVoiceChat) bubbleElement.classList.add('voice-chat-bubble');

  // Determine listening text depending on language settings.
  let listeningText = 'Höre zu...';
  if (!isAutoLanguage && currentLangIndex > 0) {
    const lang = supportedLanguages[currentLangIndex - 1];
    listeningText = lang.code.startsWith('de')
      ? 'Höre zu...'
      : lang.code.startsWith('ru')
      ? 'Слушаю...'
      : 'Listening...';
  }

  const recordingIndicator = document.createElement('div');
  recordingIndicator.classList.add('recording-indicator');
  recordingIndicator.innerHTML = `
    <div class="recording-dot"></div>
    <span class="recording-text">${listeningText}</span>
  `;

  bubbleElement.appendChild(recordingIndicator);

  const textContainer = document.createElement('div');
  textContainer.classList.add('recognition-text');
  bubbleElement.appendChild(textContainer);

  const container = getChatContainer();
  container.appendChild(bubbleElement);
  container.scrollTop = container.scrollHeight;
  return bubbleElement;
}

/**
 * Update recognition bubble text and (optionally) mark as final.
 * @param {HTMLElement} bubble
 * @param {string} text
 * @param {boolean} isFinal
 */
export function updateRecognitionBubble(bubble, text, isFinal = false) {
  const textContainer = bubble.querySelector('.recognition-text');
  if (!textContainer) return;

  textContainer.textContent = text;
  if (isFinal) {
    bubble.classList.add('final');
    const indicator = bubble.querySelector('.recording-indicator');
    if (indicator) indicator.style.display = 'none';
  }
}

/**
 * Fade-out and remove bubble from DOM.
 * @param {HTMLElement} bubble
 */
export function removeRecognitionBubble(bubble) {
  if (!bubble || !bubble.parentNode) return;
  bubble.classList.add('fade-out');
  setTimeout(() => {
    if (bubble.parentNode) bubble.parentNode.removeChild(bubble);
  }, 300);
} 