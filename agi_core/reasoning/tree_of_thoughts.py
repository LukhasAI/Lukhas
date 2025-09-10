"""
Tree of Thoughts reasoning for LUKHAS AGI.

This module implements tree-based reasoning that explores multiple thought paths
to arrive at better solutions through systematic exploration of the solution space.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ThoughtType(Enum):
    """Types of thoughts in the reasoning tree."""
    ROOT = "root"
    HYPOTHESIS = "hypothesis"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class ThoughtStatus(Enum):
    """Status of a thought node."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PRUNED = "pruned"


@dataclass
class Thought:
    """A single thought node in the reasoning tree."""

    id: str
    content: str
    thought_type: ThoughtType
    parent_id: Optional[str] = None
    confidence: float = 0.5
    status: ThoughtStatus = ThoughtStatus.PENDING
    children: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReasoningPath:
    """A path through the tree of thoughts."""

    path_id: str
    node_ids: list[str]
    total_confidence: float
    reasoning_quality: float
    path_length: int
    is_complete: bool = False
    final_conclusion: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TreeOfThoughtsResult:
    """Result of tree of thoughts reasoning."""

    problem: str
    best_path: Optional[ReasoningPath]
    all_paths: list[ReasoningPath]
    total_nodes: int
    exploration_depth: int
    reasoning_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TreeOfThoughts:
    """Tree of Thoughts reasoning engine."""

    def __init__(self, max_depth: int = 10, max_branches: int = 3, pruning_threshold: float = 0.2):
        self.max_depth = max_depth
        self.max_branches = max_branches
        self.pruning_threshold = pruning_threshold
        self.thoughts: dict[str, Thought] = {}
        self.reasoning_paths: list[ReasoningPath] = []

        logger.info(f"TreeOfThoughts initialized (depth={max_depth}, branches={max_branches})")

    async def reason(self, problem: str, context: Optional[dict[str, Any]] = None) -> TreeOfThoughtsResult:
        """Perform tree of thoughts reasoning on a problem."""

        start_time = datetime.now(timezone.utc)

        try:
            # Initialize root thought
            root_thought = await self._create_root_thought(problem, context or {})

            # Explore the reasoning tree
            await self._explore_tree(root_thought.id, depth=0)

            # Find and evaluate all complete paths
            complete_paths = await self._find_complete_paths()

            # Select the best reasoning path
            best_path = await self._select_best_path(complete_paths)

            reasoning_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            result = TreeOfThoughtsResult(
                problem=problem,
                best_path=best_path,
                all_paths=complete_paths,
                total_nodes=len(self.thoughts),
                exploration_depth=max((await self._get_node_depth(node_id) for node_id in self.thoughts.keys()), default=0),
                reasoning_time=reasoning_time,
                success=True
            )

            logger.info(f"Tree reasoning completed: {len(complete_paths)} paths, best confidence: {best_path.total_confidence if best_path else 0:.3f}")
            return result

        except Exception as e:
            logger.error(f"Tree of thoughts reasoning failed: {e}")
            reasoning_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            return TreeOfThoughtsResult(
                problem=problem,
                best_path=None,
                all_paths=[],
                total_nodes=len(self.thoughts),
                exploration_depth=0,
                reasoning_time=reasoning_time,
                success=False,
                error_message=str(e)
            )

    async def _create_root_thought(self, problem: str, context: dict[str, Any]) -> Thought:
        """Create the root thought for the reasoning tree."""

        root_id = str(uuid.uuid4())
        root_thought = Thought(
            id=root_id,
            content=f"Root problem: {problem}",
            thought_type=ThoughtType.ROOT,
            confidence=1.0,
            status=ThoughtStatus.COMPLETED,
            metadata={"context": context, "problem": problem}
        )

        self.thoughts[root_id] = root_thought
        return root_thought

    async def _explore_tree(self, node_id: str, depth: int):
        """Recursively explore the reasoning tree."""

        if depth >= self.max_depth:
            logger.debug(f"Reached max depth {self.max_depth} at node {node_id}")
            return

        current_thought = self.thoughts[node_id]

        # Generate child thoughts based on current thought type
        child_thoughts = await self._generate_child_thoughts(current_thought, depth)

        # Add children to current thought
        current_thought.children.extend([child.id for child in child_thoughts])
        current_thought.updated_at = datetime.now(timezone.utc)

        # Recursively explore each child
        for child_thought in child_thoughts:
            if child_thought.confidence > self.pruning_threshold:
                await self._explore_tree(child_thought.id, depth + 1)
            else:
                # Prune low-confidence branches
                child_thought.status = ThoughtStatus.PRUNED
                logger.debug(f"Pruned thought {child_thought.id} (confidence: {child_thought.confidence:.3f})")

    async def _generate_child_thoughts(self, parent_thought: Thought, depth: int) -> list[Thought]:
        """Generate child thoughts for a given parent thought."""

        child_thoughts = []

        # Determine next thought types based on parent type and depth
        next_types = await self._get_next_thought_types(parent_thought.thought_type, depth)

        for thought_type in next_types[:self.max_branches]:
            child_content = await self._generate_thought_content(parent_thought, thought_type)
            child_confidence = await self._calculate_thought_confidence(parent_thought, thought_type, child_content)

            child_id = str(uuid.uuid4())
            child_thought = Thought(
                id=child_id,
                content=child_content,
                thought_type=thought_type,
                parent_id=parent_thought.id,
                confidence=child_confidence,
                status=ThoughtStatus.COMPLETED
            )

            child_thoughts.append(child_thought)
            self.thoughts[child_id] = child_thought

        return child_thoughts

    async def _get_next_thought_types(self, current_type: ThoughtType, depth: int) -> list[ThoughtType]:
        """Determine the next possible thought types."""

        if current_type == ThoughtType.ROOT:
            return [ThoughtType.HYPOTHESIS, ThoughtType.ANALYSIS]
        elif current_type == ThoughtType.HYPOTHESIS:
            return [ThoughtType.ANALYSIS, ThoughtType.EVALUATION]
        elif current_type == ThoughtType.ANALYSIS:
            return [ThoughtType.EVALUATION, ThoughtType.SYNTHESIS, ThoughtType.HYPOTHESIS]
        elif current_type == ThoughtType.EVALUATION:
            return [ThoughtType.SYNTHESIS, ThoughtType.CONCLUSION]
        elif current_type == ThoughtType.SYNTHESIS:
            return [ThoughtType.CONCLUSION, ThoughtType.EVALUATION]
        else:  # CONCLUSION
            return []

    async def _generate_thought_content(self, parent_thought: Thought, thought_type: ThoughtType) -> str:
        """Generate content for a thought based on its type and parent."""

        if thought_type == ThoughtType.HYPOTHESIS:
            return f"Hypothesis based on {parent_thought.content[:50]}..."
        elif thought_type == ThoughtType.ANALYSIS:
            return f"Analysis of: {parent_thought.content[:50]}..."
        elif thought_type == ThoughtType.EVALUATION:
            return f"Evaluation of: {parent_thought.content[:50]}..."
        elif thought_type == ThoughtType.SYNTHESIS:
            return f"Synthesis combining: {parent_thought.content[:50]}..."
        elif thought_type == ThoughtType.CONCLUSION:
            return f"Conclusion from: {parent_thought.content[:50]}..."
        else:
            return f"Thought following: {parent_thought.content[:50]}..."

    async def _calculate_thought_confidence(self, parent_thought: Thought, thought_type: ThoughtType, content: str) -> float:
        """Calculate confidence for a thought."""

        # Base confidence from parent
        base_confidence = parent_thought.confidence * 0.8

        # Adjust based on thought type
        type_multipliers = {
            ThoughtType.HYPOTHESIS: 0.9,
            ThoughtType.ANALYSIS: 1.0,
            ThoughtType.EVALUATION: 0.95,
            ThoughtType.SYNTHESIS: 0.85,
            ThoughtType.CONCLUSION: 0.8
        }

        type_confidence = base_confidence * type_multipliers.get(thought_type, 0.7)

        # Add some randomness to simulate reasoning uncertainty
        import random
        randomness = random.uniform(0.8, 1.2)

        final_confidence = min(1.0, max(0.0, type_confidence * randomness))
        return final_confidence

    async def _find_complete_paths(self) -> list[ReasoningPath]:
        """Find all complete reasoning paths in the tree."""

        complete_paths = []

        # Find all leaf nodes (conclusion nodes or nodes with no children)
        leaf_nodes = [
            node for node in self.thoughts.values()
            if (not node.children or node.thought_type == ThoughtType.CONCLUSION)
            and node.status == ThoughtStatus.COMPLETED
        ]

        # Trace back from each leaf to create paths
        for leaf_node in leaf_nodes:
            path = await self._trace_path_to_root(leaf_node.id)
            if path:
                complete_paths.append(path)

        return complete_paths

    async def _trace_path_to_root(self, node_id: str) -> Optional[ReasoningPath]:
        """Trace a path from a node back to the root."""

        path_nodes = []
        current_id = node_id

        while current_id:
            if current_id not in self.thoughts:
                break

            thought = self.thoughts[current_id]
            path_nodes.append(current_id)
            current_id = thought.parent_id

        # Reverse to get root-to-leaf order
        path_nodes.reverse()

        if not path_nodes:
            return None

        # Calculate path metrics
        total_confidence = 1.0
        for node_id in path_nodes:
            total_confidence *= self.thoughts[node_id].confidence

        # Calculate reasoning quality (higher for longer, more diverse paths)
        path_types = set(self.thoughts[node_id].thought_type for node_id in path_nodes)
        type_diversity = len(path_types) / len(ThoughtType)
        reasoning_quality = (total_confidence + type_diversity) / 2

        # Check if path ends with conclusion
        final_node = self.thoughts[path_nodes[-1]]
        is_complete = final_node.thought_type == ThoughtType.CONCLUSION

        path_id = str(uuid.uuid4())
        return ReasoningPath(
            path_id=path_id,
            node_ids=path_nodes,
            total_confidence=total_confidence,
            reasoning_quality=reasoning_quality,
            path_length=len(path_nodes),
            is_complete=is_complete,
            final_conclusion=final_node.content if is_complete else None
        )

    async def _select_best_path(self, paths: list[ReasoningPath]) -> Optional[ReasoningPath]:
        """Select the best reasoning path from available options."""

        if not paths:
            return None

        # Prefer complete paths
        complete_paths = [p for p in paths if p.is_complete]
        if complete_paths:
            paths = complete_paths

        # Sort by reasoning quality (combination of confidence and diversity)
        best_path = max(paths, key=lambda p: p.reasoning_quality)
        return best_path

    async def _get_node_depth(self, node_id: str) -> int:
        """Get the depth of a node in the tree."""

        depth = 0
        current_id = node_id

        while current_id and current_id in self.thoughts:
            thought = self.thoughts[current_id]
            if thought.parent_id is None:
                break
            current_id = thought.parent_id
            depth += 1

        return depth

    def get_thought_tree(self) -> dict[str, Any]:
        """Get a representation of the entire thought tree."""

        return {
            "thoughts": {node_id: {
                "content": thought.content,
                "type": thought.thought_type.value,
                "confidence": thought.confidence,
                "status": thought.status.value,
                "children": thought.children,
                "parent": thought.parent_id
            } for node_id, thought in self.thoughts.items()},
            "statistics": {
                "total_nodes": len(self.thoughts),
                "max_depth": max((await self._get_node_depth(node_id) for node_id in self.thoughts.keys()), default=0),
                "total_paths": len(self.reasoning_paths)
            }
        }

    def reset(self):
        """Reset the reasoning tree."""
        self.thoughts.clear()
        self.reasoning_paths.clear()


# Convenience functions

async def solve_with_tree_reasoning(problem: str, max_depth: int = 8, max_branches: int = 3) -> TreeOfThoughtsResult:
    """Solve a problem using tree of thoughts reasoning."""

    tree = TreeOfThoughts(max_depth=max_depth, max_branches=max_branches)
    return await tree.reason(problem)


def create_tree_of_thoughts(max_depth: int = 10, max_branches: int = 3, pruning_threshold: float = 0.2) -> TreeOfThoughts:
    """Create a new TreeOfThoughts instance with specified parameters."""

    return TreeOfThoughts(
        max_depth=max_depth,
        max_branches=max_branches,
        pruning_threshold=pruning_threshold
    )


# Export main classes and functions
__all__ = [
    "TreeOfThoughts",
    "Thought",
    "ThoughtType",
    "ThoughtStatus",
    "ReasoningPath",
    "TreeOfThoughtsResult",
    "solve_with_tree_reasoning",
    "create_tree_of_thoughts"
]