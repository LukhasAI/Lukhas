"""
Dream Recorder for NIΛS system
Adapted from system--advanced for Lambda Products integration
"""
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DreamRecorder:
    """
    Enhanced dream recording system for NIΛS with Lambda Products integration.

    This class provides functionality to record, store, and retrieve
    dream messages, symbolic seeds, and user interaction patterns.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the dream recorder.

        Args:
            storage_path: Optional path to dream storage directory
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data/dreams")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()
        self.session_id = self._generate_session_id()
        self.recorded_dreams = []
        self.dream_seeds = {}  # Store brand dreamseeds
        self.user_dream_patterns = {}  # Track user dream interaction patterns

        # Lambda Products integration
        self.lambda_integrations = {
            "QRG": None,  # Quantum Record Generation for secure storage
            "ΛSYMBOLIC": None,  # For user authentication and symbolic processing
        }

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for dream recording"""
        logger = logging.getLogger("DreamRecorder")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            log_file = self.storage_path / "dream_recorder.log"
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"nias_session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    async def record_dream_seed(
        self,
        brand_id: str,
        dream_seed: dict[str, Any],
        user_id: str,
        consent_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Record a brand dream seed with full consent tracking.

        Args:
            brand_id: Brand identifier planting the seed
            dream_seed: Dream seed data (colors, sounds, symbols, etc.)
            user_id: User receiving the dream seed
            consent_context: Full consent context and permissions

        Returns:
            Recording result with seed_id
        """
        try:
            seed_id = f"seed_{uuid.uuid4().hex}"

            dream_seed_record = {
                "seed_id": seed_id,
                "brand_id": brand_id,
                "user_id": user_id,
                "session_id": self.session_id,
                "planted_at": datetime.now(timezone.utc).isoformat(),
                "dream_seed": dream_seed,
                "consent_context": consent_context,
                "status": "planted",
                "interactions": [],
                "symbolic_resonance": None,  # Will be filled when user interacts
            }

            # Store the seed
            self.dream_seeds[seed_id] = dream_seed_record

            # Save to persistent storage
            await self._save_dream_seed(dream_seed_record)

            self.logger.info(f"Dream seed planted: {seed_id} for brand {brand_id}")

            return {
                "success": True,
                "seed_id": seed_id,
                "planted_at": dream_seed_record["planted_at"],
                "status": "planted",
            }

        except Exception as e:
            self.logger.error(f"Failed to record dream seed: {e!s}")
            return {"success": False, "error": str(e), "seed_id": None}

    async def record_dream_interaction(
        self,
        seed_id: str,
        user_id: str,
        interaction_type: str,
        interaction_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Record user interaction with a dream seed.

        Args:
            seed_id: Dream seed identifier
            user_id: User interacting with seed
            interaction_type: Type of interaction (view, like, purchase, dismiss)
            interaction_data: Additional interaction context

        Returns:
            Interaction recording result
        """
        try:
            if seed_id not in self.dream_seeds:
                return {"success": False, "error": "Dream seed not found"}

            interaction_record = {
                "interaction_id": f"int_{uuid.uuid4().hex[:8]}",
                "seed_id": seed_id,
                "user_id": user_id,
                "interaction_type": interaction_type,
                "interaction_data": interaction_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Add to seed's interaction history
            self.dream_seeds[seed_id]["interactions"].append(interaction_record)

            # Update seed status based on interaction
            if interaction_type == "purchase":
                self.dream_seeds[seed_id]["status"] = "converted"
            elif interaction_type == "dismiss":
                self.dream_seeds[seed_id]["status"] = "dismissed"
            elif interaction_type in ["view", "like", "share"]:
                self.dream_seeds[seed_id]["status"] = "engaged"

            # Calculate symbolic resonance
            await self._update_symbolic_resonance(seed_id)

            # Save updated seed
            await self._save_dream_seed(self.dream_seeds[seed_id])

            self.logger.info(f"Dream interaction recorded: {interaction_type} on {seed_id}")

            return {
                "success": True,
                "interaction_id": interaction_record["interaction_id"],
                "seed_status": self.dream_seeds[seed_id]["status"],
            }

        except Exception as e:
            self.logger.error(f"Failed to record dream interaction: {e!s}")
            return {"success": False, "error": str(e)}

    async def record_dream_narrative(
        self,
        narrative_id: str,
        user_id: str,
        dream_narrative: dict[str, Any],
        source_seeds: list[str],
    ) -> dict[str, Any]:
        """
        Record a generated dream narrative from multiple seeds.

        Args:
            narrative_id: Unique narrative identifier
            user_id: User for whom narrative was generated
            dream_narrative: The generated narrative content
            source_seeds: List of seed IDs that contributed to this narrative

        Returns:
            Recording result
        """
        try:
            narrative_record = {
                "narrative_id": narrative_id,
                "user_id": user_id,
                "session_id": self.session_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "dream_narrative": dream_narrative,
                "source_seeds": source_seeds,
                "user_rating": None,
                "effectiveness_score": None,
                "symbolic_elements": self._extract_symbolic_elements(dream_narrative),
            }

            # Store narrative
            self.recorded_dreams.append(narrative_record)

            # Save to storage
            await self._save_dream_narrative(narrative_record)

            # Update source seeds with narrative reference
            for seed_id in source_seeds:
                if seed_id in self.dream_seeds:
                    if "narratives_generated" not in self.dream_seeds[seed_id]:
                        self.dream_seeds[seed_id]["narratives_generated"] = []
                    self.dream_seeds[seed_id]["narratives_generated"].append(narrative_id)

            self.logger.info(f"Dream narrative recorded: {narrative_id}")

            return {
                "success": True,
                "narrative_id": narrative_id,
                "generated_at": narrative_record["generated_at"],
                "source_seeds_count": len(source_seeds),
            }

        except Exception as e:
            self.logger.error(f"Failed to record dream narrative: {e!s}")
            return {"success": False, "error": str(e)}

    def _extract_symbolic_elements(self, dream_narrative: dict[str, Any]) -> list[str]:
        """Extract symbolic elements from dream narrative"""
        symbols = []

        # Extract from different narrative components
        if "visual_elements" in dream_narrative:
            symbols.extend(dream_narrative["visual_elements"].get("symbols", []))

        if "emotional_themes" in dream_narrative:
            symbols.extend(dream_narrative["emotional_themes"])

        if "symbolic_objects" in dream_narrative:
            symbols.extend(dream_narrative["symbolic_objects"])

        return list(set(symbols))  # Remove duplicates

    async def _update_symbolic_resonance(self, seed_id: str):
        """Update symbolic resonance score for a dream seed"""
        if seed_id not in self.dream_seeds:
            return

        seed = self.dream_seeds[seed_id]
        interactions = seed.get("interactions", [])

        if not interactions:
            return

        # Calculate resonance based on interaction patterns
        positive_interactions = sum(
            1 for i in interactions if i["interaction_type"] in ["view", "like", "share", "purchase"]
        )
        negative_interactions = sum(1 for i in interactions if i["interaction_type"] in ["dismiss", "block"])
        total_interactions = len(interactions)

        if total_interactions > 0:
            resonance_score = (positive_interactions - negative_interactions) / total_interactions
            seed["symbolic_resonance"] = max(-1.0, min(1.0, resonance_score))  # Clamp to [-1, 1]

    async def _save_dream_seed(self, seed_record: dict[str, Any]):
        """Save dream seed to persistent storage"""
        try:
            seeds_dir = self.storage_path / "seeds"
            seeds_dir.mkdir(exist_ok=True)

            seed_file = seeds_dir / f"{seed_record['seed_id']}.json"

            with open(seed_file, "w", encoding="utf-8") as f:
                json.dump(seed_record, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save dream seed: {e}")

    async def _save_dream_narrative(self, narrative_record: dict[str, Any]):
        """Save dream narrative to persistent storage"""
        try:
            narratives_dir = self.storage_path / "narratives"
            narratives_dir.mkdir(exist_ok=True)

            narrative_file = narratives_dir / f"{narrative_record['narrative_id']}.json"

            with open(narrative_file, "w", encoding="utf-8") as f:
                json.dump(narrative_record, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save dream narrative: {e}")

    async def get_user_dream_seeds(self, user_id: str, status: Optional[str] = None) -> list[dict[str, Any]]:
        """Get dream seeds for a specific user"""
        user_seeds = []

        for seed in self.dream_seeds.values():
            if seed["user_id"] == user_id and (status is None or seed["status"] == status):
                user_seeds.append(seed)

        return sorted(user_seeds, key=lambda x: x["planted_at"], reverse=True)

    async def get_brand_performance(self, brand_id: str) -> dict[str, Any]:
        """Get performance analytics for a brand's dream seeds"""
        brand_seeds = [seed for seed in self.dream_seeds.values() if seed["brand_id"] == brand_id]

        if not brand_seeds:
            return {"error": "No seeds found for brand"}

        total_seeds = len(brand_seeds)
        converted_seeds = len([s for s in brand_seeds if s["status"] == "converted"])
        engaged_seeds = len([s for s in brand_seeds if s["status"] == "engaged"])
        dismissed_seeds = len([s for s in brand_seeds if s["status"] == "dismissed"])

        avg_resonance = sum(
            s.get("symbolic_resonance", 0) for s in brand_seeds if s.get("symbolic_resonance") is not None
        ) / max(1, total_seeds)

        return {
            "brand_id": brand_id,
            "total_seeds_planted": total_seeds,
            "conversion_rate": converted_seeds / total_seeds if total_seeds > 0 else 0,
            "engagement_rate": engaged_seeds / total_seeds if total_seeds > 0 else 0,
            "dismissal_rate": dismissed_seeds / total_seeds if total_seeds > 0 else 0,
            "average_symbolic_resonance": avg_resonance,
            "performance_score": (avg_resonance + (converted_seeds / max(1, total_seeds))) / 2,
        }

    async def get_dream_analytics(self, user_id: Optional[str] = None, days: int = 30) -> dict[str, Any]:
        """Get comprehensive dream analytics"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Filter seeds by date and user if specified
        recent_seeds = []
        for seed in self.dream_seeds.values():
            seed_date = datetime.fromisoformat(seed["planted_at"].replace("Z", "+00:00"))
            if seed_date >= cutoff_date and (user_id is None or seed["user_id"] == user_id):
                recent_seeds.append(seed)

        total_seeds = len(recent_seeds)
        if total_seeds == 0:
            return {"message": "No dream seeds found for the specified period"}

        # Calculate analytics
        status_breakdown = {}
        brand_breakdown = {}
        user_breakdown = {}

        for seed in recent_seeds:
            # Status breakdown
            status = seed["status"]
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

            # Brand breakdown
            brand = seed["brand_id"]
            if brand not in brand_breakdown:
                brand_breakdown[brand] = {
                    "count": 0,
                    "resonance_sum": 0,
                    "resonance_count": 0,
                }
            brand_breakdown[brand]["count"] += 1
            if seed.get("symbolic_resonance") is not None:
                brand_breakdown[brand]["resonance_sum"] += seed["symbolic_resonance"]
                brand_breakdown[brand]["resonance_count"] += 1

            # User breakdown (if not filtering by specific user)
            if user_id is None:
                user = seed["user_id"]
                user_breakdown[user] = user_breakdown.get(user, 0) + 1

        # Calculate brand averages
        for brand_data in brand_breakdown.values():
            if brand_data["resonance_count"] > 0:
                brand_data["avg_resonance"] = brand_data["resonance_sum"] / brand_data["resonance_count"]
            else:
                brand_data["avg_resonance"] = 0

        return {
            "period_days": days,
            "total_seeds": total_seeds,
            "status_breakdown": status_breakdown,
            "brand_performance": brand_breakdown,
            "user_engagement": user_breakdown if user_id is None else None,
            "top_performing_brands": sorted(
                [(k, v["avg_resonance"]) for k, v in brand_breakdown.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for dream recorder"""
        return {
            "status": "healthy",
            "session_id": self.session_id,
            "storage_path": str(self.storage_path),
            "seeds_recorded": len(self.dream_seeds),
            "narratives_recorded": len(self.recorded_dreams),
            "storage_readable": self.storage_path.exists() and self.storage_path.is_dir(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }


# Global dream recorder instance
_global_dream_recorder = None


def get_dream_recorder() -> DreamRecorder:
    """Get the global dream recorder instance"""
    global _global_dream_recorder
    if _global_dream_recorder is None:
        _global_dream_recorder = DreamRecorder()
    return _global_dream_recorder


async def record_dream_seed(
    brand_id: str,
    dream_seed: dict[str, Any],
    user_id: str,
    consent_context: dict[str, Any],
) -> dict[str, Any]:
    """Convenience function to record a dream seed"""
    recorder = get_dream_recorder()
    return await recorder.record_dream_seed(brand_id, dream_seed, user_id, consent_context)


async def record_dream_interaction(
    seed_id: str, user_id: str, interaction_type: str, interaction_data: dict[str, Any]
) -> dict[str, Any]:
    """Convenience function to record dream interaction"""
    recorder = get_dream_recorder()
    return await recorder.record_dream_interaction(seed_id, user_id, interaction_type, interaction_data)