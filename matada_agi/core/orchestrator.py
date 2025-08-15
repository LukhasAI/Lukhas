#!/usr/bin/env python3
"""
MATADA Cognitive Orchestrator
Routes queries through MATADA nodes with full traceability
Implements the vision from March 24, 2025
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


@dataclass
class ExecutionTrace:
    """Complete trace of cognitive processing"""
    timestamp: datetime
    node_id: str
    input_data: Dict
    output_data: Dict
    matada_node: Dict  # The actual MATADA node created
    processing_time: float
    validation_result: bool
    reasoning_chain: List[str]


class CognitiveOrchestrator:
    """
    Main orchestrator that routes queries through MATADA nodes.
    Every thought becomes a traceable, governed node.
    """
    
    def __init__(self):
        self.available_nodes = {}
        self.context_memory = []  # Recent MATADA nodes for context
        self.execution_trace = []  # Full execution history
        self.matada_graph = {}  # All MATADA nodes by ID
        
    def register_node(self, name: str, node: 'CognitiveNode'):
        """Register a cognitive node that emits MATADA format"""
        self.available_nodes[name] = node
        print(f"✓ Registered node: {name}")
        
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process user query through MATADA nodes
        Returns result with full trace
        """
        start_time = time.time()
        
        # 1. Intent Analysis - Create INTENT node
        intent_node = self._analyze_intent(user_input)
        self.matada_graph[intent_node['id']] = intent_node
        
        # 2. Node Selection - Create DECISION node
        selected_node_name = self._select_node(intent_node)
        decision_node = self._create_decision_node(
            f"Selected {selected_node_name} for processing",
            trigger_id=intent_node['id']
        )
        self.matada_graph[decision_node['id']] = decision_node
        
        # 3. Process through selected node
        if selected_node_name not in self.available_nodes:
            return {
                'error': f'No node available for {selected_node_name}',
                'trace': self.execution_trace
            }
            
        node = self.available_nodes[selected_node_name]
        result = node.process({'query': user_input})
        
        # 4. Validation
        if 'validator' in self.available_nodes:
            validator = self.available_nodes['validator']
            validation = validator.validate_output(result)
            
            # Create validation reflection node
            reflection_node = self._create_reflection_node(
                result_node=result['matada_node'],
                validation=validation
            )
            self.matada_graph[reflection_node['id']] = reflection_node
        
        # 5. Build execution trace
        trace = ExecutionTrace(
            timestamp=datetime.now(),
            node_id=selected_node_name,
            input_data={'query': user_input},
            output_data=result,
            matada_node=result.get('matada_node', {}),
            processing_time=time.time() - start_time,
            validation_result=validation if 'validator' in self.available_nodes else True,
            reasoning_chain=self._build_reasoning_chain()
        )
        self.execution_trace.append(trace)
        
        return {
            'answer': result.get('answer', 'No answer'),
            'confidence': result.get('confidence', 0.0),
            'matada_nodes': list(self.matada_graph.values()),
            'trace': asdict(trace),
            'reasoning_chain': trace.reasoning_chain
        }
    
    def _analyze_intent(self, user_input: str) -> Dict:
        """Create INTENT MATADA node from user input"""
        intent_node = {
            'id': str(uuid.uuid4()),
            'type': 'INTENT',
            'state': {
                'confidence': 0.9,
                'salience': 1.0,
                'input_text': user_input
            },
            'timestamp': datetime.now().isoformat(),
            'links': [],
            'evolves_to': [],
            'triggers': [],
            'reflections': []
        }
        
        # Simple intent detection
        if any(op in user_input for op in ['+', '-', '*', '/', '=']):
            intent_node['state']['intent'] = 'mathematical'
        elif '?' in user_input.lower():
            intent_node['state']['intent'] = 'question'
        elif 'dog' in user_input.lower() or 'see' in user_input.lower():
            intent_node['state']['intent'] = 'perception'
        else:
            intent_node['state']['intent'] = 'general'
            
        return intent_node
    
    def _select_node(self, intent_node: Dict) -> str:
        """Select appropriate node based on intent"""
        intent = intent_node['state'].get('intent', 'general')
        
        if intent == 'mathematical':
            return 'math'
        elif intent == 'question':
            return 'facts'
        elif intent == 'perception':
            return 'vision'  # Would handle "boy sees dog"
        else:
            return 'facts'  # Default
    
    def _create_decision_node(self, decision: str, trigger_id: str) -> Dict:
        """Create DECISION MATADA node"""
        return {
            'id': str(uuid.uuid4()),
            'type': 'DECISION',
            'state': {
                'confidence': 0.85,
                'salience': 0.9,
                'decision': decision
            },
            'timestamp': datetime.now().isoformat(),
            'links': [{'target': trigger_id, 'type': 'causal', 'weight': 1.0}],
            'evolves_to': [],
            'triggers': [trigger_id],
            'reflections': []
        }
    
    def _create_reflection_node(self, result_node: Dict, validation: bool) -> Dict:
        """Create REFLECTION MATADA node"""
        reflection_type = 'affirmation' if validation else 'regret'
        return {
            'id': str(uuid.uuid4()),
            'type': 'REFLECTION',
            'state': {
                'confidence': 1.0 if validation else 0.3,
                'valence': 0.8 if validation else -0.5,
                'reflection_type': reflection_type,
                'validation_result': validation
            },
            'timestamp': datetime.now().isoformat(),
            'links': [{'target': result_node['id'], 'type': 'reflection', 'weight': 1.0}],
            'evolves_to': [],
            'triggers': [result_node['id']],
            'reflections': [{
                'type': reflection_type,
                'cause': 'validation_check',
                'timestamp': datetime.now().isoformat()
            }]
        }
    
    def _build_reasoning_chain(self) -> List[str]:
        """Build human-readable reasoning chain from MATADA nodes"""
        chain = []
        for node_id, node in self.matada_graph.items():
            if node['type'] == 'INTENT':
                chain.append(f"Understood intent: {node['state'].get('intent', 'unknown')}")
            elif node['type'] == 'DECISION':
                chain.append(f"Decision: {node['state'].get('decision', 'unknown')}")
            elif node['type'] == 'REFLECTION':
                chain.append(f"Reflection: {node['state'].get('reflection_type', 'unknown')}")
        return chain
    
    def get_causal_chain(self, node_id: str) -> List[Dict]:
        """Trace back the causal chain for any node"""
        if node_id not in self.matada_graph:
            return []
        
        chain = []
        visited = set()
        to_visit = [node_id]
        
        while to_visit:
            current_id = to_visit.pop(0)
            if current_id in visited:
                continue
                
            visited.add(current_id)
            node = self.matada_graph.get(current_id)
            if node:
                chain.append(node)
                # Follow triggers backward
                for trigger_id in node.get('triggers', []):
                    if trigger_id not in visited:
                        to_visit.append(trigger_id)
                        
        return chain