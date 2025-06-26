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
    
    // Close dropdown after selection
    const dropdown = document.getElementById('themeDropdown');
    const dropdownContainer = document.querySelector('.theme-dropdown');
    if (dropdown && dropdownContainer) {
        dropdown.classList.remove('show');
        dropdownContainer.classList.remove('open');
    }
    
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
    
    // Update dropdown button text
    const currentThemeSpan = document.querySelector('.current-theme');
    if (currentThemeSpan) {
        const themeNames = {
            'neon': '🟢 Green Neon',
            'pink-neon': '🌸 Pink Neon',
            'tron': '🔷 Tron',
            'dark': '🌙 Dark',
            'white': '☀️ White',
            'pony': '🦄 Pony'
        };
        currentThemeSpan.textContent = themeNames[theme] || 'Theme';
    }
}

function toggleThemeDropdown() {
    const dropdown = document.getElementById('themeDropdown');
    const dropdownContainer = document.querySelector('.theme-dropdown');
    
    if (dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
        dropdownContainer.classList.remove('open');
    } else {
        dropdown.classList.add('show');
        dropdownContainer.classList.add('open');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const themeDropdown = document.querySelector('.theme-dropdown');
    if (!themeDropdown.contains(event.target)) {
        const dropdown = document.getElementById('themeDropdown');
        const dropdownContainer = document.querySelector('.theme-dropdown');
        dropdown.classList.remove('show');
        dropdownContainer.classList.remove('open');
    }
});

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
            case '6':
                event.preventDefault();
                switchTheme('pony');
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

// Background image functionality (single image, no rotation needed)
document.addEventListener('DOMContentLoaded', function() {
    // Ensure bg1 is active on page load
    const bgImage = document.querySelector('.bg-image.bg1');
    if (bgImage) {
        bgImage.classList.add('active');
    }
});

// Expose functions globally for HTML onclick handlers
// Navigation dropdown functionality
function toggleNavDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    const allNavDropdowns = document.querySelectorAll('.nav-dropdown-content');
    
    // Close all other nav dropdowns
    allNavDropdowns.forEach(d => {
        if (d.id !== dropdownId) {
            d.classList.remove('show');
        }
    });
    
    // Toggle the clicked dropdown
    dropdown.classList.toggle('show');
}

// Close nav dropdowns when clicking outside
document.addEventListener('click', function(event) {
    const isNavDropdown = event.target.closest('.nav-dropdown');
    if (!isNavDropdown) {
        const navDropdowns = document.querySelectorAll('.nav-dropdown-content');
        navDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
});

// Make functions globally available
window.switchTheme = switchTheme;
window.toggleThemeDropdown = toggleThemeDropdown;
window.toggleNavDropdown = toggleNavDropdown;