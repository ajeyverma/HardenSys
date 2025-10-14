// Parameters page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initParameterSearch();
    initManualParameterSearch();
    initLinuxManualParameterSearch();
    initHeaderSearch();
    initMobileMenu();
    loadParameterData();
    bindManualCardClicks();
    initCompleteParameterTables();
});

// Parameter data loaded from JSON
let parameterData = [];

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
            searchResults.classList.remove('has-results');
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
        searchResults.classList.remove('has-results');
        this.style.display = 'none';
    });
    
    // Keyboard shortcuts
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            searchResults.innerHTML = '';
            searchResults.classList.remove('has-results');
            searchClear.style.display = 'none';
        }
    });
}

// Initialize manual section search (Windows)
function initManualParameterSearch() {
    const input = document.getElementById('parameter-search-manual');
    const results = document.getElementById('parameter-results-manual');
    if (!input || !results) return;

    input.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        if (!query) {
            results.innerHTML = '';
            results.classList.remove('has-results');
            return;
        }
        performParameterSearchWithFilter(query, results, 'windows');
    });
}

// Initialize manual section search (Linux)
function initLinuxManualParameterSearch() {
    const input = document.getElementById('linux-parameter-search-manual');
    const results = document.getElementById('linux-parameter-results-manual');
    if (!input || !results) return;

    input.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        if (!query) {
            results.innerHTML = '';
            results.classList.remove('has-results');
            return;
        }
        performParameterSearchWithFilter(query, results, 'linux');
    });
}

// Filter-aware search renderer for manual sections
function performParameterSearchWithFilter(query, resultsContainer, osFilter) {
    const scoped = (parameterData || []).filter(p => !osFilter || p.os === osFilter);
    const results = scoped.filter(parameter => {
        return parameter.title.toLowerCase().includes(query) ||
               parameter.details.toLowerCase().includes(query) ||
               parameter.category.toLowerCase().includes(query) ||
               parameter.subcategory.toLowerCase().includes(query) ||
               parameter.scriptKey.toLowerCase().includes(query);
    });

    // Display results
    if (results.length === 0) {
        resultsContainer.innerHTML = '';
        resultsContainer.classList.remove('has-results');
        return;
    }

    resultsContainer.innerHTML = results.map(parameter => `
        <div class="search-result-item" data-script-key="${parameter.scriptKey}">
            <div>
                <div class="result-title">${parameter.title}</div>
                <div class="result-meta">${parameter.category} → ${parameter.subcategory}</div>
            </div>
            <div class="result-badge">${parameter.scriptKey}</div>
        </div>
    `).join('');
    resultsContainer.classList.add('has-results');

    // Bind click handlers to open details popup
    resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const key = item.getAttribute('data-script-key');
            openParameterDetailPopup(key);
        });
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
        resultsContainer.innerHTML = '';
        resultsContainer.classList.remove('has-results');
        return;
    }
    
    resultsContainer.innerHTML = results.map(parameter => `
        <div class="search-result-item" data-script-key="${parameter.scriptKey}">
            <div>
                <div class="result-title">${parameter.title}</div>
                <div class="result-meta">${parameter.category} → ${parameter.subcategory}</div>
            </div>
            <div class="result-badge">${parameter.scriptKey}</div>
        </div>
    `).join('');
    resultsContainer.classList.add('has-results');

    // Bind click handlers to open details popup
    resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const key = item.getAttribute('data-script-key');
            openParameterDetailPopup(key);
        });
    });
}

// Show parameter details (placeholder function)
function showParameterDetails(scriptKey) {
    const parameter = parameterData.find(p => p.scriptKey === scriptKey);
    if (parameter) {
        openParameterDetailPopup(scriptKey);
    }
}

// Open parameter details popup and attempt to show the matching manual card
function openParameterDetailPopup(scriptKey) {
    const popup = document.getElementById('param-detail-popup');
    const title = document.getElementById('param-popup-title');
    const meta = document.getElementById('param-popup-meta');
    const body = document.getElementById('param-popup-body');

    const parameter = parameterData.find(p => p.scriptKey === scriptKey);
    if (!popup || !title || !meta || !body || !parameter) return;

    title.textContent = parameter.title;
    meta.textContent = `${parameter.category} → ${parameter.subcategory}`;

    // Build step-wise UI by extracting details from the matching manual card
    let cardHtml = '';
    const cards = Array.from(document.querySelectorAll('#parameters-manual-setup .parameter-card'));
    const match = cards.find(c => (c.querySelector('h4')?.textContent || '').trim().toLowerCase() === parameter.title.toLowerCase());
    if (match) {
        // Extract pieces
        const category = match.querySelector('.category')?.textContent || `${parameter.category} - ${parameter.subcategory}`;
        const description = match.querySelector('.description')?.textContent || parameter.details;
        const registryPathRaw = match.querySelector('.registry-path')?.textContent || '';
        const manualHtml = match.querySelector('.manual-setup')?.innerHTML || '';

        // Parse path (Registry: or File: prefix aware)
        let pathLabel = '';
        let pathValue = '';
        if (registryPathRaw) {
            const parts = registryPathRaw.split(':');
            if (parts.length > 1) {
                pathLabel = parts[0].trim();
                pathValue = parts.slice(1).join(':').trim();
            } else {
                pathValue = registryPathRaw.trim();
            }
        }

        // Parse commands from manual (all <code>...</code>)
        const codeRegex = /<code>([\s\S]*?)<\/code>/g;
        const cmdMatches = Array.from(manualHtml.matchAll(codeRegex)).map(m => m[1]);

        // Parse GUI/Policy path text (remove code and strong label)
        const manualTextOnly = manualHtml
            .replace(/<strong>\s*Manual Setup:\s*<\/strong>/i, '')
            .replace(/<code>[\s\S]*?<\/code>/g, '')
            .replace(/\s+/g, ' ')
            .trim();

        // If it contains arrows, split into path segments
        let guiSegments = [];
        if (manualTextOnly.includes('→')) {
            guiSegments = manualTextOnly.split('→').map(s => s.trim()).filter(Boolean);
        } else if (manualTextOnly.length) {
            guiSegments = [manualTextOnly];
        }

        // Extract recommended setting from details (e.g., "set to 'Enabled'")
        let recommended = '';
        const recMatch = /set to\s+'([^']+)'/i.exec(description || parameter.details || '');
        if (recMatch && recMatch[1]) {
            recommended = recMatch[1];
        }

        // Build steps
        const steps = [];
        if (pathValue) {
            steps.push(`
                <div class="step-item">
                    <div class="step-icon"><i class="fas fa-folder-open"></i></div>
                    <div class="step-content">
                        <h4>${pathLabel || 'Location / Path'}</h4>
                        <p><span class="path-example">${pathValue}</span></p>
                    </div>
                </div>
            `);
        }

        if (guiSegments.length) {
            steps.push(`
                <div class="step-item">
                    <div class="step-icon"><i class="fas fa-mouse-pointer"></i></div>
                    <div class="step-content">
                        <h4>GUI Path</h4>
                        <p>${guiSegments.map((seg, idx) => idx === 0 ? seg : `→ ${seg}`).join(' ')}</p>
                    </div>
                </div>
            `);
        }

        // Recommended value to set
        if (recommended || parameter.title) {
            steps.push(`
                <div class="step-item">
                    <div class="step-icon"><i class="fas fa-sliders-h"></i></div>
                    <div class="step-content">
                        <h4>Value to Configure</h4>
                        <p><strong>${parameter.title}</strong>${recommended ? ` → <span class="path-example">${recommended}</span>` : ''}</p>
                    </div>
                </div>
            `);
        }

        if (cmdMatches.length) {
            const commandsHtml = cmdMatches.map(cmd => `
                <div class="code-block">
                    <div class="code-header">
                        <span>Command</span>
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fas fa-copy"></i></button>
                    </div>
                    <pre><code>${cmd}</code></pre>
                </div>
            `).join('');

            steps.push(`
                <div class="step-item">
                    <div class="step-icon"><i class="fas fa-terminal"></i></div>
                    <div class="step-content">
                        <h4>Command Line</h4>
                        ${commandsHtml}
                    </div>
                </div>
            `);
        }

        // Always include a description/context step at the end
        if (description) {
            steps.push(`
                <div class="step-item">
                    <div class="step-icon"><i class="fas fa-info-circle"></i></div>
                    <div class="step-content">
                        <h4>About this setting</h4>
                        <p>${description}</p>
                    </div>
                </div>
            `);
        }

        cardHtml = `
            <div class="parameter-card">
                <div class="category">${category}</div>
                <h4>${parameter.title}</h4>
                <div class="steps-list">
                    ${steps.join('')}
                </div>
            </div>
        `;
    } else {
        // Fallback generic content
        cardHtml = `
            <div class="parameter-card">
                <div class="category">${parameter.category} - ${parameter.subcategory}</div>
                <h4>${parameter.title}</h4>
                <div class="description">${parameter.details}</div>
            </div>
        `;
    }

    body.innerHTML = cardHtml;
    popup.style.display = 'flex';

    // Close handlers
    const closeBtn = document.getElementById('param-popup-close');
    const closeOverlay = document.getElementById('param-popup-close-overlay');
    const close = () => { popup.style.display = 'none'; };
    if (closeBtn) closeBtn.onclick = close;
    if (closeOverlay) closeOverlay.onclick = close;

    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') { close(); document.removeEventListener('keydown', escHandler); }
    });
}

// Load parameter data (placeholder function)
async function loadParameterData() {
    try {
        const winResp = await fetch('/docs/assets/json/windows_tasks.json');
        const linuxResp = await fetch('/docs/assets/json/linux_tasks.json');
        const windows = winResp.ok ? await winResp.json() : [];
        const linux = linuxResp.ok ? await linuxResp.json() : [];

        // Normalize into unified structure
        const toEntry = (p, os) => ({
            title: p.title || p.name || '',
            details: p.details || p.description || '',
            category: p.heading || p.category || (os === 'linux' ? 'Linux' : 'Windows'),
            subcategory: p.subheading || p.subcategory || '',
            scriptKey: (p.scriptKey || p.key || sanitizeKey((p.title || '').toLowerCase())) + `_${os}`,
            os
        });

        const winEntries = Array.isArray(windows) ? windows.map(p => toEntry(p, 'windows')) : [];
        const linEntries = Array.isArray(linux) ? linux.map(p => toEntry(p, 'linux')) : [];

        parameterData = [...winEntries, ...linEntries];
    console.log('Parameter data loaded:', parameterData.length, 'parameters');

        // If user already typed, refresh results
        const inputs = [
            document.getElementById('parameter-search'),
            document.getElementById('parameter-search-manual'),
            document.getElementById('linux-parameter-search-manual')
        ];
        inputs.forEach(input => {
            const results = input && input.id === 'parameter-search' ? document.getElementById('parameter-results')
                : input && input.id === 'parameter-search-manual' ? document.getElementById('parameter-results-manual')
                : input && input.id === 'linux-parameter-search-manual' ? document.getElementById('linux-parameter-results-manual')
                : null;
            if (input && results && input.value.trim()) {
                performParameterSearch(input.value.trim().toLowerCase(), results);
            }
        });

        // Render complete tables if containers exist
        renderCompleteParameterTables();
    } catch (e) {
        console.error('Failed to load parameter data', e);
    }
}

function sanitizeKey(text) {
    return (text || '')
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .substring(0, 64);
}

// Bind click on parameter cards to open the same popup as search
function bindManualCardClicks() {
    const windowsSection = document.getElementById('parameters-manual-setup');
    const linuxSection = document.getElementById('linux-parameters-manual-setup');

    const attach = (rootEl, os) => {
        if (!rootEl) return;
        rootEl.querySelectorAll('.parameter-card').forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                const title = (card.querySelector('h4')?.textContent || '').trim();
                if (!title) return;
                // Prefer OS-matching parameter; fallback to any title match
                let param = (parameterData || []).find(p => p.os === os && p.title.toLowerCase() === title.toLowerCase());
                if (!param) param = (parameterData || []).find(p => p.title.toLowerCase() === title.toLowerCase());
                if (param) {
                    openParameterDetailPopup(param.scriptKey);
                } else {
                    // Fallback: open popup with title-only content
                    openParameterDetailPopup(sanitizeKey(title));
                }
            });
        });
    };

    attach(windowsSection, 'windows');
    attach(linuxSection, 'linux');
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

// Initialize table render hooks
function initCompleteParameterTables() {
    // No-op placeholder to keep ordering explicit
}

function renderCompleteParameterTables() {
    const windowsContainer = document.getElementById('complete-parameter-table');
    const linuxContainer = document.getElementById('linux-complete-parameter-table');
    const linuxListContainer = document.getElementById('linux-complete-parameter-list');
    if (!parameterData || parameterData.length === 0) return;

    if (windowsContainer) {
        const winRows = parameterData
            .filter(p => p.os === 'windows')
            .map((p, idx) => tableRow(idx + 1, p));
        windowsContainer.innerHTML = buildTableHtml(winRows);
        // Click to open detail popup
        windowsContainer.querySelectorAll('tbody tr').forEach(tr => {
            tr.style.cursor = 'pointer';
            tr.addEventListener('click', () => {
                const key = tr.getAttribute('data-script-key');
                if (key) openParameterDetailPopup(key);
            });
        });
    }

    if (linuxContainer) {
        const linRows = parameterData
            .filter(p => p.os === 'linux')
            .map((p, idx) => tableRow(idx + 1, p));
        linuxContainer.innerHTML = buildTableHtml(linRows);
        // Click to open detail popup
        linuxContainer.querySelectorAll('tbody tr').forEach(tr => {
            tr.style.cursor = 'pointer';
            tr.addEventListener('click', () => {
                const key = tr.getAttribute('data-script-key');
                if (key) openParameterDetailPopup(key);
            });
        });
    }

    // Also render grouped list for Linux below the table
    if (linuxListContainer) {
        const linuxItems = parameterData.filter(p => p.os === 'linux');
        const groups = linuxItems.reduce((acc, p) => {
            const head = p.category || 'General';
            const sub = p.subcategory || 'Misc';
            acc[head] = acc[head] || {};
            acc[head][sub] = acc[head][sub] || [];
            acc[head][sub].push(p);
            return acc;
        }, {});

        const html = Object.keys(groups).sort().map(head => {
            const subHtml = Object.keys(groups[head]).sort().map(sub => {
                const items = groups[head][sub]
                    .sort((a,b) => a.title.localeCompare(b.title))
                    .map(p => `<li class="param-item" data-script-key="${p.scriptKey}"><strong>${escapeHtml(p.title)}</strong> — ${escapeHtml(p.details)}</li>`)
                    .join('');
                return `
                    <div class="parameter-category">
                        <h3>${escapeHtml(head)}</h3>
                        <h4>${escapeHtml(sub)}</h4>
                        <ul class="parameter-list">${items}</ul>
                    </div>
                `;
            }).join('');
            return subHtml;
        }).join('');

        linuxListContainer.innerHTML = html;

        linuxListContainer.querySelectorAll('.param-item').forEach(li => {
            li.style.cursor = 'pointer';
            li.addEventListener('click', () => {
                const key = li.getAttribute('data-script-key');
                if (key) openParameterDetailPopup(key);
            });
        });
    }
}

function tableRow(num, p) {
    const safe = (t) => (t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return `
        <tr data-script-key="${safe(p.scriptKey)}">
            <td>${num}</td>
            <td>${safe(p.title)}</td>
            <td>${safe(p.category)}</td>
            <td>${safe(p.subcategory)}</td>
            <td>${safe(p.details)}</td>
        </tr>
    `;
}

function buildTableHtml(rows) {
    if (!rows || rows.length === 0) return '';
    return `
        <div class="table-responsive">
            <table class="param-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Name</th>
                        <th>Heading</th>
                        <th>Subheading</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.join('')}
                </tbody>
            </table>
        </div>
    `;
}

function escapeHtml(t) {
    return (t || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
