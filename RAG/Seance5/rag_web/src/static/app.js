/**
 * Application JavaScript pour l'Assistant RAG Générique - Séance 5
 * Compatible avec toute documentation fournie
 */

class GenericRAGApp {
    constructor() {
        this.apiBase = '/api/rag';
        this.isLoading = false;
        this.conversationHistory = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
    }
    
    initializeElements() {
        // Elements principaux
        this.questionInput = document.getElementById('questionInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.welcomeMessage = document.getElementById('welcomeMessage');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
        
        // Options
        this.includeSources = document.getElementById('includeSources');
        this.includeConversation = document.getElementById('includeConversation');
        
        // Boutons header
        this.newConversationBtn = document.getElementById('newConversationBtn');
        this.statsBtn = document.getElementById('statsBtn');
        this.historyBtn = document.getElementById('historyBtn');
        this.clearBtn = document.getElementById('clearBtn');
        
        // Modals
        this.statsModal = document.getElementById('statsModal');
        this.historyModal = document.getElementById('historyModal');
        
        // Status
        this.ragStatus = document.getElementById('ragStatus');
        this.dbStatus = document.getElementById('dbStatus');
        
        // Sidebar
        this.exampleQuestions = document.getElementById('exampleQuestions');
        this.Modules = document.getElementById('Modules');
    }
    
    bindEvents() {
        // Envoi de message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Boutons header
        this.newConversationBtn.addEventListener('click', () => this.startNewConversation());
        this.statsBtn.addEventListener('click', () => this.showStatistics());
        this.historyBtn.addEventListener('click', () => this.showHistory());
        this.clearBtn.addEventListener('click', () => this.clearConversation());
        
        // Fermeture des modals
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.remove('show');
            });
        });
        
        // Fermeture modal en cliquant à l'extérieur
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('show');
                }
            });
        });
    }
    
    async loadInitialData() {
        try {
            // Vérifier l'état du système
            await this.checkSystemHealth();
            
            // Charger les questions d'exemple
            await this.loadExampleQuestions();
            
            // Charger les modules 
            await this.loadModules();
            
        } catch (error) {
            console.error('Erreur lors du chargement initial:', error);
            this.showToast('Erreur lors du chargement initial', 'error');
        }
    }
    
    async checkSystemHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('ragStatus', 'En ligne', 'online');
                this.updateStatus('dbStatus', 'Connectée', 'online');
            } else {
                this.updateStatus('ragStatus', 'Hors ligne', 'offline');
                this.updateStatus('dbStatus', 'Erreur', 'offline');
            }
        } catch (error) {
            this.updateStatus('ragStatus', 'Erreur', 'offline');
            this.updateStatus('dbStatus', 'Erreur', 'offline');
        }
    }
    
    updateStatus(elementId, text, status) {
        const element = document.getElementById(elementId);
        element.textContent = text;
        element.className = `status-value status-${status}`;
    }
    
    async loadExampleQuestions() {
        try {
            const response = await fetch(`${this.apiBase}/questions/examples`);
            const data = await response.json();
            
            if (data.success) {
                this.renderExampleQuestions(data.examples);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des questions d\'exemple:', error);
        }
    }
    
    renderExampleQuestions(examples) {
        this.exampleQuestions.innerHTML = '';
        
        examples.forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'example-category';
            
            const categoryTitle = document.createElement('h4');
            categoryTitle.textContent = category.category;
            categoryTitle.style.fontSize = '0.75rem';
            categoryTitle.style.fontWeight = '600';
            categoryTitle.style.color = 'var(--text-secondary)';
            categoryTitle.style.marginBottom = '0.5rem';
            categoryDiv.appendChild(categoryTitle);
            
            category.questions.forEach(question => {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'example-question';
                questionDiv.textContent = question;
                questionDiv.addEventListener('click', () => {
                    this.questionInput.value = question;
                    this.questionInput.focus();
                });
                categoryDiv.appendChild(questionDiv);
            });
            
            this.exampleQuestions.appendChild(categoryDiv);
        });
    }
    
    async loadModules() {
        try {
            const response = await fetch(`${this.apiBase}/modules`);
            const data = await response.json();
            
            if (data.success) {
                this.renderModules(data.modules);
            }
        } catch (error) {
            console.error('Erreur lors du chargement des modules:', error);
        }
    }
    
    renderModules(modules) {
        this.Modules.innerHTML = '';
        
        modules.forEach(module => {
            const moduleDiv = document.createElement('div');
            moduleDiv.className = 'module-item';
            
            const moduleName = document.createElement('div');
            moduleName.className = 'module-name';
            moduleName.textContent = module.name;
            
            const moduleDesc = document.createElement('div');
            moduleDesc.className = 'module-description';
            moduleDesc.textContent = module.description;
            
            moduleDiv.appendChild(moduleName);
            moduleDiv.appendChild(moduleDesc);
            
            moduleDiv.addEventListener('click', () => {
                const question = `Que contient le document ${module.name} ?`;
                this.questionInput.value = question;
                this.questionInput.focus();
            });
            
            this.Modules.appendChild(moduleDiv);
        });
    }
    
    async sendMessage() {
        const question = this.questionInput.value.trim();
        if (!question || this.isLoading) return;
        
        // Masquer le message de bienvenue
        this.welcomeMessage.style.display = 'none';
        
        // Ajouter le message utilisateur
        this.addMessage('user', question);
        
        // Vider l'input
        this.questionInput.value = '';
        
        // Afficher le loading
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.apiBase}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    max_sources: 5,
                    include_conversation: this.includeConversation.checked,
                    include_sources: this.includeSources.checked
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('assistant', data.response, data.metadata, data.sources);
                this.conversationHistory.push({
                    question: question,
                    response: data.response,
                    metadata: data.metadata,
                    timestamp: new Date().toISOString()
                });
                
                // Rafraîchir l'historique après l'ajout d'un message
                setTimeout(() => this.refreshConversationHistory(), 1000);
            } else {
                this.addMessage('assistant', `Erreur: ${data.error}`, null, null, true);
                this.showToast('Erreur lors du traitement de la question', 'error');
            }
            
        } catch (error) {
            console.error('Erreur lors de l\'envoi:', error);
            this.addMessage('assistant', 'Erreur de connexion au serveur', null, null, true);
            this.showToast('Erreur de connexion', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(sender, content, metadata = null, sources = null, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (sender === 'assistant' && !isError) {
            // Utiliser marked pour le rendu Markdown
            bubble.innerHTML = marked.parse(content);
        } else {
            bubble.textContent = content;
        }
        
        if (isError) {
            bubble.style.background = 'var(--error-color)';
            bubble.style.color = 'white';
        }
        
        messageContent.appendChild(bubble);
        
        // Ajouter les métadonnées
        if (metadata) {
            const metadataDiv = document.createElement('div');
            metadataDiv.className = 'message-metadata';
            metadataDiv.innerHTML = `
                <span><i class="fas fa-clock"></i> ${new Date(metadata.timestamp).toLocaleTimeString()}</span>
                <span><i class="fas fa-database"></i> ${metadata.sources_count} sources</span>
                <span><i class="fas fa-coins"></i> ${metadata.tokens_used} tokens</span>
                <span><i class="fas fa-brain"></i> ${metadata.model}</span>
            `;
            messageContent.appendChild(metadataDiv);
        }
        
        // Ajouter les sources
        if (sources && sources.length > 0 && this.includeSources.checked) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            
            const sourcesTitle = document.createElement('h4');
            sourcesTitle.innerHTML = '<i class="fas fa-book"></i> Sources consultées';
            sourcesDiv.appendChild(sourcesTitle);
            
            sources.forEach((source, index) => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                
                sourceItem.innerHTML = `
                    <div class="source-title">${index + 1}. ${source.source || source.source_document || 'Document inconnu'}</div>
                    <div class="source-details">
                        Document: ${source.source || source.source_document || 'Document inconnu'} | 
                        Similarité: ${source.similarity ? (source.similarity * 100).toFixed(1) : '0.0'}%
                        ${source.section_title ? ` | Section: ${source.section_title}` : ''}
                    </div>
                `;
                
                sourcesDiv.appendChild(sourceItem);
            });
            
            messageContent.appendChild(sourcesDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendBtn.disabled = loading;
        this.loadingOverlay.classList.toggle('show', loading);
        
        if (loading) {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }
    
    async showStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const data = await response.json();
            
            if (data.success) {
                this.renderStatistics(data.statistics);
                this.statsModal.classList.add('show');
            } else {
                this.showToast('Erreur lors du chargement des statistiques', 'error');
            }
        } catch (error) {
            console.error('Erreur statistiques:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    renderStatistics(stats) {
        const statsContent = document.getElementById('statsContent');
        
        let html = '<div class="stats-grid">';
        
        // Statistiques générales
        if (stats.conversation) {
            html += `
                <div class="stat-card">
                    <div class="stat-value">${stats.conversation.total_interactions}</div>
                    <div class="stat-label">Interactions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.conversation.total_tokens_used}</div>
                    <div class="stat-label">Tokens utilisés</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Math.round(stats.conversation.average_tokens_per_interaction)}</div>
                    <div class="stat-label">Tokens/interaction</div>
                </div>
            `;
        }
        
        if (stats.index) {
            html += `
                <div class="stat-card">
                    <div class="stat-value">${stats.index.total_documents || 0}</div>
                    <div class="stat-label">Documents indexés</div>
                </div>
            `;
        }
        
        html += '</div>';
        
        // Détails de l'index
        if (stats.index && stats.index.modules) {
            html += '<h3>Répartition par modules</h3>';
            html += '<div class="stats-grid">';
            
            Object.entries(stats.index.modules).forEach(([module, count]) => {
                html += `
                    <div class="stat-card">
                        <div class="stat-value">${count}</div>
                        <div class="stat-label">${module}</div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        statsContent.innerHTML = html;
    }
    
    async showHistory() {
        try {
            const response = await fetch(`${this.apiBase}/conversation/sessions`);
            const data = await response.json();
            
            if (data.success) {
                this.renderSessionsList(data.sessions);
                this.historyModal.classList.add('show');
            } else {
                this.showToast('Erreur lors du chargement des sessions', 'error');
            }
        } catch (error) {
            console.error('Erreur sessions:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    renderSessionsList(sessions) {
        const historyContent = document.getElementById('historyContent');
        
        if (sessions.length === 0) {
            historyContent.innerHTML = '<p>Aucune session trouvée.</p>';
            return;
        }
        
        let html = '<h3><i class="fas fa-list"></i> Sessions de conversation</h3>';
        
        sessions.forEach((session, index) => {
            const isActive = session.is_current;
            const statusIcon = isActive ? '🟢' : '💾';
            const statusText = isActive ? 'Session active' : 'Session archivée';
            
            html += `
                <div class="session-item" style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; ${isActive ? 'background-color: #f0f8ff;' : ''}">
                    <div class="session-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div class="session-title" style="font-weight: bold; color: #333;">
                            ${statusIcon} ${session.session_id}
                        </div>
                        <div class="session-status" style="font-size: 0.8em; color: #666;">
                            ${statusText}
                        </div>
                    </div>
                    
                    <div class="session-metadata" style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
                        <div><i class="fas fa-clock"></i> Début: ${new Date(session.start_time).toLocaleString()}</div>
                        <div><i class="fas fa-history"></i> Dernière activité: ${new Date(session.last_activity).toLocaleString()}</div>
                        <div><i class="fas fa-comments"></i> ${session.turns_count} interaction(s)</div>
                    </div>
                    
                    <div class="session-actions" style="display: flex; gap: 10px;">
                        ${!isActive ? `
                            <button onclick="app.loadSession('${session.session_id}')" 
                                    style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                                <i class="fas fa-upload"></i> Charger
                            </button>
                            <button onclick="app.deleteSession('${session.session_id}')" 
                                    style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                                <i class="fas fa-trash"></i> Supprimer
                            </button>
                        ` : `
                            <span style="color: #28a745; font-weight: bold;">
                                <i class="fas fa-check-circle"></i> Session en cours
                            </span>
                        `}
                    </div>
                </div>
            `;
        });
        
        historyContent.innerHTML = html;
    }
    
    async loadSession(sessionId) {
        if (!confirm(`Charger la session ${sessionId} ? La session actuelle sera sauvegardée.`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/conversation/load`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.historyModal.classList.remove('show');
                this.showToast(`Session ${sessionId} chargée`, 'success');
                
                // Charger et afficher la conversation de la session
                this.loadAndDisplaySessionConversation(sessionId);
            } else {
                this.showToast('Erreur lors du chargement de la session', 'error');
            }
        } catch (error) {
            console.error('Erreur chargement session:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    async deleteSession(sessionId) {
        if (!confirm(`⚠️ Supprimer définitivement la session ${sessionId} ?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/conversation/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Session ${sessionId} supprimée`, 'success');
                // Rafraîchir la liste des sessions
                this.showHistory();
            } else {
                this.showToast('Erreur lors de la suppression', 'error');
            }
        } catch (error) {
            console.error('Erreur suppression session:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    async refreshConversationHistory() {
        // Mise à jour automatique de l'historique
        try {
            const response = await fetch(`${this.apiBase}/conversation/history`);
            const data = await response.json();
            
            if (data.success) {
                // Mettre à jour silencieusement l'historique local
                this.conversationHistory = data.history || [];
            }
        } catch (error) {
            // Erreur silencieuse - ne pas afficher de toast
            console.warn('Impossible de rafraîchir l\'historique:', error);
        }
    }
    
    async loadAndDisplaySessionConversation(sessionId) {
        // Charger et afficher visuellement la conversation de la session
        try {
            // Récupérer l'historique de la session chargée
            const response = await fetch(`${this.apiBase}/conversation/history`);
            const data = await response.json();
            
            if (data.success && data.history && data.history.length > 0) {
                // Vider l'interface
                this.chatMessages.innerHTML = '';
                this.welcomeMessage.style.display = 'none';
                this.conversationHistory = [];
                
                // Afficher un message de reprise
                this.addSessionResumeHeader(sessionId, data.history.length);
                
                // Afficher chaque interaction de l'historique
                data.history.forEach((entry, index) => {
                    // Ajouter la question de l'utilisateur
                    this.addMessage('user', entry.question);
                    
                    // Ajouter la réponse de l'assistant avec métadonnées
                    const metadata = {
                        timestamp: entry.timestamp,
                        sources_count: entry.sources ? entry.sources.length : 0,
                        tokens_used: entry.tokens_used || entry.tokens || 0,
                        model: 'codestral-latest'
                    };
                    
                    this.addMessage('assistant', entry.response, metadata, entry.sources);
                    
                    // Ajouter à l'historique local
                    this.conversationHistory.push({
                        question: entry.question,
                        response: entry.response,
                        metadata: metadata,
                        timestamp: entry.timestamp
                    });
                });
                
                // Ajouter un message indiquant que la conversation peut continuer
                this.addContinuationMessage();
                
            } else {
                // Session vide ou pas d'historique
                this.chatMessages.innerHTML = '';
                this.welcomeMessage.style.display = 'block';
                this.conversationHistory = [];
                this.showToast('Session chargée (aucune conversation)', 'info');
            }
            
        } catch (error) {
            console.error('Erreur lors du chargement de la conversation:', error);
            this.showToast('Erreur lors du chargement de la conversation', 'error');
        }
    }
    
    addSessionResumeHeader(sessionId, messageCount) {
        // Ajouter un en-tête de reprise de session
        const headerDiv = document.createElement('div');
        headerDiv.className = 'session-resume-header';
        headerDiv.style.cssText = `
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        `;
        
        headerDiv.innerHTML = `
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">
                📚 Reprise de la conversation
            </div>
            <div style="font-size: 0.9em; opacity: 0.9;">
                Session: ${sessionId} • ${messageCount} interaction(s) récupérées
            </div>
        `;
        
        this.chatMessages.appendChild(headerDiv);
    }
    
    addContinuationMessage() {
        // Ajouter un message indiquant que la conversation peut continuer
        const continueDiv = document.createElement('div');
        continueDiv.className = 'continuation-message';
        continueDiv.style.cssText = `
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background: #e8f5e8;
            color: #2d5a2d;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
        `;
        
        continueDiv.innerHTML = `
            <div style="font-weight: bold;">
                ✅ Conversation restaurée
            </div>
            <div style="font-size: 0.9em; margin-top: 5px;">
                Vous pouvez continuer où vous vous étiez arrêté...
            </div>
        `;
        
        this.chatMessages.appendChild(continueDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    startAutoRefresh() {
        // Rafraîchir l'historique toutes les 30 secondes
        setInterval(() => {
            this.refreshConversationHistory();
        }, 30000);
    }
    
    loadHistoryItem(index) {
        // Fermer le modal
        this.historyModal.classList.remove('show');
        
        // Charger la question dans l'input
        const entry = this.conversationHistory[index];
        if (entry) {
            this.questionInput.value = entry.question;
            this.questionInput.focus();
        }
    }
    
    async clearConversation() {
        if (!confirm('Êtes-vous sûr de vouloir effacer l\'historique de conversation ?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/conversation/clear`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.chatMessages.innerHTML = '';
                this.welcomeMessage.style.display = 'block';
                this.conversationHistory = [];
                this.showToast('Historique effacé', 'success');
            } else {
                this.showToast('Erreur lors de l\'effacement', 'error');
            }
        } catch (error) {
            console.error('Erreur effacement:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    async startNewConversation() {
        if (!confirm('Démarrer une nouvelle conversation ? (L\'actuelle sera sauvegardée)')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/conversation/new`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.chatMessages.innerHTML = '';
                this.welcomeMessage.style.display = 'block';
                this.conversationHistory = [];
                
                if (data.new_session_id) {
                    this.showToast(`Nouvelle conversation démarrée: ${data.new_session_id}`, 'success');
                } else {
                    this.showToast('Nouvelle conversation démarrée', 'success');
                }
            } else {
                this.showToast('Erreur lors du démarrage de la nouvelle conversation', 'error');
            }
        } catch (error) {
            console.error('Erreur nouvelle conversation:', error);
            this.showToast('Erreur de connexion', 'error');
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        // Animer l'apparition
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Initialiser l'application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new GenericRAGApp();
});

// Gestion des erreurs globales
window.addEventListener('error', (e) => {
    console.error('Erreur globale:', e.error);
    if (app) {
        app.showToast('Une erreur inattendue s\'est produite', 'error');
    }
});

// Gestion des erreurs de promesses non gérées
window.addEventListener('unhandledrejection', (e) => {
    console.error('Promesse rejetée:', e.reason);
    if (app) {
        app.showToast('Erreur de traitement', 'error');
    }
});

