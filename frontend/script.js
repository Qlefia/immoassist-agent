import { supportedLanguages } from './constants.js';
import { toggleLanguage as toggleLanguageLogic } from './languageManager.js';
import { createSession } from './apiClient.js';
import { convertMarkdownToHtml, renderMathFormulas } from './dom.js';
import { addMessage, showTypingIndicator } from './chatUI.js';
import { sendTextMessage } from './agentClient.js';
import { elements } from './domCache.js';
import speechManager from './speechManager.js';
import { renderChart } from './chartRenderer.js';
// Удаляю строку import { renderChart } from './chartRenderer.js'; и любые другие import/export
// Остальной код не меняется, renderChart вызывается как window.renderChart или просто renderChart

// Agent Selector Module
class AgentSelector {
    constructor() {
        this.selectedAgent = null;
        this.isAutoMode = true;
        this.modal = null;
        this.agentsSelectorBtn = null;

        
        this.agentConfig = {
            property: {
                name: 'Immobiliensuche',
                description: 'Objektsuche und Standortanalyse',
                backendKey: 'property_specialist'
            },
            calculator: {
                name: 'Renditeberechnung', 
                description: 'Investitionsberechnungen und Renditeanalyse',
                backendKey: 'calculator_specialist'
            },
            knowledge: {
                name: 'Wissensdatenbank',
                description: 'Begriffe und Definitionen im Immobilienbereich', 
                backendKey: 'knowledge_specialist'
            },
            legal: {
                name: 'Rechtsinformationen',
                description: 'Gesetze und rechtliche Aspekte',
                backendKey: 'legal_specialist'
            },
            market: {
                name: 'Marktanalyse',
                description: 'Trends und Marktentwicklungen',
                backendKey: 'market_analyst'
            },
            course: {
                name: 'Investitionskurs',
                description: 'Lernmaterialien und Präsentationen',
                backendKey: 'presentation_specialist'
            }
        };
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
    }
    
    setupElements() {
        this.modal = document.getElementById('agent-selector-modal');
        this.agentsSelectorBtn = document.getElementById('agents-selector-btn');

        
        if (!this.modal || !this.agentsSelectorBtn) {
            console.error('Agent selector elements not found');
            return;
        }
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Agents selector button
        this.agentsSelectorBtn.addEventListener('click', () => this.showModal());
        
        // Auto toggle button

        
        // Modal close button
        const closeBtn = document.getElementById('modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }
        
        // Modal overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });
        
        // Specialist cards
        const specialistCards = document.querySelectorAll('.specialist-card');
        specialistCards.forEach(card => {
            card.addEventListener('click', () => {
                const agentKey = card.getAttribute('data-agent');
                this.selectAgent(agentKey);
            });
        });
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.hideModal();
            }
        });
    }
    
    showModal() {
        if (!this.modal) return;
        
        this.modal.classList.add('active');
        this.agentsSelectorBtn.classList.add('active');
        
        // Update selected state in modal
        this.updateModalSelection();
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    hideModal() {
        if (!this.modal) return;
        
        this.modal.classList.remove('active');
        this.agentsSelectorBtn.classList.remove('active');
        
        // Restore body scroll
        document.body.style.overflow = '';
    }
    
    updateModalSelection() {
        const cards = document.querySelectorAll('.specialist-card');
        cards.forEach(card => {
            card.classList.remove('selected');
            const agentKey = card.getAttribute('data-agent');
            if (agentKey === this.selectedAgent) {
                card.classList.add('selected');
            }
        });
    }
    
    selectAgent(agentKey) {
        if (!this.agentConfig[agentKey]) return;
        
        this.selectedAgent = agentKey;
        this.isAutoMode = false;
        
        // Update UI
        this.updateAgentsSelectorButton();
        this.updateAutoToggleButton();
        this.updateModalSelection();
        
        // Hide modal
        this.hideModal();
        
        console.log('Selected agent:', agentKey, this.agentConfig[agentKey]);
          }
      
      toggleAutoMode() {
          this.isAutoMode = !this.isAutoMode;
          this.updateAutoToggleButton();
          
          // Update visual feedback
          console.log('Auto mode:', this.isAutoMode ? 'enabled' : 'disabled');
      }

      updateAutoToggleButton() {

          
          if (this.isAutoMode) {
            this.selectedAgent = null;
        }
        
        this.updateAgentsSelectorButton();
        this.updateAutoToggleButton();
        
        console.log('Auto mode:', this.isAutoMode);
    }
    
    updateAgentsSelectorButton() {
        if (!this.agentsSelectorBtn) return;
        
        const text = this.agentsSelectorBtn.querySelector('.agents-text');
        if (text) {
            if (this.isAutoMode || !this.selectedAgent) {
                text.textContent = 'Agents';
            } else {
                const config = this.agentConfig[this.selectedAgent];
                text.textContent = config ? config.name : 'Agents';
            }
        }
    }
    
    updateAutoToggleButton() {

        
        if (this.isAutoMode) {

        } else {

        }
    }
    
    getPreferredAgent() {
        if (this.isAutoMode || !this.selectedAgent) {
            return null;
        }
        
        const config = this.agentConfig[this.selectedAgent];
        return config ? config.backendKey : null;
    }
    
    reset() {
        this.selectedAgent = null;
        this.isAutoMode = true;
        this.updateAgentsSelectorButton();
        this.updateAutoToggleButton();
        this.updateModalSelection();
    }
}

// Initialize agent selector
const agentSelector = new AgentSelector();

document.addEventListener('DOMContentLoaded', () => {
    const { chatMessages, chatInput, sendButton, micButton, voiceChatButton, languageToggle, currentLang } = elements;

    let userId = null;
    let sessionId = null;
    let appName = null;
    let currentLangIndex = 0;
    let isAutoLanguage = true;

    // Check KaTeX loading
    let katexLoaded = false;
    const checkKatexInterval = setInterval(() => {
        if (window.katex && window.renderMathInElement) {
            katexLoaded = true;
            clearInterval(checkKatexInterval);
            console.log('KaTeX loaded successfully');
        }
    }, 100);

    // Language management
    function updateUILanguageButton(selectedLang, isAuto) {
        if (isAuto) {
            currentLang.textContent = 'AUTO';
            currentLang.parentElement.title = 'Automatische Spracherkennung / Auto Language Detection / Автоопределение языка';
        } else if (selectedLang) {
            currentLang.textContent = selectedLang.name;
            currentLang.parentElement.title = `Sprache: ${selectedLang.full}`;
        }
    }

    function toggleLanguage() {
        const { newIndex, isAuto, selectedLang } = toggleLanguageLogic(currentLangIndex);
        currentLangIndex = newIndex;
        isAutoLanguage = isAuto;
        updateUILanguageButton(selectedLang, isAuto);
        speechManager.updateLanguage(currentLangIndex, isAutoLanguage);
    }

    // Message sending
    function setMessageInInput(text) {
        chatInput.value = text;
        sendMessage();
    }

    async function sendMessage() {
        const userInput = chatInput.value.trim();
        if (!userInput || !sessionId) return;

        addMessage(userInput, 'user-message');
        chatInput.value = '';

        const aiMessageElement = addMessage('', 'bot-message');
        aiMessageElement.pendingSources = null;
        showTypingIndicator(aiMessageElement);

        let updateTimer = null;
        const updateUI = () => {
            const raw = aiMessageElement.getAttribute('data-raw-content') || '';
            if (raw) {
                aiMessageElement.innerHTML = convertMarkdownToHtml(raw);
                renderMathFormulas(aiMessageElement);
                
                // НЕ добавляем график здесь, так как это вызывается во время загрузки
                
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        };

        try {
            // Get preferred agent from selector
            const preferredAgent = agentSelector.getPreferredAgent();
            
            await sendTextMessage(
                { appName, userId, sessionId, message: userInput, preferredAgent },
                (jsonData, isFirst) => {
                    processEventData(jsonData, aiMessageElement, isFirst);
                    if (updateTimer) clearTimeout(updateTimer);
                    updateTimer = setTimeout(updateUI, 50);
                },
            );

            if (updateTimer) clearTimeout(updateTimer);
            updateUI();

            // Финальная проверка графика после завершения потока
            const chartData = aiMessageElement.getAttribute('data-chart');
            if (chartData) {
                // Удаляем старый график, если есть
                const existingChart = aiMessageElement.querySelector('.chart-container');
                if (existingChart) {
                    existingChart.remove();
                }
                
                // Создаём новый контейнер для графика
                try {
                    const chart = JSON.parse(chartData);
                    const chartContainer = document.createElement('div');
                    chartContainer.className = 'chart-container';
                    chartContainer.style.marginTop = '16px';
                    chartContainer.style.marginBottom = '16px';
                    aiMessageElement.appendChild(chartContainer);
                    
                    // Небольшая задержка для корректной инициализации DOM
                    setTimeout(() => {
                        renderChart(chartContainer, chart);
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }, 100);
                } catch (error) {
                    console.error('Error rendering chart:', error);
                }
            }

            if (aiMessageElement.pendingSources?.length) {
                displayRagSources(aiMessageElement.pendingSources, aiMessageElement);
            }
        } catch (err) {
            console.error('Error sending message', err);
            aiMessageElement.textContent = 'Fehler beim Senden der Nachricht.';
        }
    }

    let pendingChart = null;

    // Event data processing (moved from window scope)
    function processEventData(jsonData, messageElement, isFirstResponse) {
        try {
            const parsed = JSON.parse(jsonData);

            // Сохраняем график в атрибуте элемента, чтобы добавить после текста
            if (parsed.content?.parts) {
                for (const part of parsed.content.parts) {
                    if (part.functionResponse?.response?.type === 'chart') {
                        // Сохраняем данные графика в data-атрибуте
                        messageElement.setAttribute('data-chart', JSON.stringify(part.functionResponse.response));
                    }
                }
            }

            // Обрабатываем текст
            if (parsed.content && parsed.content.parts) {
                const textParts = parsed.content.parts
                    .filter(part => part.text)
                    .map(part => part.text);

                if (textParts.length > 0) {
                    if (isFirstResponse) {
                        messageElement.innerHTML = '';
                    }

                    const currentContent = messageElement.getAttribute('data-raw-content') || '';
                    const newContent = currentContent + textParts.join(' ');
                    messageElement.setAttribute('data-raw-content', newContent);

                    messageElement.innerHTML = convertMarkdownToHtml(newContent);
                    renderMathFormulas(messageElement);
                }
            }

            // Handle sources and grounding metadata
            handleSources(parsed, messageElement);

        } catch (e) {
            console.error("Failed to parse event data:", e, jsonData);
        }
    }

    // Source handling
    function handleSources(parsed, messageElement) {
        // Extract and display sources if available
        if (parsed.actions?.stateDelta?.sources) {
            displaySources(parsed.actions.stateDelta.sources, messageElement);
        }

        // Check for grounding metadata sources (RAG)
        let groundingChunks = null;
        
        if (parsed.grounding_metadata?.grounding_chunks) {
            groundingChunks = parsed.grounding_metadata.grounding_chunks;
        } else if (parsed.content?.parts) {
            // Handle function response sources
            for (const part of parsed.content.parts) {
                if (part.functionResponse?.response) {
                    if (part.functionResponse.response.grounding_metadata?.grounding_chunks) {
                        groundingChunks = part.functionResponse.response.grounding_metadata.grounding_chunks;
                        break;
                    } else if (part.functionResponse.response.result) {
                        try {
                            let resultString = part.functionResponse.response.result;
                            let jsonString = resultString;
                            if (resultString.includes('```json')) {
                                const jsonMatch = resultString.match(/```json\s*(\{[\s\S]*?\})\s*```/);
                                if (jsonMatch) jsonString = jsonMatch[1];
                            }

                            const resultData = JSON.parse(jsonString);
                            if (resultData.sources && Array.isArray(resultData.sources)) {
                                const ragSources = resultData.sources.map((source) => ({
                                    title: extractTitleFromPath(source),
                                    url: '#',
                                    domain: 'Wissensdatenbank'
                                }));
                                if (ragSources.length > 0) {
                                    messageElement.pendingSources = ragSources;
                                }
                                return;
                            }
                        } catch (e) {
                            console.log('Could not parse function response result as JSON:', e);
                        }
                    }
                }
            }
        } else if (parsed.candidateContent?.grounding_metadata) {
            groundingChunks = parsed.candidateContent.grounding_metadata.grounding_chunks;
        }

        if (groundingChunks?.length > 0) {
            const ragSources = extractRagSources(groundingChunks);
            if (ragSources.length > 0) {
                displayRagSources(ragSources, messageElement);
            }
        }
    }

    function displaySources(sources, messageElement) {
        if (messageElement.querySelector('.sources-container')) return;
        
        const sourceList = Object.values(sources);
        if (sourceList.length === 0) return;

        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'sources-container';

        const sourcesHeader = document.createElement('div');
        sourcesHeader.className = 'sources-header';
        sourcesHeader.innerHTML = `
            <svg class="sources-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <line x1="10" y1="9" x2="8" y2="9"/>
            </svg>
            <span>Quellen</span>
        `;

        const sourcesList = document.createElement('div');
        sourcesList.className = 'sources-list';

        sourceList.forEach((source, index) => {
            const sourceItem = document.createElement('a');
            sourceItem.className = 'source-item';
            sourceItem.href = source.url;
            sourceItem.target = '_blank';
            sourceItem.rel = 'noopener noreferrer';

            sourceItem.innerHTML = `
                <div class="source-number">${index + 1}</div>
                <div class="source-content">
                    <div class="source-title">${source.title}</div>
                    <div class="source-domain">${source.domain || getDomainFromUrl(source.url)}</div>
                </div>
                <svg class="external-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15,3 21,3 21,9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
            `;

            sourcesList.appendChild(sourceItem);
        });

        sourcesContainer.appendChild(sourcesHeader);
        sourcesContainer.appendChild(sourcesList);
        messageElement.appendChild(sourcesContainer);
    }

    function displayRagSources(sources, messageElement) {
        if (messageElement.querySelector('.sources-container') || sources.length === 0) return;

        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'sources-container';

        const sourcesHeader = document.createElement('div');
        sourcesHeader.className = 'sources-header';
        sourcesHeader.innerHTML = `
            <svg class="sources-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </svg>
            <span>Quellen</span>
        `;

        const sourcesList = document.createElement('div');
        sourcesList.className = 'sources-list';

        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item rag-source';

            sourceItem.innerHTML = `
                <div class="source-number">${index + 1}</div>
                <div class="source-content">
                    <div class="source-title">${source.title}</div>
                    <div class="source-domain">${source.domain}</div>
                </div>
                <svg class="knowledge-base-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
            `;

            sourcesList.appendChild(sourceItem);
        });

        sourcesContainer.appendChild(sourcesHeader);
        sourcesContainer.appendChild(sourcesList);

        if (sources.length > 4) {
            sourcesList.classList.add('collapsed');
            const showAllButton = document.createElement('button');
            showAllButton.className = 'show-all-sources';
            showAllButton.textContent = `${sources.length - 4} weitere anzeigen`;
            showAllButton.addEventListener('click', () => {
                sourcesList.classList.remove('collapsed');
                showAllButton.style.display = 'none';
            }, { once: true });
            sourcesContainer.appendChild(showAllButton);
        }

        messageElement.appendChild(sourcesContainer);
    }

    // Helper functions
    function getDomainFromUrl(url) {
        try {
            return new URL(url).hostname.replace('www.', '');
        } catch {
            return url;
        }
    }

    function extractTitleFromPath(filePath) {
        const parts = filePath.split('/');
        const filename = parts[parts.length - 1];
        return filename.replace(/\.[^/.]+$/, "");
    }

    function extractRagSources(groundingChunks) {
        const sources = [];
        const seenUris = new Set();

        groundingChunks.forEach(chunk => {
            if (chunk.retrieved_context?.rag_chunk) {
                const ragChunk = chunk.retrieved_context.rag_chunk;
                if (ragChunk.uri && !seenUris.has(ragChunk.uri)) {
                    seenUris.add(ragChunk.uri);
                    sources.push({
                        title: extractTitleFromPath(ragChunk.uri),
                        url: '#',
                        domain: 'Wissensdatenbank'
                    });
                }
            }
        });

        return sources;
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    if (languageToggle) {
        languageToggle.addEventListener('click', toggleLanguage);
    }

    if (micButton) {
         micButton.addEventListener('click', async () => {
             const state = speechManager.getState();
             if (state.isRecognitionActive) {
                 speechManager.stopMicrophone();
             } else {
                 const success = await speechManager.startMicrophone();
             }
         });
     }

    if (voiceChatButton) {
        voiceChatButton.addEventListener('click', async () => {
            const state = speechManager.getState();
            if (state.isVoiceChatActive) {
                speechManager.stopVoiceChat();
            } else {
                await speechManager.startVoiceChat();
            }
        });
    }

    // Make functions available for voiceChat module
    window.processEventData = processEventData;
    window.displayRagSources = displayRagSources;

    // Initialize application
    async function init() {
        console.log('Initializing application...');
        try {
            const sessionData = await createSession();
            console.log('Session created:', sessionData);
            userId = sessionData.userId;
            sessionId = sessionData.id;
            appName = sessionData.appName;
            console.log('Session info set:', { userId, sessionId, appName });

            // Initialize speech manager
            const speechInitialized = speechManager.init(
                { appName, userId, sessionId }, 
                setMessageInInput, 
                voiceChatButton,
                micButton
            );

            if (!speechInitialized) {
                console.warn('Speech recognition not available');
                if (micButton) micButton.style.display = 'none';
                if (voiceChatButton) voiceChatButton.style.display = 'none';
            }

        } catch (error) {
            console.error('Failed to create session:', error);
        }
    }

    init()
        .then(() => {
            addMessage('Beschreiben Sie Ihre Aufgabe oder Ihr Anliegen', 'bot-message');
        })
        .catch((error) => {
            console.error('Failed to create session:', error);
            addMessage('Verbindung zum Server fehlgeschlagen. Bitte versuchen Sie, die Seite zu aktualisieren.', 'bot-message');
        });
}); 