#!/usr/bin/env python3
"""

#TAG:qim
#TAG:quantum_states
#TAG:neuroplastic
#TAG:colony


Generate visual connectivity maps for LUKHAS hybrid components
Creates both JSON and HTML visualizations
"""

import json
import os
from collections import defaultdict
from datetime import datetime

def generate_connectivity_json():
    """Generate the master connectivity index"""
    
    # Load the hybrid component mapping
    with open('docs/reports/analysis/PWM_HYBRID_COMPONENT_MAPPING.json', 'r') as f:
        hybrid_data = json.load(f)
    
    connectivity = {
        "generated_at": datetime.now().isoformat(),
        "system_name": "LUKHAS AI - Neuroplastic Architecture",
        "total_modules": 7,
        "total_hybrid_components": hybrid_data['summary']['total_hybrid_components'] if 'summary' in hybrid_data else 203,
        
        "modules": {
            "CORE": {
                "role": "Brain Stem - Foundation",
                "status": "always_active",
                "hybrid_subdirs": [
                    "nervous_system/tagging",
                    "nervous_system/colony_base", 
                    "nervous_system/propagation",
                    "hybrid_components/*"
                ],
                "connections": {
                    "outgoing": ["consciousness", "memory", "quantum", "emotion", "governance", "bridge"],
                    "incoming": ["all_modules"],
                    "bidirectional": ["consciousness", "memory", "quantum"]
                },
                "hormone_production": ["GABA", "Glutamate"],
                "stress_response": "maintain_basics"
            },
            
            "CONSCIOUSNESS": {
                "role": "Cortex - Awareness & Decision",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "quantum_integration",
                    "awareness",
                    "systems/dream_engine",
                    "meta_cognitive"
                ],
                "connections": {
                    "outgoing": ["memory", "emotion", "quantum", "governance"],
                    "incoming": ["core", "memory", "emotion"],
                    "bidirectional": ["memory", "emotion", "quantum"]
                },
                "hormone_production": ["Dopamine", "Serotonin"],
                "stress_response": "delegate_to_governance"
            },
            
            "MEMORY": {
                "role": "Hippocampus - Storage & Recall",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "emotional_memory_manager",
                    "fold_system",
                    "trauma_repair",
                    "systems/dream_memory"
                ],
                "connections": {
                    "outgoing": ["consciousness", "emotion", "quantum"],
                    "incoming": ["all_modules"],
                    "bidirectional": ["consciousness", "emotion"]
                },
                "hormone_production": ["Oxytocin"],
                "stress_response": "activate_compression"
            },
            
            "QUANTUM": {
                "role": "Quantum Processor - Computation",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "processing",
                    "bio_integration",
                    "consciousness_collapse",
                    "pattern_recognition"
                ],
                "connections": {
                    "outgoing": ["consciousness", "memory", "bio"],
                    "incoming": ["core", "consciousness", "governance"],
                    "bidirectional": ["consciousness", "memory", "bio"]
                },
                "hormone_production": ["Glutamate"],
                "stress_response": "crisis_acceleration"
            },
            
            "EMOTION": {
                "role": "Limbic System - Affect & Mood",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "affect_detection",
                    "mood_regulation",
                    "colony_emotions",
                    "memory_emotions"
                ],
                "connections": {
                    "outgoing": ["memory", "consciousness", "governance"],
                    "incoming": ["consciousness", "memory", "core"],
                    "bidirectional": ["memory", "consciousness"]
                },
                "hormone_production": ["Cortisol", "Serotonin", "Oxytocin"],
                "stress_response": "trauma_processing"
            },
            
            "GOVERNANCE": {
                "role": "Immune System - Protection & Ethics",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "guardian_system",
                    "ethics_engine",
                    "drift_detection",
                    "emergency_protocols"
                ],
                "connections": {
                    "outgoing": ["all_modules"],
                    "incoming": ["core", "consciousness"],
                    "bidirectional": ["core"]
                },
                "hormone_production": ["Cortisol", "Adrenaline", "GABA"],
                "stress_response": "assume_control"
            },
            
            "BRIDGE": {
                "role": "Peripheral Nervous - I/O",
                "status": "adaptive",
                "hybrid_subdirs": [
                    "api_gateway",
                    "llm_wrappers",
                    "emergency_channel",
                    "human_interface"
                ],
                "connections": {
                    "outgoing": ["core", "consciousness", "memory"],
                    "incoming": ["all_modules"],
                    "bidirectional": ["core"]
                },
                "hormone_production": ["Dopamine"],
                "stress_response": "lockdown_mode"
            }
        },
        
        "hybrid_relationships": {
            "memory-emotion": {
                "shared_components": [
                    "emotional_memory_manager",
                    "affect_detection",
                    "mood_memory_coupling"
                ],
                "signal_types": ["Oxytocin", "Serotonin"],
                "strength": 0.85
            },
            "consciousness-quantum": {
                "shared_components": [
                    "quantum_integration",
                    "conscious_collapse",
                    "awareness_superposition"
                ],
                "signal_types": ["Glutamate", "GABA"],
                "strength": 0.75
            },
            "governance-all": {
                "shared_components": [
                    "ethics_enforcement",
                    "drift_monitoring",
                    "guardian_oversight"
                ],
                "signal_types": ["Cortisol", "Adrenaline"],
                "strength": 0.95
            }
        },
        
        "neuroplastic_states": {
            "normal": {
                "hierarchy": ["core", "consciousness", "memory", "quantum", "emotion", "governance", "bridge"],
                "active_hormones": ["Serotonin", "Dopamine", "Glutamate"]
            },
            "stress": {
                "hierarchy": ["governance", "core", "quantum", "consciousness"],
                "active_hormones": ["Cortisol", "Adrenaline", "GABA"],
                "suppressed": ["emotion", "creativity", "bridge"]
            },
            "trauma": {
                "hierarchy": ["emotion", "memory", "governance", "core"],
                "active_hormones": ["Cortisol", "Oxytocin", "GABA"],
                "enhanced": ["trauma_vault", "repair_mechanisms"]
            },
            "overload": {
                "hierarchy": ["memory", "quantum", "core"],
                "active_hormones": ["Adrenaline", "Glutamate"],
                "enhanced": ["compression", "folding"]
            }
        }
    }
    
    return connectivity

def generate_html_visualization(connectivity):
    """Generate an interactive HTML visualization"""
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS AI - Neuroplastic Connectivity Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        
        #visualization {
            width: 100%;
            height: 800px;
            border: 1px solid #00ff00;
            position: relative;
            overflow: hidden;
        }
        
        .module {
            position: absolute;
            padding: 20px;
            border: 2px solid #00ff00;
            border-radius: 10px;
            background-color: rgba(0, 50, 0, 0.8);
            cursor: move;
            transition: all 0.3s;
        }
        
        .module:hover {
            box-shadow: 0 0 20px #00ff00;
            transform: scale(1.05);
        }
        
        .module h3 {
            margin: 0 0 10px 0;
            color: #00ff00;
        }
        
        .module.stress {
            border-color: #ff0000;
            box-shadow: 0 0 20px #ff0000;
        }
        
        .connection {
            stroke: #00ff00;
            stroke-width: 2;
            fill: none;
            opacity: 0.5;
        }
        
        .connection.bidirectional {
            stroke-width: 4;
            opacity: 0.8;
        }
        
        .hormone-tag {
            display: inline-block;
            padding: 2px 8px;
            margin: 2px;
            background-color: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            border-radius: 10px;
            font-size: 12px;
        }
        
        #controls {
            margin-top: 20px;
            text-align: center;
        }
        
        button {
            background-color: #003300;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px 20px;
            margin: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background-color: #005500;
        }
        
        #info {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 300px;
            padding: 20px;
            background-color: rgba(0, 30, 0, 0.9);
            border: 1px solid #00ff00;
            display: none;
        }
    </style>
</head>
<body>
    <h1>LUKHAS AI - Neuroplastic Connectivity Map</h1>
    
    <div id="visualization">
        <svg id="connections" style="position: absolute; width: 100%; height: 100%;"></svg>
    </div>
    
    <div id="controls">
        <button onclick="setState('normal')">Normal State</button>
        <button onclick="setState('stress')">Stress Response</button>
        <button onclick="setState('trauma')">Trauma Response</button>
        <button onclick="setState('overload')">Memory Overload</button>
    </div>
    
    <div id="info"></div>
    
    <script>
        const connectivity = """ + json.dumps(connectivity, indent=2) + """;
        
        let currentState = 'normal';
        const modules = connectivity.modules;
        const states = connectivity.neuroplastic_states;
        
        // Position modules in a circle
        const centerX = 400;
        const centerY = 400;
        const radius = 250;
        const moduleNames = Object.keys(modules);
        
        moduleNames.forEach((name, index) => {
            const angle = (2 * Math.PI * index) / moduleNames.length;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            createModule(name, x, y);
        });
        
        function createModule(name, x, y) {
            const module = modules[name];
            const div = document.createElement('div');
            div.className = 'module';
            div.id = 'module-' + name;
            div.style.left = x + 'px';
            div.style.top = y + 'px';
            
            const hormones = module.hormone_production.map(h => 
                `<span class="hormone-tag">${h}</span>`
            ).join('');
            
            div.innerHTML = `
                <h3>${name}</h3>
                <div>${module.role}</div>
                <div style="margin-top: 10px;">${hormones}</div>
            `;
            
            div.onclick = () => showInfo(name);
            
            document.getElementById('visualization').appendChild(div);
        }
        
        function drawConnections() {
            const svg = d3.select('#connections');
            svg.selectAll('*').remove();
            
            moduleNames.forEach(name => {
                const module = modules[name];
                const sourceEl = document.getElementById('module-' + name);
                const sourceX = parseInt(sourceEl.style.left) + sourceEl.offsetWidth / 2;
                const sourceY = parseInt(sourceEl.style.top) + sourceEl.offsetHeight / 2;
                
                module.connections.bidirectional.forEach(target => {
                    if (moduleNames.includes(target)) {
                        const targetEl = document.getElementById('module-' + target);
                        if (targetEl) {
                            const targetX = parseInt(targetEl.style.left) + targetEl.offsetWidth / 2;
                            const targetY = parseInt(targetEl.style.top) + targetEl.offsetHeight / 2;
                            
                            svg.append('path')
                                .attr('class', 'connection bidirectional')
                                .attr('d', `M ${sourceX} ${sourceY} L ${targetX} ${targetY}`);
                        }
                    }
                });
            });
        }
        
        function setState(state) {
            currentState = state;
            const stateConfig = states[state];
            
            // Reset all modules
            document.querySelectorAll('.module').forEach(el => {
                el.classList.remove('stress');
                el.style.opacity = '0.3';
            });
            
            // Highlight active modules
            stateConfig.hierarchy.forEach((moduleName, index) => {
                const el = document.getElementById('module-' + moduleName.toUpperCase());
                if (el) {
                    el.style.opacity = '1';
                    if (state !== 'normal') {
                        el.classList.add('stress');
                    }
                }
            });
            
            // Update info
            const infoDiv = document.getElementById('info');
            infoDiv.style.display = 'block';
            infoDiv.innerHTML = `
                <h3>${state.toUpperCase()} STATE</h3>
                <p><strong>Hierarchy:</strong> ${stateConfig.hierarchy.join(' → ')}</p>
                <p><strong>Active Hormones:</strong> ${stateConfig.active_hormones.join(', ')}</p>
                ${stateConfig.suppressed ? `<p><strong>Suppressed:</strong> ${stateConfig.suppressed.join(', ')}</p>` : ''}
                ${stateConfig.enhanced ? `<p><strong>Enhanced:</strong> ${stateConfig.enhanced.join(', ')}</p>` : ''}
            `;
        }
        
        function showInfo(moduleName) {
            const module = modules[moduleName];
            const infoDiv = document.getElementById('info');
            infoDiv.style.display = 'block';
            infoDiv.innerHTML = `
                <h3>${moduleName}</h3>
                <p><strong>Role:</strong> ${module.role}</p>
                <p><strong>Status:</strong> ${module.status}</p>
                <p><strong>Hormones:</strong> ${module.hormone_production.join(', ')}</p>
                <p><strong>Stress Response:</strong> ${module.stress_response}</p>
                <p><strong>Hybrid Components:</strong></p>
                <ul>${module.hybrid_subdirs.map(d => `<li>${d}</li>`).join('')}</ul>
            `;
        }
        
        // Initial setup
        setTimeout(() => {
            drawConnections();
            setState('normal');
        }, 100);
        
        // Make modules draggable
        document.querySelectorAll('.module').forEach(el => {
            let isDragging = false;
            let startX, startY;
            
            el.addEventListener('mousedown', (e) => {
                isDragging = true;
                startX = e.clientX - parseInt(el.style.left);
                startY = e.clientY - parseInt(el.style.top);
            });
            
            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    el.style.left = (e.clientX - startX) + 'px';
                    el.style.top = (e.clientY - startY) + 'px';
                    drawConnections();
                }
            });
            
            document.addEventListener('mouseup', () => {
                isDragging = false;
            });
        });
    </script>
</body>
</html>
"""
    
    return html_template

def main():
    print("Generating LUKHAS Neuroplastic Connectivity Map...")
    
    # Generate connectivity data
    connectivity = generate_connectivity_json()
    
    # Save JSON
    json_path = 'docs/LUKHAS_CONNECTIVITY_INDEX.json'
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(connectivity, f, indent=2)
    print(f"✓ Saved connectivity index to {json_path}")
    
    # Generate and save HTML
    html = generate_html_visualization(connectivity)
    html_path = 'docs/LUKHAS_CONNECTIVITY_MAP.html'
    with open(html_path, 'w') as f:
        f.write(html)
    print(f"✓ Saved interactive map to {html_path}")
    
    # Print summary
    print("\n=== Connectivity Summary ===")
    print(f"Total Modules: {connectivity['total_modules']}")
    print(f"Total Hybrid Components: {connectivity['total_hybrid_components']}")
    print(f"\nNeuroplastic States: {list(connectivity['neuroplastic_states'].keys())}")
    print(f"\nKey Hybrid Relationships:")
    for rel, data in connectivity['hybrid_relationships'].items():
        print(f"  {rel}: strength={data['strength']}, signals={data['signal_types']}")

if __name__ == "__main__":
    main()