import logging

logger = logging.getLogger(__name__)
"""
LUKHAS Grid Size Calculator - Emoji Grid Sizing Math

This module implements dynamic emoji grid sizing calculations based on
cognitive load, screen size, and accessibility requirements.

Author: LUKHAS Team
Date: June 2025
Purpose: Optimize emoji grid sizing for different user states and devices
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class GridPattern(Enum):
    """Grid layout patterns"""

    SQUARE = "square"  # n×n square grid
    RECTANGLE = "rectangle"  # m×n rectangular grid
    CIRCULAR = "circular"  # Circular arrangement
    ADAPTIVE = "adaptive"  # Adaptive based on content
    ACCESSIBILITY = "accessibility"  # Optimized for accessibility


class SizingMode(Enum):
    """Grid sizing optimization modes"""

    COGNITIVE_LOAD = "cognitive_load"  # Based on user cognitive load
    DEVICE_SIZE = "device_size"  # Based on screen dimensions
    ACCESSIBILITY = "accessibility"  # Accessibility-first sizing
    PERFORMANCE = "performance"  # Performance-optimized
    BALANCED = "balanced"  # Balanced optimization


@dataclass
class ScreenDimensions:
    """Screen dimension parameters"""

    width: int
    height: int
    pixel_density: float
    safe_area_insets: dict[str, int]  # top, bottom, left, right
    orientation: str  # portrait, landscape


@dataclass
class GridConstraints:
    """Grid sizing constraints"""

    min_grid_size: int = 4
    max_grid_size: int = 16
    min_cell_size: float = 40.0  # Minimum touch target size
    max_cell_size: float = 120.0
    min_spacing: float = 5.0
    max_spacing: float = 20.0
    accessibility_factor: float = 1.0  # Multiplier for accessibility


@dataclass
class GridCalculationResult:
    """Result of grid size calculation"""

    grid_size: int
    pattern: GridPattern
    cell_size: float
    spacing: float
    total_width: float
    total_height: float
    cells_per_row: int
    cells_per_column: int
    reasoning: list[str]  # Explanation of sizing decisions
    confidence: float  # Confidence in the calculation


class GridSizeCalculator:
    """
    Dynamic grid size calculator for LUKHAS authentication.

    Features:
    - Cognitive load-aware sizing
    - Screen size adaptation
    - Accessibility optimization
    - Touch target size validation
    - Performance considerations
    - Cultural and regional preferences
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Sizing constraints
        self.constraints = GridConstraints()
        self.default_screen = ScreenDimensions(
            390, 844, 3.0, {"top": 44, "bottom": 34, "left": 0, "right": 0}, "portrait"
        )

        # Cognitive load impact factors
        self.cognitive_load_factors = {
            "very_low": {"size_multiplier": 1.3, "spacing_multiplier": 0.9},
            "low": {"size_multiplier": 1.1, "spacing_multiplier": 0.95},
            "moderate": {"size_multiplier": 1.0, "spacing_multiplier": 1.0},
            "high": {"size_multiplier": 0.8, "spacing_multiplier": 1.2},
            "overload": {"size_multiplier": 0.6, "spacing_multiplier": 1.4},
        }

        # Accessibility guidelines (WCAG compliance)
        self.accessibility_guidelines = {
            "min_touch_target": 44.0,  # Minimum 44pt touch targets
            "spacing_multiplier": 1.5,  # Extra spacing for accessibility
            "contrast_requirements": True,
            "large_text_support": True,
        }

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for grid calculator."""
        return {
            "sizing_mode": SizingMode.BALANCED,
            "accessibility_enabled": True,
            "cognitive_load_adaptation": True,
            "device_adaptation": True,
            "performance_optimization": True,
            "cultural_adaptation": False,
            "debug_reasoning": True,
        }

    def calculate_optimal_grid_size(
        self,
        content_count: int,
        cognitive_load_level: str = "moderate",
        screen_dimensions: Optional[ScreenDimensions] = None,
        accessibility_requirements: Optional[dict[str, Any]] = None,
    ) -> GridCalculationResult:
        """
        Calculate optimal grid size based on multiple factors.

        Args:
            content_count: Number of items to display in grid
            cognitive_load_level: Current cognitive load level
            screen_dimensions: Screen size and properties
            accessibility_requirements: Specific accessibility needs

        Returns:
            Optimal grid calculation result
        """
        screen = screen_dimensions or self.default_screen
        reasoning = []

        # Step 1: Determine base grid size from content count
        base_grid_size = self._calculate_base_grid_size(content_count)
        reasoning.append(f"Base grid size {base_grid_size} for {content_count} items")

        # Step 2: Apply cognitive load adjustments
        cognitive_adjusted_size = self._apply_cognitive_load_adjustment(base_grid_size, cognitive_load_level)
        reasoning.append(f"Cognitive load ({cognitive_load_level}) adjusted to {cognitive_adjusted_size}")

        # Step 3: Apply screen size constraints
        screen_adjusted_size = self._apply_screen_constraints(cognitive_adjusted_size, screen)
        reasoning.append(f"Screen constraints applied: {screen_adjusted_size}")

        # Step 4: Apply accessibility requirements
        final_grid_size = self._apply_accessibility_adjustments(screen_adjusted_size, accessibility_requirements)
        reasoning.append(f"Accessibility adjustments: {final_grid_size}")

        # Step 5: Calculate optimal layout
        layout_result = self._calculate_optimal_layout(
            final_grid_size, screen, cognitive_load_level, accessibility_requirements
        )

        reasoning.extend(layout_result["reasoning"])

        # Step 6: Validate and finalize
        validated_result = self._validate_grid_calculation(layout_result, screen)

        return GridCalculationResult(
            grid_size=validated_result["grid_size"],
            pattern=validated_result["pattern"],
            cell_size=validated_result["cell_size"],
            spacing=validated_result["spacing"],
            total_width=validated_result["total_width"],
            total_height=validated_result["total_height"],
            cells_per_row=validated_result["cells_per_row"],
            cells_per_column=validated_result["cells_per_column"],
            reasoning=reasoning,
            confidence=validated_result["confidence"],
        )

    def _calculate_base_grid_size(self, content_count: int) -> int:
        """Calculate base grid size from content count."""
        if content_count <= 4:
            return 4  # 2x2 minimum
        elif content_count <= 9:
            return 9  # 3x3
        elif content_count <= 16:
            return 16  # 4x4
        else:
            # For larger content, find optimal rectangular arrangement
            sqrt_count = math.sqrt(content_count)
            if sqrt_count == int(sqrt_count):
                return content_count  # Perfect square
            else:
                # Round up to next perfect square or reasonable rectangle
                return min(16, math.ceil(sqrt_count) ** 2)

    def _apply_cognitive_load_adjustment(self, base_size: int, load_level: str) -> int:
        """Apply cognitive load adjustments to grid size."""
        if load_level not in self.cognitive_load_factors:
            return base_size

        factor = self.cognitive_load_factors[load_level]["size_multiplier"]
        adjusted_size = int(base_size * factor)

        # Ensure we stay within constraints
        adjusted_size = max(
            self.constraints.min_grid_size,
            min(self.constraints.max_grid_size, adjusted_size),
        )

        # Ensure perfect squares for simple layouts
        perfect_squares = [4, 9, 16]
        if adjusted_size not in perfect_squares:
            # Find closest perfect square
            closest = min(perfect_squares, key=lambda x: abs(x - adjusted_size))
            adjusted_size = closest

        return adjusted_size

    def _apply_screen_constraints(self, grid_size: int, screen: ScreenDimensions) -> int:
        """Apply screen size constraints to grid size."""
        # Calculate available screen space
        available_width = screen.width - screen.safe_area_insets["left"] - screen.safe_area_insets["right"]
        available_height = screen.height - screen.safe_area_insets["top"] - screen.safe_area_insets["bottom"]

        # Reserve space for UI elements (roughly 40% of screen for grid)
        grid_area_width = available_width * 0.9
        grid_area_height = available_height * 0.4

        # Calculate maximum grid size that fits
        cells_per_row = int(math.sqrt(grid_size))
        min_cell_size = self.constraints.min_cell_size
        min_spacing = self.constraints.min_spacing

        # Check if current grid size fits
        required_width = cells_per_row * min_cell_size + (cells_per_row - 1) * min_spacing
        required_height = required_width  # Assume square cells

        if required_width > grid_area_width or required_height > grid_area_height:
            # Reduce grid size to fit
            max_cells_width = int((grid_area_width + min_spacing) / (min_cell_size + min_spacing))
            max_cells_height = int((grid_area_height + min_spacing) / (min_cell_size + min_spacing))
            max_total_cells = max_cells_width * max_cells_height

            # Find largest perfect square that fits
            perfect_squares = [4, 9, 16]
            for size in reversed(perfect_squares):
                if size <= max_total_cells and size <= grid_size:
                    return size

            # Fallback to minimum
            return self.constraints.min_grid_size

        return grid_size

    def _apply_accessibility_adjustments(
        self, grid_size: int, accessibility_requirements: Optional[dict[str, Any]]
    ) -> int:
        """Apply accessibility adjustments to grid size."""
        if not self.config.get("accessibility_enabled", True):
            return grid_size

        requirements = accessibility_requirements or {}

        # If accessibility is required, ensure larger touch targets
        if requirements.get("large_touch_targets", False):
            # Reduce grid size to accommodate larger touch targets
            if grid_size > 9:
                return 9  # Maximum 3x3 for large touch targets
            elif grid_size > 4:
                return 4  # Prefer 2x2 for maximum accessibility

        # If high contrast is needed, ensure enough spacing
        if requirements.get("high_contrast", False) and grid_size > 9:
            return 9  # Reduce complexity for high contrast

        # If motor impairment considerations
        if requirements.get("motor_impairment", False):
            return min(grid_size, 4)  # Maximum 2x2 for motor accessibility

        return grid_size

    def _calculate_optimal_layout(
        self,
        grid_size: int,
        screen: ScreenDimensions,
        cognitive_load_level: str,
        accessibility_requirements: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate optimal layout parameters for the grid."""
        reasoning = []

        # Determine grid pattern
        pattern = self._determine_grid_pattern(grid_size, accessibility_requirements)
        reasoning.append(f"Selected pattern: {pattern.value}")

        # Calculate cells per row/column
        if pattern == GridPattern.SQUARE:
            cells_per_row = int(math.sqrt(grid_size))
            cells_per_column = cells_per_row
        else:
            # For non-square patterns, calculate optimal rectangle
            cells_per_row, cells_per_column = self._calculate_rectangular_layout(grid_size, screen)

        reasoning.append(f"Layout: {cells_per_row}×{cells_per_column}")

        # Calculate available space
        available_width = screen.width * 0.9  # 90% of screen width
        available_height = screen.height * 0.4  # 40% of screen height for grid

        # Calculate optimal cell size
        max_cell_width = (available_width - (cells_per_row - 1) * self.constraints.min_spacing) / cells_per_row
        max_cell_height = (available_height - (cells_per_column - 1) * self.constraints.min_spacing) / cells_per_column

        # Use square cells (smallest dimension)
        optimal_cell_size = min(max_cell_width, max_cell_height)

        # Apply cognitive load adjustments to cell size
        if cognitive_load_level in self.cognitive_load_factors:
            size_factor = self.cognitive_load_factors[cognitive_load_level]["size_multiplier"]
            optimal_cell_size *= size_factor

        # Apply accessibility adjustments
        if accessibility_requirements and accessibility_requirements.get("large_touch_targets", False):
            optimal_cell_size = max(optimal_cell_size, self.accessibility_guidelines["min_touch_target"])

        # Constrain cell size
        optimal_cell_size = max(
            self.constraints.min_cell_size,
            min(self.constraints.max_cell_size, optimal_cell_size),
        )

        reasoning.append(f"Optimal cell size: {optimal_cell_size:.1f}pt")

        # Calculate optimal spacing
        optimal_spacing = self._calculate_optimal_spacing(
            cognitive_load_level, accessibility_requirements, optimal_cell_size
        )

        reasoning.append(f"Optimal spacing: {optimal_spacing:.1f}pt")

        # Calculate total dimensions
        total_width = cells_per_row * optimal_cell_size + (cells_per_row - 1) * optimal_spacing
        total_height = cells_per_column * optimal_cell_size + (cells_per_column - 1) * optimal_spacing

        # Calculate confidence based on how well constraints are satisfied
        confidence = self._calculate_layout_confidence(
            optimal_cell_size, optimal_spacing, total_width, total_height, screen
        )

        return {
            "grid_size": grid_size,
            "pattern": pattern,
            "cell_size": optimal_cell_size,
            "spacing": optimal_spacing,
            "total_width": total_width,
            "total_height": total_height,
            "cells_per_row": cells_per_row,
            "cells_per_column": cells_per_column,
            "reasoning": reasoning,
            "confidence": confidence,
        }

    def _determine_grid_pattern(
        self, grid_size: int, accessibility_requirements: Optional[dict[str, Any]]
    ) -> GridPattern:
        """Determine optimal grid pattern."""
        # For accessibility, prefer square patterns
        if accessibility_requirements and accessibility_requirements.get("simple_layout", True):
            return GridPattern.SQUARE

        # For perfect squares, use square pattern
        sqrt_size = math.sqrt(grid_size)
        if sqrt_size == int(sqrt_size):
            return GridPattern.SQUARE

        # For other sizes, use adaptive pattern
        return GridPattern.ADAPTIVE

    def _calculate_rectangular_layout(self, grid_size: int, screen: ScreenDimensions) -> tuple[int, int]:
        """Calculate optimal rectangular layout for non-square grid sizes."""
        # Find factors of grid_size
        factors = []
        for i in range(1, int(math.sqrt(grid_size)) + 1):
            if grid_size % i == 0:
                factors.append((i, grid_size // i))

        if not factors:
            # Fallback to approximate square
            sqrt_size = int(math.sqrt(grid_size))
            return sqrt_size, sqrt_size

        # Choose factors that best match screen aspect ratio
        screen_ratio = screen.width / screen.height
        best_factors = factors[0]
        best_ratio_diff = float("inf")

        for width, height in factors:
            ratio = width / height
            ratio_diff = abs(ratio - screen_ratio)
            if ratio_diff < best_ratio_diff:
                best_ratio_diff = ratio_diff
                best_factors = (width, height)

        return best_factors

    def _calculate_optimal_spacing(
        self,
        cognitive_load_level: str,
        accessibility_requirements: Optional[dict[str, Any]],
        cell_size: float,
    ) -> float:
        """Calculate optimal spacing between grid cells."""
        # Base spacing as percentage of cell size
        base_spacing = cell_size * 0.15  # 15% of cell size

        # Apply cognitive load adjustments
        if cognitive_load_level in self.cognitive_load_factors:
            spacing_factor = self.cognitive_load_factors[cognitive_load_level]["spacing_multiplier"]
            base_spacing *= spacing_factor

        # Apply accessibility adjustments
        if accessibility_requirements and accessibility_requirements.get("large_spacing", False):
            base_spacing *= self.accessibility_guidelines["spacing_multiplier"]

        # Constrain spacing
        optimal_spacing = max(
            self.constraints.min_spacing,
            min(self.constraints.max_spacing, base_spacing),
        )

        return optimal_spacing

    def _calculate_layout_confidence(
        self,
        cell_size: float,
        spacing: float,
        total_width: float,
        total_height: float,
        screen: ScreenDimensions,
    ) -> float:
        """Calculate confidence in the layout calculation."""
        confidence_factors = []

        # Cell size confidence
        ideal_cell_size = 60.0  # Ideal cell size
        cell_size_confidence = 1.0 - abs(cell_size - ideal_cell_size) / ideal_cell_size
        confidence_factors.append(max(0.0, cell_size_confidence))

        # Screen utilization confidence
        available_width = screen.width * 0.9
        available_height = screen.height * 0.4
        width_utilization = total_width / available_width
        height_utilization = total_height / available_height

        # Optimal utilization is around 80%
        optimal_utilization = 0.8
        width_confidence = 1.0 - abs(width_utilization - optimal_utilization)
        height_confidence = 1.0 - abs(height_utilization - optimal_utilization)

        confidence_factors.append(max(0.0, width_confidence))
        confidence_factors.append(max(0.0, height_confidence))

        # Accessibility compliance confidence
        if cell_size >= self.accessibility_guidelines["min_touch_target"]:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.6)

        # Calculate overall confidence
        return sum(confidence_factors) / len(confidence_factors)

    def _validate_grid_calculation(self, layout_result: dict[str, Any], screen: ScreenDimensions) -> dict[str, Any]:
        """Validate and potentially adjust the grid calculation."""
        result = layout_result.copy()

        # Ensure grid fits on screen
        available_width = screen.width * 0.9
        available_height = screen.height * 0.4

        if result["total_width"] > available_width or result["total_height"] > available_height:
            # Scale down proportionally
            scale_factor = (
                min(
                    available_width / result["total_width"],
                    available_height / result["total_height"],
                )
                * 0.95
            )  # 5% margin

            result["cell_size"] *= scale_factor
            result["spacing"] *= scale_factor
            result["total_width"] *= scale_factor
            result["total_height"] *= scale_factor
            result["confidence"] *= 0.8  # Reduce confidence due to scaling

        # Ensure minimum touch target sizes
        if result["cell_size"] < self.constraints.min_cell_size:
            result["cell_size"] = self.constraints.min_cell_size
            # Recalculate total dimensions
            result["total_width"] = (
                result["cells_per_row"] * result["cell_size"] + (result["cells_per_row"] - 1) * result["spacing"]
            )
            result["total_height"] = (
                result["cells_per_column"] * result["cell_size"] + (result["cells_per_column"] - 1) * result["spacing"]
            )
            result["confidence"] *= 0.9

        return result

    def calculate_adaptive_grid_size(
        self,
        performance_data: dict[str, Any],
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> int:
        """
        Calculate adaptive grid size based on user performance and preferences.

        Args:
            performance_data: User performance metrics
            user_preferences: User-specific preferences

        Returns:
            Recommended grid size
        """
        # Extract performance indicators
        accuracy = performance_data.get("accuracy", 0.8)
        avg_response_time = performance_data.get("avg_response_time_ms", 1000)
        error_rate = performance_data.get("error_rate", 0.1)

        # Base grid size on performance
        if accuracy > 0.9 and avg_response_time < 800:
            # High performance - can handle larger grids
            base_size = 16
        elif accuracy > 0.7 and avg_response_time < 1200:
            # Good performance - standard grids
            base_size = 9
        else:
            # Lower performance - smaller grids
            base_size = 4

        # Adjust based on error rate
        if error_rate > 0.2:
            base_size = min(base_size, 4)  # High error rate, use smallest grid
        elif error_rate < 0.05:
            base_size = min(16, base_size + 4)  # Low error rate, can increase slightly

        # Apply user preferences
        if user_preferences:
            preference_multiplier = user_preferences.get("grid_size_preference", 1.0)
            base_size = int(base_size * preference_multiplier)

        # Ensure within constraints
        return max(
            self.constraints.min_grid_size,
            min(self.constraints.max_grid_size, base_size),
        )

    def get_grid_status(self) -> dict[str, Any]:
        """Get current grid calculator status and configuration."""
        return {
            "config": self.config.copy(),
            "constraints": {
                "min_grid_size": self.constraints.min_grid_size,
                "max_grid_size": self.constraints.max_grid_size,
                "min_cell_size": self.constraints.min_cell_size,
                "max_cell_size": self.constraints.max_cell_size,
                "min_spacing": self.constraints.min_spacing,
                "max_spacing": self.constraints.max_spacing,
            },
            "cognitive_load_factors": self.cognitive_load_factors.copy(),
            "accessibility_guidelines": self.accessibility_guidelines.copy(),
            "default_screen": {
                "width": self.default_screen.width,
                "height": self.default_screen.height,
                "pixel_density": self.default_screen.pixel_density,
                "orientation": self.default_screen.orientation,
            },
        }


# Export the main classes
__all__ = [
    "GridCalculationResult",
    "GridConstraints",
    "GridPattern",
    "GridSizeCalculator",
    "ScreenDimensions",
    "SizingMode",
]