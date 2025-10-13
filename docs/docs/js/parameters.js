// Parameters page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initParameterSearch();
    initHeaderSearch();
    initMobileMenu();
    loadParameterData();
});

// Sample parameter data (in a real implementation, this would be loaded from an API or JSON file)
const parameterData = [
    {
        title: "Enforce password history",
        details: "Ensure 'Enforce password history' is set to '24 or more password(s)'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "enforce_password_history"
    },
    {
        title: "Maximum password age",
        details: "Ensure 'Maximum password age' is set to '90 days, but not 0'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "maximum_password_age"
    },
    {
        title: "Minimum password age",
        details: "Ensure 'Minimum password age' is set to '1 day'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "minimum_password_age"
    },
    {
        title: "Minimum password length",
        details: "Ensure 'Minimum password length' is set to '12 or more character(s)'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "minimum_password_length"
    },
    {
        title: "Password must meet complexity requirements",
        details: "Ensure 'Password must meet complexity requirements' is set to 'Enabled'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "password_complexity_requirements"
    },
    {
        title: "Store passwords using reversible encryption",
        details: "Ensure 'Store passwords using reversible encryption' is set to 'Disabled'",
        category: "Account Policies",
        subcategory: "Password Policy",
        scriptKey: "store_passwords_using_reversible_encryption"
    },
    {
        title: "Account lockout duration",
        details: "Ensure 'Account lockout duration' is set to '15 or more minute(s)'",
        category: "Account Policies",
        subcategory: "Account Lockout Policy",
        scriptKey: "account_lockout_duration"
    },
    {
        title: "Account lockout threshold",
        details: "Ensure 'Account lockout threshold' is set to '5 or fewer invalid logon attempt(s), but not 0'",
        category: "Account Policies",
        subcategory: "Account Lockout Policy",
        scriptKey: "account_lockout_threshold"
    },
    {
        title: "Allow Administrator account lockout",
        details: "Ensure 'Allow Administrator account lockout' is set to 'Enabled' (Manual)",
        category: "Account Policies",
        subcategory: "Account Lockout Policy",
        scriptKey: "allow_admin_account_lockout"
    },
    {
        title: "Limit local account use of blank passwords",
        details: "Ensure 'Accounts: Limit local account use of blank passwords to console logon only' is set to 'Enabled'",
        category: "Security Options",
        subcategory: "Accounts",
        scriptKey: "limit_blank_passwords"
    },
    {
        title: "Prompt user to change password before expiration",
        details: "Ensure 'Interactive logon: Prompt user to change password before expiration' is set to 'between 5 and 14 days'",
        category: "Security Options",
        subcategory: "Interactive logon",
        scriptKey: "prompt_password_change"
    },
    {
        title: "Do not allow storage of passwords for network authentication",
        details: "Ensure 'Network access: Do not allow storage of passwords and credentials for network authentication' is set to 'Enabled'",
        category: "Security Options",
        subcategory: "Microsoft network server",
        scriptKey: "storage_of_passwords"
    },
    {
        title: "Do not store LAN Manager hash on next password change",
        details: "Ensure 'Network security: Do not store LAN Manager hash value on next password change' is set to 'Enabled'",
        category: "Security Options",
        subcategory: "Network security",
        scriptKey: "disable_lan_manager_hash"
    }
];

// Initialize parameter search functionality
function initParameterSearch() {
    const searchInput = document.getElementById('parameter-search');
    const searchResults = document.getElementById('parameter-results');
    const searchClear = document.getElementById('search-clear');
    
    if (!searchInput || !searchResults || !searchClear) return;
    
    // Search functionality
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            searchResults.innerHTML = '';
            searchClear.style.display = 'none';
            return;
        }
        
        searchClear.style.display = 'block';
        performParameterSearch(query, searchResults);
    });
    
    // Clear search
    searchClear.addEventListener('click', function() {
        searchInput.value = '';
        searchResults.innerHTML = '';
        this.style.display = 'none';
    });
    
    // Keyboard shortcuts
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            searchResults.innerHTML = '';
            searchClear.style.display = 'none';
        }
    });
}

// Perform parameter search
function performParameterSearch(query, resultsContainer) {
    const results = parameterData.filter(parameter => {
        return parameter.title.toLowerCase().includes(query) ||
               parameter.details.toLowerCase().includes(query) ||
               parameter.category.toLowerCase().includes(query) ||
               parameter.subcategory.toLowerCase().includes(query) ||
               parameter.scriptKey.toLowerCase().includes(query);
    });
    
    // Display results
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="search-result">
                <div class="search-result-title">No parameters found</div>
                <div class="search-result-description">Try searching with different keywords</div>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = results.map(parameter => `
        <div class="search-result" onclick="showParameterDetails('${parameter.scriptKey}')">
            <div class="search-result-title">${parameter.title}</div>
            <div class="search-result-description">${parameter.details}</div>
            <div class="search-result-meta">${parameter.category} → ${parameter.subcategory}</div>
        </div>
    `).join('');
}

// Show parameter details (placeholder function)
function showParameterDetails(scriptKey) {
    const parameter = parameterData.find(p => p.scriptKey === scriptKey);
    if (parameter) {
        // In a real implementation, this would show a modal or navigate to a detailed view
        alert(`Parameter: ${parameter.title}\n\nDetails: ${parameter.details}\n\nCategory: ${parameter.category}\nSubcategory: ${parameter.subcategory}\n\nScript Key: ${parameter.scriptKey}`);
    }
}

// Load parameter data (placeholder function)
function loadParameterData() {
    // In a real implementation, this would load data from an API or JSON file
    console.log('Parameter data loaded:', parameterData.length, 'parameters');
}

// Initialize header search functionality
function initHeaderSearch() {
    const headerSearchInput = document.getElementById('header-search');
    const headerSearchClear = document.getElementById('header-search-clear');
    
    if (!headerSearchInput || !headerSearchClear) return;
    
    // Header search functionality
    headerSearchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length === 0) {
            headerSearchClear.style.display = 'none';
            return;
        }
        
        headerSearchClear.style.display = 'block';
        // In a real implementation, this would perform a global search
        console.log('Header search:', query);
    });
    
    // Clear header search
    headerSearchClear.addEventListener('click', function() {
        headerSearchInput.value = '';
        this.style.display = 'none';
    });
    
    // Keyboard shortcuts for header search
    headerSearchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            headerSearchClear.style.display = 'none';
        }
    });
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

// Export parameter data for use in other scripts
window.parameterData = parameterData;
