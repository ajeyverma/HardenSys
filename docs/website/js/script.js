// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Copy to clipboard functionality for code blocks
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        showNotification('Copied to clipboard!', 'success');
    }, function(err) {
        console.error('Could not copy text: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Add copy buttons to code blocks
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('.code-block, code');
    codeBlocks.forEach(block => {
        if (block.textContent.trim().length > 20) { // Only add to substantial code blocks
            const copyButton = document.createElement('button');
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.className = 'copy-button';
            copyButton.style.cssText = `
                position: absolute;
                top: 5px;
                right: 5px;
                background: #667eea;
                color: white;
                border: none;
                padding: 0.5rem;
                border-radius: 3px;
                cursor: pointer;
                font-size: 0.8rem;
            `;
            
            // Make the parent container relative
            if (block.parentElement) {
                block.parentElement.style.position = 'relative';
                block.parentElement.appendChild(copyButton);
            }
            
            copyButton.addEventListener('click', function() {
                copyToClipboard(block.textContent);
            });
        }
    });
});

// Search functionality for parameters page
function initParameterSearch() {
    const searchInput = document.getElementById('parameter-search');
    const parameterCards = document.querySelectorAll('.parameter-card');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            parameterCards.forEach(card => {
                const title = card.querySelector('h4').textContent.toLowerCase();
                const description = card.querySelector('.description').textContent.toLowerCase();
                const category = card.querySelector('.category').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || 
                    description.includes(searchTerm) || 
                    category.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', initParameterSearch);

// Tab functionality for manual setup page
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Initialize tabs when DOM is loaded
document.addEventListener('DOMContentLoaded', initTabs);

// Accordion functionality for FAQ or expandable sections
function initAccordions() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isActive = this.classList.contains('active');
            
            // Close all other accordions
            accordionHeaders.forEach(h => {
                h.classList.remove('active');
                h.nextElementSibling.style.maxHeight = null;
            });
            
            // Toggle current accordion
            if (!isActive) {
                this.classList.add('active');
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
}

// Initialize accordions when DOM is loaded
document.addEventListener('DOMContentLoaded', initAccordions);
