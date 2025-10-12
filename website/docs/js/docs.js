// GitHub-style Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize documentation features
    initSmoothScrolling();
    initCodeCopy();
    initMobileMenu();
    initActiveNavigation();
    initSearch();
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

// Search functionality
function initSearch() {
    // Create search input
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.innerHTML = `
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="docs-search" placeholder="Search documentation..." />
            <button class="search-clear" style="display: none;">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="search-results" id="search-results"></div>
    `;
    
    // Insert search after sidebar header
    const sidebarContent = document.querySelector('.sidebar-content');
    sidebarContent.insertBefore(searchContainer, sidebarContent.firstChild);
    
    const searchInput = document.getElementById('docs-search');
    const searchResults = document.getElementById('search-results');
    const searchClear = searchContainer.querySelector('.search-clear');
    
    // Search functionality
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            searchResults.innerHTML = '';
            searchClear.style.display = 'none';
            return;
        }
        
        searchClear.style.display = 'block';
        performSearch(query, searchResults);
    });
    
    // Clear search
    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchResults.innerHTML = '';
        this.style.display = 'none';
    });
    
    // Add search styles
    const searchStyles = `
        .search-container {
            padding: 0 20px 20px;
            border-bottom: 1px solid var(--sidebar-border);
            margin-bottom: 20px;
        }
        
        .search-box {
            position: relative;
            display: flex;
            align-items: center;
            background-color: var(--background-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 8px 12px;
        }
        
        .search-box i {
            color: var(--text-muted);
            margin-right: 8px;
        }
        
        .search-box input {
            flex: 1;
            border: none;
            outline: none;
            background: none;
            color: var(--text-primary);
            font-size: 14px;
        }
        
        .search-box input::placeholder {
            color: var(--text-muted);
        }
        
        .search-clear {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
            border-radius: var(--radius-sm);
        }
        
        .search-clear:hover {
            color: var(--text-primary);
        }
        
        .search-results {
            margin-top: 8px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .search-result {
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 14px;
            color: var(--text-secondary);
            transition: background-color 0.2s ease;
        }
        
        .search-result:hover {
            background-color: var(--background-tertiary);
            color: var(--text-primary);
        }
        
        .search-result-title {
            font-weight: 500;
            margin-bottom: 2px;
        }
        
        .search-result-path {
            font-size: 12px;
            color: var(--text-muted);
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = searchStyles;
    document.head.appendChild(styleSheet);
}

// Perform search
function performSearch(query, resultsContainer) {
    const sections = document.querySelectorAll('.docs-section');
    const results = [];
    
    sections.forEach(section => {
        const headings = section.querySelectorAll('h1, h2, h3, h4');
        const paragraphs = section.querySelectorAll('p');
        
        headings.forEach(heading => {
            if (heading.textContent.toLowerCase().includes(query)) {
                results.push({
                    title: heading.textContent,
                    path: getBreadcrumbPath(heading),
                    element: heading,
                    type: 'heading'
                });
            }
        });
        
        paragraphs.forEach(paragraph => {
            if (paragraph.textContent.toLowerCase().includes(query)) {
                const heading = paragraph.closest('.docs-section').querySelector('h1, h2, h3, h4');
                if (heading) {
                    results.push({
                        title: paragraph.textContent.substring(0, 100) + '...',
                        path: getBreadcrumbPath(heading),
                        element: paragraph,
                        type: 'content'
                    });
                }
            }
        });
    });
    
    // Display results
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="search-result">No results found</div>';
        return;
    }
    
    resultsContainer.innerHTML = results.map(result => `
        <div class="search-result" data-target="${result.element.id || ''}">
            <div class="search-result-title">${result.title}</div>
            <div class="search-result-path">${result.path}</div>
        </div>
    `).join('');
    
    // Add click handlers to results
    resultsContainer.querySelectorAll('.search-result').forEach(result => {
        result.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            if (targetId) {
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

// Get breadcrumb path for search results
function getBreadcrumbPath(element) {
    const section = element.closest('.docs-section');
    if (!section) return '';
    
    const sectionTitle = section.querySelector('h1, h2')?.textContent || 'Documentation';
    return sectionTitle;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('docs-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('docs-search');
        const searchResults = document.getElementById('search-results');
        const searchClear = document.querySelector('.search-clear');
        
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchResults.innerHTML = '';
            searchClear.style.display = 'none';
            searchInput.blur();
        }
    }
});

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
