// ABOUTME: Interactive functionality for design system components
// ABOUTME: Handles modals, notifications, tabs, and other dynamic behaviors

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('modal--active');
        document.body.style.overflow = 'hidden';

        // Add escape key listener
        document.addEventListener('keydown', handleModalEscape);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('modal--active');
        document.body.style.overflow = '';

        // Remove escape key listener
        document.removeEventListener('keydown', handleModalEscape);
    }
}

function handleModalEscape(event) {
    if (event.key === 'Escape') {
        const activeModal = document.querySelector('.modal.modal--active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    }
}

// Notification Functions
let notificationIdCounter = 0;

function showNotification(type) {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const id = `notification-${++notificationIdCounter}`;
    const notification = createNotificationElement(type, id);

    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        removeNotification(id);
    }, 5000);
}

function createNotificationElement(type, id) {
    const notification = document.createElement('div');
    notification.id = id;
    notification.className = `notification notification--${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ⓘ'
    };

    const titles = {
        success: 'Success!',
        error: 'Error',
        warning: 'Warning',
        info: 'Information'
    };

    const messages = {
        success: 'Your action was completed successfully.',
        error: 'Something went wrong. Please try again.',
        warning: 'Please review your input before proceeding.',
        info: 'Here\'s some helpful information for you.'
    };

    notification.innerHTML = `
        <div class="notification__icon">${icons[type]}</div>
        <div class="notification__content">
            <h4 class="notification__title">${titles[type]}</h4>
            <p class="notification__message">${messages[type]}</p>
        </div>
        <button class="notification__close" onclick="removeNotification('${id}')">&times;</button>
    `;

    return notification;
}

function removeNotification(id) {
    const notification = document.getElementById(id);
    if (notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

// Tab Functions
function switchTab(event, tabId) {
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.remove('tab-button--active');
    });

    // Add active class to clicked button
    event.target.classList.add('tab-button--active');

    // Hide all tab panes
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
        pane.classList.remove('tab-pane--active');
    });

    // Show selected tab pane
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('tab-pane--active');
    }
}

// Close notification when clicking the close button in examples
document.addEventListener('DOMContentLoaded', function() {
    const exampleNotifications = document.querySelectorAll('.notification-examples .notification__close');
    exampleNotifications.forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const notification = this.closest('.notification');
            if (notification) {
                notification.style.transform = 'translateX(100%)';
                notification.style.opacity = '0';

                setTimeout(() => {
                    notification.style.transform = '';
                    notification.style.opacity = '';
                }, 300);
            }
        });
    });

    // Add click handlers for modal overlays
    const modalOverlays = document.querySelectorAll('.modal__overlay');
    modalOverlays.forEach(overlay => {
        overlay.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    // Prevent modal content clicks from closing modal
    const modalContents = document.querySelectorAll('.modal__content');
    modalContents.forEach(content => {
        content.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });

    // Add accessibility improvements
    addAccessibilityFeatures();
});

// Accessibility Features
function addAccessibilityFeatures() {
    // Add ARIA labels to interactive elements
    const tooltipElements = document.querySelectorAll('.tooltip');
    tooltipElements.forEach(element => {
        element.setAttribute('aria-describedby', 'tooltip');
        element.setAttribute('tabindex', '0');
    });

    // Add focus management for modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');

        const closeButton = modal.querySelector('.modal__close');
        if (closeButton) {
            closeButton.setAttribute('aria-label', 'Close modal');
        }
    });

    // Add ARIA labels to tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach((button, index) => {
        button.setAttribute('role', 'tab');
        button.setAttribute('aria-selected', button.classList.contains('tab-button--active'));
        button.setAttribute('tabindex', button.classList.contains('tab-button--active') ? '0' : '-1');
    });

    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
        pane.setAttribute('role', 'tabpanel');
    });

    // Add keyboard navigation for tabs
    const tabNav = document.querySelector('.tab-nav');
    if (tabNav) {
        tabNav.setAttribute('role', 'tablist');
        tabNav.addEventListener('keydown', handleTabKeydown);
    }
}

// Keyboard navigation for tabs
function handleTabKeydown(event) {
    const tabs = event.currentTarget.querySelectorAll('.tab-button');
    const currentTab = event.target;
    const currentIndex = Array.from(tabs).indexOf(currentTab);

    let nextIndex;

    switch (event.key) {
        case 'ArrowLeft':
            event.preventDefault();
            nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
            break;
        case 'ArrowRight':
            event.preventDefault();
            nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
            break;
        case 'Home':
            event.preventDefault();
            nextIndex = 0;
            break;
        case 'End':
            event.preventDefault();
            nextIndex = tabs.length - 1;
            break;
        default:
            return;
    }

    // Update focus and activate tab
    tabs[nextIndex].focus();
    tabs[nextIndex].click();
}

// Focus management for modals
function trapFocus(modal) {
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    modal.addEventListener('keydown', function(event) {
        if (event.key === 'Tab') {
            if (event.shiftKey) {
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement.focus();
                }
            }
        }
    });

    // Focus first element when modal opens
    if (firstElement) {
        firstElement.focus();
    }
}

// Enhanced modal opening with focus management
const originalOpenModal = openModal;
openModal = function(modalId) {
    originalOpenModal(modalId);
    const modal = document.getElementById(modalId);
    if (modal) {
        trapFocus(modal);
    }
};

// Theme Management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

function initializeTheme() {
    // Check for saved theme preference or default to 'dark'
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// Chat Demo Functionality
function sendDemoMessage() {
    const input = document.getElementById('demo-chat-input');
    const messagesContainer = document.getElementById('demo-messages');
    const sendBtn = document.getElementById('demo-send-btn');

    const message = input.value.trim();
    if (!message) return;

    // Create user message
    const userMessage = createChatMessage('user', message, getCurrentTime());
    messagesContainer.appendChild(userMessage);

    // Clear input and disable send button
    input.value = '';
    sendBtn.disabled = true;

    // Show typing indicator
    const typingIndicator = createTypingIndicator();
    messagesContainer.appendChild(typingIndicator);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Simulate assistant response after 2 seconds
    setTimeout(() => {
        messagesContainer.removeChild(typingIndicator);

        const responses = [
            "That's a great question! Let me help you with that.",
            "I'd be happy to provide some guidance on that topic.",
            "Thanks for asking! Here's what I recommend...",
            "That's an interesting point. Let me break it down for you.",
            "I can definitely help with that. Here's my suggestion..."
        ];

        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        const assistantMessage = createChatMessage('assistant', randomResponse, getCurrentTime());
        messagesContainer.appendChild(assistantMessage);

        sendBtn.disabled = false;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Re-initialize Lucide icons for new messages
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }, 2000);

    // Re-initialize Lucide icons for new messages
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function createChatMessage(type, content, time) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message--${type}`;

    const avatarText = type === 'user' ? 'You' : 'AI';
    const avatarClass = type === 'assistant' ? 'chat-avatar chat-avatar--assistant' : 'chat-avatar';

    messageDiv.innerHTML = `
        <div class="${avatarClass}">${avatarText}</div>
        <div>
            <div class="chat-message__content">${content}</div>
            <div class="chat-message__time">${time}</div>
        </div>
    `;

    return messageDiv;
}

function createTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'chat-message chat-message--assistant';
    indicatorDiv.id = 'typing-indicator';

    indicatorDiv.innerHTML = `
        <div class="chat-avatar chat-avatar--assistant">AI</div>
        <div>
            <div class="chat-typing-indicator" style="margin: 0; padding: var(--space-3) var(--space-4); background-color: var(--color-surface); border-radius: var(--radius-lg);">
                <span>Assistant is typing</span>
                <div class="chat-typing-dots">
                    <div class="chat-typing-dot"></div>
                    <div class="chat-typing-dot"></div>
                    <div class="chat-typing-dot"></div>
                </div>
            </div>
        </div>
    `;

    return indicatorDiv;
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('demo-chat-input');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendDemoMessage();
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
});

// Initialize Lucide icons and theme when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme first
    initializeTheme();

    // Initialize Lucide icons if the library is available
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Add scroll handler for hero button functionality
    initializeHeroButtons();
});

// Hero button functionality
function initializeHeroButtons() {
    const exploreBtn = document.querySelector('.hero__buttons .btn--primary');
    const viewSourceBtn = document.querySelector('.hero__buttons .btn--secondary');

    if (exploreBtn) {
        exploreBtn.addEventListener('click', function() {
            // Smooth scroll to first component section
            const firstSection = document.querySelector('.section');
            if (firstSection) {
                firstSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    if (viewSourceBtn) {
        viewSourceBtn.addEventListener('click', function() {
            // This would typically link to GitHub or show source
            showNotification('info');
        });
    }
}

// Utility function to debounce events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add smooth scrolling for anchor links (if any are added in the future)
document.addEventListener('click', function(event) {
    if (event.target.matches('a[href^="#"]')) {
        event.preventDefault();
        const targetId = event.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Export functions for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        openModal,
        closeModal,
        showNotification,
        removeNotification,
        switchTab
    };
}
