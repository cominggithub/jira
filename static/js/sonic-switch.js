// Sonic Switch Interactive Elements

document.addEventListener('DOMContentLoaded', function() {
    initializeSonicSwitch();
});

function initializeSonicSwitch() {
    // Initialize control buttons
    initializeControlButtons();
    
    // Initialize feature cards
    initializeFeatureCards();
    
    // Initialize action buttons
    initializeActionButtons();
    
    // Start background animations
    startBackgroundAnimations();
    
    // Initialize sonic visualizer
    initializeSonicVisualizer();
}

function initializeControlButtons() {
    const controlButtons = document.querySelectorAll('.control-btn');
    
    controlButtons.forEach(button => {
        button.addEventListener('click', function() {
            const group = this.closest('.control-group');
            const siblings = group.querySelectorAll('.control-btn');
            
            // Remove active class from siblings
            siblings.forEach(sibling => sibling.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Trigger mode change
            const mode = this.dataset.mode;
            if (mode) {
                changeModeAnimation(mode);
            }
        });
    });
}

function initializeFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('click', function() {
            const feature = this.dataset.feature;
            showFeatureDetails(feature);
        });
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initializeActionButtons() {
    const initiateBtn = document.getElementById('initiate-sonic');
    const diagnosticsBtn = document.getElementById('diagnostics');
    
    if (initiateBtn) {
        initiateBtn.addEventListener('click', function() {
            initiateSonicSwitch();
        });
    }
    
    if (diagnosticsBtn) {
        diagnosticsBtn.addEventListener('click', function() {
            runDiagnostics();
        });
    }
}

function changeModeAnimation(mode) {
    // Create visual feedback for mode change
    const modeIndicator = document.createElement('div');
    modeIndicator.className = 'mode-indicator';
    modeIndicator.textContent = `Mode: ${mode.toUpperCase()}`;
    modeIndicator.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--accent-color);
        color: var(--accent-text);
        padding: 1rem 2rem;
        border-radius: var(--border-radius);
        z-index: 1000;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(modeIndicator);
    
    // Animate in
    setTimeout(() => {
        modeIndicator.style.opacity = '1';
    }, 10);
    
    // Animate out
    setTimeout(() => {
        modeIndicator.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(modeIndicator);
        }, 300);
    }, 2000);
    
    console.log(`AI Processing Mode changed to: ${mode}`);
}

function showFeatureDetails(feature) {
    const details = {
        neural: {
            title: 'Neural Processing',
            description: 'Advanced AI neural network processing with real-time fabric optimization and machine learning capabilities.',
            status: 'Fully Operational'
        },
        sonic: {
            title: 'Sonic Interface',
            description: 'Voice-activated commands and audio feedback system with natural language processing and contextual understanding.',
            status: 'Listening Mode Active'
        },
        fabric: {
            title: 'AI Fabric',
            description: 'Distributed AI mesh network providing scalable intelligence processing across multiple nodes with redundancy.',
            status: 'Network Connected'
        },
        quantum: {
            title: 'Quantum Switch',
            description: 'Quantum-enhanced switching technology enabling ultra-fast data processing and quantum entanglement protocols.',
            status: 'Calibration in Progress'
        }
    };
    
    const detail = details[feature];
    if (detail) {
        showModal(detail);
    }
}

function showModal(detail) {
    const modal = document.createElement('div');
    modal.className = 'sonic-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeModal(this)"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h2>${detail.title}</h2>
                <button class="modal-close" onclick="closeModal(this)">&times;</button>
            </div>
            <div class="modal-body">
                <p>${detail.description}</p>
                <div class="modal-status">
                    <strong>Status:</strong> <span class="status-text">${detail.status}</span>
                </div>
            </div>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    document.body.appendChild(modal);
    
    // Add styles for modal elements
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }
        .modal-content {
            background: var(--card-bg);
            border: 2px solid var(--accent-color);
            border-radius: var(--border-radius);
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            position: relative;
            box-shadow: 0 0 50px var(--accent-color);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .modal-header h2 {
            color: var(--heading-color);
            margin: 0;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 2rem;
            color: var(--text-color);
            cursor: pointer;
        }
        .modal-body p {
            color: var(--text-color);
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        .modal-status {
            color: var(--text-color);
        }
        .status-text {
            color: var(--accent-color);
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
}

function closeModal(element) {
    const modal = element.closest('.sonic-modal');
    if (modal) {
        document.body.removeChild(modal);
    }
}

function initiateSonicSwitch() {
    const button = document.getElementById('initiate-sonic');
    const originalText = button.innerHTML;
    
    // Change button state
    button.innerHTML = '<span class="action-icon">⚡</span><span>Initiating...</span>';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    // Simulate initialization process
    setTimeout(() => {
        button.innerHTML = '<span class="action-icon">✓</span><span>Sonic Switch Active</span>';
        button.style.background = 'var(--accent-color)';
        
        // Create system notification
        showNotification('Sonic Switch Initiated Successfully', 'success');
        
        // Reset button after delay
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.opacity = '1';
            button.style.background = '';
        }, 3000);
    }, 2000);
    
    console.log('Sonic Switch initiation sequence started');
}

function runDiagnostics() {
    const button = document.getElementById('diagnostics');
    const originalText = button.innerHTML;
    
    button.innerHTML = '<span class="action-icon">🔄</span><span>Running...</span>';
    button.disabled = true;
    
    // Simulate diagnostics
    setTimeout(() => {
        button.innerHTML = '<span class="action-icon">✓</span><span>Diagnostics Complete</span>';
        
        showNotification('System Diagnostics: All Systems Operational', 'info');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }, 1500);
    
    console.log('System diagnostics initiated');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `sonic-notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--accent-color);
        color: var(--accent-text);
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        z-index: 1001;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
        font-weight: bold;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Animate out
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

function startBackgroundAnimations() {
    // Enhanced particle system
    const particles = document.querySelectorAll('.particle');
    particles.forEach((particle, index) => {
        particle.style.animationDelay = `${index * 2}s`;
    });
    
    // Animate network nodes
    const networkNodes = document.querySelectorAll('.network-node');
    let nodeIndex = 0;
    
    setInterval(() => {
        networkNodes.forEach(node => node.classList.remove('pulse'));
        networkNodes[nodeIndex].classList.add('pulse');
        nodeIndex = (nodeIndex + 1) % networkNodes.length;
    }, 1000);
}

function initializeSonicVisualizer() {
    const waveBars = document.querySelectorAll('.wave-bar');
    
    // Randomize wave heights periodically
    setInterval(() => {
        waveBars.forEach(bar => {
            const randomHeight = Math.random() * 0.8 + 0.2;
            bar.style.setProperty('--height', randomHeight);
        });
    }, 1000);
}

// Global functions for modal closing
window.closeModal = closeModal;

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.altKey) {
        switch(event.key) {
            case 's':
                event.preventDefault();
                initiateSonicSwitch();
                break;
            case 'd':
                event.preventDefault();
                runDiagnostics();
                break;
        }
    }
});

// Theme change event listener
document.addEventListener('themeChanged', function(event) {
    console.log(`Sonic Switch theme changed to: ${event.detail.theme}`);
    
    // Update theme-specific animations
    const theme = event.detail.theme;
    if (theme === 'neon') {
        // Enhance neon effects
        document.documentElement.style.setProperty('--accent-color-rgb', '0, 255, 0');
    } else if (theme === 'tron') {
        // Enhance tron effects
        document.documentElement.style.setProperty('--accent-color-rgb', '0, 212, 255');
    } else if (theme === 'dark') {
        // Standard dark theme
        document.documentElement.style.setProperty('--accent-color-rgb', '99, 102, 241');
    } else if (theme === 'white') {
        // Light theme adjustments
        document.documentElement.style.setProperty('--accent-color-rgb', '59, 130, 246');
    }
});