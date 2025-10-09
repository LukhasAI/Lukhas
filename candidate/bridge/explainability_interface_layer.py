"""
Bridge Explainability Interface Layer

Provides multi-modal AI explanation capabilities with formal proof generation,
template-based explanations, and Guardian integration for ethical AI.

Part of BATCH-JULES-API-GOVERNANCE-02
Tasks: s5t6u7v8, w9x0y1z2, a3b4c5d6, e7f8g9h0, i1j2k3l4, m5n6o7p8, q9r0s1t2, u3v4w5x6, y7z8a9b0

Trinity Framework:
- 🧠 Consciousness: Multi-modal explanations, reasoning traces
- 🛡️ Guardian: Formal proofs, cryptographic signing, completeness metrics
- ⚛️ Identity: SRD verification, audit trails
"""

import json
import yaml
import hashlib
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from functools import lru_cache
from collections import OrderedDict


class ExplanationMode(Enum):
    """Explanation generation modes."""
    TEXT = "text"
    VISUAL = "visual"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    FORMAL_PROOF = "formal_proof"
    SYMBOLIC = "symbolic"


class ExplanationLevel(Enum):
    """Explanation detail levels."""
    SIMPLE = "simple"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    EXPERT = "expert"


class ProofSystem(Enum):
    """Formal proof systems."""
    PROPOSITIONAL = "propositional"
    FIRST_ORDER = "first_order"
    TEMPORAL = "temporal"
    MODAL = "modal"


@dataclass
class ExplanationTemplate:
    """Template for explanation generation."""
    template_id: str
    name: str
    mode: ExplanationMode
    level: ExplanationLevel
    template: str
    variables: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExplanationTemplate':
        """Create from dictionary."""
        return cls(
            template_id=data['template_id'],
            name=data['name'],
            mode=ExplanationMode(data['mode']),
            level=ExplanationLevel(data['level']),
            template=data['template'],
            variables=data['variables'],
            metadata=data.get('metadata', {})
        )


@dataclass
class FormalProof:
    """Formal proof structure."""
    proof_id: str
    system: ProofSystem
    premises: List[str]
    conclusion: str
    steps: List[Dict[str, Any]]
    valid: bool
    timestamp: int
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['system'] = self.system.value
        return result


@dataclass
class CompletenessMetrics:
    """Explanation completeness metrics."""
    coverage_score: float  # 0-1: How much of the decision is explained
    depth_score: float     # 0-1: Level of detail provided
    clarity_score: float   # 0-1: Readability/understandability
    consistency_score: float  # 0-1: Internal consistency
    overall_score: float   # Weighted average
    missing_elements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Explanation:
    """Generated explanation."""
    explanation_id: str
    mode: ExplanationMode
    level: ExplanationLevel
    content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any]
    completeness: Optional[CompletenessMetrics] = None
    formal_proof: Optional[FormalProof] = None
    reasoning_trace: Optional[List[Dict[str, Any]]] = None
    timestamp: int = field(default_factory=lambda: int(time.time()))
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'explanation_id': self.explanation_id,
            'mode': self.mode.value,
            'level': self.level.value,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
        if self.completeness:
            result['completeness'] = self.completeness.to_dict()
        if self.formal_proof:
            result['formal_proof'] = self.formal_proof.to_dict()
        if self.reasoning_trace:
            result['reasoning_trace'] = self.reasoning_trace
        return result


class ExplainabilityCache:
    """
    LRU cache for explanations.
    
    Task: TODO-HIGH-BRIDGE-EXPLAIN-e7f8g9h0 (LRU cache implementation)
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached explanations
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, Explanation] = OrderedDict()
        self._stats = {'hits': 0, 'misses': 0, 'evictions': 0}

    def get(self, key: str) -> Optional[Explanation]:
        """
        Get explanation from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached explanation or None
        """
        if key in self._cache:
            self._stats['hits'] += 1
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        else:
            self._stats['misses'] += 1
            return None

    def put(self, key: str, explanation: Explanation) -> None:
        """
        Put explanation in cache.
        
        Args:
            key: Cache key
            explanation: Explanation to cache
        """
        if key in self._cache:
            # Update existing
            self._cache.move_to_end(key)
            self._cache[key] = explanation
        else:
            # Add new
            if len(self._cache) >= self.max_size:
                # Evict least recently used
                self._cache.popitem(last=False)
                self._stats['evictions'] += 1
            self._cache[key] = explanation

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return self._stats.copy()


class ExplainabilityInterface:
    """
    Multi-Modal Explainability Interface
    
    Provides comprehensive AI explanation capabilities including:
    - Multi-modal explanations (text, visual, audio)
    - Template-based generation
    - Formal proof generation
    - Symbolic reasoning traces
    - MEG (Memory Episodic Graph) integration
    - Completeness and clarity metrics
    - Cryptographic signing (SRD)
    
    Trinity Integration:
    - 🧠 Consciousness: Reasoning traces, MEG integration
    - 🛡️ Guardian: Formal proofs, completeness verification
    - ⚛️ Identity: SRD cryptographic signing
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        cache_size: int = 1000,
        symbolic_engine: Optional[Any] = None,
        meg_client: Optional[Any] = None
    ):
        """
        Initialize Explainability Interface.
        
        Args:
            template_dir: Directory containing explanation templates
            cache_size: Maximum cache size
            symbolic_engine: Optional symbolic reasoning engine
            meg_client: Optional MEG client for episodic memory
        """
        self.template_dir = template_dir
        self.cache = ExplainabilityCache(max_size=cache_size)
        self.symbolic_engine = symbolic_engine
        self.meg_client = meg_client
        
        # Load templates
        self.templates: Dict[str, ExplanationTemplate] = {}
        if template_dir and template_dir.exists():
            self._load_templates()

    async def explain(
        self,
        decision: Dict[str, Any],
        mode: ExplanationMode = ExplanationMode.TEXT,
        level: ExplanationLevel = ExplanationLevel.DETAILED,
        include_proof: bool = False,
        include_trace: bool = False,
        sign_explanation: bool = False
    ) -> Explanation:
        """
        Generate explanation for a decision.
        
        Args:
            decision: Decision data to explain
            mode: Explanation mode (text, visual, audio, etc.)
            level: Detail level
            include_proof: Include formal proof
            include_trace: Include reasoning trace
            sign_explanation: Cryptographically sign explanation
        
        Returns:
            Generated Explanation
        
        Tasks:
        - TODO-HIGH-BRIDGE-EXPLAIN-s5t6u7v8: Multi-modal support
        - TODO-HIGH-BRIDGE-EXPLAIN-a3b4c5d6: Formal proof generation
        - TODO-HIGH-BRIDGE-EXPLAIN-m5n6o7p8: Symbolic reasoning traces
        - TODO-HIGH-BRIDGE-EXPLAIN-y7z8a9b0: SRD cryptographic signing
        """
        # Generate cache key
        cache_key = self._generate_cache_key(decision, mode, level)
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached and not include_proof and not include_trace:
            return cached
        
        # Generate explanation content based on mode
        if mode == ExplanationMode.MULTIMODAL:
            content = await self._generate_multimodal_explanation(decision, level)
        elif mode == ExplanationMode.FORMAL_PROOF:
            content = await self._generate_formal_proof_explanation(decision)
        elif mode == ExplanationMode.SYMBOLIC:
            content = await self._generate_symbolic_explanation(decision, level)
        else:
            content = await self._generate_text_explanation(decision, level)
        
        # Generate explanation ID
        explanation_id = f"exp_{hashlib.sha256(cache_key.encode()).hexdigest()[:16]}"
        
        # Create base explanation
        explanation = Explanation(
            explanation_id=explanation_id,
            mode=mode,
            level=level,
            content=content,
            metadata={
                'decision_id': decision.get('id', 'unknown'),
                'generated_at': int(time.time())
            }
        )
        
        # Add formal proof if requested
        if include_proof:
            explanation.formal_proof = await self.generate_formal_proof(decision)
        
        # Add reasoning trace if requested
        if include_trace:
            explanation.reasoning_trace = await self.generate_reasoning_trace(decision)
        
        # Calculate completeness metrics
        explanation.completeness = await self.calculate_completeness(explanation, decision)
        
        # Sign explanation if requested
        if sign_explanation:
            explanation.signature = await self._sign_explanation(explanation)
        
        # Cache explanation
        self.cache.put(cache_key, explanation)
        
        return explanation

    async def generate_formal_proof(
        self,
        decision: Dict[str, Any],
        system: ProofSystem = ProofSystem.FIRST_ORDER
    ) -> FormalProof:
        """
        Generate formal proof for a decision.
        
        Args:
            decision: Decision to prove
            system: Proof system to use
        
        Returns:
            FormalProof object
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-a3b4c5d6 (Formal proof generation)
        """
        # Extract premises from decision
        premises = decision.get('premises', [])
        conclusion = decision.get('conclusion', decision.get('result', 'unknown'))
        
        # Generate proof steps
        steps = []
        
        # Step 1: Premise validation
        for i, premise in enumerate(premises):
            steps.append({
                'step': i + 1,
                'type': 'premise',
                'statement': premise,
                'justification': 'Given'
            })
        
        # Step 2: Inference steps
        if 'reasoning_steps' in decision:
            for i, step in enumerate(decision['reasoning_steps']):
                steps.append({
                    'step': len(premises) + i + 1,
                    'type': 'inference',
                    'statement': step.get('statement', ''),
                    'justification': step.get('rule', 'Modus Ponens'),
                    'from_steps': step.get('depends_on', [])
                })
        
        # Step 3: Conclusion
        steps.append({
            'step': len(steps) + 1,
            'type': 'conclusion',
            'statement': conclusion,
            'justification': 'From previous steps',
            'from_steps': list(range(1, len(steps) + 1))
        })
        
        # Validate proof (simplified - real implementation would use theorem prover)
        valid = self._validate_proof_steps(steps, system)
        
        proof = FormalProof(
            proof_id=f"proof_{hashlib.sha256(str(decision).encode()).hexdigest()[:16]}",
            system=system,
            premises=premises,
            conclusion=conclusion,
            steps=steps,
            valid=valid,
            timestamp=int(time.time())
        )
        
        return proof

    async def generate_reasoning_trace(
        self,
        decision: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate symbolic reasoning trace.
        
        Args:
            decision: Decision data
        
        Returns:
            List of reasoning steps
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-m5n6o7p8 (Symbolic engine integration)
        """
        trace = []
        
        # Use symbolic engine if available
        if self.symbolic_engine:
            try:
                trace = await self.symbolic_engine.trace_reasoning(decision)
                return trace
            except Exception:
                pass
        
        # Fallback: Generate basic trace from decision data
        if 'reasoning_steps' in decision:
            for i, step in enumerate(decision['reasoning_steps']):
                trace.append({
                    'step_id': i + 1,
                    'operation': step.get('operation', 'infer'),
                    'input': step.get('input', {}),
                    'output': step.get('output', {}),
                    'confidence': step.get('confidence', 1.0),
                    'symbolic_form': step.get('symbolic', '')
                })
        
        # Add MEG integration if available
        if self.meg_client:
            meg_context = await self._get_meg_context(decision)
            if meg_context:
                trace.append({
                    'step_id': len(trace) + 1,
                    'operation': 'meg_recall',
                    'input': {'decision_id': decision.get('id')},
                    'output': meg_context,
                    'confidence': 1.0,
                    'symbolic_form': 'MEG_CONTEXT'
                })
        
        return trace

    async def calculate_completeness(
        self,
        explanation: Explanation,
        decision: Dict[str, Any]
    ) -> CompletenessMetrics:
        """
        Calculate explanation completeness metrics.
        
        Args:
            explanation: Generated explanation
            decision: Original decision
        
        Returns:
            CompletenessMetrics
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-q9r0s1t2 (Completeness metrics)
        """
        # Coverage: What percentage of decision factors are explained?
        decision_factors = decision.get('factors', [])
        explained_factors = 0
        content_str = str(explanation.content).lower()
        
        for factor in decision_factors:
            if str(factor).lower() in content_str:
                explained_factors += 1
        
        coverage = explained_factors / len(decision_factors) if decision_factors else 1.0
        
        # Depth: How detailed is the explanation?
        if explanation.level == ExplanationLevel.SIMPLE:
            depth = 0.3
        elif explanation.level == ExplanationLevel.DETAILED:
            depth = 0.7
        elif explanation.level == ExplanationLevel.TECHNICAL:
            depth = 0.9
        else:  # EXPERT
            depth = 1.0
        
        # Adjust depth based on content length
        content_length = len(content_str)
        if content_length < 100:
            depth *= 0.5
        elif content_length < 500:
            depth *= 0.8
        
        # Clarity: NLP-based readability score
        clarity = await self._calculate_clarity_score(content_str)
        
        # Consistency: Check for contradictions
        consistency = await self._calculate_consistency_score(explanation)
        
        # Overall weighted score
        overall = (
            coverage * 0.3 +
            depth * 0.2 +
            clarity * 0.3 +
            consistency * 0.2
        )
        
        # Identify missing elements
        missing = []
        if coverage < 0.7:
            missing.append("Not all decision factors explained")
        if depth < 0.5:
            missing.append("Insufficient detail level")
        if clarity < 0.6:
            missing.append("Low readability score")
        if consistency < 0.8:
            missing.append("Potential inconsistencies detected")
        
        return CompletenessMetrics(
            coverage_score=coverage,
            depth_score=depth,
            clarity_score=clarity,
            consistency_score=consistency,
            overall_score=overall,
            missing_elements=missing
        )

    async def _calculate_clarity_score(self, text: str) -> float:
        """
        Calculate NLP-based clarity metrics.
        
        Args:
            text: Text to analyze
        
        Returns:
            Clarity score (0-1)
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-u3v4w5x6 (NLP clarity metrics)
        """
        # Simplified clarity calculation
        # Real implementation would use NLP libraries (spaCy, TextBlob, etc.)
        
        # Factors:
        # 1. Sentence length (shorter is clearer)
        sentences = text.split('.')
        avg_sentence_length = len(text) / max(len(sentences), 1)
        length_score = 1.0 - min(avg_sentence_length / 200, 1.0)
        
        # 2. Word complexity (simpler words are clearer)
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        complexity_score = 1.0 - min(avg_word_length / 15, 1.0)
        
        # 3. Readability (presence of connectors, structure)
        connectors = ['because', 'therefore', 'thus', 'however', 'moreover', 'furthermore']
        connector_count = sum(1 for c in connectors if c in text.lower())
        structure_score = min(connector_count / 3, 1.0)
        
        # Combined clarity score
        clarity = (length_score * 0.4 + complexity_score * 0.3 + structure_score * 0.3)
        
        return max(0.0, min(1.0, clarity))

    async def _calculate_consistency_score(self, explanation: Explanation) -> float:
        """
        Calculate internal consistency score.
        
        Args:
            explanation: Explanation to check
        
        Returns:
            Consistency score (0-1)
        """
        # Check for logical consistency
        # Real implementation would use formal logic verification
        
        score = 1.0
        
        # Check proof validity if present
        if explanation.formal_proof and not explanation.formal_proof.valid:
            score *= 0.5
        
        # Check reasoning trace consistency
        if explanation.reasoning_trace:
            # Simplified: Check if confidences are reasonable
            confidences = [step.get('confidence', 1.0) for step in explanation.reasoning_trace]
            if any(c < 0 or c > 1 for c in confidences):
                score *= 0.7
        
        return score

    def _load_templates(self) -> None:
        """
        Load explanation templates from YAML/JSON files.
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-w9x0y1z2 (Template loading)
        """
        if not self.template_dir or not self.template_dir.exists():
            return
        
        # Load YAML templates
        for yaml_file in self.template_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'templates' in data:
                        for template_data in data['templates']:
                            template = ExplanationTemplate.from_dict(template_data)
                            self.templates[template.template_id] = template
            except Exception:
                continue
        
        # Load JSON templates
        for json_file in self.template_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'templates' in data:
                        for template_data in data['templates']:
                            template = ExplanationTemplate.from_dict(template_data)
                            self.templates[template.template_id] = template
            except Exception:
                continue

    async def _generate_multimodal_explanation(
        self,
        decision: Dict[str, Any],
        level: ExplanationLevel
    ) -> Dict[str, Any]:
        """
        Generate multi-modal explanation (text + visual + audio).
        
        Args:
            decision: Decision data
            level: Detail level
        
        Returns:
            Multi-modal content dictionary
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-s5t6u7v8 (Multi-modal support)
        """
        text = await self._generate_text_explanation(decision, level)
        
        # Generate visual component (simplified - would use actual visualization)
        visual = {
            'type': 'decision_tree',
            'nodes': decision.get('reasoning_steps', []),
            'format': 'svg',
            'url': f"/api/visualize/{decision.get('id')}"
        }
        
        # Generate audio component (simplified - would use TTS)
        audio = {
            'type': 'speech',
            'text': text[:500] if isinstance(text, str) else str(text)[:500],
            'format': 'mp3',
            'url': f"/api/audio/{decision.get('id')}"
        }
        
        return {
            'text': text,
            'visual': visual,
            'audio': audio
        }

    async def _generate_text_explanation(
        self,
        decision: Dict[str, Any],
        level: ExplanationLevel
    ) -> str:
        """Generate text-based explanation."""
        # Use template if available
        template_key = f"text_{level.value}"
        if template_key in self.templates:
            template = self.templates[template_key]
            return template.template.format(**decision)
        
        # Fallback: Generate basic explanation
        result = decision.get('result', decision.get('conclusion', 'unknown'))
        confidence = decision.get('confidence', 0.0)
        
        if level == ExplanationLevel.SIMPLE:
            return f"Decision: {result} (confidence: {confidence:.1%})"
        elif level == ExplanationLevel.DETAILED:
            factors = decision.get('factors', [])
            return f"Decision: {result}\nConfidence: {confidence:.1%}\nKey factors: {', '.join(map(str, factors))}"
        else:
            return str(decision)

    async def _generate_formal_proof_explanation(
        self,
        decision: Dict[str, Any]
    ) -> str:
        """Generate formal proof as explanation."""
        proof = await self.generate_formal_proof(decision)
        
        lines = [f"Formal Proof ({proof.system.value}):"]
        lines.append(f"Premises:")
        for i, premise in enumerate(proof.premises):
            lines.append(f"  P{i+1}. {premise}")
        
        lines.append(f"\nProof Steps:")
        for step in proof.steps:
            lines.append(f"  {step['step']}. {step['statement']} ({step['justification']})")
        
        lines.append(f"\nConclusion: {proof.conclusion}")
        lines.append(f"Valid: {proof.valid}")
        
        return '\n'.join(lines)

    async def _generate_symbolic_explanation(
        self,
        decision: Dict[str, Any],
        level: ExplanationLevel
    ) -> str:
        """Generate symbolic logic explanation."""
        trace = await self.generate_reasoning_trace(decision)
        
        lines = ["Symbolic Reasoning Trace:"]
        for step in trace:
            lines.append(f"  Step {step['step_id']}: {step['operation']}")
            if 'symbolic_form' in step:
                lines.append(f"    {step['symbolic_form']}")
        
        return '\n'.join(lines)

    async def _get_meg_context(self, decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Integrate with MEG for episodic memory context.
        
        Args:
            decision: Decision data
        
        Returns:
            MEG context or None
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-i1j2k3l4 (MEG integration)
        """
        if not self.meg_client:
            return None
        
        try:
            # Query MEG for related episodic memories
            decision_id = decision.get('id', '')
            context = await self.meg_client.get_context(decision_id)
            return context
        except Exception:
            return None

    async def _sign_explanation(self, explanation: Explanation) -> str:
        """
        Cryptographically sign explanation using SRD.
        
        Args:
            explanation: Explanation to sign
        
        Returns:
            Signature string
        
        Task: TODO-HIGH-BRIDGE-EXPLAIN-y7z8a9b0 (SRD cryptographic signing)
        """
        # Generate canonical representation
        canonical = json.dumps(explanation.to_dict(), sort_keys=True)
        
        # Create SHA256 hash (simplified - real implementation would use SRD)
        signature = hashlib.sha256(canonical.encode()).hexdigest()
        
        # In real implementation, this would use:
        # 1. SRD (Symbolic Response Digest) protocol
        # 2. Private key signing
        # 3. Timestamp authority
        
        return f"SRD-SHA256:{signature}"

    def _generate_cache_key(
        self,
        decision: Dict[str, Any],
        mode: ExplanationMode,
        level: ExplanationLevel
    ) -> str:
        """Generate cache key for explanation."""
        decision_id = decision.get('id', str(decision))
        return f"{decision_id}:{mode.value}:{level.value}"

    def _validate_proof_steps(
        self,
        steps: List[Dict[str, Any]],
        system: ProofSystem
    ) -> bool:
        """
        Validate formal proof steps.
        
        Args:
            steps: Proof steps
            system: Proof system
        
        Returns:
            True if valid
        """
        # Simplified validation
        # Real implementation would use automated theorem prover
        
        # Check that each step has required fields
        for step in steps:
            if 'statement' not in step or 'justification' not in step:
                return False
        
        # Check conclusion is last step
        if not steps or steps[-1]['type'] != 'conclusion':
            return False
        
        return True


# Convenience functions
async def explain_decision(
    decision: Dict[str, Any],
    mode: ExplanationMode = ExplanationMode.TEXT,
    level: ExplanationLevel = ExplanationLevel.DETAILED,
    **kwargs
) -> Explanation:
    """
    Convenience function to generate explanation.
    
    Args:
        decision: Decision to explain
        mode: Explanation mode
        level: Detail level
        **kwargs: Additional arguments
    
    Returns:
        Explanation
    """
    interface = ExplainabilityInterface()
    return await interface.explain(decision, mode, level, **kwargs)
