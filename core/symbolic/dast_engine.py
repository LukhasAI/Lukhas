"""DAST Core Engine

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Implements the task tracking and symbolic activity logic for the Golden Trio.
Follows the Phase 2 Implementation Guide.
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from ethics.core import EthicalDecision, get_shared_ethics_engine
from ethics.seedra import get_seedra
from symbolic.core import Symbol, SymbolicVocabulary, get_symbolic_vocabulary

logger = logging.getLogger(__name__)

def _clamp(value: float, minimum: float=0.0, maximum: float=1.0) -> float:
    """Clamp *value* between *minimum* and *maximum*."""
    return max(minimum, min(maximum, value))

def _to_datetime(value: Any) -> Optional[datetime]:
    """Attempt to coerce a timestamp-like value into a :class:`datetime`."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return None

@dataclass
class GestureScoreBreakdown:
    """Detailed scoring information for a single gesture."""
    score: float
    frequency: float
    context_relevance: float
    emotional_valence: float
    temporal_alignment: float
    metadata: dict[str, Any]

class DASTEngine:
    """Core DAST engine coordinating task tracking and activity scoring."""

    def __init__(self) -> None:
        self.seedra = get_seedra()
        self.symbolic: SymbolicVocabulary = get_symbolic_vocabulary()
        self.ethics = get_shared_ethics_engine()
        try:
            from orchestration.golden_trio import SystemType, get_trio_orchestrator
            self.orchestrator = get_trio_orchestrator()
            self.system_type = SystemType
        except Exception:
            self.orchestrator = None

            class _Sys:
                DAST = 'DAST'
                NIAS = 'NIAS'
            self.system_type = _Sys
        self.driftScore = 0.0
        self.affect_delta = 0.0
        self.task_engine = TaskCompatibilityEngine(self)
        self.activity_tracker = SymbolicActivityTracker(self)
        self.gesture_scorer = GestureScoringSystem()
        self.gesture_repository = GestureCorpusRepository()
        self.gesture_interpreter = GestureInterpretationSystem(self, scorer=self.gesture_scorer, repository=self.gesture_repository)
        self.data_aggregator = RealtimeDataAggregator(self)

    async def track_task(self, task: Any, user_context: dict[str, Any]) -> Symbol:
        """Track a task and return a symbolic representation."""
        return await self.activity_tracker.track_activity(task, user_context.get('user_id'))

class TaskCompatibilityEngine:
    """Scores task compatibility using SEEDRA and the ethics engine."""

    def __init__(self, engine: DASTEngine) -> None:
        self.engine = engine

    async def score_compatibility(self, task: Any, user_context: Any) -> float:
        consent = await self.engine.seedra.check_consent(user_context['user_id'], 'task_tracking')
        if not consent.get('allowed'):
            return 0.0
        task_symbol = self.engine.symbolic.create_symbol('task', {'task': str(task)})
        decision: EthicalDecision = await self.engine.ethics.evaluate_action({'type': 'track_task', 'data_type': 'behavioral_data'}, {'task': task_symbol.to_dict(), **user_context}, 'DAST')
        if decision.decision_type.value != 'allow':
            return 0.0
        return 1.0

class SymbolicActivityTracker:
    """Tracks symbolic activity for a user."""

    def __init__(self, engine: DASTEngine) -> None:
        self.engine = engine

    async def track_activity(self, activity: Any, user_id: str) -> Symbol:
        activity_symbol = self.engine.symbolic.create_symbol('activity', {'type': getattr(activity, 'type', str(activity)), 'timestamp': getattr(activity, 'timestamp', None)})
        if self.engine.orchestrator:
            await self.engine.orchestrator.send_message(source=self.engine.system_type.DAST, target=self.engine.system_type.NIAS, message_type='activity_update', payload=activity_symbol.to_dict())
        return activity_symbol

class GestureScoringSystem:
    """Compute normalized gesture scores across multiple symbolic factors."""

    def __init__(self) -> None:
        self._latest_breakdown: dict[str, GestureScoreBreakdown] = {}

    def score_gestures(self, gestures: Iterable[dict[str, Any]], context: dict[str, Any]) -> dict[str, float]:
        """Return normalized scores for each gesture in ``gestures``."""
        gestures_list = list(gestures)
        if not gestures_list:
            self._latest_breakdown = {}
            return {}
        gesture_types = [g.get('type', 'unknown') for g in gestures_list]
        frequency_counter = Counter(gesture_types)
        max_frequency = max(frequency_counter.values(), default=1)
        temporal_window = float(context.get('temporal_window', 120.0))
        now_context = _to_datetime(context.get('current_timestamp'))
        timestamps = [_to_datetime(g.get('timestamp')) for g in gestures_list if g.get('timestamp') is not None]
        if now_context is None and timestamps:
            now_context = max(timestamps)
        weights = context.get('gesture_weights', {'frequency': 0.25, 'context': 0.25, 'emotion': 0.25, 'temporal': 0.25})
        total_weight = sum(weights.values()) or 1.0
        breakdown: dict[str, GestureScoreBreakdown] = {}
        scores: dict[str, float] = {}
        active_contexts = set(context.get('active_contexts', []))
        default_context_relevance = float(context.get('default_context_relevance', 0.5))
        baseline_valence = float(context.get('baseline_emotional_valence', 0.0))
        for (index, gesture) in enumerate(gestures_list):
            gesture_id = str(gesture.get('id') or gesture.get('gesture_id') or f'gesture_{index}')
            gesture_type = gesture.get('type', gesture_id)
            frequency_score = _clamp(frequency_counter.get(gesture_type, 1) / max_frequency if max_frequency else 0.0)
            context_score = gesture.get('context_relevance')
            if context_score is None:
                gesture_tags = set(gesture.get('tags', []))
                if gesture_tags and active_contexts:
                    context_score = len(gesture_tags & active_contexts) / len(gesture_tags)
                else:
                    context_score = default_context_relevance
            context_score = _clamp(float(context_score))
            valence = gesture.get('emotional_valence', baseline_valence)
            try:
                valence = float(valence)
            except (TypeError, ValueError):
                valence = baseline_valence
            emotion_score = _clamp((valence + 1.0) / 2.0)
            if 'intensity' in gesture:
                try:
                    intensity = _clamp(float(gesture['intensity']))
                except (TypeError, ValueError):
                    intensity = 0.5
                emotion_score = (emotion_score + intensity) / 2.0
            gesture_timestamp = _to_datetime(gesture.get('timestamp'))
            if gesture_timestamp is None or now_context is None:
                temporal_score = 0.5
            else:
                delta_seconds = abs((now_context - gesture_timestamp).total_seconds())
                temporal_score = _clamp(1.0 - delta_seconds / max(temporal_window, 1.0))
            weighted_sum = frequency_score * weights.get('frequency', 0.25) + context_score * weights.get('context', 0.25) + emotion_score * weights.get('emotion', 0.25) + temporal_score * weights.get('temporal', 0.25)
            score = _clamp(weighted_sum / total_weight)
            breakdown[gesture_id] = GestureScoreBreakdown(score=score, frequency=frequency_score, context_relevance=context_score, emotional_valence=emotion_score, temporal_alignment=temporal_score, metadata={'type': gesture_type, 'timestamp': gesture.get('timestamp')})
            scores[gesture_id] = score
            logger.debug('# ΛTAG: gesture_scoring computed score', extra={'gesture_id': gesture_id, 'score': score, 'frequency': frequency_score, 'context': context_score, 'emotion': emotion_score, 'temporal': temporal_score})
        self._latest_breakdown = breakdown
        return scores

    def get_latest_breakdown(self) -> dict[str, GestureScoreBreakdown]:
        """Expose the most recent scoring breakdown for interpretation."""
        return self._latest_breakdown

class GestureCorpusRepository:
    """Retrieve gesture corpora with MATRIZ + file fallbacks."""

    def __init__(self, corpus_path: Optional[Path | str]=None) -> None:
        self._cache: dict[str, list[dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
        self._corpus_path = Path(corpus_path) if corpus_path is not None else Path(__file__).with_name('gesture_corpus.json')

    async def fetch_gesture_data(self, user_context: Optional[dict[str, Any]]=None, *, force_refresh: bool=False) -> list[dict[str, Any]]:
        """Retrieve gesture corpus using MATRIZ memory or a file fallback."""
        user_id = (user_context or {}).get('user_id', '__global__')
        if not force_refresh and user_id in self._cache:
            return self._cache[user_id]
        async with self._lock:
            if not force_refresh and user_id in self._cache:
                return self._cache[user_id]
            data = await self._fetch_from_matriz_memory(user_context or {})
            if not data:
                data = await self._fetch_from_file()
            if data is None:
                data = []
            self._cache[user_id] = data
            logger.debug('# ΛTAG: gesture_repository cache_update', extra={'user_id': user_id, 'entries': len(data)})
            return data

    async def _fetch_from_matriz_memory(self, user_context: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
        """Attempt to retrieve gesture data from MATRIZ memory systems."""
        try:
            from matriz.core.memory_system import get_memory_system
        except Exception:
            logger.debug('MATRIZ memory system unavailable for gesture fetch')
            return None
        try:
            memory_system = get_memory_system()
        except Exception as exc:
            logger.warning('Failed to initialize MATRIZ memory system: %s', exc)
            return None
        fetcher = None
        for candidate_name in ('get_gesture_corpus', 'fetch_gesture_corpus'):
            fetcher = getattr(memory_system, candidate_name, None)
            if fetcher:
                break
        if fetcher is None:
            logger.debug('Gesture corpus API not exposed by MATRIZ memory system')
            return None
        try:
            result = fetcher(user_context)
            if asyncio.iscoroutine(result):
                result = await result
            if isinstance(result, dict):
                return list(result.get('gestures', []))
            if isinstance(result, list):
                return result
        except Exception as exc:
            logger.warning('Error fetching gestures from MATRIZ memory: %s', exc)
            return None
        return None

    async def _fetch_from_file(self) -> list[dict[str, Any]]:
        """Load gesture corpus from the fallback file path."""
        if not self._corpus_path.exists():
            logger.debug('Gesture corpus fallback file missing', extra={'path': str(self._corpus_path)})
            return []
        try:
            contents = self._corpus_path.read_text(encoding='utf-8')
            data = json.loads(contents)
            if isinstance(data, dict):
                return list(data.get('gestures', []))
            if isinstance(data, list):
                return data
        except Exception as exc:
            logger.warning('Failed to read gesture corpus fallback: %s', exc)
        return []

class GestureInterpretationSystem:
    """Interprets gestures using the ethics engine."""

    def __init__(self, engine: Optional[DASTEngine], *, scorer: Optional[GestureScoringSystem]=None, repository: Optional[GestureCorpusRepository]=None, ethics: Optional[Any]=None, symbolic: Optional[SymbolicVocabulary]=None) -> None:
        self.engine = engine
        self.scorer = scorer or GestureScoringSystem()
        self.repository = repository or GestureCorpusRepository()
        self._ethics = ethics or (engine.ethics if engine else None)
        self._symbolic = symbolic or (engine.symbolic if engine else None)

    async def interpret(self, gestures: list[dict[str, Any]], user_context: dict[str, Any]) -> dict[str, Any]:
        """Return a structured symbolic interpretation for gestures."""
        if self._ethics is not None:
            decision = await self._ethics.evaluate_action({'type': 'interpret_gestures', 'data_type': 'biometric'}, {'gestures': gestures, **user_context}, 'DAST')
            if isinstance(decision, EthicalDecision) and decision.decision_type.value != 'allow':
                logger.info('Gesture interpretation denied by ethics engine')
                return {'states': [], 'scores': {}, 'anomalies': [{'type': 'ethics_denied', 'confidence': getattr(decision, 'confidence', 0.0)}], 'metrics': {'average_score': 0.0, 'drift_indicator': 0.0, 'affect_delta': 0.0}, 'overall_confidence': 0.0}
        scores = self.scorer.score_gestures(gestures, user_context)
        breakdown = self.scorer.get_latest_breakdown()
        metrics = self._compute_metrics(breakdown)
        states = self._map_states(breakdown, metrics, gestures)
        anomalies = self._detect_anomalies(breakdown, metrics)
        interpretation = {'states': states, 'scores': scores, 'anomalies': anomalies, 'metrics': metrics, 'overall_confidence': metrics.get('confidence', 0.0)}
        logger.debug('# ΛTAG: gesture_interpretation summary', extra={'states': [state['state'] for state in states], 'confidence': interpretation['overall_confidence'], 'drift_indicator': metrics.get('drift_indicator', 0.0)})
        return interpretation

    async def interpret_gesture(self, gesture_data: dict[str, Any], user_context: dict[str, Any]) -> Optional[Symbol]:
        """Compatibility shim returning a symbolic gesture interpretation."""
        interpretation = await self.interpret([gesture_data], user_context)
        if not interpretation.get('states') or self._symbolic is None:
            return None
        symbol = self._symbolic.create_symbol('gesture', {'interpretation': interpretation['states'], 'confidence': interpretation.get('overall_confidence', 0.0)})
        return symbol

    def _compute_metrics(self, breakdown: dict[str, GestureScoreBreakdown]) -> dict[str, float]:
        if not breakdown:
            return {'average_score': 0.0, 'drift_indicator': 0.0, 'affect_delta': 0.0, 'confidence': 0.0}
        count = len(breakdown)
        average_score = sum((item.score for item in breakdown.values())) / count
        average_context = sum((item.context_relevance for item in breakdown.values())) / count
        average_emotion = sum((item.emotional_valence for item in breakdown.values())) / count
        average_temporal = sum((item.temporal_alignment for item in breakdown.values())) / count
        affect_delta = average_emotion * 2.0 - 1.0
        drift_indicator = _clamp(1.0 - average_context)
        confidence = _clamp((average_score + average_temporal) / 2.0)
        return {'average_score': average_score, 'average_context': average_context, 'average_emotion': average_emotion, 'average_temporal': average_temporal, 'drift_indicator': drift_indicator, 'affect_delta': affect_delta, 'confidence': confidence}

    def _map_states(self, breakdown: dict[str, GestureScoreBreakdown], metrics: dict[str, float], gestures: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not breakdown:
            return []
        states: list[dict[str, Any]] = []
        average_score = metrics.get('average_score', 0.0)
        drift_indicator = metrics.get('drift_indicator', 0.0)
        affect_delta = metrics.get('affect_delta', 0.0)
        if average_score >= 0.7 and drift_indicator <= 0.3:
            states.append({'state': 'focused', 'confidence': _clamp(average_score - drift_indicator / 2.0), 'supporting_gestures': self._top_gestures(breakdown, limit=3), 'signals': {'affect_delta': affect_delta}})
        if affect_delta <= -0.2:
            states.append({'state': 'stressed', 'confidence': _clamp(abs(affect_delta)), 'supporting_gestures': self._gestures_with_low_emotion(breakdown), 'signals': {'affect_delta': affect_delta}})
        if drift_indicator >= 0.6:
            states.append({'state': 'drifting', 'confidence': _clamp(drift_indicator), 'supporting_gestures': self._gestures_with_low_context(breakdown), 'signals': {'drift_indicator': drift_indicator}})
        if not states:
            states.append({'state': 'calm', 'confidence': _clamp(metrics.get('average_emotion', 0.5)), 'supporting_gestures': self._top_gestures(breakdown, limit=2), 'signals': {'affect_delta': affect_delta}})
        tag_counter = Counter((tag for gesture in gestures for tag in gesture.get('tags', [])))
        if tag_counter.get('analysis', 0) >= 2:
            states.append({'state': 'cognitive_analysis', 'confidence': _clamp(average_score), 'supporting_gestures': self._top_gestures(breakdown, limit=2), 'signals': {'tag_frequency': tag_counter.get('analysis', 0)}})
        return states

    def _detect_anomalies(self, breakdown: dict[str, GestureScoreBreakdown], metrics: dict[str, float]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        if not breakdown:
            return anomalies
        average_score = metrics.get('average_score', 0.0)
        for (gesture_id, detail) in breakdown.items():
            if detail.context_relevance <= 0.2 and detail.temporal_alignment <= 0.2:
                anomalies.append({'type': 'context_misalignment', 'gesture_id': gesture_id, 'confidence': _clamp(1.0 - detail.context_relevance)})
            if abs(detail.score - average_score) >= 0.4:
                anomalies.append({'type': 'score_outlier', 'gesture_id': gesture_id, 'confidence': _clamp(abs(detail.score - average_score))})
        return anomalies

    def _top_gestures(self, breakdown: dict[str, GestureScoreBreakdown], *, limit: int) -> list[str]:
        return [gesture_id for (gesture_id, _) in sorted(breakdown.items(), key=lambda item: item[1].score, reverse=True)[:limit]]

    def _gestures_with_low_emotion(self, breakdown: dict[str, GestureScoreBreakdown]) -> list[str]:
        return [gesture_id for (gesture_id, detail) in breakdown.items() if detail.emotional_valence <= 0.4]

    def _gestures_with_low_context(self, breakdown: dict[str, GestureScoreBreakdown]) -> list[str]:
        return [gesture_id for (gesture_id, detail) in breakdown.items() if detail.context_relevance <= 0.4]

class RealtimeDataAggregator:
    """Aggregates external data sources respecting user consent."""

    def __init__(self, engine: DASTEngine) -> None:
        self.engine = engine

    async def aggregate_external_data(self, data_sources: list[str], user_id: str) -> dict[str, Symbol]:
        aggregated: dict[str, Symbol] = {}
        for source in data_sources:
            consent = await self.engine.seedra.check_consent(user_id, f'external_data_{source}')
            if consent.get('allowed'):
                data = {}
                aggregated[source] = self.engine.symbolic.create_symbol(f'{source}_data', data)
        return aggregated
