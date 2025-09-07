#!/usr/bin/env python3
"""
LUKHΛS Red Team Glyph Map Generator
===================================
Generates CSV and HTML timeline visualization of authentication events,
fallback attempts, cultural glyphs, and match scores for security audits.

🛡️ FEATURES:
- Symbolic glyph timeline tracking
- Fallback trigger analysis
- Cultural adaptation logging
- Match score visualization
- Interactive HTML dashboard
- CSV export for audit trails

Author: LUKHΛS AI Systems
Version: 1.0.0 - Red Team Glyph Map
Created: 2025-08-03
"""
import csv
import json
import logging
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class GlyphEvent:
    """Represents a single glyph event in the timeline"""

    timestamp: datetime
    user_id: str
    event_type: str
    tier: str
    consciousness_state: str
    cultural_glyph: str
    match_score: float
    success: bool
    fallback_triggered: bool
    fallback_type: Optional[str]
    glyphs_used: list[str]
    ethical_score: float
    audit_notes: str


class GlyphTimelineGenerator:
    """Generates glyph timeline for red team analysis"""

    def __init__(self, output_dir: str = "audit/red_team"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events: list[GlyphEvent] = []

        # Glyph categories for analysis
        self.glyph_categories = {
            "success": ["✅", "🌟", "✨", "💚", "🎯"],
            "failure": ["❌", "⚠️", "🚫", "💔", "🔒"],
            "fallback": ["🔄", "🔁", "↩️", "🔀", "🔃"],
            "cultural": ["🪷", "🦅", "🛡️", "🌍", "🌊", "🌸", "🎋"],
            "consciousness": ["🧘", "🎨", "🔬", "💭", "🌊", "🎯"],
            "security": ["🔐", "🔒", "🛡️", "⚡", "🔑", "🚨"],
        }

        logger.info("🛡️ Red Team Glyph Map Generator initialized")

    def generate_mock_events(self, num_events: int = 100) -> list[GlyphEvent]:
        """Generate mock authentication events for testing"""
        events = []
        base_time = datetime.now(timezone.utc) - timedelta(hours=24)

        users = [
            "t1_user_001",
            "t3_user_002",
            "t5_user_003",
            "qi_master",
            "test_attacker",
        ]
        tiers = ["T1", "T2", "T3", "T4", "T5"]
        consciousness_states = [
            "focused",
            "creative",
            "meditative",
            "analytical",
            "dreaming",
            "flow_state",
        ]
        cultures = ["asia", "americas", "europe", "africa", "oceania"]
        fallback_types = [
            "VOICE_PLUS_EMOJI",
            "BEHAVIORAL_PLUS_KEYWORD",
            "EMOJI_CONSCIOUSNESS_BOOST",
            None,
        ]

        for _i in range(num_events):
            # Simulate time progression
            base_time += timedelta(minutes=random.randint(1, 30))

            # Determine success based on tier and user
            user = random.choice(users)
            tier = random.choice(tiers)
            is_attacker = "attacker" in user

            # Calculate match score
            if is_attacker:
                match_score = random.uniform(0.3, 0.7)  # Attackers have low scores
            else:
                tier_num = int(tier[1])
                base_score = 0.7 + (tier_num * 0.05)
                match_score = min(0.99, base_score + random.uniform(-0.1, 0.1))

            success = match_score >= 0.8 and not is_attacker
            fallback_triggered = match_score < 0.85 and not success

            # Select glyphs based on outcome
            cultural_glyph = self.glyph_categories["cultural"][cultures.index(random.choice(cultures))]
            consciousness_glyph = random.choice(self.glyph_categories["consciousness"])

            glyphs_used = [cultural_glyph, consciousness_glyph]
            if success:
                glyphs_used.extend(random.sample(self.glyph_categories["success"], 2))
            else:
                glyphs_used.extend(random.sample(self.glyph_categories["failure"], 2))

            if fallback_triggered:
                glyphs_used.append(random.choice(self.glyph_categories["fallback"]))

            event = GlyphEvent(
                timestamp=base_time,
                user_id=user,
                event_type="authentication_attempt",
                tier=tier,
                consciousness_state=random.choice(consciousness_states),
                cultural_glyph=cultural_glyph,
                match_score=match_score,
                success=success,
                fallback_triggered=fallback_triggered,
                fallback_type=(random.choice(fallback_types) if fallback_triggered else None),
                glyphs_used=glyphs_used,
                ethical_score=(random.uniform(0.7, 1.0) if success else random.uniform(0.3, 0.7)),
                audit_notes=f"{'SUSPICIOUS' if is_attacker else 'Normal'} authentication attempt",
            )

            events.append(event)

        self.events.extend(events)
        return events

    def export_to_csv(self, filename: str = "glyph_timeline.csv") -> str:
        """Export events to CSV format"""
        csv_path = self.output_dir / filename

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp",
                "user_id",
                "event_type",
                "tier",
                "consciousness_state",
                "cultural_glyph",
                "match_score",
                "success",
                "fallback_triggered",
                "fallback_type",
                "glyphs_used",
                "ethical_score",
                "audit_notes",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in self.events:
                row = asdict(event)
                row["timestamp"] = event.timestamp.isoformat()
                row["glyphs_used"] = "".join(event.glyphs_used)
                writer.writerow(row)

        logger.info(f"📊 Exported {len(self.events)} events to {csv_path}")
        return str(csv_path)

    def generate_html_visualization(self, filename: str = "glyph_timeline.html") -> str:
        """Generate interactive HTML visualization"""
        html_path = self.output_dir / filename

        html_content = (
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHΛS Red Team Glyph Timeline</title>
    <style>
        body {
            font-family: 'Consolas', 'Monaco', monospace;
            background: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid #00ff00;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #333;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }

        .timeline {
            background: #111;
            padding: 20px;
            border-radius: 10px;
            max-height: 600px;
            overflow-y: auto;
        }

        .event {
            background: #1a1a1a;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #333;
            transition: all 0.3s ease;
        }

        .event:hover {
            background: #2a2a2a;
            transform: translateX(5px);
        }

        .event.success {
            border-left-color: #00ff00;
        }

        .event.failure {
            border-left-color: #ff0000;
        }

        .event.fallback {
            border-left-color: #ffaa00;
        }

        .event-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .glyphs {
            font-size: 1.5em;
            letter-spacing: 5px;
        }

        .score {
            font-size: 1.2em;
            font-weight: bold;
        }

        .score.high { color: #00ff00; }
        .score.medium { color: #ffaa00; }
        .score.low { color: #ff0000; }

        .details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }

        .filter-controls {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .filter-control {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        select, input {
            background: #0a0a0a;
            color: #00ff00;
            border: 1px solid #333;
            padding: 5px 10px;
            border-radius: 5px;
        }

        .chart-container {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            height: 300px;
            position: relative;
        }

        #scoreChart {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ LUKHΛS Red Team Glyph Timeline</h1>
        <p>Authentication Event Analysis Dashboard</p>
    </div>

    <div class="stats" id="stats">
        <!-- Stats will be populated by JavaScript -->
    </div>

    <div class="filter-controls">
        <div class="filter-control">
            <label>User Filter</label>
            <select id="userFilter" onchange="filterEvents()">
                <option value="">All Users</option>
            </select>
        </div>
        <div class="filter-control">
            <label>Tier Filter</label>
            <select id="tierFilter" onchange="filterEvents()">
                <option value="">All Tiers</option>
                <option value="T1">T1</option>
                <option value="T2">T2</option>
                <option value="T3">T3</option>
                <option value="T4">T4</option>
                <option value="T5">T5</option>
            </select>
        </div>
        <div class="filter-control">
            <label>Status Filter</label>
            <select id="statusFilter" onchange="filterEvents()">
                <option value="">All</option>
                <option value="success">Success</option>
                <option value="failure">Failure</option>
                <option value="fallback">Fallback</option>
            </select>
        </div>
        <div class="filter-control">
            <label>Score Threshold</label>
            <input type="range" id="scoreThreshold" min="0" max="100" value="0"
                   oninput="document.getElementById('scoreValue').textContent = this.value/100; filterEvents()">
            <span id="scoreValue">0</span>
        </div>
    </div>

    <div class="chart-container">
        <canvas id="scoreChart"></canvas>
    </div>

    <div class="timeline" id="timeline">
        <!-- Events will be populated by JavaScript -->
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Event data
        const events = """
            + json.dumps(
                [
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "user_id": event.user_id,
                        "event_type": event.event_type,
                        "tier": event.tier,
                        "consciousness_state": event.consciousness_state,
                        "cultural_glyph": event.cultural_glyph,
                        "match_score": event.match_score,
                        "success": event.success,
                        "fallback_triggered": event.fallback_triggered,
                        "fallback_type": event.fallback_type,
                        "glyphs_used": event.glyphs_used,
                        "ethical_score": event.ethical_score,
                        "audit_notes": event.audit_notes,
                    }
                    for event in self.events
                ]
            )
            + """;

        let filteredEvents = [...events];
        let scoreChart = null;

        function initializeDashboard() {
            // Populate user filter
            const users = [...new Set(events.map(e => e.user_id))];
            const userFilter = document.getElementById('userFilter');
            users.forEach(user => {
                const option = document.createElement('option');
                option.value = user;
                option.textContent = user;
                userFilter.appendChild(option);
            });

            // Initialize chart
            const ctx = document.getElementById('scoreChart').getContext('2d');
            scoreChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Match Score',
                        data: [],
                        borderColor: '#00ff00',
                        backgroundColor: 'rgba(0, 255, 0, 0.1)',
                        tension: 0.1
                    }, {
                        label: 'Ethical Score',
                        data: [],
                        borderColor: '#00aaff',
                        backgroundColor: 'rgba(0, 170, 255, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1,
                            grid: { color: '#333' },
                            ticks: { color: '#00ff00' }
                        },
                        x: {
                            grid: { color: '#333' },
                            ticks: { color: '#00ff00' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#00ff00' }
                        }
                    }
                }
            });

            updateStats();
            renderEvents();
            updateChart();
        }

        function updateStats() {
            const successCount = filteredEvents.filter(e => e.success).length;
            const failureCount = filteredEvents.filter(e => !e.success).length;
            const fallbackCount = filteredEvents.filter(e => e.fallback_triggered).length;
            const avgScore = filteredEvents.reduce((acc, e) => acc + e.match_score, 0) / filteredEvents.length || 0;

            const statsHtml = `
                <div class="stat-card">
                    <div class="stat-label">Total Events</div>
                    <div class="stat-value">${filteredEvents.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">✅ Success Rate</div>
                    <div class="stat-value">${((successCount/filteredEvents.length)*100).toFixed(1)}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">🔄 Fallback Rate</div>
                    <div class="stat-value">${((fallbackCount/filteredEvents.length)*100).toFixed(1)}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">📊 Avg Match Score</div>
                    <div class="stat-value">${avgScore.toFixed(3)}</div>
                </div>
            `;

            document.getElementById('stats').innerHTML = statsHtml;
        }

        function renderEvents() {
            const timeline = document.getElementById('timeline');
            timeline.innerHTML = filteredEvents.map(event => {
                const eventClass = event.success ? 'success' : (event.fallback_triggered ? 'fallback' : 'failure');
                const scoreClass = event.match_score >= 0.9 ? 'high' : (event.match_score >= 0.7 ? 'medium' : 'low');

                return `
                    <div class="event ${eventClass}">
                        <div class="event-header">
                            <div>
                                <strong>${event.user_id}</strong> - ${event.tier}
                                <span class="glyphs">${event.glyphs_used.join('')}</span>
                            </div>
                            <div>
                                <span class="score ${scoreClass}">${event.match_score.toFixed(3)}</span>
                            </div>
                        </div>
                        <div class="details">
                            <div>🕐 ${new Date(event.timestamp).toLocaleString()}</div>
                            <div>🧠 ${event.consciousness_state}</div>
                            <div>🌍 ${event.cultural_glyph}</div>
                            <div>⚖️ ${event.ethical_score.toFixed(2)}</div>
                            ${event.fallback_type ? `<div>🔄 ${event.fallback_type}</div>` : ''}
                            <div>📝 ${event.audit_notes}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function updateChart() {
            const sortedEvents = [...filteredEvents].sort((a, b) =>
                new Date(a.timestamp) - new Date(b.timestamp)
            );

            scoreChart.data.labels = sortedEvents.map((e, i) => i);
            scoreChart.data.datasets[0].data = sortedEvents.map(e => e.match_score);
            scoreChart.data.datasets[1].data = sortedEvents.map(e => e.ethical_score);
            scoreChart.update();
        }

        function filterEvents() {
            const userFilter = document.getElementById('userFilter').value;
            const tierFilter = document.getElementById('tierFilter').value;
            const statusFilter = document.getElementById('statusFilter').value;
            const scoreThreshold = document.getElementById('scoreThreshold').value / 100;

            filteredEvents = events.filter(event => {
                if (userFilter && event.user_id !== userFilter) return false;
                if (tierFilter && event.tier !== tierFilter) return false;
                if (statusFilter === 'success' && !event.success) return false;
                if (statusFilter === 'failure' && event.success) return false;
                if (statusFilter === 'fallback' && !event.fallback_triggered) return false;
                if (event.match_score < scoreThreshold) return false;
                return true;
            });

            updateStats();
            renderEvents();
            updateChart();
        }

        // Initialize on load
        initializeDashboard();
    </script>
</body>
</html>"""
        )

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"🌐 Generated HTML visualization at {html_path}")
        return str(html_path)

    def analyze_patterns(self) -> dict[str, Any]:
        """Analyze patterns in authentication events"""
        if not self.events:
            return {}

        analysis = {
            "total_events": len(self.events),
            "success_rate": sum(1 for e in self.events if e.success) / len(self.events),
            "fallback_rate": sum(1 for e in self.events if e.fallback_triggered) / len(self.events),
            "avg_match_score": sum(e.match_score for e in self.events) / len(self.events),
            "avg_ethical_score": sum(e.ethical_score for e in self.events) / len(self.events),
            "tier_distribution": {},
            "consciousness_distribution": {},
            "cultural_distribution": {},
            "suspicious_users": [],
        }

        # Tier distribution
        for tier in ["T1", "T2", "T3", "T4", "T5"]:
            tier_events = [e for e in self.events if e.tier == tier]
            if tier_events:
                analysis["tier_distribution"][tier] = {
                    "count": len(tier_events),
                    "success_rate": sum(1 for e in tier_events if e.success) / len(tier_events),
                }

        # Find suspicious patterns
        user_stats = {}
        for event in self.events:
            if event.user_id not in user_stats:
                user_stats[event.user_id] = {"attempts": 0, "failures": 0, "scores": []}
            user_stats[event.user_id]["attempts"] += 1
            if not event.success:
                user_stats[event.user_id]["failures"] += 1
            user_stats[event.user_id]["scores"].append(event.match_score)

        for user, stats in user_stats.items():
            failure_rate = stats["failures"] / stats["attempts"]
            avg_score = sum(stats["scores"]) / len(stats["scores"])
            if failure_rate > 0.7 or avg_score < 0.6:
                analysis["suspicious_users"].append(
                    {
                        "user_id": user,
                        "failure_rate": failure_rate,
                        "avg_score": avg_score,
                        "attempts": stats["attempts"],
                    }
                )

        return analysis


# Demo function
def main():
    """Demo the Red Team Glyph Map Generator"""
    print("🛡️ LUKHΛS Red Team Glyph Map Generator Demo")
    print("=" * 60)

    generator = GlyphTimelineGenerator()

    # Generate mock events
    print("\n📊 Generating mock authentication events...")
    events = generator.generate_mock_events(100)
    print(f"Generated {len(events)} events")

    # Export to CSV
    csv_path = generator.export_to_csv()
    print(f"\n📄 CSV exported to: {csv_path}")

    # Generate HTML visualization
    html_path = generator.generate_html_visualization()
    print(f"🌐 HTML visualization created at: {html_path}")

    # Analyze patterns
    print("\n🔍 Pattern Analysis:")
    analysis = generator.analyze_patterns()
    print(f"Success Rate: {analysis['success_rate']:.2%}")
    print(f"Fallback Rate: {analysis['fallback_rate']:.2%}")
    print(f"Average Match Score: {analysis['avg_match_score']:.3f}")

    if analysis["suspicious_users"]:
        print("\n⚠️ Suspicious Users Detected:")
        for user in analysis["suspicious_users"]:
            print(
                f"  - {user['user_id']}: {user['attempts']} attempts, "
                f"{user['failure_rate']:.1%} failure rate, "
                f"avg score: {user['avg_score']:.3f}"
            )

    print("\n✨ Red Team analysis complete!")
    print(f"Open {html_path} in a browser to view the interactive dashboard")


if __name__ == "__main__":
    main()
