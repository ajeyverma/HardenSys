// Parameters Popup Functionality
// This script handles the parameters popup system for the HardenSys documentation

// Parameters data loaded from JSON files
let windowsParametersData = null;
let linuxParametersData = null;

// Load parameters data from JSON files
async function loadParametersData() {
    try {
        // Load Windows parameters
        const windowsResponse = await fetch('Assets/json/windows_tasks.json');
        windowsParametersData = await windowsResponse.json();
        
        // Load Linux parameters
        const linuxResponse = await fetch('Assets/json/linux_tasks.json');
        linuxParametersData = await linuxResponse.json();
        
        console.log('Parameters data loaded successfully');
        console.log('Windows parameters count:', windowsParametersData.length);
        console.log('Linux parameters count:', linuxParametersData.length);
        console.log('Sample Windows parameter:', windowsParametersData[0]);
        console.log('Sample Linux parameter:', linuxParametersData[0]);
    } catch (error) {
        console.error('Error loading parameters data:', error);
    }
}

// Group parameters by heading and subheading
function groupParametersByCategory(parameters) {
    const grouped = {};
    
    parameters.forEach(param => {
        const heading = param.heading;
        const subheading = param.subheading;
        
        if (!grouped[heading]) {
            grouped[heading] = {};
        }
        
        if (!grouped[heading][subheading]) {
            grouped[heading][subheading] = [];
        }
        
        grouped[heading][subheading].push({
            title: param.title,
            details: param.details
        });
    });
    
    return grouped;
}

// Get category icon based on heading
function getCategoryIcon(heading) {
    const iconMap = {
        'Account Policies': 'fas fa-cogs',
        'Local Policies': 'fas fa-user-shield',
        'Security Options': 'fas fa-lock',
        'System Settings': 'fas fa-cog',
        'Windows Defender Firewall with Advanced Security': 'fas fa-fire',
        'Advanced Audit Policy Configuration': 'fas fa-search',
        'Microsoft Defender Application Guard': 'fas fa-shield-virus',
        'Filesystem': 'fas fa-hdd',
        'Package Management': 'fas fa-box',
        'Services': 'fas fa-server',
        'Network': 'fas fa-network-wired',
        'Access Control': 'fas fa-lock',
        'User Accounts and Environment': 'fas fa-users',
        'Logging and Auditing': 'fas fa-clipboard-list',
        'System Maintenance': 'fas fa-tools'
    };
    
    return iconMap[heading] || 'fas fa-cog';
}

// Open parameters popup
function openParametersPopup(category) {
    const popup = document.getElementById('parameters-popup');
    const title = document.getElementById('popup-title');
    const body = document.getElementById('popup-body');
    
    if (!popup || !title || !body) {
        console.error('Popup elements not found');
        return;
    }
    
    // Determine which dataset to use based on category
    let parametersData = null;
    let categoryName = '';
    
    // Map category keys to actual headings
    const categoryMap = {
        'account-policies': 'Account Policies',
        'user-rights': 'Local Policies',
        'security-options': 'Security Options',
        'system-settings': 'System Settings',
        'firewall': 'Windows Defender Firewall with Advanced Security',
        'audit-policy': 'Advanced Audit Policy Configuration',
        'application-guard': 'Microsoft Defender Application Guard',
        'filesystem': 'Filesystem',
        'package-management': 'Package Management',
        'services-configuration': 'Services',
        'network-configuration': 'Network',
        'access-control': 'Access Control',
        'system-hardening': 'System Maintenance'
    };
    
    categoryName = categoryMap[category] || category;
    
    // Check if we should use Windows or Linux data
    const isLinuxCategory = ['filesystem', 'package-management', 'services-configuration', 'network-configuration', 'access-control', 'system-hardening'].includes(category);
    
    if (isLinuxCategory && linuxParametersData) {
        parametersData = linuxParametersData;
    } else if (windowsParametersData) {
        parametersData = windowsParametersData;
    }
    
    if (!parametersData) {
        console.error('Parameters data not loaded');
        return;
    }
    
    // Group parameters by category
    const groupedParams = groupParametersByCategory(parametersData);
    const categoryParams = groupedParams[categoryName];
    
    console.log('Available categories:', Object.keys(groupedParams));
    console.log('Looking for category:', categoryName);
    console.log('Found category params:', categoryParams);
    
    if (!categoryParams) {
        console.error(`Category ${categoryName} not found in parameters data`);
        return;
    }
    
    // Set title with icon
    const icon = getCategoryIcon(categoryName);
    title.innerHTML = `<i class="${icon}"></i> ${categoryName}`;
    
    // Build HTML for parameters
    let html = '<div class="parameters-list">';
    let paramCount = 0;
    
    Object.keys(categoryParams).forEach(subheading => {
        const subheadingParams = categoryParams[subheading];
        
        // Add subheading
        html += `
            <div class="parameter-subheading-section">
                <h3 class="parameter-subheading-title">${subheading}</h3>
                <div class="parameter-subheading-content">
        `;
        
        // Add parameters under this subheading
        subheadingParams.forEach(param => {
            paramCount++;
            html += `
                <div class="parameter-item">
                    <div class="parameter-number">${paramCount}</div>
                    <div class="parameter-content">
                        <h4 class="parameter-name">${param.title}</h4>
                        <p class="parameter-subheading">${param.details}</p>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    body.innerHTML = html;
    popup.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Close parameters popup
function closeParametersPopup() {
    const popup = document.getElementById('parameters-popup');
    if (popup) {
        popup.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Initialize parameters popup system
function initParametersPopup() {
    // Load parameters data when DOM is ready
    loadParametersData();
    
    // Close popup on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeParametersPopup();
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initParametersPopup);

// Make functions globally available
window.openParametersPopup = openParametersPopup;
window.closeParametersPopup = closeParametersPopup;
