// LUKHAS v2 - Simple Working Neural Network Background
console.log('LUKHAS v2 Neural Network Script Loaded!');

class SimpleNeuralNetwork {
    constructor() {
        this.nodes = [];
        this.connections = [];
        this.container = null;
        this.animationId = null;
    }
    
    init() {
        console.log('Initializing simple neural network...');
        this.createBackground();
        this.createNodes();
        this.createConnections();
        this.animate();
    }
    
    createBackground() {
        this.container = document.createElement('div');
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #0f172a 50%, #1e293b 75%, #0f172a 100%);
            overflow: hidden;
            pointer-events: none;
        `;
        
        document.body.appendChild(this.container);
        console.log('Neural network background created');
    }
    
    createNodes() {
        const nodeCount = 40;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const padding = 100;
        
        for (let i = 0; i < nodeCount; i++) {
            const node = {
                x: padding + Math.random() * (viewportWidth - 2 * padding),
                y: padding + Math.random() * (viewportHeight - 2 * padding),
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: 3 + Math.random() * 3,
                element: null
            };
            
            // Create visual element
            node.element = document.createElement('div');
            node.element.style.cssText = `
                position: fixed;
                width: ${node.size}px;
                height: ${node.size}px;
                background: radial-gradient(circle, #60a5fa 0%, #3b82f6 70%, transparent 100%);
                left: ${node.x}px;
                top: ${node.y}px;
                border-radius: 50%;
                box-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
                z-index: 2;
            `;
            
            this.container.appendChild(node.element);
            this.nodes.push(node);
        }
        
        console.log(`Created ${nodeCount} nodes`);
    }
    
    createConnections() {
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const distance = this.getDistance(this.nodes[i], this.nodes[j]);
                if (distance < 150) {
                    const connection = {
                        from: this.nodes[i],
                        to: this.nodes[j],
                        element: null,
                        opacity: Math.max(0.1, 1 - distance / 150)
                    };
                    
                    connection.element = document.createElement('div');
                    connection.element.style.cssText = `
                        position: fixed;
                        background: linear-gradient(90deg, 
                            rgba(96, 165, 250, 0.3), 
                            rgba(59, 130, 246, 0.5), 
                            rgba(96, 165, 250, 0.3)
                        );
                        height: 1px;
                        z-index: 1;
                        opacity: ${connection.opacity};
                        transform-origin: 0 50%;
                    `;
                    
                    this.container.appendChild(connection.element);
                    this.connections.push(connection);
                    this.updateConnection(connection);
                }
            }
        }
        
        console.log(`Created ${this.connections.length} connections`);
    }
    
    updateConnection(connection) {
        const distance = this.getDistance(connection.from, connection.to);
        const angle = Math.atan2(
            connection.to.y - connection.from.y,
            connection.to.x - connection.from.x
        ) * 180 / Math.PI;
        
        connection.element.style.width = `${distance}px`;
        connection.element.style.left = `${connection.from.x}px`;
        connection.element.style.top = `${connection.from.y}px`;
        connection.element.style.transform = `rotate(${angle}deg)`;
    }
    
    getDistance(node1, node2) {
        const dx = node1.x - node2.x;
        const dy = node1.y - node2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    updateNode(node) {
        const padding = 50;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Update position
        node.x += node.vx;
        node.y += node.vy;
        
        // Bounce off edges
        if (node.x <= padding || node.x >= viewportWidth - padding) {
            node.vx *= -1;
            node.x = Math.max(padding, Math.min(viewportWidth - padding, node.x));
        }
        if (node.y <= padding || node.y >= viewportHeight - padding) {
            node.vy *= -1;
            node.y = Math.max(padding, Math.min(viewportHeight - padding, node.y));
        }
        
        // Update visual position
        node.element.style.left = `${node.x}px`;
        node.element.style.top = `${node.y}px`;
    }
    
    animate() {
        // Update all nodes
        this.nodes.forEach(node => this.updateNode(node));
        
        // Update all connections
        this.connections.forEach(connection => this.updateConnection(connection));
        
        // Continue animation
        this.animationId = requestAnimationFrame(() => this.animate());
    }
}

// Dashboard functionality integration
class DashboardIntegration {
    constructor() {
        this.activeTab = 'dashboard';
    }
    
    init() {
        this.initializeIcons();
        this.setupTabNavigation();
        this.setupInteractiveElements();
        console.log('Dashboard integration initialized');
    }
    
    // Initialize Lucide icons
    initializeIcons() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
            console.log('Lucide icons initialized');
        } else {
            console.warn('Lucide icons not available');
        }
    }
    
    // Setup tab navigation
    setupTabNavigation() {
        const navLinks = document.querySelectorAll('.nav-link[data-tab]');
        const tabContents = document.querySelectorAll('.tab-content');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = link.getAttribute('data-tab');
                this.switchTab(targetTab, navLinks, tabContents);
            });
        });
    }
    
    switchTab(targetTab, navLinks, tabContents) {
        // Remove active class from all nav items and tab contents
        navLinks.forEach(link => link.closest('.nav-item').classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked nav item and corresponding tab content
        const activeLink = document.querySelector(`[data-tab="${targetTab}"]`);
        const activeContent = document.getElementById(`${targetTab}-content`);
        
        if (activeLink && activeContent) {
            activeLink.closest('.nav-item').classList.add('active');
            activeContent.classList.add('active');
            this.activeTab = targetTab;
        }
    }
    
    // Setup interactive elements
    setupInteractiveElements() {
        this.setupDockToggles();
        this.setupCommandPalette();
        this.setupFloatingSearch();
    }
    
    setupDockToggles() {
        const leftToggle = document.getElementById('left-dock-toggle');
        const rightToggle = document.getElementById('right-dock-toggle');
        const leftDock = document.getElementById('left-dock');
        const rightDock = document.getElementById('right-dock');
        const mainContent = document.querySelector('.main-content');
        
        if (leftToggle && leftDock) {
            leftToggle.addEventListener('click', () => {
                leftDock.classList.toggle('collapsed');
                mainContent.classList.toggle('left-collapsed');
            });
        }
        
        if (rightToggle && rightDock) {
            rightToggle.addEventListener('click', () => {
                rightDock.classList.toggle('collapsed');
                mainContent.classList.toggle('right-collapsed');
            });
        }
    }
    
    setupCommandPalette() {
        const commandPalette = document.getElementById('command-palette');
        const commandClose = document.querySelector('.command-close');
        
        // Open command palette with Ctrl+K
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                if (commandPalette) {
                    commandPalette.classList.add('active');
                    const input = commandPalette.querySelector('.command-input');
                    if (input) input.focus();
                }
            }
            
            if (e.key === 'Escape' && commandPalette) {
                commandPalette.classList.remove('active');
            }
        });
        
        if (commandClose) {
            commandClose.addEventListener('click', () => {
                commandPalette.classList.remove('active');
            });
        }
    }
    
    setupFloatingSearch() {
        const floatingSearch = document.getElementById('floating-search');
        const mainContent = document.querySelector('.main-content');
        
        if (mainContent && floatingSearch) {
            mainContent.addEventListener('mousemove', (e) => {
                // Show search bar when mouse is in top area
                if (e.clientY < 100) {
                    floatingSearch.classList.add('visible');
                } else {
                    floatingSearch.classList.remove('visible');
                }
            });
        }
    }
}

// Dock Management Class
class DockManager {
    constructor() {
        this.leftDock = null;
        this.rightDock = null;
        this.leftToggle = null;
        this.rightToggle = null;
        this.mainContent = null;
    }

    init() {
        this.leftDock = document.getElementById('left-dock');
        this.rightDock = document.getElementById('right-dock');
        this.leftToggle = document.getElementById('left-dock-toggle');
        this.rightToggle = document.getElementById('right-dock-toggle');
        this.mainContent = document.querySelector('.main-content');

        this.setupEventListeners();
        console.log('Dock Manager initialized');
    }

    setupEventListeners() {
        if (this.leftToggle) {
            this.leftToggle.addEventListener('click', () => {
                this.toggleDock('left');
            });
        }

        if (this.rightToggle) {
            this.rightToggle.addEventListener('click', () => {
                this.toggleDock('right');
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === '[') {
                    e.preventDefault();
                    this.toggleDock('left');
                } else if (e.key === ']') {
                    e.preventDefault();
                    this.toggleDock('right');
                } else if (e.key === '\\') {
                    // Toggle distraction-free mode (hide/show all docks)
                    e.preventDefault();
                    this.toggleDistractionFreeMode();
                }
            }
        });
    }

    toggleDock(side) {
        const dock = side === 'left' ? this.leftDock : this.rightDock;
        const toggle = side === 'left' ? this.leftToggle : this.rightToggle;
        
        if (!dock) return;

        const isHidden = dock.classList.contains('hidden');
        
        if (isHidden) {
            this.showDock(side);
        } else {
            this.hideDock(side);
        }
    }

    hideDock(side) {
        const dock = side === 'left' ? this.leftDock : this.rightDock;
        const toggle = side === 'left' ? this.leftToggle : this.rightToggle;
        
        if (!dock) return;

        dock.classList.add('hidden');
        
        // Update toggle button icon
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                if (side === 'left') {
                    icon.setAttribute('data-lucide', 'panel-left');
                } else {
                    icon.setAttribute('data-lucide', 'panel-right');
                }
                // Re-initialize icons
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        }

        // Adjust main content margin
        this.adjustMainContentMargin();
        
        console.log(`${side} dock hidden`);
    }

    showDock(side) {
        const dock = side === 'left' ? this.leftDock : this.rightDock;
        const toggle = side === 'left' ? this.leftToggle : this.rightToggle;
        
        if (!dock) return;

        dock.classList.remove('hidden');
        
        // Update toggle button icon
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                if (side === 'left') {
                    icon.setAttribute('data-lucide', 'panel-left-close');
                } else {
                    icon.setAttribute('data-lucide', 'panel-right-close');
                }
                // Re-initialize icons
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        }

        // Adjust main content margin
        this.adjustMainContentMargin();
        
        console.log(`${side} dock shown`);
    }

    adjustMainContentMargin() {
        if (!this.mainContent) return;

        const leftHidden = this.leftDock?.classList.contains('hidden');
        const rightHidden = this.rightDock?.classList.contains('hidden');

        let marginLeft = leftHidden ? '0' : 'var(--dock-width)';
        let marginRight = rightHidden ? '0' : 'var(--dock-width)';

        this.mainContent.style.marginLeft = marginLeft;
        this.mainContent.style.marginRight = marginRight;
    }

    // Method to hide all docks for distraction-free mode
    hideAllDocks() {
        this.hideDock('left');
        this.hideDock('right');
    }

    // Method to show all docks
    showAllDocks() {
        this.showDock('left');
        this.showDock('right');
    }

    // Method to toggle distraction-free mode
    toggleDistractionFreeMode() {
        const leftHidden = this.leftDock?.classList.contains('hidden');
        const rightHidden = this.rightDock?.classList.contains('hidden');

        if (leftHidden && rightHidden) {
            this.showAllDocks();
        } else {
            this.hideAllDocks();
        }
    }
}

// Initialize everything together
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM LOADED - Starting LUKHAS v2 System');
    
    // Initialize neural network
    const neuralNet = new SimpleNeuralNetwork();
    neuralNet.init();
    
    // Initialize dashboard
    const dashboard = new DashboardIntegration();
    dashboard.init();
    
    // Initialize dock manager
    const dockManager = new DockManager();
    dockManager.init();
});

// Also try immediate initialization if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for it
} else {
    // DOM is already loaded
    console.log('DOM ALREADY LOADED - Starting LUKHAS v2 System immediately');
    
    const neuralNet = new SimpleNeuralNetwork();
    neuralNet.init();
    
    const dashboard = new DashboardIntegration();
    dashboard.init();
    
    const dockManager = new DockManager();
    dockManager.init();
}