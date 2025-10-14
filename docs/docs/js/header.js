// Header functionality for all documentation pages

document.addEventListener('DOMContentLoaded', function() {
    initHeaderSearch();
    initMobileMenu();
    initOSSelector();
    initSidebarCollapse();
    initOSContentFilter();
});

// Initialize header search functionality
function initHeaderSearch() {
    const headerSearchInput = document.getElementById('header-search');
    const headerSearchClear = document.getElementById('header-search-clear');
    let headerSearchSuggestions = document.getElementById('header-search-suggestions');
    
    if (!headerSearchInput || !headerSearchClear) return;

    // Ensure suggestions dropdown exists and is inside the search box
    const searchBox = headerSearchInput ? headerSearchInput.closest('.search-box') : null;
    if (!headerSearchSuggestions) {
        headerSearchSuggestions = document.createElement('div');
        headerSearchSuggestions.id = 'header-search-suggestions';
    }
    if (searchBox && !searchBox.contains(headerSearchSuggestions)) {
        searchBox.appendChild(headerSearchSuggestions);
    }
    if (searchBox && getComputedStyle(searchBox).position === 'static') {
        searchBox.style.position = 'relative';
    }
    // Minimal inline safety in case page lacks CSS
    headerSearchSuggestions.style.zIndex = '1000';

    // Build searchable index from sidebar links and visible headings
    let searchIndex = buildHeaderSearchIndex();
    window.addEventListener('osChanged', () => { searchIndex = buildHeaderSearchIndex(); });
    window.addEventListener('hashchange', () => { searchIndex = buildHeaderSearchIndex(); });
    document.addEventListener('click', (e) => {
        if (!headerSearchSuggestions.contains(e.target) && e.target !== headerSearchInput) {
            hideHeaderSuggestions();
        }
    });
    
    // Header search functionality
    headerSearchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            headerSearchClear.style.display = 'none';
            hideHeaderSuggestions();
            return;
        }
        
        headerSearchClear.style.display = 'block';
        const results = searchIndex.filter(item =>
            item.title.toLowerCase().includes(query)
        ).slice(0, 8);
        renderHeaderSuggestions(results, headerSearchSuggestions);
    });
    
    // Clear header search
    headerSearchClear.addEventListener('click', function() {
        headerSearchInput.value = '';
        this.style.display = 'none';
        hideHeaderSuggestions();
    });
    
    // Keyboard shortcuts for header search
    headerSearchInput.addEventListener('keydown', function(e) {
        const visible = headerSearchSuggestions && headerSearchSuggestions.style.display !== 'none';
        if (visible && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
            e.preventDefault();
            moveHeaderSuggestionFocus(headerSearchSuggestions, e.key === 'ArrowDown' ? 1 : -1);
            return;
        }
        if (visible && e.key === 'Enter') {
            const focused = headerSearchSuggestions.querySelector('.header-suggestion.focused');
            if (focused) {
                const href = focused.getAttribute('data-href');
                if (href) window.location.href = href;
                hideHeaderSuggestions();
                return;
            }
        }
        if (e.key === 'Escape') {
            this.value = '';
            headerSearchClear.style.display = 'none';
            hideHeaderSuggestions();
        }
    });
}

function buildHeaderSearchIndex() {
    const items = [];
    // Sidebar links
    document.querySelectorAll('#docs-sidebar .nav-list a.nav-link').forEach(link => {
        const title = (link.textContent || '').trim();
        const href = link.getAttribute('href') || '';
        if (title && href) {
            items.push({ title, href });
        }
    });
    // Visible headings with ids in main content
    document.querySelectorAll('.docs-main h1[id], .docs-main h2[id], .docs-main h3[id]').forEach(h => {
        const title = (h.textContent || '').trim();
        const id = h.getAttribute('id');
        if (title && id) {
            items.push({ title, href: `#${id}` });
        }
    });
    // De-duplicate by href
    const seen = new Set();
    return items.filter(it => {
        if (seen.has(it.href)) return false;
        seen.add(it.href);
        return true;
    });
}

function renderHeaderSuggestions(results, container) {
    if (!container) return;
    if (!results || results.length === 0) {
        hideHeaderSuggestions();
        return;
    }
    container.innerHTML = results.map((r, idx) => `
        <div class="header-suggestion${idx === 0 ? ' focused' : ''}" data-href="${r.href}" style="padding: 0.5rem 0.75rem; cursor: pointer; border-top: 1px solid #f1f3f5;">
            <div style="font-weight: 600;">${r.title}</div>
            <div style="font-size: 12px; color: #6c757d;">${r.href}</div>
        </div>
    `).join('');
    container.style.display = 'block';
    Array.from(container.children).forEach(child => {
        child.addEventListener('mouseenter', () => {
            container.querySelectorAll('.header-suggestion').forEach(el => el.classList.remove('focused'));
            child.classList.add('focused');
        });
        child.addEventListener('click', () => {
            const href = child.getAttribute('data-href');
            if (href) window.location.href = href;
            hideHeaderSuggestions();
        });
    });
}

function hideHeaderSuggestions() {
    const container = document.getElementById('header-search-suggestions');
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}

function moveHeaderSuggestionFocus(container, delta) {
    const items = Array.from(container.querySelectorAll('.header-suggestion'));
    if (items.length === 0) return;
    let idx = items.findIndex(el => el.classList.contains('focused'));
    if (idx === -1) idx = 0;
    const next = (idx + delta + items.length) % items.length;
    items.forEach(el => el.classList.remove('focused'));
    items[next].classList.add('focused');
    items[next].scrollIntoView({ block: 'nearest' });
}

// Initialize mobile menu functionality
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.getElementById('docs-sidebar');
    
    if (!mobileMenuToggle || !sidebar) return;
    
    mobileMenuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(e.target) && 
            !mobileMenuToggle.contains(e.target) && 
            sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });
    
    // Close sidebar when window is resized to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('open');
        }
    });
}

// Initialize OS selector functionality
// Detect user's operating system
function detectOS() {
    const userAgent = navigator.userAgent.toLowerCase();
    const platform = navigator.platform.toLowerCase();
    
    // Check for Windows
    if (userAgent.includes('windows') || platform.includes('win')) {
        return 'windows';
    }
    
    // Check for macOS (treat as Windows since macOS option is removed)
    if (userAgent.includes('mac') || platform.includes('mac')) {
        return 'windows';
    }
    
    // Check for Linux
    if (userAgent.includes('linux') || platform.includes('linux')) {
        return 'linux';
    }
    
    // Check for mobile platforms (treat as Windows)
    if (userAgent.includes('android')) {
        return 'windows';
    }
    
    if (userAgent.includes('iphone') || userAgent.includes('ipad')) {
        return 'windows';
    }
    
    // Default fallback
    return 'windows';
}

function initOSSelector() {
    const dropdown = document.querySelector('.os-dropdown');
    const toggle = document.querySelector('.os-dropdown-toggle');
    const options = document.querySelectorAll('.os-option');
    
    if (!dropdown || !toggle || options.length === 0) return;
    
    // Check for URL parameter first
    const urlParams = new URLSearchParams(window.location.search);
    const urlOS = urlParams.get('os');
    
    // Detect OS automatically, but respect URL parameter, then saved preference
    const detectedOS = detectOS();
    const savedOS = localStorage.getItem('selectedOS');
    
    // Use URL parameter if available, then saved preference, then detected OS
    const initialOS = urlOS || savedOS || detectedOS;
    setActiveOS(initialOS);
    
    // Save the OS preference (URL parameter takes priority)
    if (urlOS) {
        localStorage.setItem('selectedOS', urlOS);
    } else if (!savedOS) {
        localStorage.setItem('selectedOS', detectedOS);
    }
    
    // Toggle dropdown
    toggle.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('open');
    });
    
    // Handle option selection
    options.forEach(option => {
        option.addEventListener('click', function(e) {
            e.stopPropagation();
            const os = this.getAttribute('data-os');
            setActiveOS(os);
            localStorage.setItem('selectedOS', os);
            dropdown.classList.remove('open');
            
            // Trigger custom event for OS change
            window.dispatchEvent(new CustomEvent('osChanged', { 
                detail: { os: os } 
            }));
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    });
    
    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dropdown.classList.remove('open');
        }
    });
}

// Set active OS option
function setActiveOS(os) {
    const options = document.querySelectorAll('.os-option');
    const currentDisplay = document.querySelector('.os-current');
    
    options.forEach(option => {
        if (option.getAttribute('data-os') === os) {
            option.classList.add('active');
            
            // Update the display
            const icon = option.querySelector('i').className;
            const text = option.querySelector('span').textContent;
            
            currentDisplay.innerHTML = `
                <i class="${icon}"></i>
                <span>${text}</span>
            `;
        } else {
            option.classList.remove('active');
        }
    });
}

// Expose setActiveOS globally for external use
window.setActiveOS = setActiveOS;

// Get current selected OS
function getCurrentOS() {
    const activeOption = document.querySelector('.os-option.active');
    return activeOption ? activeOption.getAttribute('data-os') : 'windows';
}

// Initialize sidebar collapse functionality
function initSidebarCollapse() {
    const sectionHeaders = document.querySelectorAll('.nav-section-header');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Section headers - normal expand/collapse behavior
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const section = this.parentElement;
            const isCollapsed = section.classList.contains('collapsed');
            
            if (isCollapsed) {
                section.classList.remove('collapsed');
            } else {
                section.classList.add('collapsed');
            }
        });
    });
    
    // Navigation links - accordion behavior (collapse all others)
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const currentSection = this.closest('.nav-section');
            
            // Collapse all sections first
            document.querySelectorAll('.nav-section').forEach(section => {
                section.classList.add('collapsed');
            });
            
            // Expand the section containing the clicked link
            currentSection.classList.remove('collapsed');
            
            // Save the accordion state
            setTimeout(saveSidebarStates, 100);
        });
    });
    
    // Detect page changes and apply accordion behavior
    window.addEventListener('beforeunload', function() {
        // Save current state before page change
        saveSidebarStates();
    });
    
    // Apply accordion behavior on page load
    applyAccordionBehavior();
    
    // Watch for active link changes (for same-page navigation)
    observeActiveLinkChanges();
    
    // Load saved collapse states
    loadSidebarStates();
}

// Apply accordion behavior on page load
function applyAccordionBehavior() {
    const sections = document.querySelectorAll('.nav-section');
    const currentPage = window.location.pathname;
    
    // Find which section should be expanded based on current page or active link
    let targetSection = null;
    
    // First, check for active links
    const activeLink = document.querySelector('.nav-link.active');
    if (activeLink) {
        targetSection = activeLink.closest('.nav-section');
    } else {
        // If no active link, check each section for links that match the current page
        sections.forEach(section => {
            const links = section.querySelectorAll('.nav-link');
            links.forEach(link => {
                const href = link.getAttribute('href');
                if (href && currentPage.includes(href.split('/').pop())) {
                    targetSection = section;
                }
            });
        });
    }
    
    // Collapse all sections first
    sections.forEach(section => {
        section.classList.add('collapsed');
    });
    
    // Expand the target section if found
    if (targetSection) {
        targetSection.classList.remove('collapsed');
    } else {
        // Default: expand first section if no specific page match
        sections[0].classList.remove('collapsed');
    }
}

// Watch for active link changes and apply accordion behavior
function observeActiveLinkChanges() {
    // Use MutationObserver to watch for class changes on nav links
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.classList.contains('nav-link') && target.classList.contains('active')) {
                    // Active link changed, apply accordion behavior
                    const currentSection = target.closest('.nav-section');
                    
                    // Collapse all sections first
                    document.querySelectorAll('.nav-section').forEach(section => {
                        section.classList.add('collapsed');
                    });
                    
                    // Expand the section containing the active link
                    currentSection.classList.remove('collapsed');
                }
            }
        });
    });
    
    // Observe all nav links for class changes
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        observer.observe(link, { attributes: true, attributeFilter: ['class'] });
    });
}

// Load saved sidebar collapse states
function loadSidebarStates() {
    const sections = document.querySelectorAll('.nav-section');
    const savedStates = localStorage.getItem('sidebarStates');
    
    if (savedStates) {
        const states = JSON.parse(savedStates);
        sections.forEach((section, index) => {
            if (states[index] === true) {
                section.classList.add('collapsed');
            }
        });
    } else {
        // Apply accordion behavior on first load
        applyAccordionBehavior();
    }
}

// Save sidebar collapse states
function saveSidebarStates() {
    const sections = document.querySelectorAll('.nav-section');
    const states = Array.from(sections).map(section => 
        section.classList.contains('collapsed')
    );
    localStorage.setItem('sidebarStates', JSON.stringify(states));
}

// Add event listeners to save states when sections are toggled
document.addEventListener('DOMContentLoaded', function() {
    const sectionHeaders = document.querySelectorAll('.nav-section-header');
    
    sectionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            // Save states after a short delay to allow animation to complete
            setTimeout(saveSidebarStates, 100);
        });
    });
});

// Initialize OS-specific content filtering
function initOSContentFilter() {
    // Listen for OS changes
    window.addEventListener('osChanged', function(event) {
        const selectedOS = event.detail.os;
        filterContentByOS(selectedOS);
    });
    
    // Apply initial filter based on current OS
    const currentOS = getCurrentOS();
    filterContentByOS(currentOS);
}

// Filter content based on selected OS
function filterContentByOS(os) {
    // Find all elements with OS-specific classes
    const windowsElements = document.querySelectorAll('.windows-only, .windows-specific');
    const linuxElements = document.querySelectorAll('.linux-only, .linux-specific');
    const allOSElements = document.querySelectorAll('.os-specific');
    
    // For index.html, handle the dual content approach
    const windowsContent = document.querySelector('.windows-content');
    const linuxContent = document.querySelector('.linux-content');
    
    if (windowsContent && linuxContent) {
        // Dual content approach - show/hide entire sections
        if (os === 'windows') {
            windowsContent.style.display = 'block';
            linuxContent.style.display = 'none';
            
            // Show Windows sidebar, hide Linux sidebar
            const windowsSidebar = document.querySelectorAll('.nav-section:not(.linux-sidebar)');
            const linuxSidebar = document.querySelectorAll('.linux-sidebar');
            
            windowsSidebar.forEach(section => {
                if (!section.classList.contains('linux-sidebar')) {
                    section.style.display = '';
                }
            });
            
            linuxSidebar.forEach(section => {
                section.style.display = 'none';
            });
            
        } else if (os === 'linux') {
            windowsContent.style.display = 'none';
            linuxContent.style.display = 'block';
            
            // Show Linux sidebar, hide Windows sidebar
            const windowsSidebar = document.querySelectorAll('.nav-section:not(.linux-sidebar)');
            const linuxSidebar = document.querySelectorAll('.linux-sidebar');
            
            windowsSidebar.forEach(section => {
                if (!section.classList.contains('linux-sidebar')) {
                    section.style.display = 'none';
                }
            });
            
            linuxSidebar.forEach(section => {
                section.style.display = '';
            });
        }
    } else {
        // Standard approach - show/hide individual elements
        // Hide all OS-specific elements first
        [...windowsElements, ...linuxElements, ...allOSElements].forEach(element => {
            element.style.display = 'none';
        });
        
        // Show elements based on selected OS
        if (os === 'windows') {
            windowsElements.forEach(element => {
                element.style.display = '';
            });
        } else if (os === 'linux') {
            linuxElements.forEach(element => {
                element.style.display = '';
            });
        }
        
        // Show elements that are relevant to both OS
        allOSElements.forEach(element => {
            element.style.display = '';
        });
    }
    
    // Update any OS-specific text or instructions
    updateOSText(os);
}

// Update text content based on OS
function updateOSText(os) {
    // Update command examples
    const commandElements = document.querySelectorAll('.command-example');
    commandElements.forEach(element => {
        const windowsCmd = element.getAttribute('data-windows');
        const linuxCmd = element.getAttribute('data-linux');
        
        if (os === 'windows' && windowsCmd) {
            element.textContent = windowsCmd;
        } else if (os === 'linux' && linuxCmd) {
            element.textContent = linuxCmd;
        }
    });
    
    // Update file path examples
    const pathElements = document.querySelectorAll('.path-example');
    pathElements.forEach(element => {
        const windowsPath = element.getAttribute('data-windows-path');
        const linuxPath = element.getAttribute('data-linux-path');
        
        if (os === 'windows' && windowsPath) {
            element.textContent = windowsPath;
        } else if (os === 'linux' && linuxPath) {
            element.textContent = linuxPath;
        }
    });
    
    // Update OS-specific instructions
    const instructionElements = document.querySelectorAll('.os-instruction');
    instructionElements.forEach(element => {
        const windowsInstruction = element.getAttribute('data-windows-instruction');
        const linuxInstruction = element.getAttribute('data-linux-instruction');
        
        if (os === 'windows' && windowsInstruction) {
            element.textContent = windowsInstruction;
        } else if (os === 'linux' && linuxInstruction) {
            element.textContent = linuxInstruction;
        }
    });
}
