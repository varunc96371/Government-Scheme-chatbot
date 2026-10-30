/**
 * SchemeAI - Frontend Interaction Handler
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('SchemeAI: System initialized.');

    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const navLinks = document.querySelectorAll('.nav-item');
    const presetQueries = document.querySelectorAll('.preset-queries li');
    const historyLoader = document.getElementById('history-loader');

    // --- 1. Navigation Active State on Scroll (Only for Landing Page) ---
    if (navLinks.length > 0) {
        window.addEventListener('scroll', () => {
            let currentSection = '';
            const sections = document.querySelectorAll('section');
            const scrollPosition = window.scrollY + 160; // offset for sticky navbar

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    currentSection = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${currentSection}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    // --- 2. Chat Helper Utilities ---
    
    // Scroll Chat Messages Area to bottom
    const scrollToBottom = () => {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    // Append a message to the chat display
    const appendMessage = (sender, contentHTML) => {
        if (!chatMessages) return;
        
        const bubble = document.createElement('div');
        bubble.classList.add('chat-bubble', sender);

        if (sender === 'bot') {
            bubble.innerHTML = `
                <div class="chat-avatar"><img src="/static/images/robot_mascot.jpg?v=15" alt="SchemeAI Robot" class="bot-logo-img"></div>
                <div class="chat-message-content">${contentHTML}</div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="chat-message-content">${contentHTML}</div>
            `;
        }

        chatMessages.appendChild(bubble);
        scrollToBottom();
    };

    // Show/Hide Typing Indicator
    const showTypingIndicator = () => {
        if (!chatMessages) return;
        
        const indicator = document.createElement('div');
        indicator.classList.add('chat-bubble', 'bot', 'typing-indicator');
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="chat-avatar"><img src="/static/images/robot_mascot.jpg?v=15" alt="SchemeAI Robot" class="bot-logo-img"></div>
            <div class="chat-message-content">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(indicator);
        scrollToBottom();
    };

    const removeTypingIndicator = () => {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    };

    // --- 3. Chat History Initial Load (Dashboard Only) ---
    const loadChatHistory = async () => {
        if (!historyLoader) return; // Not on dashboard page
        
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            // Remove Loader indicator
            historyLoader.remove();
            
            if (response.ok && data.status === 'success') {
                const history = data.history;
                if (history && history.length > 0) {
                    history.forEach(item => {
                        appendMessage(item.sender, item.message);
                    });
                }
            } else {
                console.error('Failed to load chat history:', data.message);
                appendMessage('bot', '<p style="color: var(--accent-red); font-weight: 500;"><i class="fa-solid fa-circle-exclamation"></i> Could not load your past conversation history from database.</p>');
            }
        } catch (error) {
            if (historyLoader) historyLoader.remove();
            console.error('History load network error:', error);
            appendMessage('bot', '<p style="color: var(--accent-red); font-weight: 500;"><i class="fa-solid fa-wifi"></i> Connection failed while retrieving history from database.</p>');
        }
    };

    // Trigger history load on startup
    loadChatHistory();

    // --- 4. Form Submission (Send Message via Fetch API to Flask Backend) ---
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageText = chatInput.value.trim();
            
            // Client-side empty input validation
            if (!messageText) return;

            // Render User Message Bubble
            appendMessage('user', `<p>${escapeHTML(messageText)}</p>`);
            chatInput.value = '';

            // Render Typing Indicator while request is in flight
            showTypingIndicator();

            try {
                // Post query to Flask API endpoint
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: messageText })
                });

                // Remove typing indicator once response is received
                removeTypingIndicator();

                if (response.ok) {
                    const data = await response.json();
                    if (data.status === 'success' && data.response) {
                        // Display response inside the chatbot (contains formatted HTML cards)
                        appendMessage('bot', data.response);
                    } else {
                        // Handle server-returned validation error
                        const serverErrorMsg = data.message || 'Invalid server response.';
                        appendMessage('bot', `<p style="color: var(--accent-red); font-weight: 500;"><i class="fa-solid fa-triangle-exclamation"></i> Error: ${escapeHTML(serverErrorMsg)}</p>`);
                    }
                } else {
                    // Handle non-200 server status errors
                    const errData = await response.json().catch(() => ({}));
                    const errMsg = errData.message || `Server responded with status ${response.status}`;
                    appendMessage('bot', `<p style="color: var(--accent-red); font-weight: 500;"><i class="fa-solid fa-triangle-exclamation"></i> Sorry, I encountered an issue. (${escapeHTML(errMsg)})</p>`);
                }
            } catch (error) {
                // Handle basic network/connection failure errors
                removeTypingIndicator();
                console.error('Fetch error:', error);
                appendMessage('bot', `<p style="color: var(--accent-red); font-weight: 500;"><i class="fa-solid fa-wifi"></i> Connection failed. Make sure your local Flask development server is running and try again.</p>`);
            }
        });
    }

    // --- 5. Quick Preset Query Triggers (Sidebar Click Actions) ---
    presetQueries.forEach(item => {
        item.addEventListener('click', () => {
            const queryText = item.getAttribute('data-query');
            if (queryText && chatInput && chatForm) {
                chatInput.value = queryText;
                // Dispatch standard submit event
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // --- 6. Clear Conversation Logs (Database Clear Action) ---
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to permanently delete all conversation history from the database?')) {
                try {
                    const response = await fetch('/api/clear', { method: 'POST' });
                    const data = await response.json();
                    
                    if (response.ok && data.status === 'success') {
                        // Reset message area display
                        chatMessages.innerHTML = `
                            <div class="chat-bubble bot">
                                <div class="chat-avatar"><img src="/static/images/robot_mascot.jpg?v=15" alt="SchemeAI Robot" class="bot-logo-img"></div>
                                <div class="chat-message-content">
                                    <p>Conversation history cleared successfully in the database. Tell me about yourself to start a new recommendation query!</p>
                                </div>
                            </div>
                        `;
                    } else {
                        alert('Could not clear history: ' + (data.message || 'Unknown error.'));
                    }
                } catch (error) {
                    console.error('Error clearing conversation:', error);
                    alert('Network error: Could not connect to backend database.');
                }
            }
        });
    }

    // HTML Escaper to prevent XSS in client-side text display
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});


/* ==========================================================================
   Global Feedback Modal Controller
   ========================================================================== */

function openFeedbackModal() {
    const modal = document.getElementById('feedback-modal');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    }
}

function closeFeedbackModal() {
    const modal = document.getElementById('feedback-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => { modal.style.display = 'none'; }, 250);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Esc key close listener for feedback modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeFeedbackModal();
    });

    // Close on backdrop click
    const modalOverlay = document.getElementById('feedback-modal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeFeedbackModal();
        });
    }

    // Feedback Form AJAX Handler
    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const alertBox = document.getElementById('feedback-alert');
            const submitBtn = document.getElementById('feedback-submit-btn');
            
            const name = document.getElementById('contact-name').value.trim();
            const email = document.getElementById('contact-email').value.trim();
            const message = document.getElementById('contact-message').value.trim();

            if (!name || !email || !message) {
                if (alertBox) {
                    alertBox.className = 'auth-alert error';
                    alertBox.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> Please fill in all required fields.';
                    alertBox.style.display = 'flex';
                }
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>Sending...</span> <i class="fa-solid fa-spinner fa-spin"></i>';
            }

            try {
                const response = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, message })
                });
                
                const result = await response.json();
                if (alertBox) {
                    alertBox.style.display = 'flex';
                    if (response.ok && result.status === 'success') {
                        alertBox.className = 'auth-alert success';
                        alertBox.innerHTML = '<i class="fa-solid fa-circle-check"></i> ' + result.message;
                        this.reset();
                        setTimeout(() => closeFeedbackModal(), 2000);
                    } else {
                        alertBox.className = 'auth-alert error';
                        alertBox.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> ' + (result.message || 'Submission failed.');
                    }
                }
            } catch (error) {
                if (alertBox) {
                    alertBox.style.display = 'flex';
                    alertBox.className = 'auth-alert error';
                    alertBox.innerHTML = '<i class="fa-solid fa-wifi"></i> Could not connect to backend server. Please try again.';
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<span>Send Feedback</span> <i class="fa-solid fa-paper-plane"></i>';
                }
            }
        });
    }
});
