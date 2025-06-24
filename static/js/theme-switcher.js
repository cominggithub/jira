// Theme switcher functionality
let currentTheme = localStorage.getItem('theme') || 'dark';

function switchTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    
    // Update the theme stylesheet
    const themeStylesheet = document.getElementById('theme-stylesheet');
    themeStylesheet.href = `/static/css/${theme}.css`;
    
    // Update body data attribute
    document.body.setAttribute('data-theme', theme);
    
    // Update active button
    updateActiveButton(theme);
    
    // Trigger theme change event
    document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
}

function updateActiveButton(theme) {
    // Remove active class from all theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to current theme button
    const activeBtn = document.querySelector(`[data-theme="${theme}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

function initTheme() {
    // Apply saved theme on page load
    switchTheme(currentTheme);
}

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', initTheme);

// Optional: Add keyboard shortcuts for theme switching
document.addEventListener('keydown', function(event) {
    // Only trigger if Ctrl+Shift is held
    if (event.ctrlKey && event.shiftKey) {
        switch(event.key) {
            case '1':
                event.preventDefault();
                switchTheme('neon');
                break;
            case '2':
                event.preventDefault();
                switchTheme('pink-neon');
                break;
            case '3':
                event.preventDefault();
                switchTheme('tron');
                break;
            case '4':
                event.preventDefault();
                switchTheme('dark');
                break;
            case '5':
                event.preventDefault();
                switchTheme('white');
                break;
        }
    }
});

// Optional: Auto-detect system theme preference
function detectSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'white';
}

// Listen for system theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // Only auto-switch if user hasn't manually selected a theme
        if (!localStorage.getItem('theme')) {
            switchTheme(e.matches ? 'dark' : 'white');
        }
    });
}

// Expose functions globally for HTML onclick handlers
window.switchTheme = switchTheme;