// Medical Advisory Chat Interface

class MedicalChat {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        this.initializeChat();
    }
    
    initializeChat() {
        // Set up form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Handle Ctrl+Enter for quick send
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        // Scroll to bottom on load
        this.scrollToBottom();
        
        // Handle URL parameters for chat type
        this.handleUrlParameters();
    }
    
    handleUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const chatType = urlParams.get('type');
        
        if (chatType) {
            const chatTypeSelect = document.getElementById('chatType');
            if (chatTypeSelect) {
                chatTypeSelect.value = chatType;
                
                // Set appropriate placeholder based on type
                const placeholders = {
                    symptom: 'Describe your symptoms in detail...',
                    exercise: 'Ask about exercises or rehabilitation...',
                    followup: 'Questions about your treatment or recovery...',
                    general: 'Ask any health-related question...'
                };
                
                this.messageInput.placeholder = placeholders[chatType] || this.messageInput.placeholder;
            }
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        const chatType = document.getElementById('chatType').value;
        const model = document.getElementById('aiModel').value;

        console.log(`Sending message: "${message}" with type: "${chatType}" and model: "${model}"`);
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable form
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.setLoading(true);
        
        try {
            // Show typing indicator
            this.showTypingIndicator();
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    type: chatType,
                    model: model
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.addMessage(`Sorry, I encountered an error: ${data.error}`, 'bot', 'error');
            } else {
                this.addMessage(data.response, 'bot', 'success', model);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage(
                'I apologize, but I\'m experiencing technical difficulties. Please try again or consult a healthcare provider for immediate assistance.',
                'bot',
                'error'
            );
        } finally {
            this.hideTypingIndicator();
            this.setLoading(false);
            this.scrollToBottom();
        }
    }
    
    addMessage(content, sender, type = 'normal', model = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-item ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.escapeHtml(content)}
                    </div>
                    <div class="message-time">${currentTime}</div>
                </div>
                <div class="message-avatar">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            const modelBadge = model ? `<span class="badge bg-secondary ms-1">${model}</span>` : '';
            const iconClass = type === 'error' ? 'fas fa-exclamation-triangle text-warning' : 'fas fa-robot';
            
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="${iconClass}"></i>
                </div>
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.formatMedicalResponse(content)}
                    </div>
                    <div class="message-time">
                        ${currentTime}
                        ${modelBadge}
                    </div>
                </div>
            `;
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMedicalResponse(content) {
        // Format the medical response for better readability
        let formatted = this.escapeHtml(content);
        
        // Convert line breaks to HTML
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Format medical disclaimer
        formatted = formatted.replace(
            /\*\*IMPORTANT MEDICAL DISCLAIMER:\*\*(.*?)(?=<br><br>|$)/gi,
            '<div class="alert alert-warning mt-2 mb-0"><i class="fas fa-exclamation-triangle me-2"></i><strong>IMPORTANT MEDICAL DISCLAIMER:</strong>$1</div>'
        );
        
        // Format bold sections
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format lists
        formatted = formatted.replace(/^• (.*?)(<br>|$)/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul class="mt-2 mb-2">$1</ul>');
        
        // Format triage levels with appropriate colors
        formatted = formatted.replace(
            /\*\*Triage Level:\*\* (URGENT)/gi,
            '<span class="badge bg-danger fs-6">⚠️ $1</span>'
        );
        formatted = formatted.replace(
            /\*\*Triage Level:\*\* (MONITOR)/gi,
            '<span class="badge bg-warning text-dark fs-6">👁️ $1</span>'
        );
        formatted = formatted.replace(
            /\*\*Triage Level:\*\* (MILD)/gi,
            '<span class="badge bg-success fs-6">✅ $1</span>'
        );
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    setLoading(loading) {
        this.sendBtn.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Utility functions for quick messages
function setQuickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.value = message;
        messageInput.focus();
        
        // Auto-resize
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.medicalChat = new MedicalChat();
    
    // Add emergency contact button to navigation if not exists
    addEmergencyButton();
});

function addEmergencyButton() {
    const navbar = document.querySelector('.navbar-nav.me-auto');
    if (navbar && !document.getElementById('emergencyBtn')) {
        const emergencyLi = document.createElement('li');
        emergencyLi.className = 'nav-item';
        emergencyLi.innerHTML = `
            <a class="nav-link text-danger" href="#" id="emergencyBtn" onclick="showEmergencyInfo()">
                <i class="fas fa-exclamation-triangle me-1"></i>Emergency
            </a>
        `;
        navbar.appendChild(emergencyLi);
    }
}

function showEmergencyInfo() {
    const modal = new bootstrap.Modal(document.createElement('div'));
    modal._element.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i>Medical Emergency
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-3">
                        <i class="fas fa-phone fa-3x text-danger mb-3"></i>
                        <h4>If this is a medical emergency</h4>
                        <p class="lead">Do not use this chatbot</p>
                    </div>
                    <div class="alert alert-danger">
                        <h6>Call Emergency Services Immediately:</h6>
                        <ul class="mb-0">
                            <li><strong>United States:</strong> 911</li>
                            <li><strong>United Kingdom:</strong> 999</li>
                            <li><strong>European Union:</strong> 112</li>
                            <li><strong>Australia:</strong> 000</li>
                        </ul>
                    </div>
                    <p class="small text-muted">
                        Or go directly to your nearest emergency room.
                        This chatbot is for informational purposes only and cannot replace emergency medical care.
                    </p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">I Understand</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal._element);
    modal.show();
    
    // Clean up modal after hiding
    modal._element.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal._element);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + N for new message
    if (e.altKey && e.key === 'n') {
        e.preventDefault();
        document.getElementById('messageInput').focus();
    }
    
    // Esc to cancel typing
    if (e.key === 'Escape') {
        const messageInput = document.getElementById('messageInput');
        if (messageInput === document.activeElement) {
            messageInput.blur();
        }
    }
});
