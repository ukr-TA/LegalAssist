// Save this as static/js/chatbot.js
document.addEventListener('DOMContentLoaded', function() {
    const chatBody = document.querySelector('.chat-body');
    const chatInputField = document.querySelector('.chat-input-field');
    const chatSendBtn = document.querySelector('.chat-send-btn');
    
    // Initialize chat history from localStorage
    loadChatHistory();
    
    // Scroll to bottom of chat
    scrollToBottom();
    
    // Send message when clicking the send button
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', sendMessage);
    }
    
    // Send message when pressing Enter
    if (chatInputField) {
        chatInputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Select domain from sidebar
    const domainItems = document.querySelectorAll('.domain-item');
    domainItems.forEach(function(item) {
        item.addEventListener('click', function() {
            if (this.classList.contains('disabled')) {
                showToast('This domain is coming soon!');
                return;
            }
            
            // Remove active class from all items
            domainItems.forEach(function(domain) {
                domain.classList.remove('active');
            });
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Update domain title in chat header
            const domainTitle = this.querySelector('.domain-item-title').textContent;
            document.querySelector('.current-domain').textContent = domainTitle;
            
            // Clear chat history when changing domains
            if (confirm('Changing domain will clear current chat history. Continue?')) {
                clearChat();
                addBotMessage(`Welcome to the ${domainTitle} assistant! How can I help you today?`);
                saveChatHistory();
            } else {
                // If user cancels, revert to previous active domain
                this.classList.remove('active');
                const prevActive = document.querySelector('.domain-item.active');
                if (prevActive) {
                    prevActive.classList.add('active');
                }
            }
        });
    });
    
    // Toggle sidebar on mobile
    const toggleSidebarBtn = document.querySelector('.toggle-sidebar-btn');
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            const sidebar = document.querySelector('.chat-sidebar');
            sidebar.classList.toggle('active');
        });
    }
    
    function sendMessage() {
        const message = chatInputField.value.trim();
        
        if (message === '') return;
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input field
        chatInputField.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Save to chat history
        saveChatHistory();
        
        // Send to server and get response
        sendToServer(message);
    }
    
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-user';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timeString}</div>
        `;
        
        chatBody.appendChild(messageElement);
        scrollToBottom();
    }
    
    function addBotMessage(message) {
        // Remove typing indicator if exists
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-bot';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${timeString}</div>
        `;
        
        chatBody.appendChild(messageElement);
        scrollToBottom();
    }
    
    function showTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.className = 'message message-bot typing-indicator';
        
        indicatorElement.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatBody.appendChild(indicatorElement);
        scrollToBottom();
    }
    
    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    function sendToServer(message) {
        // Simulate network delay (1-2 seconds)
        const delay = Math.floor(Math.random() * 1000) + 1000;
        
        setTimeout(() => {
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                addBotMessage(data.response);
                saveChatHistory();
            })
            .catch(error => {
                console.error('Error:', error);
                addBotMessage('Sorry, I encountered an error. Please try again later.');
                saveChatHistory();
            });
        }, delay);
    }
    
    function saveChatHistory() {
        const messages = chatBody.querySelectorAll('.message');
        const history = [];
        
        messages.forEach(function(message) {
            const contentEl = message.querySelector('.message-content');
            const timeEl = message.querySelector('.message-time');
            
            if (contentEl && timeEl) {
                const content = contentEl.textContent;
                const time = timeEl.textContent;
                const isUser = message.classList.contains('message-user');
                
                history.push({
                    content: content,
                    time: time,
                    isUser: isUser
                });
            }
        });
        
        localStorage.setItem('chatHistory', JSON.stringify(history));
    }
    
    function loadChatHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
            
            history.forEach(function(message) {
                const messageElement = document.createElement('div');
                messageElement.className = message.isUser ? 'message message-user' : 'message message-bot';
                
                messageElement.innerHTML = `
                    <div class="message-content">${message.content}</div>
                    <div class="message-time">${message.time}</div>
                `;
                
                chatBody.appendChild(messageElement);
            });
            
            // If no history, add welcome message
            if (history.length === 0) {
                addBotMessage('Welcome to the LegalAssist Chatbot! How can I help you with cyber law questions today?');
                saveChatHistory();
            }
        } catch (e) {
            console.error('Error loading chat history:', e);
            // Clear potentially corrupted history
            localStorage.removeItem('chatHistory');
            addBotMessage('Welcome to the LegalAssist Chatbot! How can I help you with cyber law questions today?');
        }
    }
    
    function clearChat() {
        while (chatBody.firstChild) {
            chatBody.removeChild(chatBody.firstChild);
        }
        localStorage.removeItem('chatHistory');
    }
    
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        toast.style.color = 'white';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '9999';
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);
        
        // Hide toast after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    console.log('Chatbot.js loaded successfully');
});