// LUKHAS v2 - Clean Neural Network Background (No Lambda)
console.log('Loading clean neural network background (no lambda)...');

class NeuralNetworkBackground {
    constructor() {
        this.nodes = [];
        this.connections = [];
        this.animationId = null;
    }

    init() {
        console.log('Initializing clean neural network background...');
        this.createNeuralNetworkScene();
        this.startAnimation();
    }

    createNeuralNetworkScene() {
        const container = document.querySelector('.background-effects');
        if (!container) {
            console.log('No background-effects container found');
            return;
        }

        // Remove existing scene
        const existingScene = container.querySelector('.space-scene, .neural-network-scene');
        if (existingScene) {
            existingScene.remove();
        }

        // Create neural network container
        const networkScene = document.createElement('div');
        networkScene.className = 'neural-network-scene';
        networkScene.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            overflow: hidden;
            z-index: 1;
            background:
                radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                linear-gradient(135deg, rgba(15, 15, 35, 0.8) 0%, rgba(26, 26, 46, 0.9) 50%, rgba(22, 33, 62, 0.8) 100%);
        `;

        // Create network layers
        this.createNetworkLayers(networkScene);

        // Create flowing data connections
        this.createDataConnections(networkScene);

        // Add floating particles
        this.createFloatingParticles(networkScene);

        container.appendChild(networkScene);

        // Add styles
        this.addNeuralNetworkStyles();

        console.log('Neural network scene created successfully');
    }

    createNetworkLayers(container) {
        // Create multiple layers of nodes
        for (let layer = 0; layer < 3; layer++) {
            const layerDiv = document.createElement('div');
            layerDiv.className = `network-layer layer-${layer}`;
            layerDiv.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                opacity: ${0.3 + layer * 0.2};
                z-index: ${layer + 1};
            `;

            // Create nodes for this layer
            const nodeCount = 12 - layer * 3;
            for (let i = 0; i < nodeCount; i++) {
                const node = document.createElement('div');
                node.className = 'network-node';
                node.style.cssText = `
                    position: absolute;
                    width: ${4 + layer * 2}px;
                    height: ${4 + layer * 2}px;
                    background: rgba(59, 130, 246, ${0.6 + layer * 0.2});
                    border-radius: 50%;
                    left: ${Math.random() * 90 + 5}%;
                    top: ${Math.random() * 90 + 5}%;
                    box-shadow: 0 0 ${6 + layer * 4}px rgba(59, 130, 246, ${0.4 + layer * 0.2});
                    animation: networkPulse ${2 + Math.random() * 2}s infinite ease-in-out alternate;
                `;

                layerDiv.appendChild(node);
            }

            container.appendChild(layerDiv);
        }
    }

    createDataConnections(container) {
        // Create animated connection lines
        for (let i = 0; i < 8; i++) {
            const connection = document.createElement('div');
            connection.className = 'data-connection';
            connection.style.cssText = `
                position: absolute;
                width: 2px;
                height: ${100 + Math.random() * 200}px;
                background: linear-gradient(
                    to bottom,
                    transparent 0%,
                    rgba(59, 130, 246, 0.4) 20%,
                    rgba(139, 92, 246, 0.6) 50%,
                    rgba(59, 130, 246, 0.4) 80%,
                    transparent 100%
                );
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                transform: rotate(${Math.random() * 360}deg);
                animation: dataFlow ${3 + Math.random() * 4}s infinite linear;
                opacity: 0.7;
            `;

            container.appendChild(connection);
        }
    }

    createFloatingParticles(container) {
        // Create floating data particles
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.cssText = `
                position: absolute;
                width: 2px;
                height: 2px;
                background: rgba(59, 130, 246, 0.8);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: particleFloat ${8 + Math.random() * 12}s infinite linear;
                box-shadow: 0 0 4px rgba(59, 130, 246, 0.6);
            `;

            container.appendChild(particle);
        }
    }

    addNeuralNetworkStyles() {
        const existingStyles = document.querySelector('#neural-network-styles');
        if (existingStyles) return;

        const style = document.createElement('style');
        style.id = 'neural-network-styles';
        style.textContent = `
            @keyframes networkPulse {
                0% { transform: scale(0.8); opacity: 0.6; }
                100% { transform: scale(1.2); opacity: 1; }
            }

            @keyframes dataFlow {
                0% {
                    transform: translateY(-100px) rotate(var(--rotation));
                    opacity: 0;
                }
                10% { opacity: 0.8; }
                90% { opacity: 0.8; }
                100% {
                    transform: translateY(100vh) rotate(var(--rotation));
                    opacity: 0;
                }
            }

            @keyframes particleFloat {
                0% {
                    transform: translate(0, 100vh) scale(0);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                    transform: translate(0, 90vh) scale(1);
                }
                90% {
                    opacity: 1;
                    transform: translate(100px, 10vh) scale(1);
                }
                100% {
                    transform: translate(200px, 0) scale(0);
                    opacity: 0;
                }
            }

            .neural-network-scene .network-node {
                transition: all 0.3s ease;
            }

            .neural-network-scene .network-node:hover {
                transform: scale(1.5) !important;
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.8) !important;
            }

            .neural-network-scene .data-connection {
                will-change: transform;
            }

            .neural-network-scene .floating-particle {
                will-change: transform, opacity;
            }

            /* Responsive adjustments */
            @media (max-width: 768px) {
                .neural-network-scene .network-node {
                    width: 3px !important;
                    height: 3px !important;
                }

                .neural-network-scene .data-connection {
                    width: 1px !important;
                }
            }
        `;

        document.head.appendChild(style);
    }

    startAnimation() {
        // Animation is handled by CSS, but we can add dynamic effects here
        this.animateConnections();
    }

    animateConnections() {
        const connections = document.querySelectorAll('.data-connection');
        connections.forEach((connection, index) => {
            connection.style.setProperty('--rotation', `${Math.random() * 360}deg`);

            // Randomly restart animations
            setTimeout(() => {
                connection.style.animation = 'none';
                setTimeout(() => {
                    connection.style.animation = `dataFlow ${3 + Math.random() * 4}s infinite linear`;
                }, 100);
            }, (index * 1000) + Math.random() * 5000);
        });
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        const scene = document.querySelector('.neural-network-scene');
        if (scene) {
            scene.remove();
        }

        const styles = document.querySelector('#neural-network-styles');
        if (styles) {
            styles.remove();
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const neuralNetwork = new NeuralNetworkBackground();
        neuralNetwork.init();
        console.log('Clean Neural Network Background initialized');
    });
} else {
    const neuralNetwork = new NeuralNetworkBackground();
    neuralNetwork.init();
    console.log('Clean Neural Network Background initialized immediately');
}
