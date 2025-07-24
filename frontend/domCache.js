/**
 * Cached DOM elements to avoid repeated querySelector calls.
 * Elements are lazily cached on first access.
 */
class DOMCache {
  constructor() {
    this._cache = new Map();
  }

  /**
   * Get element by ID with caching.
   * @param {string} id
   * @returns {HTMLElement|null}
   */
  getElementById(id) {
    if (this._cache.has(id)) {
      return this._cache.get(id);
    }
    const element = document.getElementById(id);
    this._cache.set(id, element);
    return element;
  }

  /**
   * Clear cache - useful for testing or dynamic content.
   */
  clearCache() {
    this._cache.clear();
  }
}

const domCache = new DOMCache();

// Commonly used elements
export const elements = {
  get chatMessages() { return domCache.getElementById('chat-messages'); },
  get chatInput() { return domCache.getElementById('chat-input'); },
  get sendButton() { return domCache.getElementById('send-button'); },
  get micButton() { return domCache.getElementById('mic-button'); },
  get voiceChatButton() { return domCache.getElementById('voice-chat-button'); },
  get languageToggle() { return domCache.getElementById('language-toggle'); },
  get currentLang() { return domCache.getElementById('current-lang'); }
};

export { domCache }; 