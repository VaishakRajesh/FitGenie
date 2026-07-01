/**
 * FitGenie AI - Frontend Application Logic
 * Handles all client-side interactions, API calls, and UI updates
 */

// ============================================================
// DOM REFERENCES (cached for performance)
// ============================================================
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const pageTitle = document.getElementById('pageTitle');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatStatus = document.getElementById('chatStatus');
const sendBtn = document.getElementById('sendBtn');

// ============================================================
// SIDEBAR TOGGLE (Mobile Responsive)
// ============================================================
function toggleSidebar() {
    sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function (event) {
    if (window.innerWidth <= 768) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnHamburger = event.target.classList.contains('hamburger');
        if (!isClickInsideSidebar && !isClickOnHamburger && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    }
});

// ============================================================
// SECTION NAVIGATION
// ============================================================
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show the target section
    const targetSection = document.getElementById(`section-${sectionName}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update sidebar active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeNav = document.querySelector(`.nav-item[onclick*="${sectionName}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }

    // Update page title
    const sectionTitles = {
        'dashboard': 'Dashboard',
        'profile': 'My Profile',
        'bmi': 'BMI Calculator',
        'chat': 'AI Chat',
        'history': 'Chat History',
        'documents': 'Documents'
    };
    pageTitle.textContent = sectionTitles[sectionName] || 'Dashboard';

    // Load chat history when history section is shown
    if (sectionName === 'history') {
        loadHistory();
    }

    // Close sidebar on mobile after navigation
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('open');
    }
}

// ============================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================================
// PROFILE MANAGEMENT
// ============================================================

/**
 * Save user fitness profile via AJAX
 * Called when profile form is submitted
 */
document.addEventListener('DOMContentLoaded', function () {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Collect form data
            const formData = {
                age: parseInt(document.getElementById('age').value) || null,
                height: parseFloat(document.getElementById('height').value) || null,
                weight: parseFloat(document.getElementById('weight').value) || null,
                gender: document.getElementById('gender').value,
                goal: document.getElementById('goal').value,
                fitness_level: document.getElementById('fitness_level').value,
                medical_condition: document.getElementById('medical_condition').value
            };

            try {
                const response = await fetch('/save-profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    showToast('Profile saved successfully!', 'success');
                    // Refresh dashboard stats after a short delay
                    setTimeout(() => showSection('dashboard'), 500);
                    // Reload page to reflect changes
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast(data.message || 'Error saving profile', 'error');
                }
            } catch (error) {
                showToast('Network error. Please try again.', 'error');
                console.error('Profile save error:', error);
            }
        });
    }
});

// ============================================================
// BMI CALCULATOR
// ============================================================

/**
 * Calculate BMI via API call
 * Displays result with category and health advice
 */
async function calculateBMI() {
    const weight = document.getElementById('bmiWeight').value;
    const height = document.getElementById('bmiHeight').value;

    if (!weight || !height) {
        showToast('Please enter both weight and height', 'error');
        return;
    }

    if (weight <= 0 || height <= 0) {
        showToast('Values must be positive numbers', 'error');
        return;
    }

    try {
        const response = await fetch('/calculate-bmi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weight: parseFloat(weight),
                height: parseFloat(height)
            })
        });

        const data = await response.json();

        if (data.success) {
            // Display the result
            const resultDiv = document.getElementById('bmiResult');
            resultDiv.style.position = 'relative';
            resultDiv.style.overflow = 'hidden';
            document.getElementById('bmiValue').textContent = data.bmi;
            document.getElementById('bmiCategory').textContent = data.category;
            document.getElementById('bmiAdvice').textContent = data.advice;

            // Color-code the BMI category
            const categoryEl = document.getElementById('bmiCategory');
            categoryEl.className = 'bmi-category';
            if (data.category === 'Normal') {
                categoryEl.style.background = 'rgba(81, 207, 102, 0.15)';
                categoryEl.style.color = '#51CF66';
            } else if (data.category === 'Underweight') {
                categoryEl.style.background = 'rgba(255, 184, 77, 0.15)';
                categoryEl.style.color = '#FFB84D';
            } else if (data.category === 'Overweight') {
                categoryEl.style.background = 'rgba(255, 184, 77, 0.15)';
                categoryEl.style.color = '#FFB84D';
            } else {
                categoryEl.style.background = 'rgba(255, 107, 107, 0.15)';
                categoryEl.style.color = '#FF6B6B';
            }

            resultDiv.style.display = 'block';
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            // Trigger confetti celebration
            createConfetti();

            // Animate BMI number counting up
            const bmiValueEl = document.getElementById('bmiValue');
            bmiValueEl.style.opacity = '0';
            bmiValueEl.style.transform = 'scale(0.5)';
            setTimeout(() => {
                bmiValueEl.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                bmiValueEl.style.opacity = '1';
                bmiValueEl.style.transform = 'scale(1)';
            }, 100);
        } else {
            showToast(data.message || 'BMI calculation failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
        console.error('BMI calculation error:', error);
    }
}

// Allow pressing Enter in BMI input fields to calculate
document.addEventListener('DOMContentLoaded', function () {
    const bmiWeight = document.getElementById('bmiWeight');
    const bmiHeight = document.getElementById('bmiHeight');
    if (bmiWeight && bmiHeight) {
        bmiWeight.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') calculateBMI();
        });
        bmiHeight.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') calculateBMI();
        });
    }
});

// ============================================================
// AI CHAT FUNCTIONALITY
// ============================================================

/**
 * Send a chat message suggestion (from chip buttons)
 */
function sendSuggestion(text) {
    chatInput.value = text;
    sendMessage();
}

/**
 * Send user message to AI and display response
 */
async function sendMessage() {
    const question = chatInput.value.trim();

    if (!question) {
        showToast('Please enter a question', 'error');
        return;
    }

    // Disable input and show sending state
    chatInput.disabled = true;
    sendBtn.disabled = true;
    chatStatus.textContent = '🤖 FitGenie AI is thinking...';

    // Display user message in chat
    appendMessage('user', question);
    chatInput.value = '';
    autoResize(chatInput);

    // Show typing indicator
    const typingDiv = showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        // Remove typing indicator
        typingDiv.remove();

        const data = await response.json();

        if (data.success) {
            // Display AI response
            appendMessage('bot', data.answer);
            chatStatus.textContent = '✅ Response received';
        } else {
            appendMessage('bot', 'Sorry, I encountered an error. Please try again.');
            showToast(data.message || 'Chat error', 'error');
            chatStatus.textContent = '❌ Error';
        }
    } catch (error) {
        typingDiv.remove();
        appendMessage('bot', 'Network error. Please check your connection and try again.');
        showToast('Network error', 'error');
        chatStatus.textContent = '❌ Connection error';
        console.error('Chat error:', error);
    }

    // Re-enable input
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();

    // Clear status after a delay
    setTimeout(() => {
        if (chatStatus.textContent !== '🤖 FitGenie AI is thinking...') {
            chatStatus.textContent = '';
        }
    }, 3000);
}

/**
 * Append a message to the chat window
 */
function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'bot' ? '🤖' : '🙋';

    const content = document.createElement('div');
    content.className = 'message-content';

    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = getCurrentTime();

    if (sender === 'bot') {
        // Typewriter effect for bot messages
        const p = document.createElement('p');
        content.appendChild(p);
        content.appendChild(time);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);

        // Type out the text character by character
        let charIndex = 0;
        let displayText = '';

        function typeNextChar() {
            if (charIndex < text.length) {
                displayText += text[charIndex];
                // Support basic markdown
                const formatted = displayText
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n\n/g, '</p><p>')
                    .replace(/\n/g, '<br>');
                p.innerHTML = formatted + '<span class="typing-cursor"></span>';
                charIndex++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                const delay = text[charIndex - 1] === '.' || text[charIndex - 1] === '!' || text[charIndex - 1] === '?' ? 30 : 15;
                setTimeout(typeNextChar, delay);
            } else {
                // Remove cursor
                const formatted = text
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n\n/g, '</p><p>')
                    .replace(/\n/g, '<br>');
                p.innerHTML = formatted;
            }
        }

        typeNextChar();
    } else {
        // User messages appear instantly
        const formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        content.innerHTML = `<p>${formattedText}</p>`;
        content.appendChild(time);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Show typing indicator while AI is processing
 */
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-bot message-typing';
    typingDiv.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(indicator);
    chatMessages.appendChild(typingDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

/**
 * Handle Enter key in chat input (Shift+Enter for newline)
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Auto-resize chat textarea as user types
 */
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

/**
 * Get formatted current time string
 */
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================
// CHAT HISTORY
// ============================================================

/**
 * Load chat history from the server
 */
async function loadHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<div class="empty-state"><span class="empty-icon">📜</span><p>Loading chat history...</p></div>';

    try {
        const response = await fetch('/get-history');
        const data = await response.json();

        if (data.success && data.history.length > 0) {
            historyList.innerHTML = '';

            data.history.forEach(chat => {
                const item = document.createElement('div');
                item.className = 'history-item';

                item.innerHTML = `
                    <div class="history-q">🙋 ${escapeHtml(chat.question)}</div>
                    <div class="history-a">🤖 ${escapeHtml(chat.answer.substring(0, 200))}${chat.answer.length > 200 ? '...' : ''}</div>
                    <div class="history-time">${chat.timestamp}</div>
                `;

                // Click to view full conversation in chat
                item.style.cursor = 'pointer';
                item.addEventListener('click', function () {
                    chatInput.value = chat.question;
                    showSection('chat');
                });

                historyList.appendChild(item);
            });
        } else {
            historyList.innerHTML = '<div class="empty-state"><span class="empty-icon">📜</span><p>No chat history yet. Start a conversation!</p></div>';
        }
    } catch (error) {
        historyList.innerHTML = '<div class="empty-state"><span class="empty-icon">❌</span><p>Failed to load history. Check your connection.</p></div>';
        console.error('History load error:', error);
    }
}

/**
 * Clear all chat history
 */
async function clearHistory() {
    if (!confirm('Are you sure you want to delete all chat history?')) {
        return;
    }

    try {
        const response = await fetch('/clear-history', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Chat history cleared!', 'success');
            loadHistory(); // Reload the empty state
        } else {
            showToast(data.message || 'Failed to clear history', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
        console.error('Clear history error:', error);
    }
}

// ============================================================
// DOCUMENT UPLOAD
// ============================================================

/**
 * Upload a document file for RAG processing
 */
async function uploadDocument(input) {
    const file = input.files[0];

    if (!file) return;

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showToast('File too large. Maximum size is 10MB.', 'error');
        input.value = '';
        return;
    }

    // Show upload status
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">📤 Uploading ' + file.name + '...</div>';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload-document', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            statusDiv.innerHTML = `<div class="alert alert-success">✅ ${data.message}</div>`;
            showToast('Document uploaded successfully!', 'success');
        } else {
            statusDiv.innerHTML = `<div class="alert alert-error">❌ ${data.message}</div>`;
            showToast(data.message || 'Upload failed', 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = '<div class="alert alert-error">❌ Network error. Please try again.</div>';
        showToast('Upload failed', 'error');
        console.error('Upload error:', error);
    }

    // Reset file input
    input.value = '';
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Escape HTML entities to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    console.log('💪 FitGenie AI - Frontend initialized');

    // Show dashboard section by default
    showSection('dashboard');

    // Focus chat input when switching to chat section
    const chatSection = document.getElementById('section-chat');
    if (chatSection) {
        const observer = new MutationObserver(function () {
            if (chatSection.classList.contains('active')) {
                setTimeout(() => {
                    if (chatInput) chatInput.focus();
                }, 100);
            }
        });

        observer.observe(chatSection, {
            attributes: true,
            attributeFilter: ['class']
        });
    }

    // Initialize counter animations for stat cards
    setTimeout(initCounterAnimation, 500);

    // Initialize scroll-triggered animations
    setTimeout(initScrollAnimations, 300);

    // Add fade-in animation to page sections on load
    document.querySelectorAll('.page-section.active .stat-card, .page-section.active .card').forEach((el, i) => {
        el.style.opacity = '0';
        el.style.animation = `floatUp 0.5s ease ${i * 0.1}s forwards`;
    });

    // Welcome message typing effect
    const welcomeText = document.querySelector('.welcome-text h2');
    if (welcomeText) {
        welcomeText.style.opacity = '0';
        welcomeText.style.animation = 'fadeInUp 0.8s ease 0.2s forwards';
    }

    // Animated gradient for topbar
    const topbar = document.querySelector('.topbar');
    if (topbar) {
        topbar.classList.add('animate-gradient');
    }

    console.log('✨ Advanced animations enabled');
});

// ============================================================
// SCROLL ANIMATIONS - Intersection Observer for scroll effects
// ============================================================
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-float');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    // Observe stat cards, chat previews, history items
    document.querySelectorAll('.stat-card, .chat-preview, .history-item, .auth-feature, .auth-step').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// ============================================================
// COUNTER ANIMATION - Animate numbers counting up
// ============================================================
function animateCounter(element, target, duration = 1000) {
    if (!element) return;
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * eased);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target;
        }
    }

    // Reset to 0 first
    element.textContent = '0';
    requestAnimationFrame(update);
}

function initCounterAnimation() {
    const statValues = document.querySelectorAll('.stat-value');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const value = entry.target.textContent.trim();
                const num = parseFloat(value.replace(/[^0-9.]/g, ''));
                if (!isNaN(num) && num > 0) {
                    animateCounter(entry.target, Math.round(num));
                }
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(el => {
        const val = el.textContent.trim();
        if (/^\d+$/.test(val) && parseInt(val) > 0) {
            observer.observe(el);
        }
    });
}

// ============================================================
// CONFETTI EFFECT - Celebratory animation for BMI results
// ============================================================
function createConfetti() {
    const colors = ['#6C63FF', '#00D9A6', '#FFB84D', '#FF6B6B', '#4DC9F6', '#51CF66', '#FF85D4'];
    const container = document.querySelector('.bmi-result');
    if (!container) return;

    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        const color = colors[Math.floor(Math.random() * colors.length)];
        const size = Math.random() * 8 + 4;
        const left = Math.random() * 100;
        const delay = Math.random() * 2;
        const duration = Math.random() * 2 + 1;

        confetti.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size * 1.5}px;
            background: ${color};
            border-radius: 2px;
            left: ${left}%;
            top: -10px;
            animation: confettiFall ${duration}s ease-in ${delay}s forwards;
            opacity: 0;
            transform: rotate(${Math.random() * 360}deg);
            pointer-events: none;
        `;
        container.appendChild(confetti);

        // Clean up after animation
        setTimeout(() => confetti.remove(), (duration + delay) * 1000 + 100);
    }
}

// Add confetti keyframes to the page if not already there
function ensureConfettiKeyframes() {
    if (document.getElementById('confettiKeyframes')) return;
    const style = document.createElement('style');
    style.id = 'confettiKeyframes';
    style.textContent = `
        @keyframes confettiFall {
            0% { opacity: 1; transform: translateY(0) rotate(0deg); }
            100% { opacity: 1; transform: translateY(500px) rotate(720deg); }
        }
    `;
    document.head.appendChild(style);
}

ensureConfettiKeyframes();

// ============================================================
// PARTICLE SYSTEM - Background animation for auth pages
// ============================================================
function createParticles() {
    const branding = document.querySelector('.auth-branding');
    if (!branding) return;

    // Remove existing particles first
    branding.querySelectorAll('.particle').forEach(p => p.remove());

    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 6 + 2;
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: rgba(255,255,255,${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            bottom: -10px;
            animation: particleFloat ${Math.random() * 10 + 10}s linear infinite;
            animation-delay: ${Math.random() * 5}s;
            z-index: 0;
            pointer-events: none;
        `;
        branding.appendChild(particle);
    }
}

// Initialize particles when DOM is ready
if (document.querySelector('.auth-branding')) {
    document.addEventListener('DOMContentLoaded', createParticles);
}
