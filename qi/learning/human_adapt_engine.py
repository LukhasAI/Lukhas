# path: qi/learning/human_adapt_engine.py
from __future__ import annotations

# Safe I/O
import builtins
import contextlib
import hashlib
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Any

_ORIG_OPEN = builtins.open
_ORIG_MAKEDIRS = os.makedirs

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
HUMAN_DIR = os.path.join(STATE, "human_adapt")
_ORIG_MAKEDIRS(HUMAN_DIR, exist_ok=True)
INTERACTIONS = os.path.join(HUMAN_DIR, "interactions.jsonl")  # user feedback episodes
PROPOSALS = os.path.join(HUMAN_DIR, "proposals.jsonl")  # tone/style adaptations

# Approvals & sandbox reuse


def _now() -> float:
    return time.time()


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass
class Interaction:
    run_id: str
    user_id: str
    task_type: str
    interaction_kind: str  # "correction", "preference", "satisfaction_rating"
    original_output: str
    user_feedback: str
    satisfaction_score: float  # 1-5 scale
    tone_tags: list[str]  # ["formal", "technical", "concise"]
    response_length: int
    ctx: dict[str, Any]
    ts: float


class HumanAdaptEngine:
    """
    Learns from human corrections and satisfaction ratings to propose tone/style shifts.
    - Records user interactions (corrections, ratings, preferences)
    - Analyzes satisfaction patterns by task type and user
    - Proposes adaptive changes to response generation configs
    - Routes through HITL approval system for safe deployment
    """

    def record_interaction(
        self,
        *,
        run_id: str,
        user_id: str,
        task_type: str,
        interaction_kind: str,
        original_output: str,
        user_feedback: str,
        satisfaction_score: float,
        tone_tags: list[str],
        ctx: dict[str, Any],
    ):
        inter = Interaction(
            run_id,
            user_id,
            task_type,
            interaction_kind,
            original_output,
            user_feedback,
            float(satisfaction_score),
            tone_tags,
            len(original_output),
            ctx,
            _now(),
        )
        with _ORIG_OPEN(INTERACTIONS, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(inter)) + "\n")

    def analyze_satisfaction_patterns(self, *, window: int = 1000) -> dict[str, Any]:
        """Analyze satisfaction patterns by user, task type, and tone characteristics."""
        ints = self._tail(INTERACTIONS, window)
        by_user: dict[str, list[dict]] = {}
        by_task: dict[str, list[dict]] = {}
        by_tone: dict[str, list[dict]] = {}

        for i in ints:
            by_user.setdefault(i["user_id"], []).append(i)
            by_task.setdefault(i["task_type"], []).append(i)
            for tag in i.get("tone_tags", []):
                by_tone.setdefault(tag, []).append(i)

        stats = {
            "by_user": {},
            "by_task": {},
            "by_tone": {},
            "window": window,
            "ts": _now(),
        }

        for user, arr in by_user.items():
            scores = [x["satisfaction_score"] for x in arr if x.get("satisfaction_score") is not None]
            if scores:
                stats["by_user"][user] = {
                    "n": len(arr),
                    "sat_mean": round(statistics.mean(scores), 2),
                    "sat_trend": self._compute_trend([x["satisfaction_score"] for x in arr[-20:]]),
                    "common_corrections": self._extract_correction_patterns(arr),
                }

        for task, arr in by_task.items():
            scores = [x["satisfaction_score"] for x in arr if x.get("satisfaction_score") is not None]
            if scores:
                stats["by_task"][task] = {
                    "n": len(arr),
                    "sat_mean": round(statistics.mean(scores), 2),
                    "low_sat_count": len([s for s in scores if s < 3.0]),
                }

        for tone, arr in by_tone.items():
            scores = [x["satisfaction_score"] for x in arr if x.get("satisfaction_score") is not None]
            if scores:
                stats["by_tone"][tone] = {
                    "n": len(arr),
                    "sat_mean": round(statistics.mean(scores), 2),
                }

        return stats

    def propose_tone_adaptations(self, *, target_file: str, user_focus: str | None = None) -> list[dict]:
        """
        Generate proposals for tone/style adjustments based on satisfaction analysis.
        """
        stats = self.analyze_satisfaction_patterns()
        proposals = []

        # User-specific adaptations
        if user_focus and user_focus in stats["by_user"]:
            user_stats = stats["by_user"][user_focus]
            if user_stats["sat_mean"] < 3.5:  # Below average satisfaction
                corrections = user_stats["common_corrections"]
                if "too_verbose" in corrections:
                    patch = {
                        "router": {
                            "user_specific": {
                                user_focus: {
                                    "response_style": {
                                        "max_tokens": 150,
                                        "conciseness": 0.8,
                                    }
                                }
                            }
                        }
                    }
                    pid = _sha({"user": user_focus, "adaptation": "concise", "ts": int(_now())})
                    proposals.append(
                        {
                            "id": pid,
                            "target_path": target_file,
                            "patch": patch,
                            "rationale": f"User {user_focus} satisfaction {user_stats['sat_mean']}/5, frequent 'too verbose' feedback",
                            "adaptation_type": "conciseness",
                            "user_id": user_focus,
                        }
                    )

                if "too_technical" in corrections:
                    patch = {
                        "router": {
                            "user_specific": {
                                user_focus: {
                                    "response_style": {
                                        "technical_level": 0.3,
                                        "explanation_depth": "basic",
                                    }
                                }
                            }
                        }
                    }
                    pid = _sha(
                        {
                            "user": user_focus,
                            "adaptation": "simplify",
                            "ts": int(_now()),
                        }
                    )
                    proposals.append(
                        {
                            "id": pid,
                            "target_path": target_file,
                            "patch": patch,
                            "rationale": f"User {user_focus} satisfaction {user_stats['sat_mean']}/5, frequent 'too technical' feedback",
                            "adaptation_type": "simplification",
                            "user_id": user_focus,
                        }
                    )

        # Task-specific adaptations
        for task, task_stats in stats["by_task"].items():
            if task_stats["sat_mean"] < 3.0 and task_stats["low_sat_count"] >= 3:
                # Global task adaptation
                patch = {
                    "router": {
                        "task_specific": {
                            task: {
                                "response_style": {
                                    "formality": 0.6,
                                    "empathy_level": 0.7,
                                }
                            }
                        }
                    }
                }
                pid = _sha({"task": task, "adaptation": "empathy_boost", "ts": int(_now())})
                proposals.append(
                    {
                        "id": pid,
                        "target_path": target_file,
                        "patch": patch,
                        "rationale": f"Task {task} low satisfaction {task_stats['sat_mean']}/5 with {task_stats['low_sat_count']} poor ratings",
                        "adaptation_type": "empathy_enhancement",
                        "task_type": task,
                    }
                )

        # Tone-based adaptations
        tone_rankings = sorted(
            [(tone, data["sat_mean"]) for tone, data in stats["by_tone"].items()],
            key=lambda x: x[1],
            reverse=True,
        )
        if len(tone_rankings) >= 2:
            best_tone, best_score = tone_rankings[0]
            worst_tone, worst_score = tone_rankings[-1]

            if best_score - worst_score > 1.0:  # Significant difference
                patch = {
                    "router": {
                        "global": {
                            "preferred_tones": [best_tone],
                            "avoid_tones": [worst_tone],
                        }
                    }
                }
                pid = _sha({"tone_shift": f"{worst_tone}_to_{best_tone}", "ts": int(_now())})
                proposals.append(
                    {
                        "id": pid,
                        "target_path": target_file,
                        "patch": patch,
                        "rationale": f"Tone analysis: '{best_tone}' scores {best_score}/5 vs '{worst_tone}' at {worst_score}/5",
                        "adaptation_type": "tone_optimization",
                        "tone_from": worst_tone,
                        "tone_to": best_tone,
                    }
                )

        self._queue_proposals(proposals)
        return proposals

    def submit_for_approval(self, *, config_targets: list[str]) -> list[str]:
        """
        Submit tone adaptation proposals through self_healer governance system.
        """
        proposals = self._read_proposals()[-10:]  # Recent proposals
        submitted = []

        for prop_data in proposals:
            if prop_data.get("submitted"):
                continue  # Skip already submitted

            from qi.autonomy.self_healer import ChangeProposal, _attest, _queue_proposal

            pid = prop_data["id"]
            change_prop = ChangeProposal(
                id=pid,
                ts=_now(),
                author="system:human_adapt",
                risk="low",  # Tone changes are low risk
                ttl_sec=7200,  # 2 hours
                kind="config_patch",
                target_path=prop_data["target_path"],
                current_checksum=None,
                patch=prop_data["patch"],
                rationale=prop_data["rationale"],
            )

            change_prop.attestation = (
                _attest(
                    [
                        {
                            "phase": "human_adaptation",
                            "adaptation_type": prop_data.get("adaptation_type"),
                            "user_id": prop_data.get("user_id"),
                            "task_type": prop_data.get("task_type"),
                        }
                    ]
                )
                if "_attest" in globals()
                else None
            )

            _queue_proposal(change_prop)

            # Mark as submitted
            prop_data["submitted"] = True
            prop_data["submitted_ts"] = _now()
            submitted.append(pid)

        self._write_proposals(proposals)
        return submitted

    # ---------- Helper Methods ----------
    def _compute_trend(self, scores: list[float]) -> str:
        if len(scores) < 3:
            return "insufficient_data"
        recent = scores[-5:]
        older = scores[:-5] if len(scores) > 5 else scores[: len(scores) // 2]
        if not older:
            return "stable"

        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        diff = recent_avg - older_avg

        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        else:
            return "stable"

    def _extract_correction_patterns(self, interactions: list[dict]) -> list[str]:
        patterns = []
        corrections = [i for i in interactions if i.get("interaction_kind") == "correction"]

        feedback_texts = [c["user_feedback"].lower() for c in corrections]

        if sum("verbose" in f or "long" in f or "wordy" in f for f in feedback_texts) >= 2:
            patterns.append("too_verbose")
        if sum("technical" in f or "jargon" in f or "complex" in f for f in feedback_texts) >= 2:
            patterns.append("too_technical")
        if sum("formal" in f or "stiff" in f or "robotic" in f for f in feedback_texts) >= 2:
            patterns.append("too_formal")
        if sum("short" in f or "brief" in f or "more detail" in f for f in feedback_texts) >= 2:
            patterns.append("too_brief")

        return patterns

    def _tail(self, path: str, n: int) -> list[dict]:
        if not os.path.exists(path):
            return []
        sz = os.path.getsize(path)
        chunk = min(1024 * 1024, sz)
        with _ORIG_OPEN(path, "rb") as f:
            f.seek(max(0, sz - chunk))
            text = f.read().decode("utf-8", "ignore")
        lines = [x for x in text.strip().splitlines() if x.strip()][-n:]
        out = []
        for ln in lines:
            with contextlib.suppress(Exception):
                out.append(json.loads(ln))
        return out

    def _queue_proposals(self, proposals: list[dict]):
        with _ORIG_OPEN(PROPOSALS, "a", encoding="utf-8") as f:
            for p in proposals:
                f.write(json.dumps(p) + "\n")

    def _read_proposals(self) -> list[dict]:
        if not os.path.exists(PROPOSALS):
            return []
        return [json.loads(ln) for ln in _ORIG_OPEN(PROPOSALS, "r", encoding="utf-8").read().splitlines() if ln.strip()]

    def _write_proposals(self, proposals: list[dict]):
        tmp = PROPOSALS + ".tmp"
        with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
            for p in proposals:
                f.write(json.dumps(p) + "\n")
        os.replace(tmp, PROPOSALS)


# ------------- CLI -------------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Human Adaptation Engine")
    ap.add_argument("command", choices=["analyze", "propose", "submit"])
    ap.add_argument("--user-focus")
    ap.add_argument("--target-file", default="qi/safety/policy_packs/global/mappings.yaml")
    ap.add_argument(
        "--config-targets",
        nargs="*",
        default=["qi/safety/policy_packs/global/mappings.yaml"],
    )
    args = ap.parse_args()

    engine = HumanAdaptEngine()

    if args.command == "analyze":
        stats = engine.analyze_satisfaction_patterns()
        print(json.dumps(stats, indent=2))
    elif args.command == "propose":
        proposals = engine.propose_tone_adaptations(target_file=args.target_file, user_focus=args.user_focus)
        print(
            json.dumps(
                {"proposals": len(proposals), "ids": [p["id"] for p in proposals]},
                indent=2,
            )
        )
    elif args.command == "submit":
        submitted = engine.submit_for_approval(config_targets=args.config_targets)
        print(json.dumps({"submitted": len(submitted), "ids": submitted}, indent=2))


if __name__ == "__main__":
    main()
