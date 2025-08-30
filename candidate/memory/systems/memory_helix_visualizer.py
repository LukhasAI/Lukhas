"""
3D Memory Helix Visualizer for v1_AGI
Implements a 3D helical visualization of system memories,
integrating with the memory management system, Lukhas_ID, and Seedra.
"""

import logging
import time
from datetime import datetime
from typing import Any, Optional

import numpy as np
import plotly.graph_objects as go
from identity.vault.lukhas_id import AccessTier, LucasID

from memory.memory_folds import MemoryPriority, MemoryType
from memory.memory_manager import MemoryManager

# Set up logging
logger = logging.getLogger("v1_AGI.interface.memory_helix")


class MemoryHelixVisualizer:
    """
    Implements a 3D helical visualization of system memories that integrates with
    the v1_AGI memory system, Lukhas_ID for access control, and Seedra components.
    """

    def __init__(self, memory_manager: MemoryManager, id_system: Optional[LucasID] = None):
        """
        Initialize the memory helix visualizer.

        Args:
            memory_manager: The memory management system
            id_system: Optional Lukhas_ID system for identity verification
        """
        logger.info("Initializing Memory Helix Visualizer...")

        self.memory_manager = memory_manager
        self.id_system = id_system

        # Helix parameters
        self.helix_radius = 2.0
        self.helix_pitch = 0.5  # Vertical distance between turns
        self.memory_spacing = 0.1  # Spacing between memories along the helix

        # Visualization parameters
        self.memory_type_colors = {
            MemoryType.EPISODIC: "royalblue",
            MemoryType.SEMANTIC: "green",
            MemoryType.PROCEDURAL: "orange",
            MemoryType.EMOTIONAL: "red",
            MemoryType.SENSORY: "purple",
            MemoryType.SPATIAL: "cyan",
            MemoryType.ASSOCIATION: "yellow",
            MemoryType.META: "darkgray",
        }

        # Memory priority size mapping (size multiplier)
        self.priority_size = {
            MemoryPriority.CRITICAL: 2.0,
            MemoryPriority.HIGH: 1.5,
            MemoryPriority.MEDIUM: 1.0,
            MemoryPriority.LOW: 0.8,
            MemoryPriority.NEGLIGIBLE: 0.5,
        }

        logger.info("Memory Helix Visualizer initialized")

    def get_memory_coordinates(
        self, memory_id: str, index: int, total_memories: int
    ) -> tuple[float, float, float]:
        """
        Calculate the 3D coordinates for a memory along the helix.

        Args:
            memory_id: Unique identifier for the memory
            index: Index position of the memory in the visualization
            total_memories: Total number of memories being visualized

        Returns:
            Tuple of (x, y, z) coordinates
        """
        # Calculate parameter t along the helix (0 to 2π * number of turns)
        t = (index / total_memories) * 2 * np.pi * (total_memories // 10 + 1)

        # Generate unique variation based on memory_id to avoid exact overlap
        # Hash the memory_id to a float between 0 and 1
        hash_val = int(hashlib.sha256(memory_id.encode()).hexdigest(), 16) / 2**256
        t_variation = hash_val * 0.1  # Small variation in the parameter

        t = t + t_variation

        # Calculate coordinates on the helix
        x = self.helix_radius * np.cos(t)
        y = self.helix_radius * np.sin(t)
        z = self.helix_pitch * t / (2 * np.pi)

        return (x, y, z)

    def get_authorized_memories(
        self, user_id: str = None, access_tier: AccessTier = None
    ) -> list[dict[str, Any]]:
        """
        Get the list of memories that the user is authorized to view.

        Args:
            user_id: The ID of the user
            access_tier: The access tier of the user

        Returns:
            List of memory information dictionaries
        """
        # If no identity system is available, return all memories
        if not self.id_system:
            return self.memory_manager.get_all_memories_info()

        # Otherwise, filter based on access permissions
        all_memories = self.memory_manager.get_all_memories_info()
        authorized_memories = []

        for memory in all_memories:
            # Check if user has permission to access this memory
            if self.memory_manager.id_integration.check_memory_access(
                memory_id=memory["id"], user_id=user_id, access_tier=access_tier
            ):
                authorized_memories.append(memory)

        return authorized_memories

    def visualize_memory_helix(
        self,
        user_id: str = None,
        access_tier: AccessTier = None,
        height: int = 800,
        width: int = 1000,
    ) -> go.Figure:
        """
        Create a 3D visualization of the memory helix.

        Args:
            user_id: Optional user ID for access control
            access_tier: Optional access tier for filtering memories
            height: Height of the plot in pixels
            width: Width of the plot in pixels

        Returns:
            Plotly figure object with the 3D visualization
        """
        logger.info("Generating memory helix visualization...")

        # Get authorized memories
        memories = self.get_authorized_memories(user_id, access_tier)
        total_memories = len(memories)

        if total_memories == 0:
            logger.warning("No accessible memories found for visualization")
            # Create an empty visualization
            fig = go.Figure()
            fig.update_layout(
                title="Memory Helix (No accessible memories)",
                scene={"xaxis_title": "X", "yaxis_title": "Y", "zaxis_title": "Time"},
                height=height,
                width=width,
            )
            return fig

        # Sort memories by timestamp
        memories.sort(key=lambda x: x.get("timestamp", 0))

        # Create empty lists for coordinates and memory data
        xs, ys, zs = [], [], []
        colors, sizes, texts = [], [], []
        edges_x, edges_y, edges_z = [], [], []

        # Process each memory
        for i, memory in enumerate(memories):
            # Get memory coordinates
            x, y, z = self.get_memory_coordinates(memory["id"], i, total_memories)
            xs.append(x)
            ys.append(y)
            zs.append(z)

            # Set color based on memory type
            memory_type = memory.get("type", MemoryType.SEMANTIC)
            colors.append(self.memory_type_colors.get(memory_type, "gray"))

            # Set size based on memory priority
            memory_priority = memory.get("priority", MemoryPriority.MEDIUM)
            sizes.append(10 * self.priority_size.get(memory_priority, 1.0))

            # Create hover text
            created = datetime.fromtimestamp(memory.get("timestamp", 0)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            text = (
                f"ID: {memory['id'][:8]}...<br>"
                f"Type: {memory_type}<br>"
                f"Created: {created}<br>"
                f"Tags: {', '.join(memory.get('tags', []))}<br>"
                f"Priority: {memory_priority}"
            )
            texts.append(text)

            # Connect memories with related ones (if relationship data exists)
            for related_id in memory.get("related_memories", []):
                # Find the related memory in our list
                for j, rel_memory in enumerate(memories):
                    if rel_memory["id"] == related_id:
                        # Get coordinates for related memory
                        rx, ry, rz = self.get_memory_coordinates(
                            rel_memory["id"], j, total_memories
                        )

                        # Add edge between memories
                        edges_x.extend([x, rx, None])  # None creates a break
                        edges_y.extend([y, ry, None])
                        edges_z.extend([z, rz, None])
                        break

        # Create the 3D scatter plot for memories
        memory_trace = go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers",
            marker={
                "size": sizes,
                "color": colors,
                "opacity": 0.8,
                "line": {"width": 1, "color": "black"},
            },
            text=texts,
            hoverinfo="text",
            name="Memories",
        )

        # Create the helix path
        t = np.linspace(0, 2 * np.pi * (total_memories // 10 + 1), 1000)
        helix_x = self.helix_radius * np.cos(t)
        helix_y = self.helix_radius * np.sin(t)
        helix_z = self.helix_pitch * t / (2 * np.pi)

        helix_trace = go.Scatter3d(
            x=helix_x,
            y=helix_y,
            z=helix_z,
            mode="lines",
            line={"color": "lightgray", "width": 2},
            hoverinfo="none",
            name="Memory Helix",
        )

        # Create connections between related memories
        if edges_x:
            edge_trace = go.Scatter3d(
                x=edges_x,
                y=edges_y,
                z=edges_z,
                mode="lines",
                line={"color": "rgba(120, 120, 120, 0.4)", "width": 1},
                hoverinfo="none",
                name="Memory Connections",
            )
            # Create the figure with all traces
            fig = go.Figure(data=[helix_trace, memory_trace, edge_trace])
        else:
            # Create the figure without edge traces
            fig = go.Figure(data=[helix_trace, memory_trace])

        # Configure the layout
        fig.update_layout(
            title=f"Memory Helix ({total_memories} memories)",
            scene={
                "xaxis_title": "X",
                "yaxis_title": "Y",
                "zaxis_title": "Time",
                "camera": {
                    "eye": {"x": 1.5, "y": 1.5, "z": 0.8},
                    "up": {"x": 0, "y": 0, "z": 1},
                },
            },
            height=height,
            width=width,
            legend={"x": 0, "y": 0.9, "bgcolor": "rgba(255, 255, 255, 0.5)"},
            margin={"l": 0, "r": 0, "b": 10, "t": 50},
        )

        # Add legend for memory types
        for memory_type, color in self.memory_type_colors.items():
            fig.add_trace(
                go.Scatter3d(
                    x=[None],
                    y=[None],
                    z=[None],  # No actual points
                    mode="markers",
                    marker={"size": 10, "color": color},
                    name=f"{memory_type}",
                    showlegend=True,
                )
            )

        logger.info(f"Generated memory helix visualization with {total_memories} memories")
        return fig

    def create_interactive_visualization(
        self, user_id: str = None, access_tier: AccessTier = None
    ) -> str:
        """
        Create and save an interactive HTML visualization of the memory helix.

        Args:
            user_id: Optional user ID for access control
            access_tier: Optional access tier for filtering memories

        Returns:
            The path to the saved HTML file
        """
        fig = self.visualize_memory_helix(user_id, access_tier)

        # Create a unique filename based on timestamp
        timestamp = int(time.time())
        filename = f"memory_helix_{timestamp}.html"
        file_path = f"./visualizations/{filename}"

        # Ensure the directory exists
        os.makedirs("./visualizations", exist_ok=True)

        # Save the figure as an interactive HTML file
        fig.write_html(file_path)
        logger.info(f"Interactive memory helix visualization saved to {file_path}")

        return file_path

    def update_memory_links(self, memory_id: str, related_memory_ids: list[str]):
        """
        Update the links between memories in the visualization.

        Args:
            memory_id: The ID of the memory to update
            related_memory_ids: List of related memory IDs
        """
        # Delegate to memory manager to update relationships
        self.memory_manager.update_memory_relationships(memory_id, related_memory_ids)
        logger.info(f"Updated memory relationships for {memory_id}")
