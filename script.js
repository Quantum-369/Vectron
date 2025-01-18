const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-btn');
const errorMessage = document.getElementById('error-message');

let isProcessing = false;

function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', type);
    
    if (type === 'assistant') {
        // Parse markdown for assistant messages
        messageDiv.innerHTML = marked.parse(content);
    } else {
        // Regular text for user messages
        messageDiv.textContent = content;
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('visible');
    setTimeout(() => {
        errorMessage.classList.remove('visible');
    }, 5000);
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('typing-indicator');
    indicator.id = 'typing-indicator';
    indicator.textContent = 'Assistant is typing...';
    chatBox.appendChild(indicator);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function addStatusMessage(message, isTemporary = false) {
    const statusDiv = document.createElement('div');
    statusDiv.classList.add('message', 'assistant', 'status-message');
    statusDiv.innerHTML = marked.parse(message);
    chatBox.appendChild(statusDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (isTemporary) {
        setTimeout(() => {
            statusDiv.remove();
        }, 5000);
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isProcessing) return;

    isProcessing = true;
    sendButton.disabled = true;
    userInput.value = '';

    try {
        // Add user message
        addMessage(message, 'user');

        // If it's a URL, show initial processing message
        if (message.startsWith('http://') || message.startsWith('https://')) {
            addStatusMessage('🔍 Processing URL...\n- Crawling webpage\n- Creating embeddings\n- Storing data');
        }

        showTypingIndicator();

        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }

        const data = await response.json();
        removeTypingIndicator();

        // Remove the processing message if it exists
        const processingMessages = document.querySelectorAll('.status-message');
        processingMessages.forEach(msg => msg.remove());

        // Add the response
        addMessage(data.response, 'assistant');

        // If URL was processed successfully, show a temporary success message
        if (data.type === 'url_processed') {
            addStatusMessage('✨ Ready for questions about the webpage content!', true);
        }

    } catch (error) {
        removeTypingIndicator();
        showError('Failed to send message. Please try again.');
        console.error('Error:', error);
    } finally {
        isProcessing = false;
        sendButton.disabled = false;
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Focus input on load
userInput.focus();