#!/usr/bin/env python3
"""
Feedback Cards System for LUKHAS
=================================
Human-in-the-loop fine-tuning with feedback cards.
Based on GPT5 audit recommendations.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import numpy as np


class FeedbackType(Enum):
    """Types of feedback"""

    RATING = "rating"  # 1-5 star rating
    COMPARISON = "comparison"  # A vs B preference
    CORRECTION = "correction"  # Fix/improve response
    ANNOTATION = "annotation"  # Add context/explanation
    VALIDATION = "validation"  # Yes/No correctness
    FREEFORM = "freeform"  # Open text feedback


class FeedbackCategory(Enum):
    """Categories of feedback"""

    ACCURACY = "accuracy"
    HELPFULNESS = "helpfulness"
    SAFETY = "safety"
    CREATIVITY = "creativity"
    CLARITY = "clarity"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    TONE = "tone"


@dataclass
class FeedbackCard:
    """
    A feedback card for collecting human feedback.
    Like a digital comment card for AI interactions.
    """

    card_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    interaction_id: str = ""
    timestamp: float = field(default_factory=time.time)

    # Context
    user_input: str = ""
    ai_response: str = ""
    system_state: dict[str, Any] = field(default_factory=dict)

    # Feedback request
    feedback_type: FeedbackType = FeedbackType.RATING
    category: FeedbackCategory = FeedbackCategory.HELPFULNESS
    prompt: str = "Please rate this response"
    options: list[str] = field(default_factory=list)

    # User feedback
    rating: Optional[int] = None  # 1-5
    preference: Optional[str] = None  # For comparisons
    correction: Optional[str] = None  # User's improved version
    annotation: Optional[str] = None  # User's notes
    validated: Optional[bool] = None  # Yes/No
    freeform_text: Optional[str] = None  # Open feedback

    # Metadata
    user_id: Optional[str] = None
    model_version: str = ""
    experiment_id: Optional[str] = None
    tags: set[str] = field(default_factory=set)

    # Processing
    processed: bool = False
    impact_score: float = 0.0  # How much this feedback influenced the system
    applied_to_training: bool = False


class FeedbackCardsManager:
    """
    Manages feedback cards for human-in-the-loop learning.
    Stores, analyzes, and applies user feedback.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize feedback cards manager.

        Args:
            db_path: Path to SQLite database for feedback storage
        """
        self.db_path = db_path or Path("data/feedback_cards.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Active cards awaiting feedback
        self.active_cards: dict[str, FeedbackCard] = {}

        # Feedback statistics
        self.stats = {
            "total_cards": 0,
            "completed_cards": 0,
            "average_rating": 0.0,
            "categories": {},
            "impact_scores": [],
        }

        # Load existing stats
        self._load_stats()

    def _init_database(self):
        """Initialize SQLite database for feedback storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create feedback table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_cards (
                card_id TEXT PRIMARY KEY,
                session_id TEXT,
                interaction_id TEXT,
                timestamp REAL,
                user_input TEXT,
                ai_response TEXT,
                system_state TEXT,
                feedback_type TEXT,
                category TEXT,
                prompt TEXT,
                options TEXT,
                rating INTEGER,
                preference TEXT,
                correction TEXT,
                annotation TEXT,
                validated INTEGER,
                freeform_text TEXT,
                user_id TEXT,
                model_version TEXT,
                experiment_id TEXT,
                tags TEXT,
                processed INTEGER,
                impact_score REAL,
                applied_to_training INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON feedback_cards(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON feedback_cards(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON feedback_cards(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed ON feedback_cards(processed)")

        conn.commit()
        conn.close()

    def create_rating_card(
        self,
        user_input: str,
        ai_response: str,
        category: FeedbackCategory = FeedbackCategory.HELPFULNESS,
        session_id: str = "",
        **kwargs,
    ) -> FeedbackCard:
        """
        Create a rating feedback card (1-5 stars).

        Args:
            user_input: The user's original input
            ai_response: The AI's response
            category: What aspect to rate
            session_id: Session identifier
            **kwargs: Additional card fields

        Returns:
            Created feedback card
        """
        card = FeedbackCard(
            session_id=session_id,
            user_input=user_input,
            ai_response=ai_response,
            feedback_type=FeedbackType.RATING,
            category=category,
            prompt=f"Please rate the {category.value} of this response (1-5 stars)",
            options=["1", "2", "3", "4", "5"],
            **kwargs,
        )

        self.active_cards[card.card_id] = card
        self.stats["total_cards"] += 1

        return card

    def create_comparison_card(
        self,
        user_input: str,
        response_a: str,
        response_b: str,
        category: FeedbackCategory = FeedbackCategory.HELPFULNESS,
        session_id: str = "",
        **kwargs,
    ) -> FeedbackCard:
        """
        Create a comparison feedback card (A vs B).

        Args:
            user_input: The user's original input
            response_a: First response option
            response_b: Second response option
            category: What aspect to compare
            session_id: Session identifier
            **kwargs: Additional card fields

        Returns:
            Created feedback card
        """
        card = FeedbackCard(
            session_id=session_id,
            user_input=user_input,
            ai_response=f"A: {response_a}\n\nB: {response_b}",
            feedback_type=FeedbackType.COMPARISON,
            category=category,
            prompt=f"Which response is more {category.value}?",
            options=["A", "B", "Equal"],
            **kwargs,
        )

        self.active_cards[card.card_id] = card
        self.stats["total_cards"] += 1

        return card

    def create_correction_card(self, user_input: str, ai_response: str, session_id: str = "", **kwargs) -> FeedbackCard:
        """
        Create a correction feedback card.

        Args:
            user_input: The user's original input
            ai_response: The AI's response to correct
            session_id: Session identifier
            **kwargs: Additional card fields

        Returns:
            Created feedback card
        """
        card = FeedbackCard(
            session_id=session_id,
            user_input=user_input,
            ai_response=ai_response,
            feedback_type=FeedbackType.CORRECTION,
            category=FeedbackCategory.ACCURACY,
            prompt="Please provide a better response or correction:",
            **kwargs,
        )

        self.active_cards[card.card_id] = card
        self.stats["total_cards"] += 1

        return card

    def submit_feedback(
        self,
        card_id: str,
        rating: Optional[int] = None,
        preference: Optional[str] = None,
        correction: Optional[str] = None,
        annotation: Optional[str] = None,
        validated: Optional[bool] = None,
        freeform_text: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Submit feedback for a card.

        Args:
            card_id: Card identifier
            rating: 1-5 star rating
            preference: A/B/Equal preference
            correction: Corrected response
            annotation: User notes
            validated: Yes/No validation
            freeform_text: Open feedback
            user_id: User identifier

        Returns:
            True if feedback was recorded
        """
        if card_id not in self.active_cards:
            return False

        card = self.active_cards[card_id]

        # Record feedback based on type
        if card.feedback_type == FeedbackType.RATING and rating is not None:
            card.rating = rating
            self._update_rating_stats(rating, card.category)

        elif card.feedback_type == FeedbackType.COMPARISON and preference is not None:
            card.preference = preference

        elif card.feedback_type == FeedbackType.CORRECTION and correction is not None:
            card.correction = correction

        elif card.feedback_type == FeedbackType.VALIDATION and validated is not None:
            card.validated = validated

        # Always accept annotations and freeform
        if annotation:
            card.annotation = annotation
        if freeform_text:
            card.freeform_text = freeform_text

        # Set user
        if user_id:
            card.user_id = user_id

        # Calculate impact score
        card.impact_score = self._calculate_impact_score(card)

        # Save to database
        self._save_card(card)

        # Move from active to completed
        del self.active_cards[card_id]
        self.stats["completed_cards"] += 1

        # Process immediately if high impact
        if card.impact_score > 0.7:
            self._process_high_impact_feedback(card)

        return True

    def _update_rating_stats(self, rating: int, category: FeedbackCategory):
        """Update rating statistics"""
        # Update category stats
        if category.value not in self.stats["categories"]:
            self.stats["categories"][category.value] = {
                "count": 0,
                "sum": 0,
                "average": 0.0,
            }

        cat_stats = self.stats["categories"][category.value]
        cat_stats["count"] += 1
        cat_stats["sum"] += rating
        cat_stats["average"] = cat_stats["sum"] / cat_stats["count"]

        # Update overall average
        total_sum = sum(s["sum"] for s in self.stats["categories"].values())
        total_count = sum(s["count"] for s in self.stats["categories"].values())
        self.stats["average_rating"] = total_sum / total_count if total_count > 0 else 0.0

    def _calculate_impact_score(self, card: FeedbackCard) -> float:
        """
        Calculate how impactful this feedback is.
        Higher scores indicate more valuable feedback.
        """
        score = 0.0

        # Rating impact (extreme ratings are more impactful)
        if card.rating is not None:
            if card.rating in [1, 5]:
                score += 0.3
            elif card.rating in [2, 4]:
                score += 0.2
            else:
                score += 0.1

        # Corrections are highly valuable
        if card.correction:
            score += 0.4
            # Longer corrections are more valuable
            score += min(len(card.correction) / 1000, 0.2)

        # Annotations add value
        if card.annotation:
            score += 0.2

        # Safety feedback is critical
        if card.category == FeedbackCategory.SAFETY:
            score *= 1.5

        # Accuracy feedback is important
        elif card.category == FeedbackCategory.ACCURACY:
            score *= 1.2

        # User reputation boost (implemented basic system)
        if card.user_id:
            user_reputation = self._get_user_reputation(card.user_id)
            # Apply reputation boost: trusted users get up to 20% boost
            reputation_boost = min(user_reputation / 5.0, 0.2)
            score *= 1.0 + reputation_boost

        return min(score, 1.0)

    def _process_high_impact_feedback(self, card: FeedbackCard):
        """Process high-impact feedback immediately"""
        # Log for immediate attention
        print(f"⚠️ High-impact feedback received: {card.card_id}")
        print(f"   Category: {card.category.value}")
        print(f"   Impact: {card.impact_score:.2f}")

        if card.correction:
            print(f"   Correction provided: {card.correction[:100]}...")

        if card.rating == 1:
            print("   ⚠️ Low rating (1 star) - needs immediate review")

        # Alert system for high-impact feedback
        self._log_high_impact_alert(card)

    def _log_high_impact_alert(self, card: FeedbackCard):
        """Log high-impact feedback for monitoring and alerts"""
        alert_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "card_id": card.card_id,
            "user_id": card.user_id,
            "category": card.category.value,
            "impact_score": card.impact_score,
            "rating": card.rating,
            "correction": card.correction,
            "session_id": card.session_id,
        }

        # Log to file for monitoring systems
        alert_file = Path(self.db_path).parent / "high_impact_alerts.jsonl"
        with open(alert_file, "a") as f:
            f.write(json.dumps(alert_data) + "\n")

        # If extremely critical (impact > 0.9), could trigger immediate alerts
        if card.impact_score > 0.9:
            print(f"🚨 CRITICAL FEEDBACK ALERT: {card.card_id}")

    def _save_card(self, card: FeedbackCard):
        """Save feedback card to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO feedback_cards (
                card_id, session_id, interaction_id, timestamp,
                user_input, ai_response, system_state,
                feedback_type, category, prompt, options,
                rating, preference, correction, annotation,
                validated, freeform_text,
                user_id, model_version, experiment_id, tags,
                processed, impact_score, applied_to_training
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                card.card_id,
                card.session_id,
                card.interaction_id,
                card.timestamp,
                card.user_input,
                card.ai_response,
                json.dumps(card.system_state),
                card.feedback_type.value,
                card.category.value,
                card.prompt,
                json.dumps(card.options),
                card.rating,
                card.preference,
                card.correction,
                card.annotation,
                card.validated,
                card.freeform_text,
                card.user_id,
                card.model_version,
                card.experiment_id,
                json.dumps(list(card.tags)),
                card.processed,
                card.impact_score,
                card.applied_to_training,
            ),
        )

        conn.commit()
        conn.close()

    def _get_user_reputation(self, user_id: str) -> float:
        """
        Calculate user reputation based on feedback history
        Returns score from 0.0 (new/untrusted) to 5.0 (highly trusted)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get user's feedback history
        cursor.execute(
            """
            SELECT rating, category, validated, impact_score, timestamp
            FROM feedback_cards
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """,
            (user_id,),
        )

        history = cursor.fetchall()
        conn.close()

        if not history:
            return 0.5  # Default for new users

        # Calculate reputation based on multiple factors
        total_feedback = len(history)

        # Factor 1: Consistency in ratings (avoid extreme variations)
        ratings = [row[0] for row in history if row[0] is not None]
        if ratings:
            rating_variance = np.var(ratings)
            consistency_score = max(0, 1.0 - (rating_variance / 2.0))
        else:
            consistency_score = 0.5

        # Factor 2: Accuracy validation rate (when available)
        validations = [row[2] for row in history if row[2] is not None]
        accuracy_rate = sum(validations) / len(validations) if validations else 0.5

        # Factor 3: Activity level (more feedback = more reliable)
        activity_score = min(total_feedback / 20.0, 1.0)  # Max at 20 feedbacks

        # Factor 4: Quality categories (accuracy feedback is valued)
        accuracy_feedback = sum(1 for row in history if row[1] == "accuracy")
        quality_score = min(accuracy_feedback / max(total_feedback, 1) + 0.5, 1.0)

        # Factor 5: Time factor (recent activity is valued)
        recent_feedback = sum(
            1 for row in history if (datetime.now(timezone.utc).timestamp() - float(row[4])) < 604800
        )  # 1 week
        recency_score = min(recent_feedback / 5.0, 1.0)

        # Weighted combination
        reputation = (
            consistency_score * 0.25
            + accuracy_rate * 0.25
            + activity_score * 0.20
            + quality_score * 0.15
            + recency_score * 0.15
        ) * 5.0  # Scale to 0-5

        return min(reputation, 5.0)

    def get_cards_for_training(
        self,
        min_impact: float = 0.3,
        limit: int = 100,
        categories: Optional[list[FeedbackCategory]] = None,
    ) -> list[FeedbackCard]:
        """
        Get feedback cards ready for training.

        Args:
            min_impact: Minimum impact score
            limit: Maximum number of cards
            categories: Filter by categories

        Returns:
            List of feedback cards
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT * FROM feedback_cards
            WHERE processed = 0
            AND impact_score >= ?
            AND applied_to_training = 0
        """

        params = [min_impact]

        if categories:
            placeholders = ",".join("?" * len(categories))
            query += f" AND category IN ({placeholders})"
            params.extend([c.value for c in categories])

        query += " ORDER BY impact_score DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        cards = []
        for row in rows:
            card = self._row_to_card(row)
            cards.append(card)

        return cards

    def _row_to_card(self, row: tuple) -> FeedbackCard:
        """Convert database row to FeedbackCard"""
        card = FeedbackCard(
            card_id=row[0],
            session_id=row[1],
            interaction_id=row[2],
            timestamp=row[3],
            user_input=row[4],
            ai_response=row[5],
            system_state=json.loads(row[6]) if row[6] else {},
            feedback_type=FeedbackType(row[7]),
            category=FeedbackCategory(row[8]),
            prompt=row[9],
            options=json.loads(row[10]) if row[10] else [],
            rating=row[11],
            preference=row[12],
            correction=row[13],
            annotation=row[14],
            validated=bool(row[15]) if row[15] is not None else None,
            freeform_text=row[16],
            user_id=row[17],
            model_version=row[18],
            experiment_id=row[19],
            tags=set(json.loads(row[20])) if row[20] else set(),
            processed=bool(row[21]),
            impact_score=row[22],
            applied_to_training=bool(row[23]),
        )
        return card

    def mark_as_applied(self, card_ids: list[str]):
        """Mark cards as applied to training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(card_ids))
        cursor.execute(
            f"UPDATE feedback_cards SET applied_to_training = 1 WHERE card_id IN ({placeholders})",
            card_ids,
        )

        conn.commit()
        conn.close()

    def get_statistics(self, time_window: Optional[timedelta] = None) -> dict[str, Any]:
        """
        Get feedback statistics.

        Args:
            time_window: Optional time window for stats

        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Base query
        base_where = "1=1"
        params = []

        if time_window:
            cutoff = time.time() - time_window.total_seconds()
            base_where = "timestamp >= ?"
            params = [cutoff]

        # Total cards
        cursor.execute(f"SELECT COUNT(*) FROM feedback_cards WHERE {base_where}", params)
        total = cursor.fetchone()[0]

        # Completed cards (with feedback)
        cursor.execute(
            f"SELECT COUNT(*) FROM feedback_cards WHERE {base_where} AND (rating IS NOT NULL OR correction IS NOT NULL OR preference IS NOT NULL)",
            params,
        )
        completed = cursor.fetchone()[0]

        # Average rating
        cursor.execute(
            f"SELECT AVG(rating) FROM feedback_cards WHERE {base_where} AND rating IS NOT NULL",
            params,
        )
        avg_rating = cursor.fetchone()[0] or 0.0

        # Category breakdown
        cursor.execute(
            f"SELECT category, COUNT(*), AVG(rating) FROM feedback_cards WHERE {base_where} GROUP BY category",
            params,
        )
        categories = {}
        for row in cursor.fetchall():
            categories[row[0]] = {"count": row[1], "average_rating": row[2] or 0.0}

        # Impact distribution
        cursor.execute(
            f"SELECT impact_score FROM feedback_cards WHERE {base_where} AND impact_score > 0",
            params,
        )
        impact_scores = [row[0] for row in cursor.fetchall()]

        conn.close()

        return {
            "total_cards": total,
            "completed_cards": completed,
            "completion_rate": completed / total if total > 0 else 0.0,
            "average_rating": avg_rating,
            "categories": categories,
            "impact_distribution": {
                "mean": np.mean(impact_scores) if impact_scores else 0.0,
                "median": np.median(impact_scores) if impact_scores else 0.0,
                "high_impact": sum(1 for s in impact_scores if s > 0.7),
            },
        }

    def _load_stats(self):
        """Load statistics from database"""
        self.stats = self.get_statistics()

    def generate_feedback_summary(self) -> str:
        """Generate human-readable feedback summary"""
        stats = self.get_statistics(time_window=timedelta(days=7))

        summary = f"""
📊 Feedback Summary (Last 7 Days)
================================

Total Cards: {stats["total_cards"]}
Completed: {stats["completed_cards"]} ({stats["completion_rate"]:.1%})
Average Rating: {stats["average_rating"]:.1f}/5.0

Category Breakdown:
"""

        for category, data in stats["categories"].items():
            summary += f"  • {category}: {data['count']} cards, {data['average_rating']:.1f} avg\n"

        summary += f"""
Impact Analysis:
  • Mean Impact: {stats["impact_distribution"]["mean"]:.2f}
  • High Impact: {stats["impact_distribution"]["high_impact"]} cards
"""

        return summary


class FeedbackUI:
    """Simple UI generator for feedback cards"""

    @staticmethod
    def render_rating_card(card: FeedbackCard) -> str:
        """Render a rating card as HTML"""
        html = f"""
        <div class="feedback-card" data-card-id="{card.card_id}">
            <h3>Feedback Request</h3>
            <div class="context">
                <p><strong>Your input:</strong> {card.user_input}</p>
                <p><strong>AI response:</strong> {card.ai_response}</p>
            </div>
            <div class="feedback">
                <p>{card.prompt}</p>
                <div class="rating-stars">
                    {"".join(f'<button class="star" data-rating="{i}">⭐</button>' for i in range(1, 6))}
                </div>
                <textarea placeholder="Additional comments (optional)"></textarea>
                <button class="submit">Submit Feedback</button>
            </div>
        </div>
        """
        return html

    @staticmethod
    def render_comparison_card(card: FeedbackCard) -> str:
        """Render a comparison card as HTML"""
        responses = card.ai_response.split("\n\nB: ")
        response_a = responses[0].replace("A: ", "")
        response_b = responses[1] if len(responses) > 1 else ""

        html = f"""
        <div class="feedback-card" data-card-id="{card.card_id}">
            <h3>Which response is better?</h3>
            <div class="context">
                <p><strong>Your input:</strong> {card.user_input}</p>
            </div>
            <div class="comparison">
                <div class="option-a">
                    <h4>Option A</h4>
                    <p>{response_a}</p>
                    <button data-preference="A">Choose A</button>
                </div>
                <div class="option-b">
                    <h4>Option B</h4>
                    <p>{response_b}</p>
                    <button data-preference="B">Choose B</button>
                </div>
                <button data-preference="Equal">They're Equal</button>
            </div>
        </div>
        """
        return html


# Example usage
if __name__ == "__main__":
    # Create manager
    manager = FeedbackCardsManager()

    print("🎯 Feedback Cards System Demo")
    print("=" * 40)

    # Create a rating card
    card1 = manager.create_rating_card(
        user_input="What is quantum computing?",
        ai_response="Quantum computing uses quantum mechanics principles...",
        category=FeedbackCategory.CLARITY,
        session_id="demo-session-1",
    )
    print(f"Created rating card: {card1.card_id}")

    # Submit feedback
    manager.submit_feedback(
        card1.card_id,
        rating=4,
        annotation="Good explanation but could use more examples",
        user_id="demo-user",
    )
    print("Submitted feedback (5 stars)")

    # Create a comparison card
    card2 = manager.create_comparison_card(
        user_input="Explain machine learning",
        response_a="Machine learning is a subset of AI...",
        response_b="ML allows computers to learn from data...",
        category=FeedbackCategory.HELPFULNESS,
        session_id="demo-session-1",
    )
    print(f"Created comparison card: {card2.card_id}")

    # Submit preference
    manager.submit_feedback(card2.card_id, preference="B", user_id="demo-user")
    print("Submitted preference (chose B)")

    # Get statistics
    print("\n" + manager.generate_feedback_summary())

    # Get cards for training
    training_cards = manager.get_cards_for_training(min_impact=0.2)
    print(f"\nCards ready for training: {len(training_cards)}")
    for card in training_cards[:3]:
        print(f"  • {card.card_id}: impact={card.impact_score:.2f}")
