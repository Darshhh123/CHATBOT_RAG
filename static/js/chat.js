// Chat functionality
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const imageInput = document.getElementById('imageInput');
const imageBtn = document.getElementById('imageBtn');
const imagePreview = document.getElementById('imagePreview');
let selectedImage = null;

// Load chat history on page load
window.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
});

// Image upload handler
imageBtn.addEventListener('click', () => {
    imageInput.click();
});

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert('Image size should be less than 10MB');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (event) => {
            selectedImage = event.target.result;
            showImagePreview(selectedImage);
        };
        reader.readAsDataURL(file);
    }
});

function showImagePreview(imageData) {
    imagePreview.innerHTML = `
        <div class="preview-container">
            <img src="${imageData}" alt="Preview" class="preview-image">
            <button type="button" class="remove-image-btn" onclick="removeImage()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

function removeImage() {
    selectedImage = null;
    imageInput.value = '';
    imagePreview.innerHTML = '';
}

// Make removeImage available globally
window.removeImage = removeImage;

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    
    if (!message && !selectedImage) {
        return;
    }
    
    // Store image and message before clearing
    const imageToSend = selectedImage;
    // Use the actual message text, or default if only image is provided
    const messageToSend = message || (selectedImage ? 'Please analyze this image' : '');
    
    // Add user message to UI (pass image as 4th parameter)
    addMessage('user', messageToSend, null, imageToSend);
    
    // Clear inputs
    messageInput.value = '';
    removeImage();
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    // Disable input
    sendBtn.disabled = true;
    messageInput.disabled = true;
    imageBtn.disabled = true;
    
    try {
        // Send message to backend with both text and image
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: messageToSend,
                image: imageToSend,
                session_id: getSessionId()
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            // Add assistant response with typing effect
            addMessageWithTyping('assistant', data.response, data.sources);
        } else {
            addMessage('assistant', `Error: ${data.error || 'Something went wrong'}`);
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        // Re-enable input
        sendBtn.disabled = false;
        messageInput.disabled = false;
        imageBtn.disabled = false;
        messageInput.focus();
    }
});

// Add message to chat
function addMessage(role, content, sources = null, image = null) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Add image if present
    if (image) {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'message-image-container';
        imageDiv.innerHTML = `<img src="${image}" alt="Uploaded image" class="message-image">`;
        contentDiv.appendChild(imageDiv);
    }
    
    // Add text content if present
    if (content) {
        // Convert markdown-like formatting to HTML
        const formattedContent = formatMessage(content);
        const textDiv = document.createElement('div');
        textDiv.innerHTML = formattedContent;
        contentDiv.appendChild(textDiv);
    }
    
    // Add source documents if available
    if (sources && sources.length > 0) {
        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'sources-container';
        
        const sourcesToggle = document.createElement('div');
        sourcesToggle.className = 'sources-toggle';
        sourcesToggle.innerHTML = '<i class="fas fa-file-alt"></i> View Source Documents';
        sourcesToggle.onclick = () => {
            const content = sourcesContainer.querySelector('.sources-content');
            content.classList.toggle('active');
            sourcesToggle.querySelector('i').classList.toggle('fa-chevron-down');
            sourcesToggle.querySelector('i').classList.toggle('fa-chevron-up');
        };
        
        const sourcesContent = document.createElement('div');
        sourcesContent.className = 'sources-content';
        
        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `
                <strong>Source ${index + 1}:</strong>
                <p>${escapeHtml(source.content || JSON.stringify(source))}</p>
            `;
            sourcesContent.appendChild(sourceItem);
        });
        
        sourcesContainer.appendChild(sourcesToggle);
        sourcesContainer.appendChild(sourcesContent);
        contentDiv.appendChild(sourcesContainer);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message content (simple markdown-like formatting)
function formatMessage(text) {
    // Escape HTML first
    let html = escapeHtml(text);
    
    // Remove markdown headers (###, ##, #)
    html = html.replace(/^#{1,6}\s+(.+)$/gm, '<strong>$1</strong>');
    
    // Convert **bold** to <strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em> (but not if it's a bullet point)
    html = html.replace(/(?<![•\-\*])\*([^*]+?)\*(?![*])/g, '<em>$1</em>');
    
    // Convert bullet points (• or -) to list items
    html = html.replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Convert line breaks to <br>
    html = html.replace(/\n/g, '<br>');
    
    // Convert numbered lists
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
    
    return html;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTypingIndicator() {
    const typingId = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = typingId;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    contentDiv.appendChild(typingDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return typingId;
}

// Remove typing indicator
function removeTypingIndicator(typingId) {
    const typingElement = document.getElementById(typingId);
    if (typingElement) {
        typingElement.remove();
    }
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.messages && data.messages.length > 0) {
            // Remove welcome message
            const welcomeMsg = chatMessages.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }
            
            // Add all messages
            data.messages.forEach(msg => {
                addMessage(msg.role, msg.content, msg.sources, msg.image);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// Clear chat
clearBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
        try {
            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Clear UI
                chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">🐾</div>
                        <h3>Welcome!</h3>
                        <p>I'm here to help with animal care questions and find veterinary hospitals in Nashik.</p>
                        <p>How can I assist you today?</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }
});

// Get or create session ID
function getSessionId() {
    let sessionId = sessionStorage.getItem('chatSessionId');
    if (!sessionId) {
        sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('chatSessionId', sessionId);
    }
    return sessionId;
}

// Add message with typing effect for AI responses
function addMessageWithTyping(role, content, sources = null) {
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Create a container for the typing text
    const textContainer = document.createElement('div');
    textContainer.className = 'typing-text-container';
    contentDiv.appendChild(textContainer);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Type out the message character by character
    let index = 0;
    const typingSpeed = 15; // milliseconds per character
    
    function typeNextChar() {
        if (index < content.length) {
            // Get the next chunk of text
            const chunk = content.substring(0, index + 1);
            const formattedContent = formatMessage(chunk);
            textContainer.innerHTML = formattedContent;
            index++;
            
            // Scroll to bottom as text appears
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Continue typing
            setTimeout(typeNextChar, typingSpeed);
        } else {
            // Typing complete, add sources if available
            if (sources && sources.length > 0) {
                addSourcesToMessage(contentDiv, sources);
            }
        }
    }
    
    // Start typing
    typeNextChar();
}

function addSourcesToMessage(contentDiv, sources) {
    const sourcesContainer = document.createElement('div');
    sourcesContainer.className = 'sources-container';
    
    const sourcesToggle = document.createElement('div');
    sourcesToggle.className = 'sources-toggle';
    sourcesToggle.innerHTML = '<i class="fas fa-file-alt"></i> View Source Documents';
    sourcesToggle.onclick = () => {
        const content = sourcesContainer.querySelector('.sources-content');
        content.classList.toggle('active');
        sourcesToggle.querySelector('i').classList.toggle('fa-chevron-down');
        sourcesToggle.querySelector('i').classList.toggle('fa-chevron-up');
    };
    
    const sourcesContent = document.createElement('div');
    sourcesContent.className = 'sources-content';
    
    sources.forEach((source, index) => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';
        sourceItem.innerHTML = `
            <strong>Source ${index + 1}:</strong>
            <p>${escapeHtml(source.content || JSON.stringify(source))}</p>
        `;
        sourcesContent.appendChild(sourceItem);
    });
    
    sourcesContainer.appendChild(sourcesToggle);
    sourcesContainer.appendChild(sourcesContent);
    contentDiv.appendChild(sourcesContainer);
}

// Auto-focus input
messageInput.focus();

