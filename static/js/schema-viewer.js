/**
 * Schema Viewer JavaScript
 * Handles markdown rendering, tab switching, and view modes
 */

let currentDb = null;
let currentView = 'rendered';

document.addEventListener('DOMContentLoaded', function() {
    initializeSchemaViewer();
});

function initializeSchemaViewer() {
    // Set current database
    if (window.selectedDb) {
        currentDb = window.selectedDb;
    } else if (window.schemaData) {
        currentDb = Object.keys(window.schemaData)[0];
    }
    
    // Initialize markdown rendering
    renderAllMarkdown();
    
    // Initialize tab switching
    initializeTabs();
    
    // Initialize view switching
    initializeViewSwitching();
    
    // Update statistics
    updateSchemaStats();
    
    // Set up keyboard shortcuts
    setupKeyboardShortcuts();
}

function renderAllMarkdown() {
    if (!window.schemaData) return;
    
    Object.keys(window.schemaData).forEach(db => {
        renderMarkdownForDb(db);
    });
}

function renderMarkdownForDb(db) {
    const content = window.schemaData[db];
    
    // Render for main rendered view
    const renderedElement = document.querySelector(`#rendered-${db} .markdown-content`);
    if (renderedElement) {
        renderedElement.innerHTML = marked.parse(content);
    }
    
    // Render for split view
    const splitElement = document.querySelector(`#split-${db} .split-right .markdown-content`);
    if (splitElement) {
        splitElement.innerHTML = marked.parse(content);
    }
}

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetDb = this.dataset.db;
            switchToDatabase(targetDb);
        });
    });
}

function switchToDatabase(db) {
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-db="${db}"]`).classList.add('active');
    
    // Update active panel
    document.querySelectorAll('.schema-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`panel-${db}`).classList.add('active');
    
    currentDb = db;
    updateSchemaStats();
}

function initializeViewSwitching() {
    const viewButtons = document.querySelectorAll('.view-btn');
    
    viewButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetView = this.dataset.view;
            switchToView(targetView);
        });
    });
}

function switchToView(view) {
    // Update active view button
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    // Update active view for current database
    if (currentDb) {
        const panel = document.getElementById(`panel-${currentDb}`);
        panel.querySelectorAll('.rendered-view, .source-view, .split-view').forEach(viewEl => {
            viewEl.classList.remove('active');
        });
        
        const targetViewElement = panel.querySelector(`#${view}-${currentDb}`);
        if (targetViewElement) {
            targetViewElement.classList.add('active');
        }
    }
    
    currentView = view;
}

function updateSchemaStats() {
    if (!currentDb || !window.schemaData) return;
    
    const content = window.schemaData[currentDb];
    const lines = content.split('\n').length;
    const words = content.split(/\s+/).length;
    const chars = content.length;
    
    // Count tables (look for "### " patterns which indicate table headers)
    const tableMatches = content.match(/^### \w+/gm);
    const tables = tableMatches ? tableMatches.length : 0;
    
    // Count columns (look for table rows with pipe separators)
    const columnMatches = content.match(/^\|[^|]+\|[^|]+\|/gm);
    const columns = columnMatches ? Math.max(0, columnMatches.length - tables * 2) : 0; // Subtract headers
    
    const statsElement = document.getElementById('schema-stats');
    if (statsElement) {
        statsElement.textContent = `${currentDb.toUpperCase()}: ${tables} tables, ${columns} columns, ${lines} lines, ${words} words, ${chars} characters`;
    }
}

function refreshSchema() {
    // Refresh the current page to reload schema data
    window.location.reload();
}

function exportSchema() {
    if (!currentDb || !window.schemaData) return;
    
    const content = window.schemaData[currentDb];
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `schema_${currentDb}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only activate shortcuts if not typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    switchToView('rendered');
                    break;
                case '2':
                    e.preventDefault();
                    switchToView('source');
                    break;
                case '3':
                    e.preventDefault();
                    switchToView('split');
                    break;
                case 'r':
                    e.preventDefault();
                    refreshSchema();
                    break;
                case 's':
                    e.preventDefault();
                    exportSchema();
                    break;
            }
        }
        
        // Tab navigation with arrow keys
        if (e.key === 'ArrowLeft' && e.altKey) {
            e.preventDefault();
            switchToPreviousDatabase();
        } else if (e.key === 'ArrowRight' && e.altKey) {
            e.preventDefault();
            switchToNextDatabase();
        }
    });
}

function switchToPreviousDatabase() {
    if (!window.schemaData) return;
    
    const databases = Object.keys(window.schemaData);
    const currentIndex = databases.indexOf(currentDb);
    const previousIndex = currentIndex > 0 ? currentIndex - 1 : databases.length - 1;
    
    switchToDatabase(databases[previousIndex]);
}

function switchToNextDatabase() {
    if (!window.schemaData) return;
    
    const databases = Object.keys(window.schemaData);
    const currentIndex = databases.indexOf(currentDb);
    const nextIndex = currentIndex < databases.length - 1 ? currentIndex + 1 : 0;
    
    switchToDatabase(databases[nextIndex]);
}

// Configure marked.js options for better rendering
if (typeof marked !== 'undefined') {
    marked.setOptions({
        highlight: function(code, lang) {
            // Basic syntax highlighting for SQL if available
            if (lang === 'sql' && typeof hljs !== 'undefined') {
                return hljs.highlight(code, {language: 'sql'}).value;
            }
            return code;
        },
        breaks: true,
        gfm: true
    });
}