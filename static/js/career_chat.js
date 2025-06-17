let messageHistory = [];
let isProcessing = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeChatForm();
    setupExampleQuestions();
});

// Initialize chat form
function initializeChatForm() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const clearChatButton = document.getElementById('clear-chat-button');
    
    if (!chatForm || !chatInput) return;
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        
        if (!message || isProcessing) return;
        
        sendMessage(message);
        chatInput.value = '';
        chatInput.focus();
    });
}

// Send a message to the AI
function sendMessage(message) {
    if (isProcessing) return;
    
    addMessageToChat('user', message);
    setProcessingState(true);
    addTypingIndicator();
    
    fetch('/api/career-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        removeTypingIndicator();
        setProcessingState(false);
        addMessageToChat('bot', data.response || "I'm sorry, I couldn't generate a response. Please try again.");
    })
    .catch(error => {
        removeTypingIndicator();
        setProcessingState(false);
        addMessageToChat('bot', "I'm sorry, there was an error processing your request. Please try again.");
        showToast('Error', error.message);
    });
}

// Manage UI state during processing
function setProcessingState(state) {
    isProcessing = state;
    const sendButton = document.getElementById('send-button');
    const clearChatButton = document.getElementById('clear-chat-button');
    
    if (sendButton) sendButton.disabled = state;
    if (clearChatButton) clearChatButton.disabled = state;
}

// Add a message to the chat
function addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}-message`;
    
    messageElement.innerHTML = formatMessageWithLinks(message);
    chatMessages.appendChild(messageElement);
    
    messageHistory.push({ sender, message });
    scrollChatToBottom();
}

// Add typing indicator
function addTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const typingIndicator = document.createElement('div');
    typingIndicator.id = 'typing-indicator';
    typingIndicator.className = 'chat-message bot-message';
    typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    chatMessages.appendChild(typingIndicator);
    scrollChatToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) typingIndicator.remove();
}

// Scroll chat to bottom
function scrollChatToBottom() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Setup example questions
function setupExampleQuestions() {
    const exampleQuestions = document.querySelectorAll('.example-question');
    
    exampleQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const questionText = this.textContent.trim();
            const chatInput = document.getElementById('chat-input');
            
            if (chatInput) {
                chatInput.value = questionText;
                chatInput.focus();
            }
        });
        
        // Optional: allow keyboard accessibility (enter key)
        question.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

// Format message with clickable links
function formatMessageWithLinks(text) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
}

// Clear chat
function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) chatMessages.innerHTML = '';
    messageHistory = [];
    addMessageToChat('bot', "Hi there! I'm your AI career assistant. How can I help you today?");
}
