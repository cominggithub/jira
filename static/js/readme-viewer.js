// README Viewer JavaScript
// Handles tab switching, view modes, and markdown rendering

class ReadmeViewer {
    constructor() {
        this.docs = {};
        this.currentDoc = 'README';
        this.currentView = 'rendered';
        this.init();
    }

    init() {
        this.loadDocsData();
        this.setupEventListeners();
        this.renderCurrentDoc();
        this.updateLastUpdated();
    }

    loadDocsData() {
        try {
            const docsElement = document.getElementById('docs-data');
            if (docsElement) {
                this.docs = JSON.parse(docsElement.textContent);
                console.log('Loaded documentation data:', Object.keys(this.docs));
            }
        } catch (error) {
            console.error('Error loading docs data:', error);
            this.docs = {
                'README': '# Error\n\nFailed to load documentation data.',
                'FEATURES': '# Error\n\nFailed to load features documentation.',
                'DEPLOY': '# Error\n\nFailed to load deployment documentation.'
            };
        }
    }

    setupEventListeners() {
        // Tab switching
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const doc = btn.getAttribute('data-doc');
                this.switchDoc(doc);
            });
        });

        // View mode switching
        const viewButtons = document.querySelectorAll('.view-btn');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const view = btn.getAttribute('data-view');
                this.switchView(view);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey) {
                switch(e.key) {
                    case 'R':
                        e.preventDefault();
                        this.switchDoc('README');
                        break;
                    case 'F':
                        e.preventDefault();
                        this.switchDoc('FEATURES');
                        break;
                    case 'D':
                        e.preventDefault();
                        this.switchDoc('DEPLOY');
                        break;
                    case '1':
                        e.preventDefault();
                        this.switchView('rendered');
                        break;
                    case '2':
                        e.preventDefault();
                        this.switchView('source');
                        break;
                    case '3':
                        e.preventDefault();
                        this.switchView('split');
                        break;
                }
            }
        });

        // Refresh button (could be added later)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                // Allow normal page refresh to get updated docs
            }
        });
    }

    switchDoc(docName) {
        if (!this.docs[docName]) {
            console.error(`Document ${docName} not found`);
            return;
        }

        this.currentDoc = docName;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-doc="${docName}"]`).classList.add('active');

        // Update document title
        const docTitle = document.getElementById('current-doc-title');
        if (docTitle) {
            docTitle.textContent = `${docName}.md`;
        }

        // Render the document
        this.renderCurrentDoc();
        
        // Update URL without page reload
        const url = new URL(window.location);
        url.searchParams.set('doc', docName.toLowerCase());
        window.history.pushState({}, '', url);
    }

    switchView(viewMode) {
        this.currentView = viewMode;

        // Update view buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewMode}"]`).classList.add('active');

        // Update content panels
        document.querySelectorAll('.content-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        const targetPanel = document.getElementById(`${viewMode}-panel`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }

        // Render content for the current view
        this.renderCurrentDoc();
    }

    renderCurrentDoc() {
        const content = this.docs[this.currentDoc] || '# Document not found';
        
        // Update word count
        const wordCount = this.countWords(content);
        const wordCountElement = document.getElementById('word-count');
        if (wordCountElement) {
            wordCountElement.textContent = `${wordCount} words`;
        }

        // Render based on current view
        switch(this.currentView) {
            case 'rendered':
                this.renderMarkdown(content, 'markdown-content');
                break;
            case 'source':
                this.renderSource(content, 'source-code');
                break;
            case 'split':
                this.renderMarkdown(content, 'split-markdown-content');
                this.renderSource(content, 'split-source-code');
                break;
        }
    }

    renderMarkdown(content, targetId) {
        const target = document.getElementById(targetId);
        if (!target) return;

        try {
            // Configure marked options
            marked.setOptions({
                highlight: function(code, lang) {
                    // Simple syntax highlighting for code blocks
                    return `<code class="language-${lang}">${this.escapeHtml(code)}</code>`;
                },
                breaks: true,
                gfm: true
            });

            const html = marked.parse(content);
            target.innerHTML = html;

            // Add classes for styling
            target.querySelectorAll('table').forEach(table => {
                table.classList.add('markdown-table');
            });

            target.querySelectorAll('pre').forEach(pre => {
                pre.classList.add('markdown-pre');
            });

            target.querySelectorAll('code').forEach(code => {
                if (!code.parentElement.tagName === 'PRE') {
                    code.classList.add('inline-code');
                }
            });

            target.querySelectorAll('blockquote').forEach(quote => {
                quote.classList.add('markdown-quote');
            });

        } catch (error) {
            console.error('Error rendering markdown:', error);
            target.innerHTML = `<div class="error">Error rendering markdown: ${error.message}</div>`;
        }
    }

    renderSource(content, targetId) {
        const target = document.getElementById(targetId);
        if (!target) return;

        target.textContent = content;
    }

    countWords(text) {
        // Remove markdown syntax and count words
        const cleanText = text
            .replace(/[#*_`~\[\]()]/g, '') // Remove markdown characters
            .replace(/!\[.*?\]\(.*?\)/g, '') // Remove images
            .replace(/\[.*?\]\(.*?\)/g, '') // Remove links
            .replace(/```[\s\S]*?```/g, '') // Remove code blocks
            .replace(/`.*?`/g, '') // Remove inline code
            .trim();

        if (!cleanText) return 0;
        return cleanText.split(/\s+/).length;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateLastUpdated() {
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date().toLocaleString();
        }
    }

    // Public method to refresh docs (could be called externally)
    refresh() {
        window.location.reload();
    }
}

// Initialize the viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const viewer = new ReadmeViewer();
    
    // Make viewer globally accessible for debugging
    window.readmeViewer = viewer;
    
    // Check URL parameters for initial doc
    const urlParams = new URLSearchParams(window.location.search);
    const docParam = urlParams.get('doc');
    if (docParam) {
        const docName = docParam.toUpperCase();
        if (viewer.docs[docName]) {
            viewer.switchDoc(docName);
        }
    }
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReadmeViewer;
}