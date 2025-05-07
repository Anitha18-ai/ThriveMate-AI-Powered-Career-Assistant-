// Career Chat JavaScript

let messageHistory = [];
let isProcessing = false;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat form
    initializeChatForm();
    
    // Add example questions
    setupExampleQuestions();
});

// Initialize chat form
function initializeChatForm() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    
    if (!chatForm || !chatInput) return;
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        
        if (!message || isProcessing) return;
        
        // Send the message
        sendMessage(message);
        
        // Clear input
        chatInput.value = '';
    });
}

// Send a message to the AI
function sendMessage(message) {
    // Check if already processing
    if (isProcessing) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Set processing state
    isProcessing = true;
    
    // Show typing indicator
    addTypingIndicator();
    
    // Make API request
    fetch('/api/career-advice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Reset processing state
        isProcessing = false;
        
        // Add bot response to chat
        if (data.response) {
            addMessageToChat('bot', data.response);
        } else {
            addMessageToChat('bot', "I'm sorry, I couldn't generate a response. Please try again.");
        }
        
        // Scroll to bottom
        scrollChatToBottom();
    })
    .catch(error => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Reset processing state
        isProcessing = false;
        
        // Add error message
        addMessageToChat('bot', "I'm sorry, there was an error processing your request. Please try again.");
        
        // Show error toast
        showToast('Error', error.message);
        
        // Scroll to bottom
        scrollChatToBottom();
    });
}

// Add a message to the chat
function addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}-message`;
    
    // Format URLs in the message
    const formattedMessage = formatMessageWithLinks(message);
    
    messageElement.innerHTML = formattedMessage;
    chatMessages.appendChild(messageElement);
    
    // Add to message history
    messageHistory.push({
        sender: sender,
        message: message
    });
    
    // Scroll to bottom
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
    
    // Scroll to bottom
    scrollChatToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll chat to bottom
function scrollChatToBottom() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Setup example questions
function setupExampleQuestions() {
    const exampleQuestions = document.querySelectorAll('.example-question');
    
    exampleQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const questionText = this.textContent;
            
            // Set input value
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                chatInput.value = questionText;
                chatInput.focus();
            }
            
            // Optionally, send the message directly
            // sendMessage(questionText);
        });
    });
}

// Format message with clickable links
function formatMessageWithLinks(text) {
    // URL regex pattern
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    
    // Replace URLs with clickable links
    return text.replace(urlRegex, function(url) {
        return `<a href="${url}" target="_blank">${url}</a>`;
    });
}

// Clear chat
function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }
    
    // Reset message history
    messageHistory = [];
    
    // Add welcome message
    addMessageToChat('bot', 'Hi there! I\'m your AI career assistant. How can I help you today?');
}
