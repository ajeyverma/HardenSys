// GitHub-style Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize documentation features
    initSmoothScrolling();
    initCodeCopy();
    initMobileMenu();
    initActiveNavigation();
});

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update active navigation
                    updateActiveNavigation(this);
                }
            }
        });
    });
}

// Code copy functionality
function initCodeCopy() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const codeBlock = this.closest('.code-block');
            const codeElement = codeBlock.querySelector('pre code');
            const text = codeElement.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                // Show success feedback
                showCopySuccess(this);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                showCopyError(this);
            });
        });
    });
}

// Show copy success feedback
function showCopySuccess(button) {
    const originalIcon = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.style.color = '#28a745';
    
    setTimeout(() => {
        button.innerHTML = originalIcon;
        button.style.color = '';
    }, 2000);
}

// Show copy error feedback
function showCopyError(button) {
    const originalIcon = button.innerHTML;
    button.innerHTML = '<i class="fas fa-times"></i>';
    button.style.color = '#dc3545';
    
    setTimeout(() => {
        button.innerHTML = originalIcon;
        button.style.color = '';
    }, 2000);
}

// Mobile menu functionality
function initMobileMenu() {
    // Create mobile menu toggle button
    const mobileToggle = document.createElement('button');
    mobileToggle.className = 'mobile-menu-toggle';
    mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
    mobileToggle.setAttribute('aria-label', 'Toggle navigation menu');
    
    document.body.appendChild(mobileToggle);
    
    const sidebar = document.querySelector('.docs-sidebar');
    
    mobileToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        
        // Update button icon
        const icon = this.querySelector('i');
        if (sidebar.classList.contains('open')) {
            icon.className = 'fas fa-times';
        } else {
            icon.className = 'fas fa-bars';
        }
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('open');
                mobileToggle.querySelector('i').className = 'fas fa-bars';
            }
        }
    });
    
    // Close sidebar when window is resized to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
            mobileToggle.querySelector('i').className = 'fas fa-bars';
        }
    });
}

// Active navigation highlighting
function initActiveNavigation() {
    const sections = document.querySelectorAll('.docs-section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Intersection Observer for highlighting active section
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                const correspondingLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
                
                if (correspondingLink) {
                    updateActiveNavigation(correspondingLink);
                }
            }
        });
    }, {
        rootMargin: '-20% 0px -70% 0px'
    });
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

// Update active navigation state
function updateActiveNavigation(activeLink) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    activeLink.classList.add('active');
}



// Utility function for copying code (used by HTML)
function copyCode(button) {
    const codeBlock = button.closest('.code-block');
    const codeElement = codeBlock.querySelector('pre code');
    const text = codeElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showCopySuccess(button);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showCopyError(button);
    });
}
