import { supportedLanguages, audioConstraints } from './constants.js';
import { getRecognitionLanguage } from './languageManager.js';
import { createRecognitionBubble, updateRecognitionBubble, removeRecognitionBubble } from './chatUI.js';
import { 
  processVoiceChatInput, 
  setVoiceChatActive, 
  getVoiceChatActive, 
  getLastTTS, 
  similarityRatio,
  updateVoiceChatButtonState 
} from './voiceChat.js';

/**
 * Central speech recognition manager.
 * Handles both microphone and voice chat recognition.
 */
class SpeechManager {
  constructor() {
    this.recognition = null;
    this.voiceChatRecognition = null;
    this.isRecognitionActive = false;
    this.currentRecognitionBubble = null;
    this.currentVoiceChatBubble = null;
    this.voiceChatBuffer = '';
    this.voiceChatRestartTimer = null;
    this.voiceChatRestartCount = 0;
    this.maxRestartAttempts = 3;
    this.currentLangIndex = 0;
    this.isAutoLanguage = true;
    this.sessionInfo = null;
    this.onMessageSend = null;
    this.voiceChatButton = null;
    this.micButton = null;
  }

  /**
   * Initialize speech recognition.
   * @param {Object} sessionInfo - Session information
   * @param {Function} onMessageSend - Callback for sending messages
   * @param {HTMLElement} voiceChatButton - Voice chat button element
   */
  init(sessionInfo, onMessageSend, voiceChatButton, micButton) {
    this.sessionInfo = sessionInfo;
    this.onMessageSend = onMessageSend;
    this.voiceChatButton = voiceChatButton;
    this.micButton = micButton;

    if (!this._checkSpeechSupport()) return false;

    this._initMicrophoneRecognition();
    this._initVoiceChatRecognition();
    return true;
  }

  /**
   * Check if speech recognition is supported.
   */
  _checkSpeechSupport() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported in this browser.');
      return false;
    }
    this.SpeechRecognition = SpeechRecognition;
    return true;
  }

  /**
   * Initialize microphone recognition.
   */
  _initMicrophoneRecognition() {
    this.recognition = new this.SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.lang = getRecognitionLanguage(this.isAutoLanguage, this.currentLangIndex);
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 5;

    this.recognition.onresult = (event) => this._handleMicrophoneResult(event);
    this.recognition.onstart = () => this._handleMicrophoneStart();
    this.recognition.onend = () => this._handleMicrophoneEnd();
    this.recognition.onspeechend = () => this._handleMicrophoneSpeechEnd();
    this.recognition.onsoundend = () => this._handleMicrophoneSoundEnd();
    this.recognition.onnomatch = () => this._handleMicrophoneNoMatch();
    this.recognition.onerror = (event) => this._handleMicrophoneError(event);

    console.log('Microphone recognition initialized, language:', this.recognition.lang);
  }

  /**
   * Initialize voice chat recognition.
   */
  _initVoiceChatRecognition() {
    this.voiceChatRecognition = new this.SpeechRecognition();
    this.voiceChatRecognition.continuous = true;
    this.voiceChatRecognition.lang = getRecognitionLanguage(this.isAutoLanguage, this.currentLangIndex);
    this.voiceChatRecognition.interimResults = true;
    this.voiceChatRecognition.maxAlternatives = 3;

    this.voiceChatRecognition.onresult = (event) => this._handleVoiceChatResult(event);
    this.voiceChatRecognition.onstart = () => this._handleVoiceChatStart();
    this.voiceChatRecognition.onend = () => this._handleVoiceChatEnd();
    this.voiceChatRecognition.onerror = (event) => this._handleVoiceChatError(event);

    console.log('Voice chat recognition initialized, language:', this.voiceChatRecognition.lang);
  }

  /**
   * Update language settings for both recognizers.
   */
  updateLanguage(currentLangIndex, isAutoLanguage) {
    this.currentLangIndex = currentLangIndex;
    this.isAutoLanguage = isAutoLanguage;
    
    const newLang = getRecognitionLanguage(isAutoLanguage, currentLangIndex);
    
    if (this.recognition) {
      this.recognition.lang = newLang;
      console.log('Updated microphone recognition language:', newLang);
    }
    
    if (this.voiceChatRecognition) {
      this.voiceChatRecognition.lang = newLang;
      console.log('Updated voice chat recognition language:', newLang);
    }

    // Update active recognition bubbles
    this._updateActiveBubbleLanguage();
  }

  /**
   * Update language text in active recognition bubbles.
   */
  _updateActiveBubbleLanguage() {
    const activeBubbles = document.querySelectorAll('.recognition-bubble .recording-text');
    activeBubbles.forEach(text => {
      if (this.isAutoLanguage) {
        text.textContent = 'Höre zu...';
      } else {
        const selectedLang = supportedLanguages[this.currentLangIndex - 1];
        text.textContent = selectedLang.code.startsWith('de') ? 'Höre zu...' :
                          selectedLang.code.startsWith('ru') ? 'Слушаю...' :
                          'Listening...';
      }
    });
  }

  /**
   * Start microphone recognition.
   */
  async startMicrophone() {
    if (!this.recognition || this.isRecognitionActive) return false;

    try {
      // Request audio with filters
      if (!await this._requestAudioWithFilters()) {
        alert('Achtung: Echo- und Rauschunterdrückung konnten nicht aktiviert werden. Es wird empfohlen, Kopfhörer zu verwenden!');
      }
      
      console.log('Starting microphone recognition...');
      this.recognition.start();
      this._updateMicButtonState(true);
      return true;
    } catch (error) {
      console.error('Failed to start microphone recognition:', error);
      return false;
    }
  }

  /**
   * Stop microphone recognition.
   */
  stopMicrophone() {
    if (!this.recognition || !this.isRecognitionActive) return;
    
    console.log('Stopping microphone recognition...');
    this.recognition.stop();
    this._updateMicButtonState(false);
  }

  /**
   * Start voice chat.
   */
  async startVoiceChat() {
    if (!this.voiceChatRecognition || getVoiceChatActive()) return false;

    try {
      // Request audio with filters
      if (!await this._requestAudioWithFilters()) {
        alert('Achtung: Echo- und Rauschunterdrückung konnten nicht aktiviert werden. Es wird empfohlen, Kopfhörer zu verwenden!');
      }

      console.log('Starting voice chat...');
      setVoiceChatActive(true);
      this._updateVoiceChatButtonState('active');
      this.voiceChatRecognition.start();
      return true;
    } catch (error) {
      console.error('Failed to start voice chat:', error);
      setVoiceChatActive(false);
      this._updateVoiceChatButtonState('inactive');
      return false;
    }
  }

  /**
   * Stop voice chat.
   */
  stopVoiceChat() {
    if (!this.voiceChatRecognition || !getVoiceChatActive()) return;

    console.log('Stopping voice chat...');
    setVoiceChatActive(false);
    this._updateVoiceChatButtonState('inactive');
    
    try {
      this.voiceChatRecognition.stop();
    } catch (error) {
      console.error('Error stopping voice chat recognition:', error);
    }

    this._clearVoiceChatState();
  }

  /**
   * Request audio stream with filters.
   */
  async _requestAudioWithFilters() {
    if (!navigator.mediaDevices?.getUserMedia) return false;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia(audioConstraints);
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (err) {
      console.warn('Could not get microphone access with filters:', err);
      return false;
    }
  }

  /**
   * Update voice chat button state.
   */
  _updateVoiceChatButtonState(state) {
    if (this.voiceChatButton) {
      updateVoiceChatButtonState(this.voiceChatButton, state);
    }
  }

  /**
   * Update microphone button state.
   */
  _updateMicButtonState(active) {
    if (this.micButton) {
      if (active) {
        this.micButton.classList.add('active');
      } else {
        this.micButton.classList.remove('active');
      }
    }
  }

  /**
   * Clear voice chat state.
   */
  _clearVoiceChatState() {
    if (this.currentVoiceChatBubble) {
      removeRecognitionBubble(this.currentVoiceChatBubble);
      this.currentVoiceChatBubble = null;
    }
    this.voiceChatBuffer = '';
    
    if (this.voiceChatRestartTimer) {
      clearTimeout(this.voiceChatRestartTimer);
      this.voiceChatRestartTimer = null;
    }
  }

  /**
   * Restart voice chat recognition with debouncing.
   */
  _restartVoiceChatRecognition() {
    if (this.voiceChatRestartTimer) {
      clearTimeout(this.voiceChatRestartTimer);
      this.voiceChatRestartTimer = null;
    }

    if (!this.voiceChatRecognition || !getVoiceChatActive()) return;

    this.voiceChatRestartTimer = setTimeout(() => {
      if (getVoiceChatActive() && this.voiceChatRestartCount < this.maxRestartAttempts) {
        try {
          this.voiceChatRecognition.start();
          this.voiceChatRestartCount = 0;
        } catch (error) {
          console.log('Recognition restart error:', error.message);
          this.voiceChatRestartCount++;
          if (this.voiceChatRestartCount < this.maxRestartAttempts) {
            setTimeout(() => this._restartVoiceChatRecognition(), 1000);
          } else {
            console.warn('Max restart attempts reached, stopping voice chat');
            this.stopVoiceChat();
          }
        }
      }
    }, 800);
  }

  // Microphone event handlers
  _handleMicrophoneResult(event) {
    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    if (this.currentRecognitionBubble) {
      const textToShow = finalTranscript || interimTranscript;
      updateRecognitionBubble(this.currentRecognitionBubble, textToShow, !!finalTranscript);
    }

    if (finalTranscript && this.onMessageSend) {
      removeRecognitionBubble(this.currentRecognitionBubble);
      this.currentRecognitionBubble = null;
      this.onMessageSend(finalTranscript);
    }
  }

  _handleMicrophoneStart() {
    this.isRecognitionActive = true;
    this.currentRecognitionBubble = createRecognitionBubble(false, this.isAutoLanguage, this.currentLangIndex);
    console.log('Microphone recognition started');
  }

  _handleMicrophoneEnd() {
    this.isRecognitionActive = false;
    if (this.currentRecognitionBubble) {
      const textContainer = this.currentRecognitionBubble.querySelector('.recognition-text');
      if (!textContainer?.textContent.trim()) {
        removeRecognitionBubble(this.currentRecognitionBubble);
      }
      this.currentRecognitionBubble = null;
    }
    this._updateMicButtonState(false);
    console.log('Microphone recognition ended');
  }

  _handleMicrophoneSpeechEnd() {
    console.log('Speech ended, stopping microphone recognition');
    if (this.isRecognitionActive) {
      this.recognition.stop();
    }
  }

  _handleMicrophoneSoundEnd() {
    console.log('Sound ended, stopping microphone recognition');
    if (this.isRecognitionActive) {
      this.recognition.stop();
    }
  }

  _handleMicrophoneNoMatch() {
    console.log('No match, stopping microphone recognition');
    if (this.isRecognitionActive) {
      this.recognition.stop();
    }
  }

  _handleMicrophoneError(event) {
    console.error('Microphone recognition error:', event.error);
    this.isRecognitionActive = false;
    this._updateMicButtonState(false);
    if (this.currentRecognitionBubble) {
      removeRecognitionBubble(this.currentRecognitionBubble);
      this.currentRecognitionBubble = null;
    }
  }

  // Voice chat event handlers
  async _handleVoiceChatResult(event) {
    this.voiceChatRestartCount = 0;

    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript + ' ';
      } else {
        interimTranscript += transcript;
      }
    }

    // Show interim results
    if (getVoiceChatActive()) {
      if (!this.currentVoiceChatBubble && (finalTranscript || interimTranscript)) {
        this.currentVoiceChatBubble = createRecognitionBubble(true, this.isAutoLanguage, this.currentLangIndex);
      }

      if (this.currentVoiceChatBubble) {
        const currentText = this.voiceChatBuffer + (finalTranscript || interimTranscript);
        updateRecognitionBubble(this.currentVoiceChatBubble, currentText.trim(), false);
      }
    }

    // Process final result
    if (finalTranscript && getVoiceChatActive()) {
      this.voiceChatBuffer += finalTranscript;
      const fullTranscript = this.voiceChatBuffer.trim();

      // Echo cancellation filter
      if (getLastTTS()) {
        const ratio = similarityRatio(fullTranscript, getLastTTS());
        if (ratio > 0.8) {
          console.log('Ignoring TTS echo (similarity', Math.round(ratio*100)+'%):', fullTranscript);
          this.voiceChatBuffer = '';
          removeRecognitionBubble(this.currentVoiceChatBubble);
          this.currentVoiceChatBubble = null;
          return;
        }
      }

      // Process voice input
      if (fullTranscript) {
        console.log('Processing voice chat input:', fullTranscript, this.sessionInfo);
        
        if (this.currentVoiceChatBubble) {
          updateRecognitionBubble(this.currentVoiceChatBubble, fullTranscript, true);
          removeRecognitionBubble(this.currentVoiceChatBubble);
          this.currentVoiceChatBubble = null;
        }

        this.voiceChatBuffer = '';
        try {
          await processVoiceChatInput(fullTranscript, this.sessionInfo);
        } catch (error) {
          console.error('Voice chat error:', error);
          this.stopVoiceChat();
        }
      }
    }
  }

  _handleVoiceChatStart() {
    console.log('Voice Chat - начало распознавания');
    this._updateVoiceChatButtonState('listening');
  }

  _handleVoiceChatEnd() {
    console.log('Voice Chat - конец распознавания');
    this._clearVoiceChatState();

    if (getVoiceChatActive()) {
      this._restartVoiceChatRecognition();
    } else {
      this._updateVoiceChatButtonState('inactive');
    }
  }

  _handleVoiceChatError(event) {
    console.error('Voice Chat - ошибка распознавания:', event.error);

    switch (event.error) {
      case 'no-speech':
        console.log('No speech detected, continuing...');
        break;
      case 'network':
        console.error('Network error in voice recognition');
        this.stopVoiceChat();
        break;
      case 'not-allowed':
        console.error('Microphone access denied');
        this.stopVoiceChat();
        break;
      default:
        console.error('Unknown recognition error:', event.error);
        break;
    }
  }

  /**
   * Finalize voice chat after TTS completes.
   */
  finalizeVoiceChat() {
    if (getVoiceChatActive()) {
      setTimeout(() => {
        this._updateVoiceChatButtonState('listening');
        this._restartVoiceChatRecognition();
      }, 500);
    }
  }

  /**
   * Get current recognition state.
   */
  getState() {
    return {
      isRecognitionActive: this.isRecognitionActive,
      isVoiceChatActive: getVoiceChatActive(),
      currentLangIndex: this.currentLangIndex,
      isAutoLanguage: this.isAutoLanguage
    };
  }
}

// Create singleton instance
const speechManager = new SpeechManager();

export default speechManager; 