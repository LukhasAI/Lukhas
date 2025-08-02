#!/usr/bin/env python3
"""
LUKHAS Insight Analyzer
Analyze what worked, what didn't, and extract learnings
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import json
from pathlib import Path

from .journal_engine import JournalEngine, JournalEntry

class Insight:
    """Represents an insight or learning"""
    
    def __init__(
        self,
        content: str,
        category: str,
        sentiment: str,  # positive, negative, neutral
        impact_level: str,  # high, medium, low
        actionable: bool,
        related_files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ):
        self.content = content
        self.category = category
        self.sentiment = sentiment
        self.impact_level = impact_level
        self.actionable = actionable
        self.related_files = related_files or []
        self.tags = tags or []
        self.timestamp = datetime.now()
        self.applied = False  # Track if insight was acted upon

class InsightAnalyzer:
    """
    Analyze insights from your development journey
    Helps identify what works and what doesn't
    """
    
    def __init__(self, journal_engine: Optional[JournalEngine] = None):
        self.journal = journal_engine or JournalEngine()
        self.insight_categories = {
            "success": ["worked", "successful", "great", "excellent", "solved", "fixed"],
            "failure": ["failed", "broke", "didn't work", "issue", "problem", "bug"],
            "learning": ["learned", "realized", "discovered", "understood", "found out"],
            "improvement": ["could be better", "should", "next time", "improve", "optimize"],
            "surprise": ["unexpected", "surprised", "didn't expect", "turned out"],
            "challenge": ["difficult", "challenging", "struggle", "hard", "complex"]
        }
        self.sentiment_words = {
            "positive": ["happy", "excited", "confident", "proud", "satisfied", "great"],
            "negative": ["frustrated", "confused", "worried", "stressed", "disappointed"],
            "neutral": ["okay", "fine", "normal", "expected", "typical"]
        }
    
    def capture_insight(
        self,
        content: str,
        category: Optional[str] = None,
        impact_level: str = "medium",
        related_files: Optional[List[str]] = None,
        from_failure: bool = False
    ) -> Insight:
        """Capture a new insight"""
        # Auto-categorize if not provided
        if not category:
            category = self._categorize_insight(content)
        
        # Determine sentiment
        sentiment = self._analyze_sentiment(content)
        
        # Check if actionable
        actionable = self._is_actionable(content)
        
        # Extract tags
        tags = self._extract_tags(content, category)
        
        # Create insight
        insight = Insight(
            content=content,
            category=category,
            sentiment=sentiment,
            impact_level=impact_level,
            actionable=actionable,
            related_files=related_files,
            tags=tags
        )
        
        # Determine emotional state
        emotional_state = self._create_emotional_state(insight, from_failure)
        
        # Add to journal
        metadata = {
            "category": category,
            "sentiment": sentiment,
            "impact_level": impact_level,
            "actionable": actionable,
            "from_failure": from_failure
        }
        
        entry = self.journal.add_entry(
            type="insight",
            content=content,
            metadata=metadata,
            tags=tags,
            emotional_state=emotional_state,
            linked_files=related_files
        )
        
        return insight
    
    def _categorize_insight(self, content: str) -> str:
        """Auto-categorize insight based on content"""
        content_lower = content.lower()
        
        category_scores = {}
        for category, keywords in self.insight_categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return "general"
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of the insight"""
        content_lower = content.lower()
        
        sentiment_scores = {}
        for sentiment, keywords in self.sentiment_words.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                sentiment_scores[sentiment] = score
        
        if sentiment_scores:
            return max(sentiment_scores.items(), key=lambda x: x[1])[0]
        
        # Default based on category keywords
        if any(word in content_lower for word in self.insight_categories["success"]):
            return "positive"
        elif any(word in content_lower for word in self.insight_categories["failure"]):
            return "negative"
        
        return "neutral"
    
    def _is_actionable(self, content: str) -> bool:
        """Determine if insight is actionable"""
        actionable_patterns = [
            r"\bshould\b", r"\bcould\b", r"\bwill\b", r"\bneed to\b",
            r"\bmust\b", r"\bhave to\b", r"\btry\b", r"\bimplement\b",
            r"\bfix\b", r"\bimprove\b", r"\bchange\b"
        ]
        
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in actionable_patterns)
    
    def _extract_tags(self, content: str, category: str) -> List[str]:
        """Extract relevant tags from insight"""
        tags = [category]
        
        # Look for technical terms
        tech_terms = ["api", "database", "ui", "performance", "security", "testing", 
                     "architecture", "refactor", "bug", "feature", "optimization"]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.append(term)
        
        # Look for LUKHAS concepts
        lukhas_concepts = ["memory_fold", "dream", "consciousness", "quantum", 
                          "emotional", "glyph", "symbolic", "ethical"]
        
        for concept in lukhas_concepts:
            if concept in content_lower:
                tags.append(f"lukhas_{concept}")
        
        return list(set(tags))  # Remove duplicates
    
    def _create_emotional_state(self, insight: Insight, from_failure: bool) -> Dict[str, float]:
        """Create emotional state based on insight"""
        emotions = {
            "curiosity": 0.5,
            "satisfaction": 0.5,
            "concern": 0.3,
            "excitement": 0.4,
            "frustration": 0.2
        }
        
        # Adjust based on sentiment
        if insight.sentiment == "positive":
            emotions["satisfaction"] += 0.3
            emotions["excitement"] += 0.2
            emotions["frustration"] -= 0.1
        elif insight.sentiment == "negative":
            emotions["satisfaction"] -= 0.2
            emotions["concern"] += 0.3
            emotions["frustration"] += 0.3
        
        # Adjust based on category
        if insight.category == "learning":
            emotions["curiosity"] += 0.3
            emotions["excitement"] += 0.1
        elif insight.category == "failure":
            emotions["frustration"] += 0.2
            emotions["concern"] += 0.2
        elif insight.category == "success":
            emotions["satisfaction"] += 0.3
            emotions["excitement"] += 0.2
        
        # From failure but learned something
        if from_failure and insight.category == "learning":
            emotions["satisfaction"] += 0.2  # Satisfaction from learning
            emotions["frustration"] -= 0.1  # Less frustrated because learned
        
        # Normalize
        for emotion in emotions:
            emotions[emotion] = min(1.0, max(0.0, emotions[emotion]))
        
        return emotions
    
    def analyze_daily_insights(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze insights from a specific day"""
        if date is None:
            date = datetime.now()
        
        # Get insights from the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        insights = self.journal.search(
            type="insight",
            date_range=(start_of_day, end_of_day)
        )
        
        analysis = {
            "date": date.strftime("%Y-%m-%d"),
            "total_insights": len(insights),
            "by_category": Counter(),
            "by_sentiment": Counter(),
            "actionable_insights": [],
            "key_learnings": [],
            "emotional_journey": [],
            "success_failure_ratio": 0
        }
        
        success_count = 0
        failure_count = 0
        
        for insight in insights:
            metadata = insight.metadata
            
            # Count by category
            category = metadata.get("category", "general")
            analysis["by_category"][category] += 1
            
            # Count by sentiment
            sentiment = metadata.get("sentiment", "neutral")
            analysis["by_sentiment"][sentiment] += 1
            
            # Track success/failure
            if category == "success":
                success_count += 1
            elif category == "failure":
                failure_count += 1
            
            # Collect actionable insights
            if metadata.get("actionable", False):
                analysis["actionable_insights"].append({
                    "content": insight.content[:100] + "...",
                    "impact": metadata.get("impact_level", "medium")
                })
            
            # Collect key learnings
            if category == "learning":
                analysis["key_learnings"].append(insight.content[:150] + "...")
            
            # Track emotional journey
            if insight.emotional_vector:
                analysis["emotional_journey"].append({
                    "time": insight.timestamp.strftime("%H:%M"),
                    "emotions": insight.emotional_vector,
                    "category": category
                })
        
        # Calculate success/failure ratio
        if failure_count > 0:
            analysis["success_failure_ratio"] = success_count / failure_count
        elif success_count > 0:
            analysis["success_failure_ratio"] = float('inf')
        
        return analysis
    
    def find_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Find patterns in insights over time"""
        start_date = datetime.now() - timedelta(days=days)
        insights = self.journal.search(
            type="insight",
            date_range=(start_date, datetime.now())
        )
        
        patterns = {
            "recurring_challenges": self._find_recurring_themes(insights, "challenge"),
            "repeated_successes": self._find_recurring_themes(insights, "success"),
            "learning_velocity": self._calculate_learning_velocity(insights, days),
            "sentiment_trends": self._analyze_sentiment_trends(insights),
            "impact_distribution": self._analyze_impact_distribution(insights),
            "actionable_completion_rate": self._calculate_actionable_completion(insights),
            "growth_indicators": self._identify_growth_indicators(insights)
        }
        
        return patterns
    
    def _find_recurring_themes(self, insights: List[JournalEntry], category: str) -> List[Dict[str, Any]]:
        """Find recurring themes in a specific category"""
        category_insights = [i for i in insights if i.metadata.get("category") == category]
        
        # Extract key phrases
        phrase_counts = Counter()
        for insight in category_insights:
            # Simple phrase extraction (can be made more sophisticated)
            words = insight.content.lower().split()
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                phrase_counts[phrase] += 1
        
        # Find recurring phrases
        recurring = []
        for phrase, count in phrase_counts.most_common(10):
            if count >= 2:  # Appears at least twice
                recurring.append({
                    "theme": phrase,
                    "occurrences": count,
                    "examples": [i.content[:100] for i in category_insights if phrase in i.content.lower()][:3]
                })
        
        return recurring
    
    def _calculate_learning_velocity(self, insights: List[JournalEntry], days: int) -> Dict[str, float]:
        """Calculate how fast you're learning"""
        learning_insights = [i for i in insights if i.metadata.get("category") == "learning"]
        
        # Group by week
        weeks = defaultdict(int)
        for insight in learning_insights:
            week_num = (datetime.now() - insight.timestamp).days // 7
            weeks[week_num] += 1
        
        # Calculate velocity metrics
        if weeks:
            recent_week_avg = sum(weeks[i] for i in range(2)) / 2  # Last 2 weeks
            older_week_avg = sum(weeks[i] for i in range(2, 4)) / 2  # Weeks 3-4
            
            acceleration = recent_week_avg - older_week_avg if older_week_avg > 0 else 0
        else:
            recent_week_avg = older_week_avg = acceleration = 0
        
        return {
            "learnings_per_week": sum(weeks.values()) / max(len(weeks), 1),
            "recent_velocity": recent_week_avg,
            "acceleration": acceleration,
            "total_learnings": len(learning_insights)
        }
    
    def _analyze_sentiment_trends(self, insights: List[JournalEntry]) -> Dict[str, Any]:
        """Analyze how sentiment changes over time"""
        # Group by day
        daily_sentiments = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        
        for insight in insights:
            day = insight.timestamp.strftime("%Y-%m-%d")
            sentiment = insight.metadata.get("sentiment", "neutral")
            daily_sentiments[day][sentiment] += 1
        
        # Calculate trend
        days_sorted = sorted(daily_sentiments.keys())
        if len(days_sorted) >= 2:
            first_half = days_sorted[:len(days_sorted)//2]
            second_half = days_sorted[len(days_sorted)//2:]
            
            first_half_positive = sum(daily_sentiments[d]["positive"] for d in first_half)
            second_half_positive = sum(daily_sentiments[d]["positive"] for d in second_half)
            
            trend = "improving" if second_half_positive > first_half_positive else "declining"
        else:
            trend = "insufficient_data"
        
        return {
            "overall_trend": trend,
            "daily_breakdown": dict(daily_sentiments),
            "most_positive_day": max(daily_sentiments.items(), 
                                   key=lambda x: x[1]["positive"])[0] if daily_sentiments else None,
            "most_challenging_day": max(daily_sentiments.items(), 
                                      key=lambda x: x[1]["negative"])[0] if daily_sentiments else None
        }
    
    def _analyze_impact_distribution(self, insights: List[JournalEntry]) -> Dict[str, int]:
        """Analyze distribution of impact levels"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for insight in insights:
            impact = insight.metadata.get("impact_level", "medium")
            distribution[impact] += 1
        
        return distribution
    
    def _calculate_actionable_completion(self, insights: List[JournalEntry]) -> float:
        """Calculate what percentage of actionable insights were acted upon"""
        actionable = [i for i in insights if i.metadata.get("actionable", False)]
        
        if not actionable:
            return 0.0
        
        # Look for follow-up entries that reference the actionable insights
        completed = 0
        for insight in actionable:
            # Simple check - look for references in subsequent entries
            subsequent = self.journal.search(
                query=insight.id[:8],  # Search for partial ID
                date_range=(insight.timestamp, datetime.now())
            )
            if len(subsequent) > 1:  # More than just the original
                completed += 1
        
        return (completed / len(actionable)) * 100
    
    def _identify_growth_indicators(self, insights: List[JournalEntry]) -> List[str]:
        """Identify indicators of growth and improvement"""
        indicators = []
        
        # Check learning velocity
        velocity = self._calculate_learning_velocity(insights, 30)
        if velocity["acceleration"] > 0:
            indicators.append("Learning velocity is increasing")
        
        # Check success/failure ratio over time
        early_insights = [i for i in insights if (datetime.now() - i.timestamp).days > 15]
        recent_insights = [i for i in insights if (datetime.now() - i.timestamp).days <= 15]
        
        early_success_rate = sum(1 for i in early_insights if i.metadata.get("category") == "success") / max(len(early_insights), 1)
        recent_success_rate = sum(1 for i in recent_insights if i.metadata.get("category") == "success") / max(len(recent_insights), 1)
        
        if recent_success_rate > early_success_rate:
            indicators.append("Success rate is improving")
        
        # Check complexity of challenges
        early_challenges = [i for i in early_insights if i.metadata.get("category") == "challenge"]
        recent_challenges = [i for i in recent_insights if i.metadata.get("category") == "challenge"]
        
        if recent_challenges and early_challenges:
            # Simple complexity measure - length of description
            early_complexity = sum(len(i.content) for i in early_challenges) / len(early_challenges)
            recent_complexity = sum(len(i.content) for i in recent_challenges) / len(recent_challenges)
            
            if recent_complexity > early_complexity:
                indicators.append("Taking on more complex challenges")
        
        # Check emotional resilience
        early_emotions = [i.emotional_vector for i in early_insights if i.emotional_vector]
        recent_emotions = [i.emotional_vector for i in recent_insights if i.emotional_vector]
        
        if early_emotions and recent_emotions:
            early_frustration = sum(e.get("frustration", 0) for e in early_emotions) / len(early_emotions)
            recent_frustration = sum(e.get("frustration", 0) for e in recent_emotions) / len(recent_emotions)
            
            if recent_frustration < early_frustration:
                indicators.append("Building emotional resilience")
        
        return indicators
    
    def generate_weekly_reflection(self) -> str:
        """Generate a weekly reflection based on insights"""
        # Get last 7 days of insights
        week_analysis = {}
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            week_analysis[date.strftime("%A")] = self.analyze_daily_insights(date)
        
        # Find patterns
        patterns = self.find_patterns(days=7)
        
        # Generate reflection
        reflection = f"""
# Weekly Learning Reflection
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## Overview
This week you captured {sum(day['total_insights'] for day in week_analysis.values())} insights.

## Key Learnings
"""
        
        # Collect all learnings
        all_learnings = []
        for day_data in week_analysis.values():
            all_learnings.extend(day_data.get("key_learnings", []))
        
        if all_learnings:
            for learning in all_learnings[:5]:  # Top 5
                reflection += f"- {learning}\n"
        else:
            reflection += "- No specific learnings captured this week\n"
        
        reflection += "\n## Challenges Faced\n"
        
        if patterns["recurring_challenges"]:
            for challenge in patterns["recurring_challenges"][:3]:
                reflection += f"- **{challenge['theme']}** (occurred {challenge['occurrences']} times)\n"
        else:
            reflection += "- No recurring challenges identified\n"
        
        reflection += "\n## Successes\n"
        
        if patterns["repeated_successes"]:
            for success in patterns["repeated_successes"][:3]:
                reflection += f"- {success['theme']}\n"
        else:
            reflection += "- Capture more successes to see patterns\n"
        
        reflection += "\n## Growth Indicators\n"
        
        if patterns["growth_indicators"]:
            for indicator in patterns["growth_indicators"]:
                reflection += f"- ✅ {indicator}\n"
        else:
            reflection += "- Continue capturing insights to measure growth\n"
        
        reflection += f"\n## Emotional Journey\n"
        sentiment_trends = patterns["sentiment_trends"]
        if sentiment_trends["overall_trend"] == "improving":
            reflection += "- 📈 Overall sentiment is improving\n"
        elif sentiment_trends["overall_trend"] == "declining":
            reflection += "- 📉 Overall sentiment is declining - consider what might help\n"
        
        reflection += f"\n## Action Items\n"
        
        # Collect actionable insights
        actionable_items = []
        for day_data in week_analysis.values():
            actionable_items.extend(day_data.get("actionable_insights", []))
        
        if actionable_items:
            # Sort by impact
            high_impact = [a for a in actionable_items if a["impact"] == "high"]
            medium_impact = [a for a in actionable_items if a["impact"] == "medium"]
            
            if high_impact:
                reflection += "### High Priority\n"
                for item in high_impact[:3]:
                    reflection += f"- {item['content']}\n"
            
            if medium_impact:
                reflection += "\n### Medium Priority\n"
                for item in medium_impact[:3]:
                    reflection += f"- {item['content']}\n"
        else:
            reflection += "- No specific action items identified\n"
        
        reflection += f"\n---\n*Keep learning, keep growing! Your learning velocity: {patterns['learning_velocity']['learnings_per_week']:.1f} insights/week*"
        
        return reflection

if __name__ == "__main__":
    # Example usage
    analyzer = InsightAnalyzer()
    
    # Capture an insight
    insight = analyzer.capture_insight(
        "Realized that using memory_fold pattern helps maintain consistency across the codebase. Should apply this to more modules.",
        impact_level="high"
    )
    print(f"Captured insight: {insight.category} - {insight.sentiment}")
    
    # Capture a learning from failure
    failure_insight = analyzer.capture_insight(
        "The API integration failed because I didn't account for rate limits. Learned to always implement exponential backoff.",
        from_failure=True,
        impact_level="high"
    )
    print(f"Learning from failure: {failure_insight.content[:50]}...")
    
    # Analyze today's insights
    today_analysis = analyzer.analyze_daily_insights()
    print(f"Today's analysis: {today_analysis}")
    
    # Generate weekly reflection
    reflection = analyzer.generate_weekly_reflection()
    print(f"Weekly reflection:\n{reflection}")