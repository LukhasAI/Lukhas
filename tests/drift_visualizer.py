#!/usr/bin/env python3
"""
LUKHΛS Drift Map Visualizer
Generate entropy/drift visualizations over time
Trinity Framework: ⚛️🧠🛡️
"""

import json
import math
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriftVisualizer:
    """
    Creates ASCII and SVG visualizations of symbolic drift patterns
    """
    
    def __init__(self, data_path: str = "data/drift_audit_results.jsonl"):
        """
        Initialize the visualizer.
        
        Args:
            data_path: Path to drift audit results
        """
        self.data_path = Path(data_path)
        self.sessions = []
        self._load_data()
        
        # Visualization settings
        self.ascii_width = 80
        self.ascii_height = 20
        self.svg_width = 800
        self.svg_height = 400
        
        # Trinity glyphs
        self.trinity_glyphs = "⚛️🧠🛡️"
        
        logger.info("📊 Drift Visualizer initialized")
        logger.info(f"   Loaded {len(self.sessions)} sessions")
    
    def _load_data(self):
        """Load drift audit results"""
        if not self.data_path.exists():
            logger.warning(f"No data found at {self.data_path}")
            return
        
        with open(self.data_path, 'r') as f:
            for line in f:
                try:
                    session = json.loads(line.strip())
                    self.sessions.append(session)
                except:
                    continue
    
    def generate_ascii_drift_map(self, output_path: str = "visualizations/drift_log.txt") -> str:
        """
        Generate ASCII visualization of drift over time.
        
        Args:
            output_path: Where to save the visualization
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.sessions:
            logger.error("No sessions to visualize")
            return ""
        
        # Prepare data
        drift_scores = [s['metrics']['drift_score'] for s in self.sessions]
        entropy_scores = [s['metrics']['entropy'] for s in self.sessions]
        trinity_scores = [s['metrics']['trinity_coherence'] for s in self.sessions]
        
        # Create ASCII art
        lines = []
        lines.append("=" * self.ascii_width)
        lines.append("LUKHΛS DRIFT MAP - ASCII VISUALIZATION".center(self.ascii_width))
        lines.append(f"Trinity Framework: {self.trinity_glyphs}".center(self.ascii_width))
        lines.append("=" * self.ascii_width)
        lines.append("")
        
        # Drift chart
        lines.append("DRIFT SCORE (0.0 - 1.0)")
        lines.extend(self._create_ascii_chart(drift_scores, "Drift", "🔥"))
        lines.append("")
        
        # Entropy chart
        lines.append("ENTROPY LEVEL (0.0 - 1.0)")
        lines.extend(self._create_ascii_chart(entropy_scores, "Entropy", "🌀"))
        lines.append("")
        
        # Trinity coherence chart
        lines.append("TRINITY COHERENCE (0.0 - 1.0)")
        lines.extend(self._create_ascii_chart(trinity_scores, "Trinity", "🛡️"))
        lines.append("")
        
        # Session details
        lines.append("=" * self.ascii_width)
        lines.append("SESSION DETAILS")
        lines.append("=" * self.ascii_width)
        
        for i, session in enumerate(self.sessions):
            lines.append(f"\nSession {i+1}: {session['category']}")
            lines.append(f"  Drift: {session['metrics']['drift_score']:.2f} | "
                        f"Entropy: {session['metrics']['entropy']:.2f} | "
                        f"Trinity: {session['metrics']['trinity_coherence']:.2f}")
            lines.append(f"  Risk: {session['risk_level']} | "
                        f"Persona: {session['persona_aligned']}")
            lines.append(f"  Intervention: {'Yes' if session['intervention_applied'] else 'No'} | "
                        f"Issue: {session['diagnosis']}")
            
            # Show glyphs
            if session['glyphs_detected']:
                lines.append(f"  Glyphs: {' '.join(session['glyphs_detected'])}")
        
        # Risk summary
        lines.append("")
        lines.append("=" * self.ascii_width)
        lines.append("RISK SUMMARY")
        lines.append("=" * self.ascii_width)
        
        risk_counts = {}
        for s in self.sessions:
            risk = s['risk_level']
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        for risk, count in sorted(risk_counts.items()):
            bar_length = int((count / len(self.sessions)) * 40)
            bar = "█" * bar_length
            lines.append(f"{risk:8s}: {bar} ({count}/{len(self.sessions)})")
        
        # Recommendations
        avg_drift = sum(drift_scores) / len(drift_scores)
        avg_trinity = sum(trinity_scores) / len(trinity_scores)
        
        lines.append("")
        lines.append("=" * self.ascii_width)
        lines.append("RECOMMENDATIONS")
        lines.append("=" * self.ascii_width)
        
        if avg_drift > 0.7:
            lines.append("⚠️  High average drift - immediate intervention needed")
        if avg_trinity < 0.3:
            lines.append("🛡️  Critical Trinity deficit - restore core framework")
        if risk_counts.get('critical', 0) > len(self.sessions) / 2:
            lines.append("🚨 Majority critical risk - system realignment required")
        
        # Save to file
        content = '\n'.join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📄 ASCII drift map saved to {output_path}")
        return str(output_path)
    
    def _create_ascii_chart(self, values: List[float], label: str, 
                           symbol: str = "█") -> List[str]:
        """Create ASCII bar chart"""
        lines = []
        
        # Scale values to ASCII height
        max_height = 10
        scaled_values = [int(v * max_height) for v in values]
        
        # Create chart
        for h in range(max_height, 0, -1):
            line = f"{h/10:3.1f} |"
            for v in scaled_values:
                if v >= h:
                    line += f" {symbol} "
                else:
                    line += "   "
            lines.append(line)
        
        # X-axis
        lines.append("    +" + "-" * (len(values) * 3))
        x_labels = "     "
        for i in range(len(values)):
            x_labels += f"{i+1:^3}"
        lines.append(x_labels)
        
        return lines
    
    def generate_svg_drift_map(self, output_path: str = "visualizations/drift_map.svg") -> str:
        """
        Generate SVG visualization of drift patterns.
        
        Args:
            output_path: Where to save the SVG
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.sessions:
            logger.error("No sessions to visualize")
            return ""
        
        # Prepare data
        drift_scores = [s['metrics']['drift_score'] for s in self.sessions]
        entropy_scores = [s['metrics']['entropy'] for s in self.sessions]
        trinity_scores = [s['metrics']['trinity_coherence'] for s in self.sessions]
        
        # SVG header
        svg_lines = [
            f'<svg width="{self.svg_width}" height="{self.svg_height}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            '<rect width="100%" height="100%" fill="#1a1a1a"/>',
            '<style>',
            '.title { fill: #fff; font-family: monospace; font-size: 20px; }',
            '.label { fill: #aaa; font-family: monospace; font-size: 12px; }',
            '.drift { stroke: #ff6b6b; stroke-width: 2; fill: none; }',
            '.entropy { stroke: #4ecdc4; stroke-width: 2; fill: none; }',
            '.trinity { stroke: #45b7d1; stroke-width: 2; fill: none; }',
            '.grid { stroke: #333; stroke-width: 1; }',
            '</style>'
        ]
        
        # Title
        svg_lines.append(f'<text x="{self.svg_width/2}" y="30" text-anchor="middle" '
                        f'class="title">LUKHΛS Drift Map - {self.trinity_glyphs}</text>')
        
        # Chart area
        chart_x = 60
        chart_y = 60
        chart_width = self.svg_width - 120
        chart_height = self.svg_height - 120
        
        # Grid
        for i in range(11):
            y = chart_y + (i * chart_height / 10)
            svg_lines.append(f'<line x1="{chart_x}" y1="{y}" x2="{chart_x + chart_width}" '
                           f'y2="{y}" class="grid"/>')
            svg_lines.append(f'<text x="{chart_x - 10}" y="{y + 5}" text-anchor="end" '
                           f'class="label">{1 - i/10:.1f}</text>')
        
        # Plot lines
        x_step = chart_width / (len(self.sessions) - 1) if len(self.sessions) > 1 else chart_width
        
        # Drift line
        drift_path = self._create_svg_path(drift_scores, chart_x, chart_y, 
                                         chart_width, chart_height)
        svg_lines.append(f'<path d="{drift_path}" class="drift"/>')
        
        # Entropy line
        entropy_path = self._create_svg_path(entropy_scores, chart_x, chart_y,
                                           chart_width, chart_height)
        svg_lines.append(f'<path d="{entropy_path}" class="entropy"/>')
        
        # Trinity line
        trinity_path = self._create_svg_path(trinity_scores, chart_x, chart_y,
                                           chart_width, chart_height)
        svg_lines.append(f'<path d="{trinity_path}" class="trinity"/>')
        
        # Legend
        legend_y = self.svg_height - 30
        svg_lines.append(f'<line x1="100" y1="{legend_y}" x2="130" y2="{legend_y}" '
                        f'class="drift"/>')
        svg_lines.append(f'<text x="135" y="{legend_y + 5}" class="label">Drift</text>')
        
        svg_lines.append(f'<line x1="200" y1="{legend_y}" x2="230" y2="{legend_y}" '
                        f'class="entropy"/>')
        svg_lines.append(f'<text x="235" y="{legend_y + 5}" class="label">Entropy</text>')
        
        svg_lines.append(f'<line x1="320" y1="{legend_y}" x2="350" y2="{legend_y}" '
                        f'class="trinity"/>')
        svg_lines.append(f'<text x="355" y="{legend_y + 5}" class="label">Trinity</text>')
        
        # Risk indicators
        for i, session in enumerate(self.sessions):
            if session['risk_level'] == 'critical':
                x = chart_x + (i * x_step)
                svg_lines.append(f'<circle cx="{x}" cy="{chart_y - 10}" r="5" '
                               f'fill="#ff0000" opacity="0.7"/>')
        
        # Close SVG
        svg_lines.append('</svg>')
        
        # Save to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(svg_lines))
        
        logger.info(f"🎨 SVG drift map saved to {output_path}")
        return str(output_path)
    
    def _create_svg_path(self, values: List[float], x: int, y: int, 
                        width: int, height: int) -> str:
        """Create SVG path for line chart"""
        if not values:
            return ""
        
        x_step = width / (len(values) - 1) if len(values) > 1 else 0
        
        points = []
        for i, v in enumerate(values):
            px = x + (i * x_step)
            py = y + height - (v * height)
            
            if i == 0:
                points.append(f"M {px},{py}")
            else:
                points.append(f"L {px},{py}")
        
        return " ".join(points)
    
    def generate_cumulative_report(self, output_path: str = "visualizations/cumulative_drift_report.txt") -> str:
        """
        Generate cumulative drift analysis report.
        
        Args:
            output_path: Where to save the report
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.sessions:
            logger.error("No sessions to analyze")
            return ""
        
        lines = []
        lines.append("="*60)
        lines.append("LUKHΛS CUMULATIVE DRIFT ANALYSIS")
        lines.append(f"Trinity Framework: {self.trinity_glyphs}")
        lines.append("="*60)
        lines.append(f"\nTotal Sessions Analyzed: {len(self.sessions)}")
        lines.append(f"Analysis Period: {self.sessions[0]['timestamp']} to {self.sessions[-1]['timestamp']}")
        
        # Calculate cumulative metrics
        total_drift = sum(s['metrics']['drift_score'] for s in self.sessions)
        total_entropy = sum(s['metrics']['entropy'] for s in self.sessions)
        total_trinity = sum(s['metrics']['trinity_coherence'] for s in self.sessions)
        
        lines.append("\nCUMULATIVE METRICS:")
        lines.append(f"  Total Drift Accumulated: {total_drift:.2f}")
        lines.append(f"  Total Entropy Generated: {total_entropy:.2f}")
        lines.append(f"  Total Trinity Coherence: {total_trinity:.2f}")
        
        # Trend analysis
        mid_point = len(self.sessions) // 2
        first_half_drift = sum(s['metrics']['drift_score'] for s in self.sessions[:mid_point]) / mid_point
        second_half_drift = sum(s['metrics']['drift_score'] for s in self.sessions[mid_point:]) / (len(self.sessions) - mid_point)
        
        drift_trend = "increasing" if second_half_drift > first_half_drift else "decreasing"
        
        lines.append(f"\nDRIFT TREND: {drift_trend}")
        lines.append(f"  First Half Average: {first_half_drift:.3f}")
        lines.append(f"  Second Half Average: {second_half_drift:.3f}")
        
        # Intervention effectiveness
        interventions = [s for s in self.sessions if s['intervention_applied']]
        if interventions:
            healing_improvements = []
            for s in interventions:
                if s['healing_metrics']:
                    healing_improvements.append(s['healing_metrics']['improvement'])
            
            if healing_improvements:
                avg_improvement = sum(healing_improvements) / len(healing_improvements)
                lines.append(f"\nINTERVENTION EFFECTIVENESS:")
                lines.append(f"  Total Interventions: {len(interventions)}")
                lines.append(f"  Average Drift Reduction: {avg_improvement:.3f}")
        
        # Persona distribution
        persona_counts = {}
        for s in self.sessions:
            persona = s['persona_aligned']
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        lines.append("\nPERSONA DISTRIBUTION:")
        for persona, count in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.sessions)) * 100
            lines.append(f"  {persona}: {count} ({percentage:.1f}%)")
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"📊 Cumulative report saved to {output_path}")
        return str(output_path)


def main():
    """Generate all drift visualizations"""
    visualizer = DriftVisualizer()
    
    # Generate ASCII map
    ascii_path = visualizer.generate_ascii_drift_map()
    print(f"✅ ASCII drift map: {ascii_path}")
    
    # Generate SVG map
    svg_path = visualizer.generate_svg_drift_map()
    print(f"✅ SVG drift map: {svg_path}")
    
    # Generate cumulative report
    report_path = visualizer.generate_cumulative_report()
    print(f"✅ Cumulative report: {report_path}")
    
    # Display ASCII preview
    if ascii_path and Path(ascii_path).exists():
        print("\n📊 ASCII Drift Map Preview:")
        print("-" * 60)
        with open(ascii_path, 'r', encoding='utf-8') as f:
            preview = f.read().split('\n')[:30]
            print('\n'.join(preview))
        print("... (truncated)")


if __name__ == "__main__":
    main()