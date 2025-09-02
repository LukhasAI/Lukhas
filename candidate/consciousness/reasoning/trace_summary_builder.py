"""
Trace Summary Builder
Converts reasoning traces and decision trees into symbolic narratives
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class TraceNode:
    """Represents a node in the reasoning trace tree"""

    def __init__(self, node_id: str, node_type: str, content: Any):
        self.id = node_id
        self.type = node_type
        self.content = content
        self.children = []
        self.metadata = {
            "timestamp": datetime.now().isoformat(),
            "depth": 0,
            "confidence": 0.0,
        }

    def add_child(self, child: "TraceNode"):
        """Add a child node"""
        child.metadata["depth"] = self.metadata["depth"] + 1
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children],
        }


class TraceSummaryBuilder:
    """
    Builds comprehensive summaries from reasoning traces,
    converting complex decision trees into understandable narratives
    """

    def __init__(self):
        self.trace_cache = {}
        self.summary_templates = {
            "deductive": "Applied logical rules: {premise} → {conclusion}",
            "inductive": "Generalized from examples: {examples} → {pattern}",
            "abductive": "Best explanation: {observation} likely caused by {hypothesis}",
            "analogical": "Similar to {source}: {mapping} suggests {conclusion}",
            "causal": "Causal chain: {cause} → {effect} (mechanism: {mechanism})",
            "probabilistic": "Probability analysis: {event} has {probability}% chance given {conditions}",
            "symbolic": "Formal proof: {axioms} ⊢ {theorem} via {steps}",
            "hybrid": "Combined analysis using {strategies}: {synthesis}",
        }
        self.narrative_styles = ["technical", "explanatory", "simplified"]
        self.current_style = "explanatory"

    async def build_summary(self, reason_tree: dict[str, Any], style: str = "explanatory") -> dict[str, Any]:
        """
        Build a comprehensive summary from a reasoning trace tree

        Args:
            reason_tree: The reasoning trace tree
            style: Narrative style (technical, explanatory, simplified)

        Returns:
            Summary with narrative, key insights, and recommendations
        """
        self.current_style = style
        logger.info(f"Building trace summary in {style} style")

        try:
            # Parse the trace tree
            root_node = self._parse_trace_tree(reason_tree)

            # Extract key information
            insights = await self._extract_insights(root_node)
            decision_path = self._trace_decision_path(root_node)
            confidence_analysis = self._analyze_confidence(root_node)

            # Generate narrative
            narrative = await self._generate_narrative(root_node, insights)

            # Create recommendations
            recommendations = self._generate_recommendations(insights, confidence_analysis)

            summary = {
                "narrative": narrative,
                "insights": insights,
                "decision_path": decision_path,
                "confidence_analysis": confidence_analysis,
                "recommendations": recommendations,
                "metadata": {
                    "style": style,
                    "generated_at": datetime.now().isoformat(),
                    "tree_depth": self._calculate_tree_depth(root_node),
                    "node_count": self._count_nodes(root_node),
                },
            }

            # Cache the summary
            cache_key = self._generate_cache_key(reason_tree)
            self.trace_cache[cache_key] = summary

            return summary

        except Exception as e:
            logger.error(f"Error building trace summary: {e}")
            return {
                "error": str(e),
                "narrative": "Failed to build reasoning summary",
                "insights": [],
                "recommendations": ["Review reasoning trace for errors"],
            }

    def _parse_trace_tree(self, tree_data: dict[str, Any]) -> TraceNode:
        """Parse raw trace data into TraceNode structure"""
        node_type = tree_data.get("type", "unknown")
        node_id = tree_data.get("id", f"node_{datetime.now().timestamp()}")
        content = tree_data.get("content", tree_data.get("reason", {}))

        root = TraceNode(node_id, node_type, content)

        # Set metadata
        if "confidence" in tree_data:
            root.metadata["confidence"] = tree_data["confidence"]
        if "timestamp" in tree_data:
            root.metadata["timestamp"] = tree_data["timestamp"]

        # Parse children
        for child_data in tree_data.get("children", []):
            child_node = self._parse_trace_tree(child_data)
            root.add_child(child_node)

        return root

    async def _extract_insights(self, root: TraceNode) -> list[dict[str, Any]]:
        """Extract key insights from the reasoning trace"""
        insights = []

        # Traverse tree to find significant nodes
        queue = [(root, [])]
        while queue:
            node, path = queue.pop(0)

            # Check for insight patterns
            if self._is_insight_node(node):
                insight = {
                    "type": node.type,
                    "content": node.content,
                    "confidence": node.metadata.get("confidence", 0.0),
                    "path": [n.id for n in path],
                    "depth": node.metadata.get("depth", 0),
                }
                insights.append(insight)

            # Add children to queue
            for child in node.children:
                queue.append((child, [*path, node]))

        # Sort by confidence and depth
        insights.sort(key=lambda x: (x["confidence"], -x["depth"]), reverse=True)

        return insights[:10]  # Top 10 insights

    def _is_insight_node(self, node: TraceNode) -> bool:
        """Determine if a node represents a significant insight"""
        # High confidence nodes
        if node.metadata.get("confidence", 0.0) > 0.8:
            return True

        # Conclusion nodes
        if node.type in ["conclusion", "decision", "discovery"]:
            return True

        # Nodes with significant content
        return bool(isinstance(node.content, dict) and node.content.get("significance", 0) > 0.7)

    def _trace_decision_path(self, root: TraceNode) -> list[dict[str, Any]]:
        """Trace the main decision path through the reasoning tree"""
        path = []
        current = root

        while current:
            path.append(
                {
                    "node_id": current.id,
                    "type": current.type,
                    "summary": self._summarize_node(current),
                    "confidence": current.metadata.get("confidence", 0.0),
                }
            )

            # Follow highest confidence child
            if current.children:
                current = max(current.children, key=lambda c: c.metadata.get("confidence", 0.0))
            else:
                current = None

        return path

    def _summarize_node(self, node: TraceNode) -> str:
        """Generate a brief summary of a node's content"""
        if isinstance(node.content, str):
            return node.content[:100]
        elif isinstance(node.content, dict):
            if "summary" in node.content:
                return node.content["summary"]
            elif "conclusion" in node.content:
                return node.content["conclusion"]
            elif "reason" in node.content:
                return node.content["reason"]
        return f"{node.type} node"

    def _analyze_confidence(self, root: TraceNode) -> dict[str, Any]:
        """Analyze confidence levels throughout the trace"""
        confidences = []

        # Collect all confidence values
        queue = [root]
        while queue:
            node = queue.pop(0)
            conf = node.metadata.get("confidence", 0.0)
            if conf > 0:
                confidences.append(conf)
            queue.extend(node.children)

        if not confidences:
            return {"status": "no_confidence_data"}

        return {
            "average": sum(confidences) / len(confidences),
            "min": min(confidences),
            "max": max(confidences),
            "count": len(confidences),
            "low_confidence_nodes": len([c for c in confidences if c < 0.5]),
            "high_confidence_nodes": len([c for c in confidences if c > 0.8]),
        }

    async def _generate_narrative(self, root: TraceNode, insights: list[dict[str, Any]]) -> str:
        """Generate a narrative summary of the reasoning process"""
        narrative_parts = []

        # Opening
        if self.current_style == "technical":
            narrative_parts.append(f"Reasoning trace analysis for {root.type} process:")
        elif self.current_style == "simplified":
            narrative_parts.append("Here's what the system figured out:")
        else:  # explanatory
            narrative_parts.append("The reasoning process proceeded as follows:")

        # Main reasoning path
        path = self._trace_decision_path(root)
        for i, step in enumerate(path[:5]):  # First 5 steps
            if self.current_style == "technical":
                narrative_parts.append(
                    f"{i + 1}. {step['type'].upper()}: {step['summary']} (confidence: {step['confidence']:.2f})"
                )
            else:
                narrative_parts.append(f"{i + 1}. {step['summary']}")

        # Key insights
        if insights:
            if self.current_style == "simplified":
                narrative_parts.append("\nMain findings:")
            else:
                narrative_parts.append("\nKey insights derived:")

            for insight in insights[:3]:  # Top 3 insights
                narrative_parts.append(f"• {self._format_insight(insight)}")

        # Conclusion
        conclusion = self._find_conclusion_node(root)
        if conclusion:
            if self.current_style == "technical":
                narrative_parts.append(
                    f"\nFinal conclusion: {self._summarize_node(conclusion)} "
                    f"(confidence: {conclusion.metadata.get('confidence', 0.0):.2f})"
                )
            else:
                narrative_parts.append(f"\nConclusion: {self._summarize_node(conclusion)}")

        return "\n".join(narrative_parts)

    def _format_insight(self, insight: dict[str, Any]) -> str:
        """Format an insight for the narrative"""
        content = insight.get("content", {})
        if isinstance(content, dict):
            # Try to use a template
            insight_type = insight.get("type", "general")
            if insight_type in self.summary_templates:
                template = self.summary_templates[insight_type]
                try:
                    return template.format(**content)
                except BaseException:
                    pass

        # Fallback to simple formatting
        return str(content)[:100]

    def _find_conclusion_node(self, root: TraceNode) -> Optional[TraceNode]:
        """Find the conclusion node in the tree"""
        # BFS to find conclusion node
        queue = [root]
        while queue:
            node = queue.pop(0)
            if node.type in ["conclusion", "final_decision", "result"]:
                return node
            queue.extend(node.children)
        return None

    def _generate_recommendations(
        self, insights: list[dict[str, Any]], confidence_analysis: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on the analysis"""
        recommendations = []

        # Check overall confidence
        avg_confidence = confidence_analysis.get("average", 0)
        if avg_confidence < 0.5:
            recommendations.append(
                "Low overall confidence detected. Consider gathering more data or refining reasoning parameters."
            )

        # Check for low confidence nodes
        low_conf_count = confidence_analysis.get("low_confidence_nodes", 0)
        if low_conf_count > 5:
            recommendations.append(
                f"Found {low_conf_count} low-confidence decision points. Review these areas for potential improvements."
            )

        # Strategy-specific recommendations
        for insight in insights:
            if insight["type"] == "deductive" and insight["confidence"] < 0.7:
                recommendations.append("Deductive reasoning shows uncertainty. Verify logical premises.")
            elif insight["type"] == "inductive" and len(insights) < 3:
                recommendations.append("Limited inductive examples. Gather more data for stronger patterns.")

        # General recommendations
        if not recommendations:
            recommendations.append("Reasoning trace appears sound. No immediate actions required.")

        return recommendations[:5]  # Limit to 5 recommendations

    def _calculate_tree_depth(self, root: TraceNode) -> int:
        """Calculate the maximum depth of the trace tree"""
        if not root.children:
            return 1
        return 1 + max(self._calculate_tree_depth(child) for child in root.children)

    def _count_nodes(self, root: TraceNode) -> int:
        """Count total nodes in the tree"""
        return 1 + sum(self._count_nodes(child) for child in root.children)

    def _generate_cache_key(self, tree_data: dict[str, Any]) -> str:
        """Generate a cache key for the trace tree"""
        # Simple hash of tree structure
        tree_str = json.dumps(tree_data, sort_keys=True, default=str)
        return f"trace_{hash(tree_str)}"

    def get_cached_summary(self, tree_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Retrieve a cached summary if available"""
        cache_key = self._generate_cache_key(tree_data)
        return self.trace_cache.get(cache_key)

    def clear_cache(self):
        """Clear the trace cache"""
        self.trace_cache.clear()
        logger.info("Trace cache cleared")


# Backward compatibility function
def summarize_reason_trace(reason_tree: dict) -> str:
    """
    Convert recursive cause maps into symbolic narrative.
    Maintains backward compatibility with existing code.
    """
    if not reason_tree:
        return "No reasoning trace provided."

    # Use the new TraceSummaryBuilder
    builder = TraceSummaryBuilder()

    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        summary = loop.run_until_complete(builder.build_summary(reason_tree, style="simplified"))

        if "error" in summary:
            return f"Error building summary: {summary['error']}"

        # Return simplified narrative
        return summary.get("narrative", "Failed to generate summary")

    except Exception as e:
        logger.error(f"Error in summarize_reason_trace: {e}")

        # Fallback to original simple implementation
        reason = reason_tree.get("reason", "Unknown reason")
        confidence = reason_tree.get("confidence", 0.0)

        if "Low overall confidence" in str(reason):
            return (
                f"Reasoning failure due to low overall confidence ({confidence:.2f}). Suggest review of reasoning path."
            )

        return f"Reasoning failure due to {reason}. Suggest correction path via fold revision."

    finally:
        loop.close()
